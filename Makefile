PYTHON ?= python

.PHONY: install test lint build release clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

build:
	$(PYTHON) -m build

release: test build
	$(PYTHON) scripts/create_source_release.py

clean:
	rm -rf build dist .pytest_cache htmlcov .coverage *.egg-info
