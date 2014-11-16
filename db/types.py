import mongoengine as db

class RawRecipe(db.Document):
	uid = db.StringField(primary_key=True)
	parser = db.StringField(required=True)
	payload = db.StringField(required=True)

	meta = {
		'indexes': ['parser']
	}

