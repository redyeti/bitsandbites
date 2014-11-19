import sys
reload(sys)
sys.setdefaultencoding("utf8")

args = sys.argv[1:]

# -- stage 1 --

if "1" in args:
	from stage1 import fetch
	from stage2.layoutparse import Layoutparser
	from pprint import pprint

	fetch.wikibooks(["Cake recipes"])

# -- stage 2 --

if "2" in args:
	from stage2.layoutparse import Layoutparser
	from stage2 import lang, mktree, SyntaxParsedRecipe, Block
	SyntaxParsedRecipe.objects.delete()

	for doc, d in Layoutparser.parseDB(ignore_errors=True):
		print "origin:", doc.uid
		spr = SyntaxParsedRecipe(origin=doc)
		for i,ingr in enumerate(d['Ingredients']):
			t = lang.process(ingr)
			m = mktree(t)
			s = Block(tree=m, position=(i,))
			spr.ingredients.append(s)
		for i,step in enumerate(d['Procedure']):
			for j,sentence in enumerate(step):
				t = lang.process(sentence)
				m = mktree(t)
				print "Tr:", m
				s = Block(tree=m, position=(i,j))
				spr.sentences.append(s)
		spr.save()

# -- stage 3 --

if "3" in args:
	from stage2 import SyntaxParsedRecipe
	import db
	from pprint import pprint

	from stage3 import InstructionFactory

	ifc = InstructionFactory()
	for spr in SyntaxParsedRecipe.objects:
		for i in spr.ingredients:
			if i.tree.children:
				print i.tree
				print ifc.interpretDeclaration(i.tree, i.position)
		for s in spr.sentences:
			instructs = s.tree.children['Instruct']
			print
			print "Coverage: %i%%" % (100.*len(instructs.leaves)/float(len(s.tree.leaves)))
			print s.tree
			print "--"
			for n, ins in enumerate(instructs.children):
				if ins.children:
					print ifc.interpretInstruction(ins, s.position+[n])
