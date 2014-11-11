from fetcher import Fetcher, RawRecipe
import mwapi

class WikibooksFetcher(Fetcher):
	def fetch(self, categories=["Recipes"]):
		for cat in categories:
			for doc in self.fetchPage(cat):
				yield doc

	def fetchPage(self, category):
		g = mwapi.query("http://en.wikibooks.org/w/api.php", dict(
			generator = "categorymembers",
			gcmtitle = category if category.startswith("Category:") else "Category:"+category,
			gcmlimit = "100",
			prop = "revisions",
			rvprop = "content",
		))
		for querypage in g:
			for page in querypage['pages'].values():
				pageid = page['pageid']
				payload = page['revisions'][0]["*"]
				uid = "{http://en.wikibooks.org:%i}" % pageid
				doc = RawRecipe(uid=uid, payload=payload, format="wiki")
				doc.save()
				yield doc
