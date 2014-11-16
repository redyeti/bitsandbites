from util import LCDispatchMeta
from collections import Sequence
import nltk

class Node(Sequence):
	__metaclass__ = LCDispatchMeta

	_dispatch = {}

	@classmethod
	def fromTree(cls, tree):
		if isinstance(tree, nltk.tree.Tree):
			return cls._dispatch[tree.node.lower()](list(tree))
		else:
			return cls._dispatch["leaf"]([], *tree)

	def __init__(self, children):
		self.__children = []
		for child in children:
			if isinstance(child, Node):
				self.__children.append(child)
			else:
				self.__children.append(self.fromTree(child))
	
	def cut(self):
		return Node(reduce(lambda a,b: a+b, [x.__children for x in self.__children], []))

	def __getitem__(self, i):
		if isinstance(i,basestring):
			return Node([x for x in self.__children if x.__class__.__name__.lower() == i.lower()])
		elif isinstance(i, slice):
			print "Slice:", type(i)
			return Node(self.__children[i])
		else:
			print "Single:", type(i)
			return self.__children[i]

	def __len__(self):
		return len(self.__children)

	def __repr__(self):
		return "<%s %s>" % (self.__class__.__name__, repr(self.__children))
	
	@property	
	def leaves(self):
		return reduce(lambda a,b: a+b, [x.leaves for x in self.__children], [])

	@property	
	def words(self):
		return reduce(lambda a,b: a+b, [x.words for x in self.__children], [])

	@property	
	def text(self):
		return " ".join([x.text for x in self.__children])

	@property
	def html(self):
		from lxml.html import builder as E
		return E.SPAN(
			E.CLASS("tree"+self.__class__.__name__),
			*[x.html for x in self.__children]
		)
