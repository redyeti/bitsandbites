from tree import mktree, Node
import db

class Block(db.EmbeddedDocument):
	tree = db.EmbeddedDocumentField('Node', required=True)
	position = db.ListField()

class SyntaxParsedRecipe(db.Document):
	origin = db.ReferenceField('RawRecipe', reverse_delete_rule=db.CASCADE, required=True)
	ingredients = db.ListField()
	sentences = db.ListField()

if __name__ == "__main__":
	import sys
	reload(sys)
	sys.setdefaultencoding("utf8")
	
