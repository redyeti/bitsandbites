import urllib2, urllib
import json
from pprint import pprint

def query(base, args):
	myargs = args.copy()
	myargs['continue'] = ""
	myargs['format'] = "json"
	myargs['action'] = "query"

	while True:
		print "Fetching page ..."
		print urllib.urlencode(myargs)
		u = urllib2.urlopen(
			base + "?" + urllib.urlencode(myargs)
		)

		page = u.read()
		data = json.loads(page)

		if 'error' in data:
			raise RuntimeError(data['error'])
		if 'warnings' in data:
			print data['warnings']
		if 'query' in data:
			yield data['query']
		if 'continue' in data:
			myargs.update(data['continue'])
		else:
			break

if __name__ == "__main__":
	g = query("http://en.wiktionary.org/w/api.php", dict(
			titles = "cheddar",
			prop = "categories",
			format = "json",
	))

	pprint(g)
	print "---------"
	for x in g:
		pprint(x)
