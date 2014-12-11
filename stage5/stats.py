#-*- coding: utf8 -*-
from __future__ import division
from stage2 import RecipeMeta
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
	def rep(self):
		"""Repetition score"""
		text = self.__rtr.toText()
		return len(bz2.compress(text)) / len(text)

	@XProperty
	def xis(self):
		"""Cross ingredience score"""

	@XProperty
	def ihs(self):
		"""Ingredience histogram score"""

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


