clean:
	find . -name "__pycache__" | xargs rm -rf
	rm -rf htmlcov

test:
	py.test --cov=. --cov-report html

test_over:
	py.test --overwrite


style:
	isort .
	flake8 .