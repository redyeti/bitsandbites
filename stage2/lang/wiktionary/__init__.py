import urllib2, urllib
import json
import db

TOS_CATEGORIES = {
	"Category:English verbs": "VB",
	"Category:English plurals": "NNS",
	"Category:English nouns": "NN",
	"Category:English adjectives": "JJ",
	"Category:English present participles": "VBG",
}

class WiktionaryWordType(db.Document):
	word = db.StringField(required=True, primary_key=True)
	type = db.StringField()

def lookupTos(w):
	cached = WiktionaryWordType.objects(word=w)
	print cached
	if cached:
		print "USING CACHED WIKT RESULT:", w
		return cached[0].type

	print "LOOKING UP WIKT RESULT:", w

	u = urllib2.urlopen(
		"http://en.wiktionary.org/w/api.php?" + urllib.urlencode(dict(
			action = "query",
			titles = w.lower(),
			prop = "categories",
			format = "json",
			cllimit = "500",
		))
	)

	data = json.loads(u.read())
	try:
		data = data["query"]["pages"].values()[0]["categories"]
	except KeyError:
		WiktionaryWordType(word=w, type=None).save()
		return None
	data = [x["title"] for x in data]
	# take the order of the categories into account: 
	# categories mentioned first are more probable!
	for d in data:
		if d in TOS_CATEGORIES:
			WiktionaryWordType(word=w, type=TOS_CATEGORIES[d]).save()
			return TOS_CATEGORIES[d]
	WiktionaryWordType(word=w, type=None).save()
	return None
