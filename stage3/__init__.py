#-*- coding: utf8 -*-
import db
import traceback

GREEDY = True

#from pprint import pprint

# a. define instruction families sharing a signature

# define
# - initialize objects and set pointers

# simple-inplace
# - operate on entities in parallel
# - no transfer/repointing

# simple-combine
# - repoint entites to their new sets

# refactor
# - delete old entities and create new ones

# most of the operations need lookups:
# - {output(s)} <-- INSTRUCT({input(s)}, {setting(s)}, {meta})
# datasets have a flat format:
# ({basictype, op{meta}...}, {meta...})

# b. identify entities as ingrediences, tools or other
#    1. use declarations
#    2. use database
#    3. use wikibook lookup

# Precompile instructions/ Instruction Lookup:
# - Sentence -> FN(...)
# - Storage: None
# Compile instructions by resolving the pointers Pointer Lookup:
# - FN(sentence_args...) -> FN(pointer_args...) # use FN.defines, FN.deletes
# - Storage: Embedded (Recipe Source Code)
# Run the code by just using the pointers:
# - RuntimeEnvironment = {pointers, ...}
# - RuntimeEnvironment.execute(FN...)
# - Storage: Document (before.serialize, FN.name, after.serialize)

IGNORE_LIST = {
	"minutes",
}

class InstructionError(RuntimeError):
	def __init__(self, msg, context):
		RuntimeError.__init__(self, msg)
		self.__context = context
		traceback.print_exc()
		
	@property
	def context(self):
		return self.__context

class InstructionAssertError(InstructionError):
	def __init__(self, msg, context):
		RuntimeError.__init__(self, "Invalid usage.", context)
	@property
	def key(self):
		return "*OP"


class InstructionLookupError(InstructionError):
	def __init__(self, ins, context):
		InstructionError.__init__(self, "Could not lookup instruction: "+ins, context)
		self.__ins = ins

	@property
	def instruction(self):
		return self.__ins

	@property
	def key(self):
		return "+"+self.__ins

class PointerResolutionError(InstructionError):
	def __init__(self, p, context):
		InstructionError.__init__(self, "Could not resolve pointer: "+p, context)
		self.__p = p

	@property
	def pointer(self):
		return self.__p

	@property
	def key(self):
		return "@"+self.__p

from collections import MutableMapping

class Remap(object):
	def __init__(self, *args):
		self.__s = set(args)
		
	def __call__(self, cls):
		for r in self.__s:
			cls.remap[r] = self.__s
		return cls

@Remap("bread crumbs", "breadcrumbs")
@Remap("vanilla extract", "vanilla essence")
@Remap("cake meal", "meal")
@Remap("cake meal", "meal")
@Remap("cake flour", "flour")
class Lookup(MutableMapping):
	remap = {
	}

	def __init__(self, p):
		self.__p = p

	def __getitem__(self, i):
		try:
			return self.__p[i]
		except KeyError as e:
			if i in ("them", "mixture","ingredients"):
				return self.__p["_"]
			
			for r in self.remap.get(i, ()):
				if r in self.__p:
					return self.__p[r]
			raise

	def __setitem__(self, i, v):
		self.__p[i] = v

	def __delitem__(self, i):
		del self.__p[i]

	def  __iter__(self):
		return iter(self.__p)

	def  __len__(self):
		return len(self.__p)

class RuntimeEnvironment(object):
	def __init__(self):
		self.__pointers = {}
		self.__p = Lookup(self.__pointers)

	@property
	def pointers(self):
		return self.__p

	@property
	def html(self):
		from lxml.html import builder as E
		return E.TABLE(
			E.CLASS("register"),
			E.TR(
				E.TH(
					"Register Table",
					colspan = "3"
				)
			),
			*[E.TR(E.TD(k), E.TD(E.CLASS("fixed"), "%x"%id(v)), E.TD(str(v))) for k,v in self.__p.iteritems()]
		)
		

#class DbObject(db.EmbeddedDocument):
#	primary = db.StringField()
#	data = db.DictField()
#
#	def __str__(self):
#		return "%(primary)s: %(data)s" % self
#	__repr__ = __str__

class DataObject(object):
	def __init__(self,primary, data):
		self.__primary = primary
		self.__data = data

	@property
	def primary(self):
		return self.__primary

	def __setitem__(self, i, v):
		self.__data[i] = v

	def __getitem__(self, i):
		return self.__data[i]

	@property
	def data(self):
		return self.__data

	def toDbObject(self):
		return self.__data.copy()

	def __repr__(self):
		return repr(self.__data)

class RuleSample(db.Document):
	name = db.StringField(required=True)
	inPointers = db.ListField()
	outPointers = db.ListField()
	inData = db.ListField()
	outData = db.ListField()
	requires = db.ListField()
	index = db.IntField()

	def __str__(self):
		return "%(name)s %(inPointers)s/%(inData)s -> %(outPointers)s/%(outData)s" % self

	@property
	def html(self):
		from lxml.html import builder as E
		return E.TABLE(
			E.CLASS("instruct"),
			E.TR(
				E.TH(
					"Instruction",
					colspan = "2"
				)
			),
			E.TR(E.TD(
				str(tuple(self.outPointers)) +
				" ← "+self.name +
				str(tuple(self.inPointers)),
				colspan = "2"
			)),
			E.TR(
				E.TD(
					*[E.DIV(str(k)) for k in self.outData]
				),
				E.TD(
					*[E.DIV(str(k)) for k in self.inData]
				),
			),
		)

	__repr__ = __str__

class RasmInstruction(db.Document):
	name = db.StringField(primary_key=True)
	words = db.ListField(required=True)
	meta = {
		"allow_inheritance": True,
		"indexes" : ['words'],
	}

	def foreach(self, re, entities):
		for ent in entities:
			if ent in IGNORE_LIST:
				continue #FIXME: handle this intelligently!
			try:
				for ing in re.pointers[ent]:
					yield ent, ing
			except KeyError:
				if not GREEDY: raise

RasmInstruction.objects.delete()	

class RasmInstance(object):
	def __init__(self, name, words, **params):
		self.__name = name
		self.__words = words
		self.__params = params

	def __call__(self, cls):
		cls(
			name = self.__name,
			words = self.__words,
			**self.__params
		).save()
		return cls

@RasmInstance("DECLARE", ["--declare--"])
class Declaration(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		yield [] # no input

		try:
			entity = l[0]
		except:
			raise InstructionAssertError(l,s)
		unit = entity['UNIT'].text
		var = entity['!UNIT'].text
		pointers = {var}
		var2 = entity['!UNIT']['!IMP'].text
		if var2 not in re.pointers:
			pointers.add(var2)
		try:
			#print "WORDS:",entity['!UNIT']['!IMP'].words
			for word in entity['!UNIT']['!IMP'].words:
				if word not in re.pointers:
					pointers.add(word)
		except IndexError:
			pass #sic!


		myset = {DataObject(var,
				{
					var: {"amount": unit, "index": 0},
				}
		)}

		for pointer in pointers:
			re.pointers[pointer] = myset

		yield pointers

@RasmInstance("FINALIZE", ["--finalize--"])
class Finalize(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		yield ["_"]
		yield [] # no output 


@RasmInstance("NOP", ["allow"])
class Nop(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		yield [] # no input
		yield [] # no output

@RasmInstance("REMAP", ["take"])
class Remap(RasmInstruction):
	def run(self, re, l, s):
		entities = [x['!Unit']['!Imp'].text for x in l['Entity']]
		yield []
		yield entities
		yield ["_"]

@RasmInstance("HEAT_OVEN", ["preheat"])
class Heat(RasmInstruction):
	def run(self, re, l, s):
		entity = l['Entity'][0].text
		assert(entity == "oven")
		yield ["oven"]

		yield ["oven"]
		try:
			unit = s['UNIT'][0]['Counter'].text
		except IndexError:
			try:
				unit = s['List']()['Entity']()['UNIT'][0]['Counter'].text
			except IndexError:
				unit = ""
	
		for oven in re.pointers['oven']:
			oven['oven']['to'] = unit
		yield ["oven"]

@RasmInstance("COOK", ["heat", "cook"])
@RasmInstance("SIFT", ["sift"])
@RasmInstance("BAKE", ["bake"])
@RasmInstance("FROST", ["frost"])
@RasmInstance("BEAT", ["beat"])
@RasmInstance("STIR", ["stir", "mix"])
@RasmInstance("BLEND", ["blend"])
@RasmInstance("MELT", ["melt"])
@RasmInstance("CUT", ["cut"])
@RasmInstance("PEEL", ["peel"])
@RasmInstance("CLEAN", ["clean"])
@RasmInstance("MICROWAVE", ["microwave"])
@RasmInstance("COOL", ["cool"])
@RasmInstance("POUR-PAN", ["pour"])
@RasmInstance("CHOP", ["chop"])
@RasmInstance("WHISK", ["whisk"])
@RasmInstance("CREAM", ["cream"])
class Inplace(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		entities = [x['!Unit']['!Imp'].text for x in l['Entity']]
		if not entities:
			entities = ["_"]
		yield entities
		for ent, ing in self.foreach(re, entities):
			ing["+"+self.name.lower()] = {}
		yield entities + ["_"]

@RasmInstance("GREASE", ["grease"])
class TInplace(RasmInstruction):
	def run(self, re, l, s):
		entities = [x['!Unit'].text for x in l['Entity']]
		yield entities
		yield entities
		for ent, ing in self.foreach(re, entities):
			ing["+"+self.name.lower()] = {}
		yield entities

#FIXME: mix should be "+mix"!
@RasmInstance("COMBINE", ["add", "mix in", "stir in","beat in", "pour in", "combine"])
@RasmInstance("SPRINKLE", ["sprinkle"])
class Add(RasmInstruction):
	def run(self, re, l, s):
		#if s:
		#	raise Exception("NYE.")
		#else:
		#	ptr = "_"
		ptr = "_"
		yield []
		entities = [x['!Unit'].text for x in l['Entity']]
		yield entities + ["_"]
		for ent, ing in self.foreach(re, entities):
			ing["+"+self.name.lower()] = {}
			re.pointers[ptr].add(ing)
		yield entities + ["_"]
		
class InstructionFactory(object):
	def __init__(self):
		self.__re = RuntimeEnvironment()

	def interpretDeclaration(self, s, pos):
		print "S:", s
		ins = self.__lookupInstruction("--declare--")
		return self.__run(ins, s)

	@property
	def re(self):
		return self.__re

	def finalize(self):
		ins = self.__lookupInstruction("--finalize--")
		from stage2.tree import Node
		return self.__run(ins, Node().children)

	def interpretInstruction(self, s, pos):
		# 1. identify and lookup command
		cmd = s['Verb'].text

		try:
			ins = self.__lookupInstruction(cmd)
		except KeyError as e:
			raise InstructionLookupError(cmd, s)

		# 2. get the arguments and pass them to the instruction
		return self.__run(ins, s)

	def __run(self, ins, s):
		settings = s['Setting']()
		lists = s['List']()

		r = ins.run(self.__re, lists, settings)
		# yieds 3 times:
		# 1. requirements
		# 2. inPointers
		# 3. outPointers
		requirements = list(r.next())
		for req in requirements:
			myset = {DataObject(req,
				{
					req: {"prop": "tool"},
				}
			)}
			if req not in self.__re.pointers:
				self.__re.pointers[req] = myset

		try: 
			inPointers = list(r.next())
			inData = set()
			for p in inPointers:
				if p in IGNORE_LIST:
					continue #FIXME: handle this intelligently!
				try:
					for ing in self.__re.pointers[p]:
						inData.add(ing)
				except KeyError:
					if not GREEDY: raise
			inData = [x.toDbObject() for x in inData]

			outPointers = list(r.next())
			nset = set()
			if "_" in outPointers:
				for p in outPointers:
					try:
						nset.update(self.__re.pointers[p])
					except KeyError:
						pass #FIXME: later
				self.__re.pointers["_"] = nset

			outData = set()
			for p in outPointers:
				if p in IGNORE_LIST:
					continue #FIXME: handle this intelligently!
				try:
					for ing in self.__re.pointers[p]:
						outData.add(ing)
				except KeyError:
					if not GREEDY: raise
			outData = [x.toDbObject() for x in outData]
			for d in outData:
				for k,v in d.iteritems():
					if "index" in v:
						v["index"] += 1
		except KeyError as e:
			#pprint(self.__re.pointers)
			raise PointerResolutionError(e.args[0], s)

		
		indexData = [x.values() for x in inData]
		indexData = reduce(lambda a,b: a+b, indexData, [])
		indexData = [x["index"] for x in indexData if "index" in x]
		index = max(indexData + [0])

		rs = RuleSample(
			name = ins.name,
			inPointers = inPointers,
			inData = inData,
			requires = requirements,
			outPointers = outPointers,
			outData = outData,
			index = index,
		)
		rs.save()
		return rs
		


	def __lookupInstruction(self, s):
		# 1. database
		try:
			return RasmInstruction.objects(words=s.lower())[0]
		except IndexError:
			pass #sic!

		# 2. wikibooks
		#TODO!
		
		# 3. fail
		raise KeyError(s)		
