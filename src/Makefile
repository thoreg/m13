.PHONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Delete all bytecode and coverage data
	find . -name "__pycache__" | xargs rm -rf
	rm -rf htmlcov

test: ## Run the tests
	uv run pytest --import-mode=importlib --ds=m13.config.develop .

testv: ## Run the tests in verbose mode
	uv run pytest -vv -s --import-mode=importlib --ds=m13.config.develop .

test_over: ## Run the tests and overwrite the dumps
	uv run pytest --overwrite --import-mode=importlib --ds=m13.config.develop .

style: ## Run style checks and static code analyzers
	# ruff .
	flake8 --config ./tox.ini
	pylint .

format: ## Run formatter
	isort .
	black .

check: clean style test

py-cov: ## Run the tests and collect coverage data
	rm -rf htmlcov
	uv run pytest --import-mode=importlib --ds=m13.config.develop --cov-report=html --cov=.
