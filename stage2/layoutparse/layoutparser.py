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
	def parseDB(cls, ignore_errors = False):
		for doc in RawRecipe.objects():
			try:
				data = cls.parseDoc(doc)
				yield (doc, data)
			except: #sic!
				if not ignore_errors:
					raise

	@classmethod
	def parseDoc(cls, doc):
		return cls.dispatch(doc.parser).parseText(doc.payload)

	@abc.abstractmethod
	def parseText(self, text):
		pass

__all__ = ("Layoutparser",)
