import abc
from db.types import RawRecipe
from util import DispatchMeta

class Layoutparser(object):
	__metaclass__ = DispatchMeta

	_dispatch = {}

	@classmethod
	def dispatch(cls, name, *args, **params):
		return cls._dispatch[name](*args, **params)

	@classmethod
	def parseDB(cls):
		for doc in RawRecipe.objects():
			data = cls.parseDoc(doc)
			yield data

	@classmethod
	def parseDoc(cls, doc):
		return cls.dispatch(doc.parser).parseText(doc.payload)

	@abc.abstractmethod
	def parseText(self, text):
		pass

__all__ = ("Layoutparser",)
