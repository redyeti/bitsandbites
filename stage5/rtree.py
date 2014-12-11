from __future__ import division
import db
from stage4 import Rule
from random import random, seed
import time
import numpy as np

P = 0.01

seed(time.time())

def shuf(*args, **params):
	d = list(Rule.objects(*args, **params))
	d.sort(key=lambda x:-random()*x.conf*x.freq)
	return d

def getrand(*args, **params):
	return shuf(*args, **params)[0]


import abc
class RecipeNodeBase(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, depth, parent=None):
		self.children = []
		self.__depth = depth
		self.__parent = parent
		self._satisfied = set()

	@property
	def parent(self):
		return self.__parent

	@property
	def depth(self):
		return self.__depth

	def getDescendants(self):
		return reduce(lambda a,b: a+b, [x.getDescendants() for x in self.children], []) + self.children

	def getDescendantsAndSelf(self):
		return self.getDescendants()+[self]

	def addChild(self, node):
		self.children.append(node)

	openRules = abc.abstractproperty()
	rules = abc.abstractproperty()
	name = abc.abstractproperty()

	@abc.abstractmethod
	def toText(self):
		pass

	def satisfy(self):
		# first satisfy operations
		operations = [x[1:].upper() for x in self.openRules if x.startswith("+")]
		malus = lambda x: -10 if x == self.name else 0
		operations = [(x,Rule.objects(action=x).average("index")+malus(x)) for x in operations]

		for op, index in sorted(operations, key=lambda x: -x[1]):
			try:
				self.addChild(RecipeTreeNode(action=op, parent=self, depth=self.depth+1))
			except IndexError:
				self.addChild(TrivialNode(parent=self, depth=self.depth+1, req=self.openRules))
			self._satisfied.add("+"+op.lower())
			return True
		return False

	def _mk(self, l):
		def _m():
			for i, x in enumerate(l):
				if i == 0:
					pass
				elif i == len(l) - 1:
					yield " and "
				else:
					yield ", "
				yield x
		return "".join(_m())



class TrivialNode(RecipeNodeBase):
	def __init__(self, depth, parent, req):
		RecipeNodeBase.__init__(self, depth, parent)
		self.__req = req

	def __str__(self):
		return "%3i: TRIVIAL%s\n" % (self.depth, tuple(self.__req))

	vioScore = -0.1
	idxScore = 0
	
	def toText(self):
		op = set()
		ig = set()
		for x in self.__req:
			if x.startswith("+"):
				op.add(x[1:]+"ed") 
			else:
				ig.add(x)
		if ig:
			return ["Take "+self._mk(op) + " " + self._mk(ig)]
		else:
			return []


	@property
	def name(self):
		return "triv"

	@property
	def openRules(self):
		return set()

	@property
	def rules(self):
		return self.__req

class RecipeTreeNode(RecipeNodeBase):
	def __init__(self, depth, parent=None, **params):
		self.__rule = getrand(direction="in-fwd", **params)
		RecipeNodeBase.__init__(self, depth, parent)

	@property
	def index(self):
		return self.__rule.index

	@property
	def name(self):
		return self.__rule.action

	@property
	def vioScore(self):
		bwd_rules = Rule.objects(direction="in-bwd", action=self.__rule.action)
		childsat = self.__childsat()
		score = 0
		for rule in bwd_rules:
			if set(self.__rule.data).difference(childsat):
				score += 1
			else:
				score -= 1
		if bwd_rules:
			return score / len(bwd_rules)
		else:
			return 0

	@property
	def idxScore(self):
		req = self.__rule.index
		mdp = max([x.depth for x in self.getDescendants()])

		return 1 - abs(req - (mdp - self.depth))

	@property
	def rules(self):
		return self.__rule.data + ["+"+self.name.lower()]

	def toText(self):
		t = []
		for x in self.children:
			t.extend(x.toText())

		j = k = ""
		if self.openRules and self.children:
			j = "Add %s and " % self._mk(self.openRules)
		elif self.openRules:
			k = " %s " % self._mk(self.openRules)
		t.append(j+self.name.lower()+k)
		return t

	def delete(self, n=0):
		if n == 0:
			if isinstance(self.parent, RecipeTreeRoot):
				self.parent.init()
			else:
				self.parent.children.remove(self)
			return True
		else:
			if isinstance(self.parent, RecipeTreeRoot):
				return False
			else:
				return self.parent.delete(n-1)

	def __str__(self):
		return "%3i: %s<%.2f>%s\n%s" % (
			self.depth,
			self.__rule.action, self.index,
			tuple(self.openRules),
			"".join(("\t"*(self.depth+1))+str(x) for x in self.children),
		)

	def __repr__(self):
		return "<%s %.2f %s>" % (self.__rule.action, self.index, self.openRules)

	def __childsat(self):
		childsat = [x.rules for x in self.getDescendants()]
		childsat = reduce(lambda a,b:a.union(b), childsat, set())
		return childsat
		

	@property
	def openRules(self):
		childsat = self.__childsat()
		return set(self.__rule.data).difference(childsat)


class RecipeTreeRoot(object):
	def __init__(self):
		self.init()

	def init(self):
		self.__root = RecipeTreeNode(action="FINALIZE", parent=self, depth=0)

	def getAllNodes(self):
		return self.__root.getDescendantsAndSelf()

	def getUnsatisfiedNodes(self):
		return [x for x in self.getAllNodes() if x.openRules]

	def getActiveNodes(self):
		return sorted(self.getUnsatisfiedNodes(), key=lambda x: x.index - x.depth)

	@property
	def name(self):
		return "(root)"

	def satisfy(self):
		p = np.random.geometric(P)
		for n in self.getActiveNodes():
			if n.delete(p-1):
				return True
		for n in self.getActiveNodes():
			if n.satisfy():
				return True
		return False

	def __getattr__(self, a):
		return getattr(self.__root, a)

	@property
	def root(self):
		return self.__root

	def __str__(self):
		return str(self.__root)

	def toText(self):
		return "\n".join([("%2i. "%i)+x for (i,x) in enumerate(self.root.toText()[:-1])])

	@property
	def vioScore(self):
		n = self.getAllNodes()
		return sum([x.vioScore for x in n]) / len(n)

	@property
	def idxScore(self):
		n = self.getAllNodes()
		return sum([x.idxScore for x in n]) / len(n)
