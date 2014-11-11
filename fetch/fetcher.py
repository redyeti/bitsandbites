import abc
import db

class RawRecipe(db.Document):
	uid = db.StringField(primary_key=True)
	format = db.StringField(required=True, index=True)
	payload = db.StringField(required=True)

class Fetcher(object):
	__METACLASS__ = abc.ABCMeta

	@abc.abstractmethod
	def fetch(self):
		pass

	@classmethod
	def run(cls, *args, **params):
		return list(cls().fetch(*args,**params))
