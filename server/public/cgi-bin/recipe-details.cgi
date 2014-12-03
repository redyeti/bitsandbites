#!/usr/bin/env python

print 'Content-Type: text/html' 
print                          

import cgitb, cgi
cgitb.enable()
form = cgi.FieldStorage()

# fix the import paths
import sys, os
reload(sys)
sys.setdefaultencoding("utf8")

sys.path.insert(0, os.path.abspath("."))

import json
import db
from stage2 import SyntaxParsedRecipe

pk = form.getfirst("recipe")

print "Id:", pk

spr = SyntaxParsedRecipe.objects(id=pk)[0]

from stage2 import SyntaxParsedRecipe
import db
from pprint import pprint
from collections import defaultdict
from stage3 import InstructionFactory
from stage3 import InstructionError
from lxml import etree

ifc = InstructionFactory()
for i in spr.ingredients:
	if i.tree.children:
		print etree.tostring(ifc.re.html)
		print "<div class='tree'>"
		print etree.tostring(i.tree.html)
		print "</div>"
		print etree.tostring(ifc.interpretDeclaration(i.tree.children, i.position).html)
for s in spr.sentences:
	instructs = s.tree.children['Instruct']
	print
	#print "Coverage: %i%%" % (100.*len(instructs.leaves)/float(len(s.tree.leaves)))
	for n, ins in enumerate(instructs.children):
		if ins.children:
			print etree.tostring(ifc.re.html)
			print "<div class='tree'>"
			print etree.tostring(ins.html)
			print "</div>"
			try:
				print etree.tostring(ifc.interpretInstruction(ins, s.position+[n]).html)
			except AssertionError as e:
				print "<b>%s</b>" % e
			except InstructionError as e:
				print "<b>%s</b>" % e
try:
	ifc.finalize()
except InstructionError as e:
	print "<b>%s</b>" % e
