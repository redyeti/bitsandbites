import re
class Linkmatch(object):
	re_link = re.compile(r"\[\[(?:([^|\]]*)\|)?([^|\]]*)\]\]")

	@classmethod
	def sub(cls, text, callback=None):
		if callback is None:
			def callback(ref,text):
				return text

		def _callback(match):
			g = match.groups()
			if g[0] is None:
				# no bar
				return callback(g[1], g[1])
			elif g[0] == "":
				raise Exception("Not implemented (Reverse Pipe Trick).")
			elif g[1] == "":
				raise Exception("Not implemented (Pipe Trick).")
			else:
				return callback(*g)

		return cls.re_link.sub(_callback, text)
