import fetch
from layoutparse import Layoutparser
from pprint import pprint

#fetch.wikibooks(["Cake recipes"])
d = Layoutparser.parseDB().next()
pprint(d)
