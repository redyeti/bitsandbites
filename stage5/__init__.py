import db
from stage4 import Rule
from random import random, seed
import time
seed(time.time())

def shuf(*args, **params):
	d = list(Rule.objects(*args, **params))
	d.sort(key=lambda x:-random()*x.conf*x.freq)
	return d

def getrand(*args, **params):
	return shuf(*args, **params)[0]

class RecipeTreeNode(object):
	def __init__(self, depth, **params):
		self.__rule = getrand(direction="in-fwd", **params)
		self.__children = []
		self.__depth = depth
		self.__satisfied = set()

	@property
	def depth(self):
		return self.__depth

	@property
	def index(self):
		return self.__rule.index

	def getDescendants(self):
		return reduce(lambda a,b: a+b, [x.getDescendants() for x in self.__children], []) + self.__children

	def getDescendantsAndSelf(self):
		return self.getDescendants()+[self]

	def addChild(self, node):
		self.__children.append(node)

	@property
	def openRules(self):
		s = [x.__satisfied for x in self.getDescendantsAndSelf()]
		s = reduce(lambda a,b:a.union(b), s, set())
		return set(self.__rule.data).difference(s)

	def satisfy(self):
		# first satisfy operations
		operations = [x[1:].upper() for x in self.openRules if x.startswith("+")]
		operations = [(x,Rule.objects(action=x).average("index")) for x in operations]
		print "Ops:", operations
		for op, index in sorted(operations, key=lambda x: -x[1]):
			print "Op:", op
			self.addChild(RecipeTreeNode(action=op, depth=self.depth+1))
			self.__satisfied.add("+"+op.lower())
			return True
		return False

	def __str__(self):
		return "%s<%.2f>(%s)" % (self.__rule.action, self.index, ", ".join(str(x) for x in self.__children))

	def __repr__(self):
		return "<%s %.2f %s>" % (self.__rule.action, self.index, self.openRules)

class RecipeTreeRoot(object):
	def __init__(self):
		self.__root = RecipeTreeNode(action="FINALIZE", depth=0)

	def getAllNodes(self):
		return self.__root.getDescendantsAndSelf()

	def getUnsatisfiedNodes(self):
		return [x for x in self.getAllNodes() if x.openRules]

	def getActiveNode(self):
		return max(self.getUnsatisfiedNodes(), key=lambda x: x.depth - x.index)

	def __getattr__(self, a):
		return getattr(self.__root, a)

	@property
	def root(self):
		return self.__root

	def __str__(self):
		return str(self.__root)

rtr = RecipeTreeRoot()
print "All:", rtr.getAllNodes()

ok = True
while ok:
	print "--"
	print "Act:", rtr.getActiveNode()
	ok = rtr.getActiveNode().satisfy()
	print "Sat:", ok
	print "All:", rtr.getAllNodes()
	print rtr

## pick a root node
#root = shuf(action="FINALIZE", direction="in-fwd")[0]
#print root.__dict__
#
## now try to satisfy the rules:
