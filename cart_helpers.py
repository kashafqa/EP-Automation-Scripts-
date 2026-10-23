# Shared constants and a few small helpers for the cart and small order fee tests.
# Site URL comes from the .env file (see config.py).
from playwright.sync_api import Page, expect

from config import HOME_URL

# ---- Pages ----
CART_URL = f"{HOME_URL}cart/"
CHECKOUT_URL = f"{HOME_URL}checkout/"
ALL_PRODUCTS_URL = f"{HOME_URL}all-products/" 

# ---- Products (non-Rx, prices as shown on the site) ----
MAALOX_URL = f"{HOME_URL}pharmacy/maalox-oral-suspension-sachet/"
MAALOX_NAME = "Maalox Oral Suspension Sachet"
MAALOX_PRICE = "RM1.70"
MAALOX_PACK = "4.3ml x1"
MAALOX_IMAGE = "maalox-oral-suspension-sachet-featured"
MAALOX_BIG_PACK = "4.3ml x20"
MAALOX_BIG_PACK_PRICE = "RM26.60"

UPHALYTE_URL = f"{HOME_URL}pharmacy/duopharma-uphalyte-oral-rehydration-salts-natural-flavour/"
UPHALYTE_NAME = "Duopharma Uphalyte Oral Rehydration Salts – Natural Flavour"
# The cart writes the en dash (–) of the product title as a plain hyphen (-).
UPHALYTE_CART_NAME = "Duopharma Uphalyte Oral Rehydration Salts - Natural Flavour"
UPHALYTE_PRICE = "RM0.90"
UPHALYTE_PACK = "1s"
UPHALYTE_IMAGE = "duopharma-uphalyte-oral-rehydration-salts-natural-flavour-featured"

RAZOR_URL = f"{HOME_URL}pharmacy/gillette-blue-ii-plus-hanging-card-razor/"
RAZOR_PRICE = "RM3.20"

DIMECTAL_URL = f"{HOME_URL}pharmacy/dimectal-powder-for-oral-suspension-3g/"
DIMECTAL_PRICE = "RM1.83"

FEE = "RM5.00"

# ---- Promo popup (appears ~1.5s after load and blocks clicks) ----
PROMO_POPUP = "#doc-promo-popup-lightbox.active"

# ---- Product page ----
PRODUCT_TITLE = "h1.product-title"
PRODUCT_PRICE = ".current-dynamic-price"
PRODUCT_PACK = "form.cart .swatch-item:has(input.swatch-input:checked) label.swatch-label"
PACK_BUTTON = "form.cart .swatch-item label.swatch-label"
PRODUCT_IMAGE = ".main-image-wrapper img"
ADD_QTY_BOX = "form.cart input.qty"
ADD_TO_CART_BUTTON = "form.cart .single_add_to_cart_button"
CART_BADGE = ".doc-cart-count-fragment"

# ---- Search box ----
SEARCH_BOX = "#doc-search-desktop-input"
SEARCH_RESULTS = "#doc-search-desktop-dropdown .doc-search-results-list h5"

# ---- Cart page ----
CART_LINE = ".cart-item"
LINE_NAME = ".product-name a"
LINE_IMAGE = ".cart-item-image img"
LINE_PACK = "dl.variation dd"
LINE_PRICE = ".product-price"
QTY_BOX = "input.qty"
PLUS_BUTTON = "input.plus"
MINUS_BUTTON = "input.minus"
TRASH_BUTTON = "a.remove-item"
CART_SUMMARY = "#cart-summary"
SUBTOTAL = '#cart-summary [data-title="Subtotal"]'
FEE_ROW = '#cart-summary [data-title="Small Order Fee"]'
ESTIMATED_TOTAL = '#cart-summary [data-title="Estimated Total"]'
VOUCHER_ROWS = "#cart-summary .applied-vochers .cart-discount"
VOUCHER_AMOUNTS = "#cart-summary .applied-vochers .cart-discount .amount"
REMOVE_COUPON_LINK = "#cart-summary a.woocommerce-remove-coupon"
CHECKOUT_BUTTON = "#cart-summary a.checkout-button"
PROMO_CODE_TOGGLE = "#cart-summary details.sidebar-coupon-details > summary"
COUPON_BOX = "#coupon_code"
APPLY_COUPON_BUTTON = '#cart-summary button[name="apply_coupon"]'
AUTO_APPLY_VOUCHERS_BUTTON = 'button[name="doc_auto_apply_vouchers"]'
ERROR_MESSAGE = ".woocommerce-error"
NOTICE_MESSAGE = ".woocommerce-message"
FREE_DELIVERY_BAR = ".free-delivery-message-wrapper"

# ---- "Remove Item" popup (shown by - at qty 1) ----
REMOVE_POPUP = "#doc-confirm-lightbox"
REMOVE_POPUP_OPEN = "#doc-confirm-lightbox.active"
REMOVE_POPUP_TITLE = "#doc-confirm-title"
REMOVE_POPUP_MESSAGE = "#doc-confirm-message"
REMOVE_POPUP_CONFIRM = "#doc-confirm-action-btn"
REMOVE_POPUP_CANCEL = "#doc-confirm-lightbox a.doc-close-lightbox.main-button"
REMOVE_POPUP_X = "#doc-confirm-lightbox a.doc-close-lightbox.x"

# ---- Empty cart ----
EMPTY_CART = ".doc-empty-cart-wrapper"
EMPTY_CART_HEADING = ".doc-empty-cart-wrapper h2"
EMPTY_CART_BUTTON = ".doc-empty-cart-wrapper a.button"

# ---- Checkout page (order review box) ----
CHECKOUT_SUBTOTAL = '#order_review [data-title="Subtotal"]'
CHECKOUT_FEE_ROW = '#order_review [data-title="Small Order Fee"]'
CHECKOUT_GRAND_TOTAL = '#order_review [data-title="Grand Total"]'


# Helper: closes the promo popup (Playwright calls this automatically whenever the popup blocks a click).
def close_promo_popup(popup):
    popup.locator(".doc-close-lightbox").first.click()


# Helper: opens a product page, sets the quantity, clicks Add to Cart and waits until the header badge goes up.
def add_to_cart(page: Page, product_url: str, qty: int = 1):
    page.goto(product_url)
    badge = page.locator(CART_BADGE).first
    items_before = 0
    if badge.count() > 0 and badge.inner_text().strip() != "":
        items_before = int(badge.inner_text().strip())
    page.locator(ADD_QTY_BOX).fill(str(qty))
    page.locator(ADD_TO_CART_BUTTON).click()
    expect(badge).to_have_text(str(items_before + qty), timeout=15_000)


# Helper: clicks a cart button that reloads the page (+, -, trash) and waits for the new page to load.
def click_and_wait(page: Page, button):
    with page.expect_navigation(wait_until="load", timeout=30_000):
        button.click()


# Helper: types a value into a cart quantity box key by key, then presses Tab so the cart updates.
def type_quantity(qty_box, value: str):
    qty_box.click()
    qty_box.press("Control+a")
    qty_box.press("Delete")
    if value != "":
        qty_box.press_sequentially(value, delay=50)
    qty_box.press("Tab")


# Helper: opens the promo-code box on the cart, types a coupon code and clicks Apply.
def apply_coupon(page: Page, code: str):
    page.locator(PROMO_CODE_TOGGLE).click()
    page.locator(COUPON_BOX).fill(code)
    page.locator(APPLY_COUPON_BUTTON).click()


# Helper: removes every applied coupon/voucher from the cart, one by one.
def remove_coupons(page: Page):
    page.goto(CART_URL)
    while page.locator(REMOVE_COUPON_LINK).count() > 0:
        links_before = page.locator(REMOVE_COUPON_LINK).count()
        page.locator(REMOVE_COUPON_LINK).first.click()
        expect(page.locator(REMOVE_COUPON_LINK)).to_have_count(links_before - 1, timeout=15_000)
        page.goto(CART_URL)
    expect(page.locator(VOUCHER_ROWS)).to_have_count(0)


# Helper: reads the RM amount(s) in a summary row as a number, e.g. "RM8.50" -> 8.5 (adds up several rows, 0 if none).
def get_amount(page: Page, selector: str) -> float:
    total = 0.0
    for text in page.locator(selector).all_text_contents():
        number = text.split("RM")[-1].strip().replace(",", "")
        total = total + float(number)
    return round(total, 2)
