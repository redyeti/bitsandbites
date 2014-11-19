import db

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
		entity = l()
		unit = entity['UNIT'].text
		var = entity['!UNIT'].text

		re.pointers[var] = DataObject(var,
			{
				var: {"amount": unit},
			}
		)

		return InstructionInfo(
			name = self.name,
			outPointers = [var],
			outData = [re.pointers[var].toDbObject()],
		)

@RasmInstance("HEAT", ["preheat"])
class Heat(RasmInstruction):
	def run(self, re, l, s):
		entity = l['Entity'][0].text
		assert(entity == "oven")
		print "S:", s
		print "Set:", s['UNIT'][0] 
		1/0

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
		return ins.run(self.__re, lists, settings)


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
