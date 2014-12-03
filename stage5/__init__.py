import db
from stage4 import Rule
from random import random

def shuf(*args, **params):
	d = list(Rule.objects(*args, **params))
	d.sort(key=lambda x:-random()*x.conf*x.freq)
	return d

# pick a root node
root = shuf(action="FINALIZE", direction="in-fwd")[0]
print root.__dict__

# now try to satisfy the rules:
for data in sorted(root.data, key=lambda x:random()):
	print data
	# get suitable operations
	#TODO: over the whole tree: select node with max(depth-index) and update child with max(depth+index)
	if data.startswith("+"):
		op = data[1:].upper()
		print op
		print shuf(action=op, direction="in-fwd")[0].__dict__
