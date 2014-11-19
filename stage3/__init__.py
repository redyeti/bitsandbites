import db
from pprint import pprint

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

class RuntimeEnvironment(object):
	def __init__(self):
		self.pointers = {}

class DbObject(db.EmbeddedDocument):
	primary = db.StringField()
	data = db.DictField()

	def __str__(self):
		return "%(primary)s: %(data)s" % self
	__repr__ = __str__

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
		return DbObject(
			primary = self.primary,
			data = self.data,
		)

class InstructionInfo(db.EmbeddedDocument):
	name = db.StringField(required=True)
	inPointers = db.ListField()
	outPointers = db.ListField()
	inData = db.ListField()
	outData = db.ListField()
	requires = db.ListField()

	def __str__(self):
		return "%(name)s %(inPointers)s/%(inData)s -> %(outPointers)s/%(outData)s" % self

	__repr__ = __str__

class RasmInstruction(db.Document):
	name = db.StringField(primary_key=True)
	words = db.ListField(required=True)
	meta = {
		"allow_inheritance": True,
		"indexes" : ['words'],
	}


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

@RasmInstance("DECLARE", ["declare"])
class Declaration(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		yield [] # no input

		entity = l()
		unit = entity['UNIT'].text
		var = entity['!UNIT'].text
		pointers = {var}
		var2 = entity['!UNIT']['!IMP'].text
		if var2 not in re.pointers:
			pointers.add(var2)

		for pointer in pointers:
			re.pointers[pointer] = DataObject(var,
				{
					var: {"amount": unit},
				}
			)

		yield list(pointers)


#FIXME: these are only temporary, we'll deal with them later
@RasmInstance("NOP", ["place on", "reach"])
class Nop(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		yield [] # no input
		yield [] # no output

@RasmInstance("ALIAS", ["take"])
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
		unit = s['UNIT'][0]['Counter'].text
	
		pre = re.pointers['oven'].toDbObject()
		re.pointers['oven']['oven']['to'] = unit
		yield ["oven"]

@RasmInstance("COOK", ["heat"])
class Inplace(RasmInstruction):
	def run(self, re, l, s):
		yield [] # no requirements
		entities = [x['!Unit']['!Imp'].text for x in l['Entity']]
		yield entities
		for ent in entities:
			re.pointers[ent]["+"+self.name.lower()] = {}
		yield entities + ["_"]

@RasmInstance("GREASE", ["grease"])
class TInplace(RasmInstruction):
	def run(self, re, l, s):
		entities = [x['!Unit'].text for x in l['Entity']]
		yield entities
		yield entities
		for ent in entities:
			re.pointers[ent]["+"+self.name.lower()] = {}
		yield entities

class InstructionFactory(object):
	def __init__(self):
		self.__re = RuntimeEnvironment()

	def interpretDeclaration(self, s, pos):
		print "S:", s
		ins = self.__lookupInstruction("declare")
		return self.__run(ins, s)

	def interpretInstruction(self, s, pos):
		# 1. identify and lookup command
		cmd = s['Verb'].text

		try:
			ins = self.__lookupInstruction(cmd)
		except KeyError as e:
			raise KeyError(e.message + ": " + str(s))

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
		requirements = r.next()
		for req in requirements:
			if req not in self.__re.pointers:
				self.__re.pointers[req] = DataObject(req,
					{
						req: {"prop": "tool"},
					}
				)

		try: 
			inPointers = r.next()
			inData = [self.__re.pointers[x].toDbObject() for x in inPointers]

			outPointers = r.next()
			if outPointers:
				self.__re.pointers["_"] = self.__re.pointers[outPointers[0]]
			outData = [self.__re.pointers[x].toDbObject() for x in outPointers]
		except KeyError:
			pprint(self.__re.pointers)
			raise
				
		return InstructionInfo(
			name = ins.name,
			inPointers = inPointers,
			inData = inData,
			requires = requirements,
			outPointers = outPointers,
			outData = outData,
		)
		


	def __lookupInstruction(self, s):
		# 1. database
		try:
			return RasmInstruction.objects(words=s.lower())[0]
		except IndexError:
			pass #sic!

		# 2. wikibooks
		#TODO!
		
		# 3. fail
		raise KeyError("Could not lookup instruction: %s" % repr(s))		
