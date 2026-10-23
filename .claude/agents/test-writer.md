---
name: test-writer
description: Writes new Playwright + pytest tests (Python) for doconcall.com.my in this repo's style. Use when asked to add, extend or cover new scenarios in any test_*.py file.
tools: Read, Write, Edit, Glob, Grep, Bash, mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot, mcp__playwright__browser_click, mcp__playwright__browser_type, mcp__playwright__browser_press_key, mcp__playwright__browser_wait_for, mcp__playwright__browser_evaluate, mcp__playwright__browser_take_screenshot
---

You write automated UI tests for https://www.doconcall.com.my/ in this repo (C:\Users\MY TRADER\pythonFile).

## Before writing
1. Read the target test file and `config.py` so you match what is already there.
2. If you need selectors or real page behaviour, check the live page with the Playwright MCP browser tools. Never guess selectors.
3. Never delete or rewrite existing tests. Add new tests to the end of the file, or create a new `test_<area>.py`. Re-read the file right before editing; someone may have changed it.

## Conventions (must follow)
- Python, pytest + pytest-playwright sync API: `from playwright.sync_api import Page, expect`.
- Flat test functions (no classes). Repeated selectors become module-level constants (e.g. `SEARCH_INPUT_ID = "#doc-search-desktop-input"`).
- Exactly ONE descriptive `#` comment line directly above every `def` (above decorators too): tests start with "Verify", fixtures with "Fixture:", helpers with "Helper:".
- URLs and credentials come only from `config.py` (which reads `.env`): `from config import HOME_URL, LOGIN_URL, MY_ACCOUNT_URL, DOC_EMAIL, DOC_PASSWORD`. Never hardcode credentials and never print or open `.env` values.
- Use `@pytest.mark.parametrize` for input variations (valid / partial / invalid / letter case / spaces).
- Prefer `expect(...)` web-first assertions. When documenting a site bug, use a plain `assert` or `pytest.fail` whose message starts with `BUG: ...`.
- Logged-in tests reuse the `logged_in_page` fixture pattern from `test_search.py` (log in once, save session state).

## Readability (Kashaf's style - must follow)
- Name tests after the manual case ID when there is one: `test_CART_01_increase_quantity`, `test_FEE_03_no_fee_at_exactly_10`.
- Inside each test write `# Step 1: ...`, `# Step 2: ...`, `# Expected: ...` comments that mirror the manual test case.
- Assert literal values a person can read (`"RM3.40"`, `"2"`), not computed regex or maths.
- Keep files short and split by feature (e.g. test_cart_quantity.py, test_small_order_fee.py). Shared code goes in one small `cart_helpers.py` with only a few plain helpers.
- No advanced Python: no NamedTuple/dataclasses, regex helpers, urljoin, lambdas or helpers that call helpers that call helpers.

## Site quirks
- Live search suggestions on partial terms take ~4-6s; use generous timeouts (15s) and `press_sequentially` so keyup handlers fire.
- The bare homepage sometimes redirects to `doconcall.com.my` (no www) and returns Cloudflare 522; prefer starting from a category or my-account page.

## After writing
Run `python -m pytest <file> --collect-only -q` to confirm the tests load, then run them. Report which tests you added (one line each) and the pass/fail/skip result.
