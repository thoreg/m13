clean:
	find . -name "__pycache__" | xargs rm -rf
	rm -rf htmlcov

test:
	py.test --cov=. --cov-report html

test_over:
	py.test --overwrite

style:
	# black .
	flake8 --config ./tox.ini
	pylint .


check: clean style test

py-cov:
	rm -rf htmlcov
	pytest --cov-report=html --cov=.
