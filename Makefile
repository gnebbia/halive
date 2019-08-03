.PHONY: default,dev


default:
	python -m halive
dev:
	vim -S Session.vim
test1:
	python -m halive tests/data/urls.txt tests/data/urls2.txt  
test2:
	python -m halive tests/data/urls.txt tests/data/urls2.txt -t 2 -s
