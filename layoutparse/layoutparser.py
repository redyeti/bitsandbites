import abc
from fetch.fetcher import RawRecipe

class ParseMeta(abc.ABCMeta):
	def __init__(cls, *args, **params):
		abc.ABCMeta.__init__(cls, *args, **params)
		cls._dispatch[cls.__name__] = cls

class Layoutparser(object):
	__metaclass__ = ParseMeta

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
