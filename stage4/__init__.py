from __future__ import division
from stage3 import RuleSample

class Q(object):
	def __init__(self, key, name, values=None):
		self.__name = name
		self.__key = key
		if values is None:
			self.__values = set()
		else:
			self.__values = set(values)

	@property
	def signature(self):
		return (self.__key, self.__name, tuple(sorted(self.__values)))

	@property
	def values(self):
		return self.__values

	def copy(self):
		return Q(self.__key, self.__name, self.__values)

	def __str__(self):
		return "%s %s: %s" % (self.__name, self.__key, sorted(self.__values))

	def proceed(self, v):
		n = self.copy()
		n.__values.add(v)
		return n

	@property
	def vdict(self):
		v = [{'$elemMatch': {x: {'$exists': True }}} for x in self.__values]

		if v:
			return {
				self.__key: {
					'$all': v
				}
			}
		else:
			return {}

	@property
	def dict(self):
		v = [{'$elemMatch': {x: {'$exists': True }}} for x in self.__values]

		if v:
			return {
				"name": self.__name,
				self.__key: {
					'$all': v
				}
			}
		else:
			return {"name": self.__name}

# find operations

MINFREQ = 0.01
MINCONF_FWD = 0.000023
MINCONF_BWD = 0.000023
MINQ_FWD = 0.000001
MINQ_BWD = 0.000001

total = RuleSample.objects.count()

s = {}
def cache(fn):
	def _fn(q, t):
		if q.signature in s:
			yield s[q.signature]
			return
		y = 0
		for x in fn(q, t):
			if x != 0:
				y = 1
				yield x
		s[q.signature] = y
	return _fn

@cache
def discover(q, t):
	obj = RuleSample.objects(__raw__=q.dict)
	
	freq = obj.count() / total

	if freq < MINFREQ:
		return

	oset = obj.distinct(t)
	keys = reduce(lambda a,b: a+b, [x.keys() for x in oset], [])
	keys = sorted(set(keys))

	#maxval = max(q.values.union([""]))
	ismax = True

	for k in keys:
		if k not in q.values:
			qn = q.proceed(k)
			for x in discover(qn, t):
				if x == 0:
					pass
				elif x == 1:
					yield 1
					ismax = False
				else:
					yield x
					ismax = False

	#if ismax:
	yield q, freq
		

import db

class Rule(db.Document):
	action = db.StringField()
	data = db.ListField()

	freq = db.FloatField()
	conf = db.FloatField()
	q = db.FloatField()
	
	direction = db.StringField()

def run():
	for rule in RuleSample.objects.distinct("name"):
		q = Q("inData", rule)
		for x in discover(q, "inData"):
			if isinstance(x, tuple):
				conf_fwd = x[1] / RuleSample.objects(__raw__=x[0].vdict).count()
				conf_bwd = x[1] / RuleSample.objects(name=rule).count()

				q_fwd = conf_fwd * x[1]
				q_bwd = conf_bwd * x[1]

				fwd_rule = bool(conf_fwd > MINCONF_FWD and q_fwd > MINQ_FWD)
				bwd_rule = bool(conf_bwd > MINCONF_BWD and q_bwd > MINQ_BWD)

				if fwd_rule or bwd_rule:
					print x[0], x[1]
				if fwd_rule:
					print "\tConfidence --> %.20f (%.20f)" % (conf_fwd, q_fwd)
				if bwd_rule:
					print "\tConfidence <-- %.20f (%.20f)" % (conf_bwd, q_bwd)

				# save iff the rule is frequent and confident
				r = [
					(fwd_rule, conf_fwd, q_fwd, "in-fwd"),
					(bwd_rule, conf_bwd, q_bwd, "in-bwd"),
				]
				for _, conf, q, direction in [z for z in r if z[0]]:
					Rule(
						action = rule,
						data = list(x[0].values),
						freq = x[1],
						conf = conf,
						q = q,
						direction = direction,
					).save()

