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

from collections import namedtuple
TagTuple = namedtuple("TagTuple", "word tag")
def prettify(tagged):
	return [TagTuple(*x) for x in tagged]

tags = [
	# tuples: (word, tag)
	# or functions: (index, word, tag, context) -> tag
	splitTagUnit,
	TagTuple(u"°", "U°"),
	TagTuple(u"½", "AT"),
	TagTuple(u"¼", "AT"),
	TagTuple(u"¾", "AT"),
	TagTuple(u"⅜", "AT"),
	TagTuple(u"⅝", "AT"),
	TagTuple(u"⅞", "AT"),
	TagTuple(u"⅛", "AT"),
	lambda i,w,t,c: wiktionary.lookupTos(w),
	lambda i,w,t,c: "AT" if i>0 and c[i-1][1] else None,
	lambda i,w,t,c: "UNK"
]

def completeTags(tagged):
	"""Completes Tags tagged with None."""
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
					if nexttag.word == w:
						yield (w, nexttag.tag)
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



def fixTags(tagged, step=True):
	"""Correct typical tagging errors"""
	for i, c in enumerate(tagged):
		if c.tag == "MD" and i>=1 and tagged[i-1].tag.startswith("CD"):
			yield (c.word, "NN")
		elif c.tag == "VBZ" and i>=1 and tagged[i-1].tag == "AT":
			yield (c.word, "NNS")
		elif c.word == "in" and i>=1 and tagged[i-1].tag == "VB":
			yield (c.word, "INX")
		elif c.tag == "VB" and i>=1 and tagged[i-1].tag == "AT":
			yield (c.word, "NN")
		elif c.tag == "NN" and i>=2 and tagged[i-1].tag == "CC" and tagged[i-2].tag == "VB":
			yield (c.word, "VB")
		elif step and i == 0 and c.tag in ("NN","NP"):
			yield (c.word, "VB")
		elif c.word.lower() == "extract" and i>=1 and tagged[i-1].tag == "NN":
			yield (c.word, "NN")
		elif c.word.lower() in ("heat","pinch"):
			yield (c.word, "NN")
		else:
			yield c

def process(sentence, step=True):
	tokens = nltk.word_tokenize(sentence)
	tagged = prettify(tt.tag(tokens))
	tagged = prettify(completeTags(tagged))
	tagged = prettify(fixTags(tagged, step))

	grammar = ur"""
		COUNTER:
			{<ABN> <AT>}
			{<CD|CD-.*|AT>+ }

		COUNTER:
			{<COUNTER> <TO|IN> <COUNTER>}

		VERB:
			{<VB> <INX>?}
			{<VB> <TO|IN>?}
			# {<VBG> <TO|IN>}
			# {<VBG>} <COUNTER|AT>
			(^ | <,> ) { <NP|JJ-TL> }

		VERB:
			{ <VERB> <CC> <VERB> }

		IMP:
			{<UNK|JJR?|RB|RP|QL|QLP|DT>+}
			{<VBN>} <NNS?|NP>

		UNIT:
			{<COUNTER> <NP> <IN>?}
			{<COUNTER> <NNS?>? <IN>?} <VBG|VBD|IMP|NNS?|\(|\)>
			{<COUNTER> <NNS?> <IN>?}
			{<COUNTER> <NNS?> <(> <COUNTER> <NNS?> <)> <IN>? } <.*>
			{<COUNTER> <U°> <NP|NNS?> <IN>?}

		UNIT:
			{ <UNIT> <\(> <UNIT> <\)> <IN>? }

		ENTITY:
			{<UNIT>? <IMP>? <NNS?|VBG|VBD|NN-HL>* <NNS?|NN-HL>}
			{<PPS|PPO>}
			{<UNIT>? <IMP>? <NNS?|NN-HL>* <VBG|VBD>} <,|CC|.>

		LIST:
			{<ENTITY> (<,>? <,|CC> <ENTITY>)* }
			{<ENTITY>}

		SETTING: 
			{<IN> <IMP>? <LIST>}
			{<IN|TO> <LIST>}
			{<CS> <IMP>? <VBN>}

		INSTRUCT:
			# { (<SETTING> <,>?)? <VERB> <IMP>? <SETTING>* <LIST>? <TO|IN> <LIST> <SETTING>* <IMP>?}
			{ (<SETTING> <,>?)? <VERB> <IMP>? <SETTING>* <LIST> <IMP>? <SETTING>* <IMP>?}
			{ (<SETTING> <,>?)? <VERB> <IMP>? <SETTING>* <IMP>?}

		AVOID:
			{<DO> <\*> <INSTRUCT>}
			
	"""
	cp = nltk.RegexpParser(grammar)

	t = cp.parse([tuple(x) for x in tagged])
	told = None

	while told != t:
		told = t
		t = cp.parse(t)
		

	return t
