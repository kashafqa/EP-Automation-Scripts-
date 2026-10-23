# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a small Playwright browser-automation/testing practice repository written in Python. Tests drive real pages on `https://testautomationpractice.blogspot.com/` (a public test-automation sandbox site) and `https://www.doconcall.com.my/` using Playwright's sync API together with pytest.

This is a git repository. Packages are listed in `requirements.txt`. Settings and credentials live in `.env` (git-ignored; `.env.example` shows the keys). `.github/workflows/tests.yml` runs the suite on GitHub Actions and attaches the Allure report to each run.

## Environment

- Python 3.13
- pytest 9.0.2 with the `pytest-playwright` plugin (provides the `page` fixture and the `--browser`/`--headed` CLI options)
- Playwright 1.58.0

## Commands

Run all tests (headless, Chromium by default):
```
python -m pytest
```

Run a single test file:
```
python -m pytest test_automation.py
```

Run a single test by name:
```
python -m pytest test_automation.py::test_verify_the_field
```

Run headed (watch the browser) for debugging:
```
python -m pytest --headed
```

Run against a different browser:
```
python -m pytest --browser webkit
```

If Playwright browser binaries are missing, install them with:
```
python -m playwright install
```

## Browser testing / UI checks workflow

For any interactive browser testing, UI checks, or clicking through an app (exploring a page, verifying a flow, taking screenshots), always drive the browser via the **Playwright MCP** tools rather than writing and running a throwaway script. Reserve actual Python test code (see Commands above) for when the deliverable is a persisted test in this repo.

## Architecture / conventions

- Each `test_*.py` file is a standalone, flat collection of pytest test functions — there are no classes, fixtures files, or page-object abstractions yet. Every test takes a `page: Page` fixture (injected by `pytest-playwright`) and calls `page.goto(...)` itself; there is no shared `conftest.py` or base URL setup.
- `test_automation.py` targets `https://testautomationpractice.blogspot.com/`'s name-input field and exercises both "happy path" assertions (`expect(...).to_have_value(...)`) and negative/validation checks written as plain `assert` with a descriptive `BUG: ...` failure message — this is the established pattern for documenting expected-vs-actual behavior when a site doesn't enforce the validation a test expects.
- `NAME_FIELD_ID = "#name"` is defined as a module-level locator constant and reused across tests in the same file; prefer this pattern (a module-level constant for a repeated selector) over inlining the same locator string in every test.
- `test_practice.py` is currently empty — treat it as a scratch/placeholder file rather than an indication of removed functionality.
