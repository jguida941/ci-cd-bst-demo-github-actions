
# Binary Search Tree (BST) + GitHub Actions CI/CD

⚡ This simple project demonstrates a **Binary Search Tree** implemented in **Python**, automatically tested through **GitHub Actions CI/CD**.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Recursion](https://img.shields.io/badge/Recursion-Enabled-green)
![Data Structures](https://img.shields.io/badge/Data%20Structures-BST-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
[![Tests - main](https://github.com/jguida941/GithubActionsDemo/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jguida941/GithubActionsDemo/actions/workflows/tests.yml?query=branch%3Amain)
[![Tests - fail-demo](https://github.com/jguida941/GithubActionsDemo/actions/workflows/tests.yml/badge.svg?branch=fail-demo)](https://github.com/jguida941/GithubActionsDemo/actions/workflows/tests.yml?query=branch%3Afail-demo)
[![Coverage](https://codecov.io/gh/jguida941/GithubActionsDemo/branch/main/graph/badge.svg)](https://codecov.io/gh/jguida941/GithubActionsDemo)
![Mutation Testing](https://img.shields.io/badge/Mutation%20Testing-mutmut%20clean-brightgreen)
[![Security Scan](https://github.com/jguida941/GithubActionsDemo/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/jguida941/GithubActionsDemo/actions/workflows/security.yml?query=branch%3Amain)


## Branch Demo

- `main` stays green with the fixed BST implementation.
- `fail-demo` intentionally keeps the buggy insert/search logic so the red badge proves CI catches regressions.
- Both branches run the exact same workflow, so you see green vs. red side-by-side.

Quick way to recreate the failing branch:

```bash
git checkout -b fail-demo
# flip a comparison in bst/binary_search.py (for example change `<` to `>` inside _insert)
git commit -am "demo: introduce BST regression"
git push origin fail-demo
```

Then open a PR from `fail-demo` into `main`. The tests, coverage gate, and mutmut job all fail. Push a fix to that PR and the badges turn green again.


## Continuous Integration (CI)

Every time you **push** or **open a pull request**, GitHub Actions automatically:

1. Runs `ruff` for linting (style, import order, best practices).
2. Runs `mypy` to ensure the tree implementation type-checks.
3. Spins up Python 3.10, installs from `requirements-dev.txt`, and executes the suite with coverage enabled (matching `pytest.ini` defaults).
4. Generates a Markdown test report, attaches logs/JUnit XML, updates the job summary, and comments on pull requests.
5. Optionally emails the same report if SMTP credentials are configured (see below).

### Workflow breakdown

- **lint** job: installs tooling via `requirements-dev.txt` and runs `ruff check .` so style violations fail fast.
- **type-check** job: runs `mypy bst` to catch interface mistakes before runtime.
- **test** job: depends on both jobs, runs the full pytest suite with coverage (enforcing a 95% minimum), produces a Markdown summary, uploads artifacts, posts PR comments, emails the report (optional), and ships coverage to Codecov.
- **mutation** job: runs `mutmut` after unit tests, failing the workflow if any mutants survive the suite.
- **security** workflow: executes `pip-audit`, Bandit, Ruff security rules, CodeQL analysis, dependency review, and CycloneDX SBOM generation on push/PR/weekly cron, with SARIF artifacts uploaded to the Security tab.
- Workflow triggers on `main` (healthy) and `fail-demo` (intentionally broken) so you always see a green and red badge side-by-side.

### Why CI/CD matters here

Automated verification means every commit proves that:

- The tree still respects ordering guarantees (traversal tests).
- Lookup paths return the right nodes (search tests).
- Critical deletion scenarios keep the tree valid (delete tests).
- Duplicate inserts are rejected while new inserts stay ordered (insert tests).
- Style and typing remain consistent with the shared guidelines.

That combination is good practice: fast feedback, reproducible environments, and a clear demonstration that regressions are caught before they reach production.


## Local Setup

Replicate the CI environment locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

`requirements.txt` stays empty on purpose: there are no runtime dependencies, while `requirements-dev.txt` layers on linting, typing, and test tooling.

### Local dev quickstart (Python 3.10)

```bash
# activate your virtualenv first
python -m pytest -q
coverage run -m pytest -q && coverage xml
coverage report --fail-under=95
rm -rf .mutmut-cache && mutmut run && mutmut results | head -40
ruff check .
mypy bst
```

Those are the exact commands the workflows run: unit tests with coverage, mutation testing without coverage noise, and the fast lint/type passes.



## Purpose

This repo intentionally includes both a **broken** and a **fixed** version of the `insert()` method to demonstrate automated testing through CI/CD.



### Broken Code Example

This version has **directions flipped**, causing unit tests to fail.

```python
if key > node.key:
    node.left = self._insert(node.left, key)
elif key < node.key:
    node.right = self._insert(node.right, key)
return node
```


### Correct Code Example

This fixes the insertion direction logic.

```Python
if key < node.key:
    node.left = self._insert(node.left, key)
elif key > node.key:
    node.right = self._insert(node.right, key)
return node
```



### Failed Unit Test Example

When the logic is wrong, GitHub Actions automatically catches it:

```
_____________________________ test_inorder_traversal ___________________________

    def test_inorder_traversal(bst_tree):
>       assert bst_tree.inorder() == [20, 30, 40, 50, 60, 70, 80]
E       assert [80, 70, 60, 50, 40, 30, 20] == [20, 30, 40, 50, 60, 70, 80]

tests/test_traversal.py:2: AssertionError
```



### Passing Unit Tests Example

After fixing the code, the CI pipeline passes cleanly:

```
============================= test session starts ==============================
platform linux -- Python 3.10.x, pytest-8.x, pluggy-1.x
collected 18 items

tests/test_delete.py ........
tests/test_delete_missing.py .
tests/test_delete_one_child.py ..
tests/test_delete_successor.py .
tests/test_edge_cases.py ...
tests/test_fuzz_invariants.py .
tests/test_insert.py ..
tests/test_search.py ...
tests/test_traversal.py .
tests/test_traversal_empty.py .

============================== 18 passed in 0.2s ==============================
Required test coverage of 95% reached: 100.00%
```


## Test Reporting, Coverage & Notifications

- The `test` job writes `reports/report.md`, `reports/pytest.log`, `reports/junit.xml`, and `reports/coverage.txt`/`coverage.xml`.
- The Markdown report is visible in the GitHub Actions job summary, stored as an artifact, posted as a PR comment, and the coverage XML is uploaded to Codecov for tracking the badge above.
- Email delivery requires repository secrets (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `MAIL_FROM`, `MAIL_TO`). Set `MAIL_TO` to `justinguidascell@gmail.com` (or any recipient) and use an App Password/API key when your provider requires it.
- Codecov uploads require a `CODECOV_TOKEN` secret (Settings → Secrets and variables → Actions). Paste the repository token from Codecov so the workflow can authenticate uploads—no token is embedded in the badge URL.

## Test Suite Highlights

- `tests/test_traversal.py` validates in-order traversal stays sorted.
- `tests/test_search.py` covers hits and misses in the tree search.
- `tests/test_delete.py` exercises leaf removal, interior node removal, and root replacement.
- `tests/test_insert.py` checks duplicate guard rails and ordering when new keys are added.
- `tests/conftest.py` centralizes the baseline tree fixture so every test starts from the same state.
- `tests/test_edge_cases.py` hits empty-tree searches/deletes and duplicate inserts (covering early returns on lines 33–57).
- `tests/test_delete_one_child.py` validates deleting roots with a single child on either side (lines 80–91).
- `tests/test_delete_missing.py` ensures deleting a non-existent key leaves the tree untouched (line 80 guard).
- `tests/test_delete_successor.py` drives the inorder-successor loop deep into the right subtree (lines 119–129).
- `tests/test_traversal_empty.py` covers the empty traversal path so the DFS guard stays exercised.

## Coverage, Mutation, and Security Testing

**Coverage**
- Pytest runs with `--cov=bst --cov-fail-under=95`, and the workflow uploads `reports/coverage.xml` to Codecov.

**Mutation testing**
- `mutmut run` executes after unit tests; the job fails if any mutants survive. The mutation report is archived as an artifact.

**Property-based fuzzing**
- `tests/test_fuzz_invariants.py` (Hypothesis) hammers random insert/delete sequences to ensure BST invariants hold.

**Security scanning**
- `pip-audit` checks dependencies for known CVEs (SARIF uploaded to GitHub code scanning).
- `bandit` runs security-focused static analysis on the BST module (SARIF uploaded).
- `ruff` security/bugbear rules lint for insecure Python patterns (SARIF uploaded).
- GitHub CodeQL analyzes the repository and surfaces alerts in Security → Code scanning.
- CycloneDX SBOM (`cyclonedx-bom`) generates `sbom.json` so dependency inventories are tracked.
- Dependabot opens weekly grouped PRs for pip packages and GitHub Actions, keeping dependencies current.

Sample local/CI run (coverage gate satisfied):

```bash
# coverage & mutation
pip install -r requirements-dev.txt
make test
make mutation
# security checks (local)
pip-audit -r requirements.txt
bandit -r bst -f txt
ruff check . --select S,B
```


## Make Targets

- `make test` : run the full pytest suite with `--cov` enabled and a 95 % fail-under gate (mirrors the CI workflow).
- `make coverage` : rerun tests, print the terminal coverage report, and regenerate `reports/coverage.xml`.
- `make mutation` : execute `mutmut` against `bst/binary_search.py` (pytest runs without coverage but must still kill every mutant).
- `make clean` : remove caches (`.mutmut-cache`, `.coverage`, `reports/`).

## Unit Testing with Pytest

<img width="670" height="871" alt="Screenshot 2025-10-14 at 11 48 16 AM" src="https://github.com/user-attachments/assets/c13eac36-b918-4516-88ea-beb95aaa20c3" />


## Coverage & Mutation Analysi

<img width="500" height="488" alt="Screenshot 2025-10-14 at 11 43 02 AM" src="https://github.com/user-attachments/assets/b9558c2b-b726-4f3f-a30f-01927acdb5d4" />

## Property-Based Fuzz Testing (Hypothesis)

<img width="1027" height="523" alt="Screenshot 2025-10-14 at 11 47 30 AM" src="https://github.com/user-attachments/assets/4e2923e8-60fd-4500-9e3d-e06e86ee2a7b" />




## Tech Stack
- Python 3.10
- Pytest & unittest (unit tests + Hypothesis property tests)
- Mutation testing with mutmut
- Linting with Ruff
- Type checking with mypy
- Coverage via coverage.py / Codecov
- Security scans: pip-audit, Bandit, Ruff security, CodeQL
- CycloneDX SBOM generation
- GitHub Actions (CI/CD)


## Project Structure

```text
binary_search_tree/
├── bst/
│   └── binary_search.py
├── tests/
│   ├── conftest.py
│   ├── test_delete.py
│   ├── test_delete_missing.py
│   ├── test_delete_one_child.py
│   ├── test_delete_successor.py
│   ├── test_edge_cases.py
│   ├── test_insert.py
│   ├── test_search.py
│   ├── test_traversal.py
│   └── test_traversal_empty.py
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── pytest.ini
├── pytest.mutmut.ini
├── setup.cfg
├── CODEOWNERS
├── SECURITY.md
├── LICENSE
├── .gitignore
└── .github/
    └── workflows/
        ├── tests.yml
        └── security.yml
```

## License
```

MIT License © 2025
