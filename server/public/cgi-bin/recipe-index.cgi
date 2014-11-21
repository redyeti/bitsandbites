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
from stage2 import SyntaxParsedRecipe

print "<ul>"
for spr in SyntaxParsedRecipe.objects:
	print "<li>"
	print "<a href='recipe.html?recipe=%s'>" % spr.pk
	print spr.origin.uid
	print "</a>"
	print "</li>"
print "</ul>"
