from rtree import *
from stats import Stat

N_REPS = 5

if __name__ == "__main__":
	import sys
	reload(sys)
	sys.setdefaultencoding("utf8")

	mrtr = None
	for i in xrange(N_REPS):
		rtr = RecipeTreeRoot()
		#print "All:", rtr.getAllNodes()

		ok = True
		while ok:
			ok = rtr.satisfy()

		if not rtr.prune():
			mrtr = None
			continue

		s_rtr = Stat(rtr)
		t_rtr = s_rtr.total
		print "#%02i, Score % .2f" % (i, t_rtr)
		if mrtr is None:
			mrtr = rtr
			t_mrtr = t_rtr
		else:
			if t_mrtr < t_rtr:
				mrtr = rtr
				t_mrtr = t_rtr

	print mrtr
	print "---"
	print mrtr.toText()
	print "---"
	print Stat(mrtr)
	print "==="

## pick a root node
#root = shuf(action="FINALIZE", direction="in-fwd")[0]
#print root.__dict__
#
## now try to satisfy the rules:
