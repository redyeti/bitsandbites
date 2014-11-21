from node import Node
import db

@Node.attach
class Leaf(Node):

	__name = db.StringField(required=True)
	__tag = db.StringField()

	def _init(self, children, name, tag):
		Node._init(self, children)
		assert(children == [])
		self.__name = name
		self.__tag = tag


	@property
	def tag(self):
		return self.__tag

	def __repr__(self):
		return "<%s, %s>" % (self.__class__.__name__, repr((self.__name, self.__tag)))

	def __str__(self):
		return "%s[%s]" % (self.__tag, self.__name)

	@property	
	def leaves(self):
		return [self]

	@property	
	def words(self):
		return [self.__name]

	@property	
	def text(self):
		return self.__name 

	@property
	def html(self):
		from lxml.html import builder as E
		return E.DIV(
			E.CLASS("treeObject tree"+self.__class__.__name__),
			self.__tag,
			E.DIV(
				E.CLASS("treeObject treeLeaf"+self.__class__.__name__),
				self.__name
			)
		)
