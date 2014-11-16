
.PHONY: depends

depends: maltparser-1.8/maltparser-1.8.jar engmalt.linear-1.7.mco
	python ./depends.py
	
maltparser.tar.gz:
	wget -O $@ http://maltparser.org/dist/maltparser-1.8.tar.gz

maltparser-1.8/maltparser-1.8.jar: maltparser.tar.gz
	tar xf maltparser.tar.gz

engmalt.linear-1.7.mco:
	wget -O $@ http://www.maltparser.org/mco/english_parser/engmalt.linear-1.7.mco
