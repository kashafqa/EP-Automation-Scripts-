# Small Order Fee (RM5.00 when the cart subtotal is below RM10.00) for a guest user: REQ-1 to REQ-4,
# the RM10.00 / RM9.99 boundary, cart changes, totals, checkout, free-delivery bar and refresh.
from playwright.sync_api import Page, expect

from cart_helpers import (
    ADD_QTY_BOX, ADD_TO_CART_BUTTON, CART_BADGE, CART_LINE, CART_URL, CHECKOUT_BUTTON, CHECKOUT_FEE_ROW,
    CHECKOUT_GRAND_TOTAL, CHECKOUT_SUBTOTAL, CHECKOUT_URL, DIMECTAL_URL, ESTIMATED_TOTAL, FEE_ROW, FREE_DELIVERY_BAR,
    LINE_PACK, MAALOX_BIG_PACK, MAALOX_BIG_PACK_PRICE, MAALOX_NAME, MAALOX_PACK, MAALOX_URL, MINUS_BUTTON,
    PACK_BUTTON, PLUS_BUTTON, PRODUCT_PACK, PRODUCT_PRICE, QTY_BOX, RAZOR_URL, REMOVE_POPUP_CONFIRM,
    REMOVE_POPUP_OPEN, SUBTOTAL, TRASH_BUTTON, UPHALYTE_CART_NAME, UPHALYTE_URL, VOUCHER_ROWS, add_to_cart,
    click_and_wait,
)


# Verify FEE-01 (REQ-2): 1 x Maalox = RM1.70 with no voucher gets the RM5.00 fee, Estimated Total RM6.70.
def test_FEE_01_fee_below_10(guest_page: Page):
    # Step 1: add 1 Maalox (RM1.70) and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=1)
    guest_page.goto(CART_URL)

    # Expected: subtotal RM1.70, fee RM5.00, no voucher, total RM6.70
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(VOUCHER_ROWS)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM6.70")


# Verify FEE-02 (REQ-1/2): 11 x Uphalyte = RM9.90 at sale price (RM10.45 at original price) still gets the fee.
def test_FEE_02_fee_uses_sale_price(guest_page: Page):
    # Step 1: add 11 Uphalyte (sale price RM0.90) and open the cart
    add_to_cart(guest_page, UPHALYTE_URL, qty=11)
    guest_page.goto(CART_URL)

    # Expected: subtotal RM9.90, fee RM5.00, total RM14.90
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM9.90")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM14.90")


# Verify FEE-03 (REQ-3): 6 x Maalox = RM10.20 has no fee, Estimated Total RM10.20.
def test_FEE_03_no_fee_above_10(guest_page: Page):
    # Step 1: add 6 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=6)
    guest_page.goto(CART_URL)

    # Expected: subtotal RM10.20, no fee row, total RM10.20
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.20")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM10.20")


# Verify FEE-06 (REQ-3 boundary): exactly RM10.00 (1 x Razor RM3.20 + 4 x Maalox RM1.70) has NO fee.
def test_FEE_06_no_fee_at_exactly_10(guest_page: Page):
    # Step 1: add 1 Gillette razor and 4 Maalox, open the cart
    add_to_cart(guest_page, RAZOR_URL, qty=1)
    add_to_cart(guest_page, MAALOX_URL, qty=4)
    guest_page.goto(CART_URL)

    # Expected: subtotal RM10.00, no fee row, total RM10.00
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.00")
    expect(guest_page.locator(FEE_ROW), "BUG: Small Order Fee shown for a subtotal of exactly RM10.00").to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM10.00")


# Verify FEE-07 (REQ-2 boundary): RM9.99 (3 x Dimectal RM1.83 + 5 x Uphalyte RM0.90) gets the fee, total RM14.99.
def test_FEE_07_fee_at_9_99(guest_page: Page):
    # Step 1: add 3 Dimectal and 5 Uphalyte, open the cart
    add_to_cart(guest_page, DIMECTAL_URL, qty=3)
    add_to_cart(guest_page, UPHALYTE_URL, qty=5)
    guest_page.goto(CART_URL)

    # Expected: subtotal RM9.99, fee RM5.00, total RM14.99
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM9.99")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM14.99")


# Verify FEE-08 (REQ-4): on the cart screen, - (qty 6 -> 5, RM8.50) adds the fee to the total and + (5 -> 6, RM10.20) removes it.
def test_FEE_08_fee_follows_quantity_changes(guest_page: Page):
    # Step 1: add 6 Maalox and open the cart -> no fee, total RM10.20
    add_to_cart(guest_page, MAALOX_URL, qty=6)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM10.20")

    # Step 2: click - -> Expected: qty 5, subtotal RM8.50, fee RM5.00, total RM13.50
    click_and_wait(guest_page, guest_page.locator(MINUS_BUTTON))
    expect(guest_page.locator(QTY_BOX)).to_have_value("5")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM8.50")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM13.50")

    # Step 3: click + -> Expected: qty 6, subtotal RM10.20, no fee, total RM10.20
    click_and_wait(guest_page, guest_page.locator(PLUS_BUTTON))
    expect(guest_page.locator(QTY_BOX)).to_have_value("6")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.20")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM10.20")


# Verify FEE-09 (REQ-4): trashing Uphalyte drops the cart from RM10.30 to RM8.50 and the RM5.00 fee appears.
def test_FEE_09_fee_appears_after_trash_removal(guest_page: Page):
    # Step 1: add 5 Maalox and 2 Uphalyte, open the cart -> RM10.30, no fee
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    add_to_cart(guest_page, UPHALYTE_URL, qty=2)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.30")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)

    # Step 2: click the trash icon on Uphalyte
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)
    click_and_wait(guest_page, uphalyte_line.locator(TRASH_BUTTON))

    # Expected: Uphalyte gone, subtotal RM8.50, fee RM5.00, total RM13.50
    expect(uphalyte_line).to_have_count(0)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM8.50")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM13.50")


# Verify FEE-10 (REQ-4): removing Maalox with - and Confirm drops RM10.70 to RM9.00 and the RM5.00 fee appears.
def test_FEE_10_fee_appears_after_popup_removal(guest_page: Page):
    # Step 1: add 1 Maalox and 10 Uphalyte, open the cart -> RM10.70, no fee
    add_to_cart(guest_page, MAALOX_URL, qty=1)
    add_to_cart(guest_page, UPHALYTE_URL, qty=10)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.70")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)

    # Step 2: click - on Maalox and Confirm in the 'Remove Item' popup
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    maalox_line.locator(MINUS_BUTTON).click()
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_be_visible()
    guest_page.locator(REMOVE_POPUP_CONFIRM).click()
    guest_page.wait_for_url("**/cart/?removed_item=1**")
    guest_page.wait_for_load_state("load")

    # Expected: Maalox gone, subtotal RM9.00, fee RM5.00, total RM14.00
    expect(maalox_line).to_have_count(0)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM9.00")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM14.00")


# Verify FEE-11 (REQ-4): adding 2 Uphalyte to a RM8.50 cart (fee shown) lifts it to RM10.30 and the fee goes away.
def test_FEE_11_fee_removed_when_product_added(guest_page: Page):
    # Step 1: add 5 Maalox and open the cart -> fee RM5.00
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")

    # Step 2: add 2 Uphalyte and open the cart again
    add_to_cart(guest_page, UPHALYTE_URL, qty=2)
    guest_page.goto(CART_URL)

    # Expected: subtotal RM10.30, no fee, total RM10.30
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.30")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM10.30")


# Verify FEE-12 (REQ-4): adding the bigger Maalox pack (4.3ml x20, RM26.60) to a RM1.70 cart removes the fee (RM28.30).
def test_FEE_12_bigger_pack_removes_fee(guest_page: Page):
    # Step 1: add 1 Maalox (4.3ml x1) and open the cart -> fee RM5.00
    add_to_cart(guest_page, MAALOX_URL, qty=1)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")

    # Step 2: open Maalox again, choose the 4.3ml x20 pack (RM26.60) and add it
    guest_page.goto(MAALOX_URL)
    guest_page.locator(PACK_BUTTON, has_text=MAALOX_BIG_PACK).click()
    expect(guest_page.locator(PRODUCT_PACK)).to_have_text(MAALOX_BIG_PACK)
    expect(guest_page.locator(PRODUCT_PRICE).first).to_have_text(MAALOX_BIG_PACK_PRICE)
    guest_page.locator(ADD_QTY_BOX).fill("1")
    guest_page.locator(ADD_TO_CART_BUTTON).click()
    expect(guest_page.locator(CART_BADGE).first).to_have_text("2", timeout=15_000)

    # Expected: two lines (4.3ml x1 and 4.3ml x20), subtotal RM28.30, no fee, total RM28.30
    guest_page.goto(CART_URL)
    expect(guest_page.locator(CART_LINE)).to_have_count(2)
    expect(guest_page.locator(LINE_PACK)).to_have_text([MAALOX_PACK, MAALOX_BIG_PACK])
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM28.30")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM28.30")


# Verify FEE-16: a guest clicking Checkout sees the "Wait! You're leaving" popup, and "No thanks" opens the checkout page.
def test_FEE_16_checkout_button_opens_checkout(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart -> Checkout button links to /checkout/
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(CHECKOUT_BUTTON)).to_have_attribute("href", CHECKOUT_URL)

    # Step 2: click Checkout
    guest_page.locator(CHECKOUT_BUTTON).click()

    # Expected: the "Wait! You're leaving" popup shows with the sign-up button and the No thanks link
    expect(guest_page.get_by_text("Wait! You're leaving")).to_be_visible(timeout=15_000)
    expect(guest_page.get_by_text("SIGN UP / IN & CLAIM MY VOUCHERS")).to_be_visible()
    no_thanks = guest_page.get_by_text("No thanks, continue as guest and forfeit savings")
    expect(no_thanks).to_be_visible()

    # Step 3: click No thanks
    no_thanks.click()

    # Expected: the checkout page opens
    guest_page.wait_for_url(CHECKOUT_URL + "**", timeout=30_000)


# Verify FEE-18 (REQ-3): checkout for exactly RM10.00 (1 x Razor + 4 x Maalox) has no fee and Grand Total RM10.00.
def test_FEE_18_no_fee_on_checkout_at_exactly_10(guest_page: Page):
    # Step 1: add 1 Gillette razor and 4 Maalox, open the cart -> no fee
    add_to_cart(guest_page, RAZOR_URL, qty=1)
    add_to_cart(guest_page, MAALOX_URL, qty=4)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)

    # Step 2: open checkout
    guest_page.goto(CHECKOUT_URL)

    # Expected: Grand Total RM10.00, Subtotal RM10.00, no fee row
    expect(guest_page.locator(CHECKOUT_GRAND_TOTAL)).to_have_text("RM10.00", timeout=15_000)
    expect(guest_page.locator(CHECKOUT_SUBTOTAL)).to_have_text("RM10.00")
    expect(guest_page.locator(CHECKOUT_FEE_ROW)).to_have_count(0)


# Verify FEE-19: the fee is a flat RM5.00 charged once (one row) for a 3-line RM7.93 cart, in cart and checkout.
def test_FEE_19_fee_charged_once(guest_page: Page):
    # Step 1: add 2 Maalox (RM3.40), 3 Uphalyte (RM2.70) and 1 Dimectal (RM1.83), open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=2)
    add_to_cart(guest_page, UPHALYTE_URL, qty=3)
    add_to_cart(guest_page, DIMECTAL_URL, qty=1)
    guest_page.goto(CART_URL)

    # Expected (cart): subtotal RM7.93, exactly one fee row of RM5.00, total RM12.93
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM7.93")
    expect(guest_page.locator(FEE_ROW)).to_have_count(1)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM12.93")

    # Step 2: open checkout
    guest_page.goto(CHECKOUT_URL)

    # Expected (checkout): Grand Total RM12.93 and exactly one fee row of RM5.00
    expect(guest_page.locator(CHECKOUT_GRAND_TOTAL)).to_have_text("RM12.93", timeout=15_000)
    expect(guest_page.locator(CHECKOUT_FEE_ROW)).to_have_count(1)
    expect(guest_page.locator(CHECKOUT_FEE_ROW)).to_have_text("RM5.00")


# Verify FEE-20: the free-delivery bar asks for RM111.50 more (RM120.00 - RM8.50); the RM5.00 fee does not count.
def test_FEE_20_free_delivery_bar_ignores_fee(guest_page: Page):
    # Step 1: add 5 Maalox (RM8.50) and open the cart -> fee RM5.00
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")

    # Expected: bar target RM120.00 and 'Add RM111.50 more' (not RM106.50, which would count the fee)
    bar = guest_page.locator(FREE_DELIVERY_BAR).first
    expect(bar).to_contain_text("RM120.00")
    expect(
        bar,
        "BUG: free-delivery bar should ask for RM120.00 - RM8.50 = RM111.50 more (the RM5.00 fee must not count)",
    ).to_contain_text("Add RM111.50 more")


# Verify FEE-21: the guest cart and its RM5.00 fee are unchanged after refreshing the cart page.
def test_FEE_21_fee_kept_after_refresh(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart -> fee RM5.00
    add_to_cart(guest_page, MAALOX_URL, qty=1)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")

    # Step 2: refresh the page
    guest_page.reload(wait_until="load")

    # Expected: qty 1, subtotal RM1.70, fee RM5.00, total RM6.70
    expect(guest_page.locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM6.70")
