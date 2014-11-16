import sys
reload(sys)
sys.setdefaultencoding("utf8")

from stage1 import fetch
from stage2.layoutparse import Layoutparser
from pprint import pprint

from stage2 import lang

# -- stage 1 --
#fetch.wikibooks(["Cake recipes"])

# -- stage 2 --
d = Layoutparser.parseDB().next()
pprint(d)

for step in d['Procedure']:
	for sentence in step:
		print lang.process(sentence)

for line in d['Ingredients']:
	print lang.process(line)
