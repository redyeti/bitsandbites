import abc
import db

class RawRecipe(db.Document):
	uid = db.StringField(primary_key=True)
	parser = db.StringField(required=True)
	payload = db.StringField(required=True)

	meta = {
		'indexes': ['parser']
	}

class Fetcher(object):
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def fetch(self):
		pass

	@classmethod
	def run(cls, *args, **params):
		return list(cls().fetch(*args,**params))
