clean:
	find . -name "__pycache__" | xargs rm -rf
	rm -rf htmlcov

test:
	pytest --import-mode=importlib --ds=m13.config.develop .

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
