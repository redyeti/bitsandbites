import nltk

def nltk_depends():
	ressources = [
		"maxent_treebank_pos_tagger",
		"maxent_ne_chunker",
		"words",
		"brown",
		"conll2000",
		"punkt",
	]
	dl = nltk.downloader.Downloader("http://nltk.github.com/nltk_data/")
	for r in ressources:
		dl.download(r)


nltk_depends()
