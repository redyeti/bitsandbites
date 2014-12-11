import sys, bz2
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
	from stage2 import lang, mktree, SyntaxParsedRecipe, Block, RecipeMeta
	SyntaxParsedRecipe.objects.delete()
	RecipeMeta.objects.delete()

	for doc, d in Layoutparser.parseDB(ignore_errors=True):
		print "origin:", doc.uid
		spr = SyntaxParsedRecipe(origin=doc)
		for i,ingr in enumerate(d['Ingredients']):
			t = lang.process(ingr, False)
			m = mktree(t)
			s = Block(tree=m, position=(i,))
			spr.ingredients.append(s)
		for i,step in enumerate(d['Procedure']):
			for j,sentence in enumerate(step):
				t = lang.process(sentence, True)
				m = mktree(t)
				print "Tr:", m
				s = Block(tree=m, position=(i,j))
				spr.sentences.append(s)
		spr.save()

		textblob = reduce(lambda a,b:a+b, d['Procedure'], [])
		textblob = "".join(textblob)
		RecipeMeta(spr=spr, sblob=textblob).save()

# -- stage 3 --

if "3" in args:
	from stage2 import SyntaxParsedRecipe
	import db
	from pprint import pprint
	from collections import defaultdict
	from stage3 import InstructionFactory
	from stage3 import InstructionError
	from stage3 import RuleSample, RasmInstruction

	RuleSample.objects.delete()	

	errors = defaultdict(lambda:0)
	for spr in SyntaxParsedRecipe.objects:
		ifc = InstructionFactory()
		for i in spr.ingredients:
			if i.tree.children:
				print i.tree
				try:
					print ifc.interpretDeclaration(i.tree.children, i.position)
				except InstructionError as e:
					errors[e.key] += 1
		for s in spr.sentences:
			instructs = s.tree.children['Instruct']
			print
			#print "Coverage: %i%%" % (100.*len(instructs.leaves)/float(len(s.tree.leaves)))
			for n, ins in enumerate(instructs.children):
				if ins.children:
					try:
						print ifc.interpretInstruction(ins, s.position+[n])
					except AssertionError as e:
						errors["assertion"] += 1
					except InstructionError as e:
						errors[e.key] += 1
		try:
			ifc.finalize()
		except InstructionError as e:
			errors[e.key] += 1

	m = max(errors.values())
	for i in range(m):
		for k,v in errors.iteritems():
			if v == i+1:
				print v, k

if "4" in args:
	import stage4
	import db
	stage4.Rule.objects.delete()
	stage4.run()
