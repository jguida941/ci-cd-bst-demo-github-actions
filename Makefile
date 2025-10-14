PYTHON ?= python
PYTEST ?= $(PYTHON) -m pytest

.PHONY: test coverage mutation clean

test:
	mkdir -p reports
	PYTEST_ADDOPTS="--cov=bst --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-fail-under=95" $(PYTEST)

coverage:
	mkdir -p reports
	PYTEST_ADDOPTS="--cov=bst --cov-report=term-missing --cov-report=xml:reports/coverage.xml --cov-fail-under=95" $(PYTEST)
	coverage report

mutation:
	rm -rf .mutmut-cache
	mutmut run
	mutmut results

clean:
	rm -rf .mutmut-cache .coverage reports
