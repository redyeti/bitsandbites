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

	@property
	def ingredients(self):
		return set(x for x in self.props if not x.startswith("+"))

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
		p = np.random.geometric(P)
		if p < self.depth and [x for x in self.openRules if not x.startswith("+")]:
			self.setRules([x for x in self.rules if not x.startswith("+")])
			return 

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

	def _mk2(self, req):
		op = set()
		ig = set()
		for x in req:
			if x.startswith("+"):
				op.add(x[1:]+"ed") 
			else:
				ig.add(x)
		return bool(ig), self._mk(op) + " " + self._mk(ig)

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

	def delete(self, n=0):
		if n == 0:
			if isinstance(self.parent, RecipeTreeRoot):
				self.parent.init()
			else:
				try:
					self.parent.children.remove(self)
				except ValueError:
					pass #!sic
			return True
		else:
			if isinstance(self.parent, RecipeTreeRoot):
				return False
			else:
				return self.parent.delete(n-1)




class TrivialNode(RecipeNodeBase):
	def __init__(self, depth, parent, req):
		RecipeNodeBase.__init__(self, depth, parent)
		self.__req = req

	def __str__(self, n=None):
		return "%3i: TRIVIAL%s\n" % (n or self.depth, tuple(self.__req))

	vioScore = -0.1
	idxScore = 0
	index = float("Inf")

	@property
	def props(self):
		return set(self.__req)
	
	def toText(self):
		a, s = self._mk2(self.__req)
		if a:
			z = "Take"
			return [z+" "+ s]
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

	def setRules(self, r):
		self.__req = set(r)

class RecipeTreeNode(RecipeNodeBase):
	def __init__(self, depth, parent=None, **params):
		self.__rule = getrand(direction="in-fwd", **params)
		RecipeNodeBase.__init__(self, depth, parent)

	@property
	def props(self):
		s = set()
		for c in self.children:
			s.update(c.props)
		return s

	@property
	def index(self):
		return self.__rule.index

	@property
	def name(self):
		return self.__rule.action

	@property
	def orderedChildren(self):
		return sorted(self.children, key=lambda x:x.index)

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
		try:
			mdp = max([x.depth for x in self.getDescendants()])
			return 1 - abs(req - (mdp - self.depth))
		except ValueError:
			return 0

	def prune(self):
		r = set()
		for child in self.orderedChildren:
			if set(child.rules).issubset(r):
				child.delete()
	
			if isinstance(child, TrivialNode):
				cs = child.rules
			else:
				cs = child.__childsat().union(child.rules)
			r.update(cs)

			
			

	@property
	def rules(self):
		return self.__rule.data + ["+"+self.name.lower()]

	def setRules(self, r):
		self.__rule.data = list(r)

	def toText(self):
		t = []
		for x in self.orderedChildren:
			t.extend(x.toText())

		j = k = ""
		a, s = self._mk2(self.openRules)
		if a and self.children:
			j = "Add %s and " % s
		elif a:
			k = " %s " % s
		t.append(j+self.name.lower()+k)
		return t

	def __str__(self, n=None):
		return "%3i: %s<%.2f>%s\n%s" % (
			n or self.depth,
			self.__rule.action, self.index,
			tuple(self.openRules),
			"".join(("\t"*(self.depth+1))+x.__str__(n) for x in self.orderedChildren),
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

	def prune(self):
		self.__root.prune()
		c = sorted(self.getAllNodes(), key=lambda x:x.depth)
		for i in c:
			for j in c:
				if i.__str__(1) == j.__str__(1) and i is not j:
					if i.depth < j.depth:
						j.delete()
		return self.getAllNodes()

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
