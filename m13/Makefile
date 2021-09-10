clean:
	find . -name "__pycache__" | xargs rm -rf
	rm -rf htmlcov

test:
	py.test --cov=. --cov-report html

style:
	isort .
	flake8 .