import abc
from fetch/fetcher import RawRecipe

class Layoutparser(object):
	__METACLASS__ = abc.ABCMeta

	type = abc.abstractproperty()

	def parseDB(self):
		for doc in RawRecipe.objects(type=self.type):
			data = self.parseDoc(doc)

	def parseDoc(self, doc):
		return self.parseText(doc.payload)

	@abc.abstractmethod
	def parseText(self, text):
		pass
