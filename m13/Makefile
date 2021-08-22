clean:
	find . -name "__pycache__" | xargs rm -rf

test:
	py.test

style:
	isort .
	flake8 .