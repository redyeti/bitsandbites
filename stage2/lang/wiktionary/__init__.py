import urllib2, urllib
from lxml import etree
import db

TOS_CATEGORIES = {
	"Category:English verbs": "VB",
	"Category:English plurals": "NNS",
	"Category:English nouns": "NN",
	"Category:English adjectives": "JJ",
	"Category:English adverbs": "RB",
	"Category:English present participles": "VBG",
	"Category:English third-person singular forms": "VBZ",
	"Category:English past participles": "VBN",
	"Category:English conjuctions": "CS",
}

class WiktionaryWordType(db.Document):
	word = db.StringField(required=True, primary_key=True)
	type = db.StringField()

def lookupTos(w, redirect=True):
	cached = WiktionaryWordType.objects(word=w)
	print cached
	if cached:
		print "USING CACHED WIKT RESULT:", w
		return cached[0].type

	print "LOOKING UP WIKT RESULT:", w

	# IMPORTANT:
	# Use the actual wikipedia page instead of the API because in the page
	# the category links are in document order and thus ordered by probability!

	try:
		u = urllib2.urlopen(
			"http://en.wiktionary.org/w/index.php?" + urllib.urlencode(dict(
				title = w.lower(),
			))
		)
	except (urllib2.HTTPError, urllib2.URLError) :
		WiktionaryWordType(word=w, type=None).save()
		return None

	global html
	html = etree.HTML(u.read())
	data = html.xpath("//div[@id='mw-normal-catlinks']//a/@title")

	print data
	# take the order of the categories into account: 
	# categories mentioned first are more probable!
	for d in data:
		if d in TOS_CATEGORIES:
			WiktionaryWordType(word=w, type=TOS_CATEGORIES[d]).save()
			return TOS_CATEGORIES[d]

	if redirect and (
			"Category:English abbreviations" in data or
			"Category:English colloquialisms" in data or
			"Category:English suffixes" in data):
		ref = html.xpath("//div[@id='mw-content-text']//ol//a/@title")[0]
		res = lookupTos(ref, False)
		WiktionaryWordType(word=w, type=res).save()
		return res
		

	print "--------------------------"
	print "Undecided Word:", w
	print data
	print "--------------------------"

	WiktionaryWordType(word=w, type=None).save()
	return None
