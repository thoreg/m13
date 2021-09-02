clean:
	find . -name "__pycache__" | xargs rm -rf

test:
	py.test --cov=. --cov-report html

style:
	isort .
	flake8 .