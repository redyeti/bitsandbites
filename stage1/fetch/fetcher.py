import abc
import db

class Fetcher(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def fetch(self):
		pass

	@classmethod
	def run(cls, *args, **params):
		return list(cls().fetch(*args,**params))
