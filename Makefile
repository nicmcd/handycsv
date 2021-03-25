.SUFFIXES:
.PHONY: help install clean lint test benchmark count

help:
	@echo "options are: install clean lint test count"

install:
	python3 setup.py install --user --record files.txt

uninstall:
	cat files.txt | xargs rm -rf

clean:
	rm -rf build dist handycsv.egg-info handycsv/*.pyc handycsv/__pycache__ test/*.pyc test/__pycache__

lint:
	pylint -r n handycsv

test:
	python3 -m unittest -v -f

count:
	@wc handycsv/*.py test/*.py | sort -n -k1
	@echo "files : "$(shell echo handycsv/*.py test/*.py | wc -w)
	@echo "commits : "$(shell git rev-list HEAD --count) 
