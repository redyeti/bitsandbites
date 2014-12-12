#-*- coding: utf8 -*-
from __future__ import division
from stage2 import RecipeMeta
from stage3 import RuleSample
from util.ncd import ncd
import bz2

class XProperty(property):
	FMT = "%s"
	ADD = False

class FProperty(XProperty):
	FMT = "% .2f"
	ADD = True

# NOTE:
# Bigger means better!
# (Greater scores indicate better results)

class Stat(object):
	def __init__(self, rtr):
		self.__rtr = rtr

	@FProperty
	def xrd(self):
		"""NCD Cross recipe similarity"""	
		v = float("Inf")
		for rm in RecipeMeta.objects:
			if not rm.sblob.strip():
				continue
			v = min(v, ncd(self.__rtr.toText(), rm.sblob))
		return -v

	@FProperty
	def vrs(self):
		"""Violated rules score"""
		return self.__rtr.vioScore

	@FProperty
	def mdg(self):
		"""Manual downgrade"""
		mdg = 0
		ing = self.__rtr.ingredients

		if not [x for x in ing if "flour" in x]:
			mdg -= 5

		return mdg
		

	@FProperty
	def xis(self):
		"""Cross ingredience score"""
		ing = self.__rtr.ingredients
		c = 0 
		t = 0
		for i in ing:
			for j in ing:
				l = RuleSample.objects(__raw__ = {
					'$and': [
						{'inData': {'$elemMatch': { i: {'$exists': True }}}},
						{'inData': {'$elemMatch': { j: {'$exists': True }}}}
					]
				})
				if l:
					c += 1
				t += 1
		return (c + 1) / (t + 1)

	@FProperty
	def ixs(self):
		"""Index score"""
		return self.__rtr.idxScore

	@property
	def __all(self):
		d = {}
		for pname in dir(Stat):
			clattr = getattr(Stat, pname)
			if isinstance(clattr, XProperty):
				d[pname] = clattr

		def attrs():
			for pname, clattr in d.iteritems():
				inattr = getattr(self, pname)
				yield pname, clattr, inattr
		return d, attrs
		
	@property
	def total(self):
		z = 0

		d, attrs = self.__all
		l1 = max(len(x) for x in d.keys())
		l2 = max(4 if x.__doc__ is None else len(x.__doc__) for x in d.values())

		for pname, clattr, inattr in attrs():
			if clattr.ADD:
				z += inattr
		return z

	def __str__(self):
		s = []
		z = 0

		d, attrs = self.__all
		l1 = max(len(x) for x in d.keys())
		l2 = max(4 if x.__doc__ is None else len(x.__doc__) for x in d.values())

		for pname, clattr, inattr in attrs():
			s.append(("%*s: %*s = "+clattr.FMT) % (l2, clattr.__doc__, l1, pname, inattr))
			if clattr.ADD:
				z += inattr
		s.append(("%*s: %*s = % .2f") % (l2, "TOTAL SCORE", l1, u"Σ", z))
		return "\n".join(s)


