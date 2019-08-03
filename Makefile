.PHONY: default,dev


default:
	python -m halive
dev:
	vim -S Session.vim
test1:
	python -m halive tests/data/urls.txt tests/data/urls2.txt  
test2:
	python -m halive tests/data/urls.txt tests/data/urls2.txt -t 2 -s
test3:
	python -m halive tests/data/urls.txt tests/data/urls2.txt -t 2 -s -o report_test_3.txt
test4:
	python -m halive tests/data/urls.txt tests/data/urls2.txt -t 2 -s --only-urls -o report_test_4.txt
test5:
	python -m halive tests/data/urls3.txt
