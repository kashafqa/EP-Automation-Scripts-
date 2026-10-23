# pytest loads this file automatically, so every test file can use the guest_page fixture without importing it.
import allure
import pytest
from playwright.sync_api import Page

from cart_helpers import PROMO_POPUP, close_promo_popup


# Hook: saves each test's result on the test (request.node.result) so the fixture below can see if it failed.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.result = report


# Fixture: a fresh guest (not logged in) page that closes the promo popup automatically whenever it blocks a click.
# After the test, if it failed, a screenshot of the page is attached to the Allure report
# (skipped if the browser has already closed, so it never adds an extra error).
@pytest.fixture
def guest_page(page: Page, request) -> Page:
    page.add_locator_handler(page.locator(PROMO_POPUP), close_promo_popup)
    yield page

    result = getattr(request.node, "result", None)
    if result is not None and result.failed:
        try:
            allure.attach(page.screenshot(full_page=True), name="Screenshot on failure", attachment_type=allure.attachment_type.PNG)
        except Exception:
            print("Could not take the failure screenshot - the browser was already closed")
