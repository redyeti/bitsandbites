from node import Node
import leaf

class Imp(Node):
	pass

class List(Node):
	pass

class S(Node):
	pass

class Setting(Node):
	pass

class Counter(Node):
	pass

class Unit(Node):
	pass

class Entity(Node):
	pass

mktree = Node.fromTree

if __name__ == "__main__":
	import sys
	reload(sys)
	sys.setdefaultencoding("utf8")
	
	from stage2.layoutparse import Layoutparser
	from stage2 import lang

	d = Layoutparser.parseDB().next()
	for step in d['Procedure']:
		for sentence in step:
			t = lang.process(sentence)
