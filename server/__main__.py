from CGIHTTPServer import CGIHTTPRequestHandler as SimpleHandler
from BaseHTTPServer import HTTPServer
import socket
import os

PORT = 2020

class Handler(SimpleHandler):
	def __init__(self, *args, **params):
		SimpleHandler.__init__(self, *args, **params)

	def translate_path(self, path):
		"""Use server/public as default server directory"""
		path = path.split('?',1)[0]
		path = path.split('#',1)[0]

		path2 = os.path.normpath(os.path.dirname(__file__) + "/public/" + path)
		return path2

	def manage(rule):
		return lambda x:x

	def do_GET(self):
		print "PATH", self.path
		SimpleHandler.do_GET(self)

#class ExampleHandler(Handler):
#	@attach(r"GET /asdf")
#	@attach(r"GET /asdf/bla")
#	def doSomething(self):
#		self.stem
#		self.args

while 1:
	try:
		httpd = HTTPServer(("", PORT), Handler)
		break
	except socket.error:
		PORT += 1


print "serving at http://localhost:%i" % PORT
httpd.serve_forever()
