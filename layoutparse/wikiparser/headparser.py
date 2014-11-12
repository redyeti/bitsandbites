import abc

class HeadParser(object):
	__metaclass__ = abc.ABCMeta

	re_head = abc.abstractproperty()

	def __init__(self):
		self.data = []

	def parse(self, text):
		findings = []
		for match in self.re_head.finditer(text):
			findings.append(match.span()+match.groups())

		for i,s in enumerate(findings):
			title = s[2]
			if i == len(findings) - 1:
				section = text[s[1]:]
			else:
				section = text[s[1]:findings[i+1][0]]

			self.data.append((title, section))
		return self

	def toDict(self):
		return dict(self.data)

	def toList(self):
		return [x[0] for x in self.data]
