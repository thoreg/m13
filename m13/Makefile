clean:
	find . -name "__pycache__" | xargs rm -rf
	rm -rf htmlcov

test:
	pytest --import-mode=importlib --ds=m13.config.develop .

testv:
	pytest -vv -s --import-mode=importlib --ds=m13.config.develop .

test_over:
	pytest --overwrite --import-mode=importlib --ds=m13.config.develop .

style:
	# ruff .
	flake8 --config ./tox.ini
	pylint .

format:
	isort .
	black .

check: clean style test

py-cov:
	rm -rf htmlcov
	pytest --import-mode=importlib --ds=m13.config.develop --cov-report=html --cov=.
