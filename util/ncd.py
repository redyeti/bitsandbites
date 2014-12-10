from __future__ import division
import zlib

def z(x):
	return len(zlib.compress(x))

def ncd(x, y, compressed=None):
		
	zx = z(x)
	if compressed is None:
		zy = z(y)
	else:
		zy = compressed

	return (min(z(x+"\033"+y), z(y+"\033"+x)) - min(zx, zy)) / max(zx, zy)

__all__ = ["ncd"]
