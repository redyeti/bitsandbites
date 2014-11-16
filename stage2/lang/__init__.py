#-*- coding: utf8 -*-
import nltk
import os
import types

try:
	import cPickle as pickle
except ImportError:
	import pickle
import re
import wiktionary

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


def splitTagUnit(i,w,t,c):
	RE_SPLIT_UNIT = re.compile(r"([0-9]+)(.*)")
	if w[0].isdigit():
		n, u = RE_SPLIT_UNIT.match(w).groups()
		yield (n, "CD")
		if u:
			yield (u, "NP")
tags = [
	# tuples: (word, tag)
	# or functions: (index, word, tag, context) -> tag
	splitTagUnit,
	(u"°", "U°"),
	(u"½", "AT"),
	(u"¼", "AT"),
	(u"¾", "AT"),
	(u"⅜", "AT"),
	(u"⅝", "AT"),
	(u"⅞", "AT"),
	(u"⅛", "AT"),
	lambda i,w,t,c: wiktionary.lookupTos(w),
	lambda i,w,t,c: "AT" if i>0 and c[i-1][1] else None,
	lambda i,w,t,c: "UNK"
]

def fixtags(tagged):
	# okay, this looks ugly, but it simplifies
	# the definition of manual tag entries as
	# above
	for i,(w,t) in enumerate(tagged):
		if t is None:
			newtag = None
			itertags = iter(tags)
			while True:
				nexttag = itertags.next()
				if isinstance(nexttag, tuple):
					if nexttag[0] == w:
						yield (w, nexttag[1])
						break
				else:
					n = nexttag(i,w,t,tagged)
					if isinstance(n, types.GeneratorType):
						one = False
						for x in nexttag(i,w,t,tagged):
							yield x
							one = True
						if one:
							break
					elif n is not None:
						yield (w, n)
						break
		else:
			yield (w,t)

def process(sentence):
	tokens = nltk.word_tokenize(sentence)
	tagged = tt.tag(tokens)


	tagged = list(fixtags(tagged))

	grammar = ur"""
		COUNTER:
			{<CD|CD-HL|AT>+ }
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
			{<COUNTER> <NNS?>? } <.*>
			{<COUNTER> <NNS?> <(> <COUNTER> <NNS?> <)> } <.*>
			{<COUNTER> <NP>}
			{<COUNTER> <U°> <NP|NNS?>}

		UNIT:
			{ <UNIT> <\(> <UNIT> <\)> }

		ENTITY:
			{<UNIT>? <IMP>? <NNS?|VBG>* <NNS?>}
			{<PPS>}
			{<UNIT>? <IMP>? <NNS?>* <VBG>} <,|CC|.>

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
		

	return t
