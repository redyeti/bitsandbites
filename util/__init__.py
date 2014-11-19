import abc
import db

class DispatchMeta(abc.ABCMeta):
	def __init__(cls, *args, **params):
		abc.ABCMeta.__init__(cls, *args, **params)
		cls._dispatch[cls.__name__] = cls

class LcDispatchMeta(abc.ABCMeta):
	def __init__(cls, *args, **params):
		abc.ABCMeta.__init__(cls, *args, **params)
		cls._dispatch[cls.__name__.lower()] = cls
