from collections import Sequence
import nltk
import db

class ChildrenView(Sequence):
	def __init__(self, base):
		self.__base = base
	def __getitem__(self, i):
		if isinstance(i,basestring):
			i = i.lower()
			if i.startswith("!."):
				cond = lambda n,x: not(n == "leaf" and x.tag == i[1:])
			elif i.startswith("."):
				cond = lambda n,x: n == "leaf" and x.tag == i[1:]
			elif i.startswith("!"):
				cond = lambda n,x: n != i[1:]
			else:
				cond = lambda n,x: n == i
			return Node([x for x in self.__base._children if cond(x.__class__.__name__.lower(),x)])
		elif isinstance(i, slice):
			return Node(self.__base._children[i])
		else:
			return self.__base._children[i]
	def __len__(self):
		return len(self.__base._children)

class Node(db.EmbeddedDocument):
	_dispatch = {}

	_children = db.ListField()

	@classmethod
	def attach(cls, other):
		cls._dispatch[other.__name__.lower()] = other
		return other

	@classmethod
	def fromTree(cls, tree):
		if isinstance(tree, nltk.tree.Tree):
			return cls._dispatch[tree.node.lower()](list(tree))
		else:
			return cls._dispatch["leaf"]([], *tree)

	def __init__(self, *args, **kwargs):
		if kwargs:
			db.EmbeddedDocument.__init__(self, **kwargs)
			return
		else:
			db.EmbeddedDocument.__init__(self)
			self._init(*args)

	def _init(self, children):
		for child in children:
			if isinstance(child, Node):
				self._children.append(child)
			else:
				self._children.append(self.fromTree(child))
	
	def cut(self):
		return Node(reduce(lambda a,b: a+b, [x._children for x in self._children], []))

	@property
	def children(self):
		return ChildrenView(self)

	def __repr__(self):
		return "<%s %s>" % (self.__class__.__name__, repr(self._children))

	def __str__(self):
		return "[%s %s]" % (self.__class__.__name__, " ".join([str(x) for x in self._children]))
	
	@property	
	def leaves(self):
		return reduce(lambda a,b: a+b, [x.leaves for x in self._children], [])

	@property	
	def words(self):
		return reduce(lambda a,b: a+b, [x.words for x in self._children], [])

	@property	
	def text(self):
		return " ".join([x.text for x in self._children])

	@property
	def html(self):
		from lxml.html import builder as E
		return E.SPAN(
			E.CLASS("tree"+self.__class__.__name__),
			*[x.html for x in self._children]
		)

