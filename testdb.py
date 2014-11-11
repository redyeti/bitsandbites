from mongoengine import *
from pprint import *

connect("Test")

class X(DynamicDocument):

	def __str__(self):
		return pformat(self.__dict__)

	__repr__ = __str__
