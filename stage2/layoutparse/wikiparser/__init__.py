from ..layoutparser import Layoutparser
from headparser import HeadParser
from linkmatch import Linkmatch
import re
import nltk
import HTMLParser

class H1Parser(HeadParser):
	re_head = re.compile(r"(?:^|\n)\s*==\s*(.*?)\s*==\s*(?=\n)")

class ItemParser(HeadParser):
	re_head = re.compile(r"(?:^|\n)\s*[*#]\s*(.*?)(?=\n|$)")

class WikiParser(Layoutparser):
	re_html = re.compile(r"</?[a-zA-Z]+\s*/?>")
	html_parser = HTMLParser.HTMLParser()

	def preparse(self, text):
		text = Linkmatch.sub(text)
		text = text.replace("'''", "")
		text = text.replace("''", "")
		text = self.re_html.sub("", text)
		text = self.html_parser.unescape(text)
		return text

	def parseText(self, text):
		#TODO
		# verify this is a recipe -> {{recipe}}

		#TODO
		# extract metadata from {{recipesummary}}
		# {{recipesummary|$ignore|$servings|$time|$difficulty|$ignore...}}

		#TODO
		# Basic Format I:
		# == Ingredients ==
		# *$ingredients...
		# == Procedure == | == Method == //ignore spaces
		# #$steps... | *$steps...

		# ignore subheadings and text
	
		# recognize == Notes, tips, and variations ==
		# issue warnings for all other sections

		# Implementation:

		# Use a Section.parse to find all section headings
		# Use this array to create Section objects with headline/body
		d = H1Parser().parse(text).toDict()


		d['Ingredients'] = map(self.preparse, ItemParser().parse(d['Ingredients']).toList())
		d['Procedure'] = ItemParser().parse(d['Procedure']).toList()
		for i, step in enumerate(d['Procedure']):
			d['Procedure'][i] = map(self.preparse, nltk.sent_tokenize(step))

		return d

		# Use an Item.parse to find all items
		# Use this array to create Item objects

		#NOTE: for Procedure, also parse Sentence
		#	-> use punkt tokenizer
		#NOTE: if no items in procedure, only parse Sentence

		# Store as Sections:
		# dict[section] = 
		# store as Blocks:
		# Block(text, ((Item, 1), (Sentence, 4)) )
