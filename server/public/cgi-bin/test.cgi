#!/usr/bin/env python

print 'Content-Type: application/json' 
print                          

import cgitb, cgi
cgitb.enable()
form = cgi.FieldStorage()

# fix the import paths
import sys, os
sys.path.insert(0, os.path.abspath("."))

import json
import db

print json.dumps({
	"a": form.getfirst("a"),
	"b": form.getlist("b"),
})
