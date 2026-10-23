import re

import pytest
from playwright.sync_api import Page, expect

# URLs and login credentials are read from the .env file (see config.py).
from config import DOC_EMAIL, DOC_PASSWORD, LOGIN_URL, MY_ACCOUNT_URL

SEARCH_INPUT_ID = "#doc-search-desktop-input"
SEARCH_DROPDOWN_ID = "#doc-search-desktop-dropdown"
RESULT_TITLES = f"{SEARCH_DROPDOWN_ID} .doc-search-results-list h5"
NO_RESULTS_TEXT = "No products found matching your search."

FULL_PRODUCT_NAME = "Panadol Extend SR 665mg Caplet"
# Live search is slow on partial terms (~4-6s), so give suggestions room to load.
SEARCH_TIMEOUT_MS = 15_000

pytestmark = pytest.mark.skipif(
    not (DOC_EMAIL and DOC_PASSWORD),
    reason="Fill in DOC_EMAIL and DOC_PASSWORD in .env to run logged-in search tests",
)


# Fixture: logs in once per test run and saves the session cookies to a temp file that every test reuses.
@pytest.fixture(scope="session")
def auth_state_file(browser, tmp_path_factory) -> str:
    state_file = tmp_path_factory.mktemp("auth") / "state.json"
    context = browser.new_context()
    page = context.new_page()
    page.goto(LOGIN_URL)
    page.get_by_role("button", name="Continue with Email / Password").click()
    page.locator("#email").fill(DOC_EMAIL)
    page.locator("#password").fill(DOC_PASSWORD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url(f"{MY_ACCOUNT_URL}**", timeout=30_000)
    context.storage_state(path=state_file)
    context.close()
    return str(state_file)


# Fixture: starts every test's fresh browser context with the saved login session.
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, auth_state_file):
    return {**browser_context_args, "storage_state": auth_state_file}


# Fixture: opens My Account with the saved session and verifies the user is still logged in.
@pytest.fixture
def logged_in_page(page: Page) -> Page:
    page.goto(MY_ACCOUNT_URL)
    expect(page.get_by_role("link", name="Sign Up/In")).to_have_count(0)
    return page


# Helper: clears the search box and types the term key by key to trigger live search suggestions.
def search_for(page: Page, term: str) -> None:
    search_box = page.locator(SEARCH_INPUT_ID)
    search_box.fill("")
    # Type key by key so the site's live-search (keyup) handler fires.
    search_box.press_sequentially(term, delay=50)

# Verify the search bar is visible, enabled, has the 'Search medicines' placeholder and a Submit button for a logged-in user.
def test_search_bar_displayed_to_logged_in_user(logged_in_page: Page):
    search_box = logged_in_page.locator(SEARCH_INPUT_ID)
    expect(search_box).to_be_visible()
    expect(search_box).to_be_enabled()
    expect(search_box).to_have_attribute("placeholder", "Search medicines")
    expect(logged_in_page.get_by_role("button", name="Submit Search").first).to_be_visible()


# Verify a valid medicine name in lowercase, UPPERCASE, Title case and MiXeD case returns only matching Panadol products.
@pytest.mark.parametrize("term", ["panadol", "PANADOL", "Panadol", "PaNaDoL"])
def test_search_valid_medicine_name_any_letter_case(logged_in_page: Page, term: str):
    search_for(logged_in_page, term)
    titles = logged_in_page.locator(RESULT_TITLES)
    expect(titles.first).to_be_visible(timeout=SEARCH_TIMEOUT_MS)
    for title in titles.all_inner_texts():
        assert "panadol" in title.lower(), f"BUG: '{term}' returned unrelated product '{title}'"


# Verify the full product name typed as-is, in all CAPS and in all small letters returns exactly that one product.
@pytest.mark.parametrize("term", [FULL_PRODUCT_NAME, FULL_PRODUCT_NAME.upper(), FULL_PRODUCT_NAME.lower()])
def test_search_full_product_name_any_letter_case(logged_in_page: Page, term: str):
    search_for(logged_in_page, term)
    titles = logged_in_page.locator(RESULT_TITLES)
    expect(titles).to_have_count(1, timeout=SEARCH_TIMEOUT_MS)
    expect(titles.first).to_have_text(FULL_PRODUCT_NAME)


# Verify a half/partial medicine name (start or middle of the word, any case) still suggests Panadol products.
@pytest.mark.parametrize("term", ["pana", "PANA", "nadol"])
def test_search_partial_medicine_name(logged_in_page: Page, term: str):
    search_for(logged_in_page, term)
    titles = logged_in_page.locator(RESULT_TITLES)
    expect(titles.filter(has_text=re.compile("panadol", re.IGNORECASE)).first).to_be_visible(timeout=SEARCH_TIMEOUT_MS)


# Verify an invalid name, a misspelling and special characters show 'No products found' with no product results.
@pytest.mark.parametrize("term", ["xyzqwe123", "panadoll", "@@@###"])
def test_search_invalid_medicine_name_shows_no_results(logged_in_page: Page, term: str):
    search_for(logged_in_page, term)
    dropdown = logged_in_page.locator(SEARCH_DROPDOWN_ID)
    expect(dropdown).to_contain_text(NO_RESULTS_TEXT, timeout=SEARCH_TIMEOUT_MS)
    expect(logged_in_page.locator(RESULT_TITLES)).to_have_count(0)


# Verify leading and trailing spaces around a valid medicine name are ignored and results still appear.
def test_search_trims_surrounding_spaces(logged_in_page: Page):
    search_for(logged_in_page, "   panadol   ")
    titles = logged_in_page.locator(RESULT_TITLES)
    expect(titles.first).to_contain_text("Panadol", timeout=SEARCH_TIMEOUT_MS)


# Verify results refresh (no stale Panadol results) when a valid search is replaced with an invalid term.
def test_search_results_refresh_after_changing_term(logged_in_page: Page):
    search_for(logged_in_page, "panadol")
    expect(logged_in_page.locator(RESULT_TITLES).first).to_be_visible(timeout=SEARCH_TIMEOUT_MS)

    search_for(logged_in_page, "xyzqwe123")
    dropdown = logged_in_page.locator(SEARCH_DROPDOWN_ID)
    try:
        expect(dropdown).to_contain_text(NO_RESULTS_TEXT, timeout=SEARCH_TIMEOUT_MS)
    except AssertionError:
        stale = logged_in_page.locator(RESULT_TITLES).all_inner_texts()
        pytest.fail(f"BUG: after replacing 'panadol' with an invalid term the dropdown still shows stale results: {stale}")
