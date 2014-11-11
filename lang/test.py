#-*- coding: utf8 -*-
import nltk
import os
import time
try:
	import cpickle as pickle
except ImportError:
	import pickle
import re
import wiktionary

import sys
reload(sys)
sys.setdefaultencoding("utf8")

#sentence = "In large bowl, combine 1-1/2 cups flour and yeast. "
#sentence = "Mix water, 3 tablespoons sugar and salt together, and add to the dry ingredients."
#sentence = "Beat with a mixer for half a minute at a low speed, scraping the sides of the bowl clean."
#sentence = "Beat at a higher speed for 3 minutes."
#sentence = "Then, by hand, mix in enough flour to make a moderately stiff dough."
#sentence = "Preheat oven to 300 F (150C)."
#sentence = "Grate the cheddar."
#
## THIS ONE IS DIFFICULT:
#sentence = "In a large bowl, blend the margarine and cheddar."
#
#sentence = "Add the flour, salt, and powdered cayenne pepper to the bowl."
#sentence = "Stir in the cereal"
#sentence = "Mix it thoroughly."
#sentence = "Shape into small balls, flattening each ball with a fork. Place each cookie onto an ungreased cookie sheet."
#sentence = "Bake at 300F (150C) for 20 minutes.""
#sentence = u"Preheat oven to 425 °F (220 °C)"
#sentence = "Grease muffin pans with cold butter, shortening, or pan spray"
#sentence = "In a large bowl, thoroughly combine flour, oats, baking powder and baking soda"
#sentence = "In a smaller bowl, thoroughly combine eggs, sugar, milk, oil, apple, cinnamon, nutmeg, salt, vanilla and raisins"
#sentence = "Add wet ingredients to the dry ingredients and mix with bare hands until just combined."
#sentence = "Do not overmix!"
#
## VERY DIFFICULT SENTENCE!
sentence = u"Fill muffin cups about three-quarters full, then place on oven's upper rack and turn the oven down to 375 °F (190 °C)"
## ALSO DIFFICULT
#sentence = u"Turn muffin pans 180° after 10 minutes; check for doneness after 15 minutes"
#sentence = "Muffins usually take 20 to 25 minutes to cook completely"
#sentence = "Allow to cool briefly (2-5 minutes) before removing from pan"

print "tokens:"

tokens = nltk.word_tokenize(sentence)
#tagged = nltk.pos_tag(tokens)
print tokens


print "prepare tagging"

class InstanceLoader(object):
	def __new__(cls, *args, **params):
		inst = object.__new__(cls)
		
		here = os.path.dirname(cls.basefile)
		instancefile = os.path.join(here, cls.filename)
		if os.path.isfile(instancefile):
			print "%s: Loading instance ..." % cls.__name__
			with open(instancefile) as f:
				return pickle.load(f)
		else:
			print "%s: Creating instance ..." % cls.__name__
			instance = inst.createInstance(*args, **params)
			with open(instancefile,"w") as f:
				pickle.dump(instance, f)
				return instance
	
class UnigramTaggerLoader(InstanceLoader):
	basefile = __file__
	filename = "tagger_unigram.pickle"

	def createInstance(cls):
		from nltk.corpus import brown
		brown_tagged_sents = brown.tagged_sents()
		return nltk.UnigramTagger(brown_tagged_sents)
		
class BigramTaggerLoader(InstanceLoader):
	basefile = __file__
	filename = "tagger_bigram.pickle"

	def createInstance(cls, backoff):
		from nltk.corpus import brown
		brown_tagged_sents = brown.tagged_sents()
		return nltk.BigramTagger(brown_tagged_sents, backoff=backoff)

class TrigramTaggerLoader(InstanceLoader):
	basefile = __file__
	filename = "tagger_trigram.pickle"

	def createInstance(cls, backoff):
		from nltk.corpus import brown
		brown_tagged_sents = brown.tagged_sents()
		return nltk.TrigramTagger(brown_tagged_sents, backoff=backoff)

ut = UnigramTaggerLoader()
bt = BigramTaggerLoader(ut)
tt = TrigramTaggerLoader(bt)

print "tags:"

tagged = tt.tag(tokens)

print tagged

def fixtags(tagged):
	RE_SPLIT_UNIT = re.compile(r"([0-9]+)(.*)")

	for i,(w,t) in enumerate(tagged):
		if t is None:
			if w[0].isdigit():
				n, u = RE_SPLIT_UNIT.match(w).groups()
				yield (n, "CD")
				if u:
					yield (u, "NP")
			elif w == u"°":
				yield (w, "U°")
			elif wiktionary.lookupTos(w) is not None:
				yield (w, wiktionary.lookupTos(w))
			elif i>0 and tagged[i-1][1] == "AT":
				yield (w, "NN")
			else:
				yield (w,"UNK")
		else:
			yield (w,t)

tagged = list(fixtags(tagged))

print "chunk:"
grammar = ur"""
	COUNTER:
		{<CD>}
		{<ABN> <AT>}

	COUNTER:
		{<COUNTER> <TO> <COUNTER>}

	VERB:
		{<VB> <TO|IN>?}
		{<VBG> <TO|IN>}
		{<VBG>} <COUNTER|AT>
		(^ | <,> ) { <NP|JJ-TL> }

	IMP:
		{<UNK|JJR?|RB|RP|QL|QLP|DT>+}
		{<VBN>} <NNS?|NP>

	UNIT:
		{<COUNTER> <NNS?>? }<NNS?>
		{<COUNTER> <NP>}
		{<COUNTER> <U°> <NP|NNS?>}

	UNIT:
		{ <UNIT> <\(> <UNIT> <\)> }

	ENTITY:
		{<AT> <IMP>? <NNS?|VBG>* <NNS?>}
		{<UNIT>? <IMP>? <NNS?|VBG>* <NNS?>}
		{<PPS>}
		{<AT>? <IMP>? <NNS?>* <VBG>} <,|CC|.>

	SETTING: 
		{<IN> <IMP>? <LIST>}
		{<IN|TO> <UNIT>}
		{<CS> <IMP>? <VBN>}

	LIST:
		{<ENTITY> (<,> <ENTITY>)* <,>? <CC> <ENTITY>}
		{<ENTITY>}

	INSTRUCT:
		{ (<SETTING> <,>?)? <VERB> <SETTING>* <LIST>? <TO|IN> <LIST> <SETTING>* <IMP>?}
		{ (<SETTING> <,>?)? <VERB> <SETTING>* <LIST> <IMP>? <SETTING>* <IMP>?}
		{ (<SETTING> <,>?)? <VERB> <SETTING>* <IMP>?}

	AVOID:
		{<DO> <\*> <INSTRUCT>}
		
"""
cp = nltk.RegexpParser(grammar)

t = cp.parse(tagged)
told = None

while told != t:
	told = t
	t = cp.parse(t)
	
print t

