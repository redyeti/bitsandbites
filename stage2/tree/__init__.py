from node import Node
import leaf

@Node.attach
class Imp(Node):
	pass

@Node.attach
class List(Node):
	pass

@Node.attach
class S(Node):
	pass

@Node.attach
class Setting(Node):
	pass

@Node.attach
class Counter(Node):
	pass

@Node.attach
class Unit(Node):
	pass

@Node.attach
class Entity(Node):
	pass

@Node.attach
class Instruct(Node):
	pass

@Node.attach
class Verb(Node):
	pass

mktree = Node.fromTree

