from __future__ import division
import bz2

def z(x):
	return len(bz2.compress(x,9))

def ncd(x, y, compressed=None):
		
	zx = z(x)
	if compressed is None:
		zy = z(y)
	else:
		zy = compressed

	n = min(z(x+"\000"+y), z(y+"\000"+x)) - min(zx, zy) - 1
	d = max(zx, zy) - z("")

	if d == 0:
		return 0

	return n / d

__all__ = ["ncd"]

if __name__ == "__main__":
	print ncd("","")
	print "----"
	print ncd("potato eggs","potato eggs")
	print "----"
	print ncd("potato eggs","ham zucchini")

