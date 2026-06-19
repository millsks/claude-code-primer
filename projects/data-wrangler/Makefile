ENV_NAME := data-wrangler
RUN := conda run --no-capture-output -n $(ENV_NAME)

.PHONY: bootstrap fmt lint check test test-integration cov build ci

bootstrap:
	conda env create -f environment.yml 2>/dev/null || conda env update -f environment.yml
	$(RUN) pre-commit install

fmt:
	$(RUN) ruff format .

lint:
	$(RUN) ruff check .

check:
	$(RUN) mypy src/

test:
	$(RUN) pytest tests/unit/

test-integration:
	$(RUN) pytest tests/integration/

cov:
	$(RUN) pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=90

build:
	$(RUN) python -m build

ci: bootstrap
	$(RUN) pre-commit run --all-files
	$(MAKE) build
	$(MAKE) check
	$(MAKE) lint
	$(MAKE) cov
