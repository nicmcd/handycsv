.SUFFIXES:
.PHONY: help install clean lint test benchmark count

help:
	@echo "options are: install clean lint test count"

install:
	python3 setup.py install --user --record files.txt

uninstall:
	cat files.txt | xargs rm -rf

clean:
	rm -rf build dist simplecsv.egg-info simplecsv/*.pyc simplecsv/__pycache__ test/*.pyc test/__pycache__

lint:
	pylint -r n simplecsv

test:
	python3 -m unittest -v -f

count:
	@wc simplecsv/*.py test/*.py | sort -n -k1
	@echo "files : "$(shell echo simplecsv/*.py test/*.py | wc -w)
	@echo "commits : "$(shell git rev-list HEAD --count) 
