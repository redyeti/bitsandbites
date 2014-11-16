from node import Node

class Leaf(Node):
	def __init__(self, children, name, tag):
		assert(children == [])
		Node.__init__(self, children)
		self.__name = name
		self.__tag = tag

	def __repr__(self):
		return "<%s, %s>" % (self.__class__.__name__, repr((self.__name, self.__tag)))

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
		return E.SPAN(
			E.CLASS("tree"+self.__class__.__name__),
			self.__name
		)
