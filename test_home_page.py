from playwright.sync_api import Page, expect

# Home page URL is read from the .env file (see config.py).
from config import HOME_URL

# Verify the DoctorOnCall home page opens on the expected URL.
def test_doconcall_homepage_url(page: Page):
    page.goto(HOME_URL)
    expect(page).to_have_url(HOME_URL)
    current_url = page.url
    print(f"Current URL: {current_url}")
