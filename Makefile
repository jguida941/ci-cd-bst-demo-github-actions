PYTHON ?= python
PYTEST ?= $(PYTHON) -m pytest

.PHONY: test coverage mutation clean

test:
	PYTEST_ADDOPTS="--cov=bst --cov-report=term-missing --cov-report=xml --cov-fail-under=95" $(PYTEST)

coverage:
	PYTEST_ADDOPTS="--cov=bst --cov-report=term-missing --cov-report=xml --cov-fail-under=95" $(PYTEST)
	coverage report
	coverage xml -o reports/coverage.xml

mutation:
	rm -rf .mutmut-cache
	mutmut run
	mutmut results

clean:
	rm -rf .mutmut-cache .coverage reports
