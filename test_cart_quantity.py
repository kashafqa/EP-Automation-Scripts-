# Cart tests for a guest user: + / - buttons, typed quantities, removing products (Remove Item popup and trash),
# the empty cart, header badge, merging lines, product details and keeping the cart after refresh (CART-01 to CART-23).
import pytest
from playwright.sync_api import Page, expect

from cart_helpers import (
    ADD_QTY_BOX, ADD_TO_CART_BUTTON, ALL_PRODUCTS_URL, CART_BADGE, CART_LINE, CART_SUMMARY, CART_URL, CHECKOUT_BUTTON,
    EMPTY_CART, EMPTY_CART_BUTTON, EMPTY_CART_HEADING, LINE_IMAGE, LINE_NAME, LINE_PACK, LINE_PRICE, MAALOX_IMAGE,
    MAALOX_NAME, MAALOX_PACK, MAALOX_PRICE, MAALOX_URL, MINUS_BUTTON, NOTICE_MESSAGE, PLUS_BUTTON, PRODUCT_IMAGE,
    PRODUCT_PACK, PRODUCT_PRICE, PRODUCT_TITLE, QTY_BOX, REMOVE_POPUP_CANCEL, REMOVE_POPUP_CONFIRM,
    REMOVE_POPUP_MESSAGE, REMOVE_POPUP_OPEN, REMOVE_POPUP_TITLE, REMOVE_POPUP_X, SEARCH_BOX, SEARCH_RESULTS, SUBTOTAL,
    TRASH_BUTTON, UPHALYTE_CART_NAME, UPHALYTE_IMAGE, UPHALYTE_NAME, UPHALYTE_PACK, UPHALYTE_PRICE, UPHALYTE_URL,
    add_to_cart, click_and_wait, type_quantity,
)


# Verify CART-01: + raises the quantity from 1 to 2 and the subtotal becomes RM3.40 (2 x RM1.70).
def test_CART_01_increase_quantity(guest_page: Page):
    # Step 1: add 1 Maalox (RM1.70) to the cart and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=1)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(QTY_BOX)).to_have_value("1")

    # Step 2: click +
    click_and_wait(guest_page, guest_page.locator(PLUS_BUTTON))

    # Expected: quantity 2, unit price still RM1.70, subtotal RM3.40
    expect(guest_page.locator(QTY_BOX)).to_have_value("2")
    expect(guest_page.locator(LINE_PRICE)).to_have_text("RM1.70")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM3.40")


# Verify CART-02: - lowers the quantity from 2 to 1, the subtotal drops from RM3.40 to RM1.70 and no Remove popup opens.
def test_CART_02_decrease_quantity(guest_page: Page):
    # Step 1: add 2 Maalox to the cart and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=2)
    guest_page.goto(CART_URL)                                                      
    expect(guest_page.locator(QTY_BOX)).to_have_value("2")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM3.40")

    # Step 2: click -
    click_and_wait(guest_page, guest_page.locator(MINUS_BUTTON))

    # Expected: quantity 1, subtotal RM1.70 and no 'Remove Item' popup (it only opens at qty 1)
    expect(guest_page.locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_have_count(0)


# Verify CART-03: - at quantity 1 opens the 'Remove Item' popup with the exact texts and Confirm, Cancel and X buttons.
def test_CART_03_minus_at_qty_1_shows_remove_popup(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: click -
    guest_page.locator(MINUS_BUTTON).click()

    # Expected: the 'Remove Item' popup opens with its message and three buttons
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_be_visible()
    expect(guest_page.locator(REMOVE_POPUP_TITLE)).to_have_text("Remove Item")
    expect(guest_page.locator(REMOVE_POPUP_MESSAGE)).to_have_text(
        "You are about to remove this product from your cart. Are you certain you want to do this?"
    )
    expect(guest_page.locator(REMOVE_POPUP_CONFIRM)).to_be_visible()
    expect(guest_page.locator(REMOVE_POPUP_CANCEL)).to_be_visible()
    expect(guest_page.locator(REMOVE_POPUP_X)).to_be_visible()


# Verify CART-04: Confirm in the remove popup removes the item and shows the '"Maalox ..." removed.' notice.
def test_CART_04_confirm_removes_item(guest_page: Page):
    # Step 1: add 1 Maalox, open the cart and click -
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)
    guest_page.locator(MINUS_BUTTON).click()
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_be_visible()

    # Step 2: click Confirm
    guest_page.locator(REMOVE_POPUP_CONFIRM).click()

    # Expected: the cart reloads with the 'removed.' notice and is empty
    guest_page.wait_for_url("**/cart/?removed_item=1**")
    expect(guest_page.locator(NOTICE_MESSAGE).first).to_contain_text("“Maalox Oral Suspension Sachet” removed.")
    expect(guest_page.locator(CART_LINE)).to_have_count(0)
    expect(guest_page.locator(EMPTY_CART)).to_be_visible()


# Verify CART-05: Cancel in the remove popup closes it and keeps Maalox at qty 1 (subtotal RM1.70).
def test_CART_05_cancel_keeps_item(guest_page: Page):
    # Step 1: add 1 Maalox, open the cart and click -
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)
    guest_page.locator(MINUS_BUTTON).click()
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_be_visible()

    # Step 2: click Cancel
    guest_page.locator(REMOVE_POPUP_CANCEL).click()

    # Expected: popup closed, item still there with qty 1 and subtotal RM1.70
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_have_count(0)
    expect(guest_page.locator(CART_LINE)).to_have_count(1)
    expect(guest_page.locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")


# Verify CART-06: X in the remove popup closes it and keeps Maalox at qty 1 (subtotal RM1.70).
def test_CART_06_x_keeps_item(guest_page: Page):
    # Step 1: add 1 Maalox, open the cart and click -
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)
    guest_page.locator(MINUS_BUTTON).click()
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_be_visible()

    # Step 2: click X
    guest_page.locator(REMOVE_POPUP_X).click()

    # Expected: popup closed, item still there with qty 1 and subtotal RM1.70
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_have_count(0)
    expect(guest_page.locator(CART_LINE)).to_have_count(1)
    expect(guest_page.locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")


# Verify CART-07: an empty guest cart shows the empty-cart message and no items, summary or checkout button.
def test_CART_07_empty_cart_page(guest_page: Page):
    # Step 1: open the cart without adding anything
    guest_page.goto(CART_URL)

    # Expected: empty-cart message and 'Start Shopping' button; no lines, no summary, no checkout button
    expect(guest_page.locator(EMPTY_CART)).to_be_visible()
    expect(guest_page.locator(EMPTY_CART_HEADING)).to_have_text("Your cart is feeling a bit empty...")
    expect(guest_page.locator(EMPTY_CART_BUTTON)).to_have_text("Start Shopping")
    expect(guest_page.locator(CART_LINE)).to_have_count(0)
    expect(guest_page.locator(CART_SUMMARY)).to_have_count(0)
    expect(guest_page.locator(CHECKOUT_BUTTON)).to_have_count(0)


# Verify CART-08: the empty-cart 'Start Shopping' button opens the All Products page.
def test_CART_08_start_shopping_button(guest_page: Page):
    # Step 1: open the empty cart
    guest_page.goto(CART_URL)

    # Step 2: click 'Start Shopping'
    guest_page.locator(EMPTY_CART_BUTTON).click()

    # Expected: the All Products page opens
    guest_page.wait_for_url(ALL_PRODUCTS_URL + "**")
    assert guest_page.url.startswith(ALL_PRODUCTS_URL)


# Verify CART-09: the header badge counts items: 1 after Maalox, 2 after Uphalyte, 3 after +, 2 after trashing Uphalyte.
def test_CART_09_header_badge_count(guest_page: Page):
    badge = guest_page.locator(CART_BADGE).first
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)

    # Step 1: add 1 Maalox -> Expected: badge shows 1
    add_to_cart(guest_page, MAALOX_URL)
    expect(badge).to_have_text("1")

    # Step 2: add 1 Uphalyte -> Expected: badge shows 2
    add_to_cart(guest_page, UPHALYTE_URL)
    expect(badge).to_have_text("2")

    # Step 3: on the cart click + on Maalox -> Expected: badge shows 3
    guest_page.goto(CART_URL)
    click_and_wait(guest_page, maalox_line.locator(PLUS_BUTTON))
    expect(badge).to_have_text("3")

    # Step 4: click the trash icon on Uphalyte -> Expected: Uphalyte is gone and badge shows 2
    click_and_wait(guest_page, uphalyte_line.locator(TRASH_BUTTON))
    expect(uphalyte_line).to_have_count(0)
    expect(badge).to_have_text("2")


# Verify CART-10: adding Maalox from its page and again via search gives ONE cart line with qty 2 (RM3.40).
def test_CART_10_same_product_twice_merges(guest_page: Page):
    # Step 1: add 1 Maalox from the product page
    add_to_cart(guest_page, MAALOX_URL)

    # Step 2: search "maalox oral suspension" and open the Maalox result
    guest_page.locator(SEARCH_BOX).click()
    guest_page.locator(SEARCH_BOX).press_sequentially("maalox oral suspension", delay=50)
    result = guest_page.locator(SEARCH_RESULTS, has_text=MAALOX_NAME).first
    expect(result).to_be_visible(timeout=15_000)
    result.click()
    guest_page.wait_for_url("**/maalox-oral-suspension-sachet**")
    expect(guest_page.locator(PRODUCT_PACK)).to_have_text(MAALOX_PACK)

    # Step 3: add 1 more from this page
    guest_page.locator(ADD_QTY_BOX).fill("1")
    guest_page.locator(ADD_TO_CART_BUTTON).click()
    expect(guest_page.locator(CART_BADGE).first).to_have_text("2", timeout=15_000)

    # Expected: the cart has one line, qty 2, subtotal RM3.40
    guest_page.goto(CART_URL)
    expect(guest_page.locator(CART_LINE)).to_have_count(1)
    expect(guest_page.locator(QTY_BOX)).to_have_value("2")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM3.40")


# Verify CART-11: 2 x Maalox (RM1.70) + 1 x Uphalyte (RM0.90) show the right lines and subtotal RM4.30.
def test_CART_11_two_products_subtotal(guest_page: Page):
    # Step 1: add 2 Maalox and 1 Uphalyte, open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=2)
    add_to_cart(guest_page, UPHALYTE_URL, qty=1)
    guest_page.goto(CART_URL)
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)

    # Expected: two lines with the right qty and price
    expect(guest_page.locator(CART_LINE)).to_have_count(2)
    expect(maalox_line.locator(QTY_BOX)).to_have_value("2")
    expect(maalox_line.locator(LINE_PRICE)).to_have_text("RM1.70")
    expect(uphalyte_line.locator(QTY_BOX)).to_have_value("1")
    expect(uphalyte_line.locator(LINE_PRICE)).to_have_text("RM0.90")

    # Expected: subtotal = 2 x 1.70 + 1 x 0.90 = RM4.30
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM4.30")


# Verify CART-12: the qty box allows at most 9998 (set in the backend); typing 9999 shows the max message and the cart stays RM1.70, badge 1.
def test_CART_12_max_quantity(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Expected: the qty box has max 9998
    expect(guest_page.locator(QTY_BOX)).to_have_attribute("max", "9998")

    # Step 2: type 9999 in the qty box
    type_quantity(guest_page.locator(QTY_BOX), "9999")
    guest_page.wait_for_timeout(3_000)

    # Expected: the qty box shows the max message
    message = guest_page.locator(QTY_BOX).evaluate("box => box.validationMessage")
    assert message == "Value must be less than or equal to 9998.", f"Max message not shown, got: '{message}'"

    # Expected: cart unchanged (RM1.70, badge 1)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("1")


# Verify CART-13: typing 0, -1, 'abc' or nothing in the cart qty box removes the line with a 'Basket updated.' notice.
@pytest.mark.parametrize("typed", ["0", "-1", "abc", ""], ids=["zero", "negative", "letters", "blank"])
def test_CART_13_typed_quantity_removes_line(guest_page: Page, typed: str):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: type the value in the qty box
    type_quantity(guest_page.locator(QTY_BOX), typed)

    # Expected: 'Basket updated.' shows, the line is removed and the empty-cart message appears
    expect(guest_page.get_by_text("Basket updated.").first).to_be_visible(timeout=15_000)
    expect(guest_page.locator(CART_LINE)).to_have_count(0, timeout=15_000)
    expect(guest_page.locator(EMPTY_CART)).to_be_visible()


# Verify CART-13: decimals are not allowed; typing 1.5 shows the 'valid value' message and the cart stays RM1.70, badge 1.
def test_CART_13_typed_decimal_quantity_rejected(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: type 1.5 in the qty box
    type_quantity(guest_page.locator(QTY_BOX), "1.5")
    guest_page.wait_for_timeout(3_000)

    # Expected: the qty box shows the 'valid value' message
    message = guest_page.locator(QTY_BOX).evaluate("box => box.validationMessage")
    assert message == "Please enter a valid value. The two nearest valid values are 1 and 2.", (
        f"BUG: decimal qty '1.5' gives no message to the user, got: '{message}'"
    )

    # Expected: cart unchanged (RM1.70, badge 1)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("1")


# Verify CART-14: 5 quick + clicks then 3 quick - clicks from qty 1 end at qty 3 (no clicks lost).
def test_CART_14_rapid_plus_minus_clicks(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: click + five times and - three times quickly (without waiting for the page reloads)
    for click_number in range(5):
        guest_page.locator(PLUS_BUTTON).click(no_wait_after=True)
    for click_number in range(3):
        guest_page.locator(MINUS_BUTTON).click(no_wait_after=True)
    guest_page.wait_for_load_state("load")
    guest_page.wait_for_timeout(5_000)

    # Expected: after reopening the cart the qty is 3 (1 + 5 - 3)
    guest_page.goto(CART_URL)
    expect(
        guest_page.locator(QTY_BOX),
        "BUG: rapid clicks lost - 1 + 5 - 3 should give qty 3",
    ).to_have_value("3")


# Verify CART-14: clicking + five times, waiting for each reload, ends at qty 6, subtotal RM10.20, badge 6.
def test_CART_14_plus_clicks_with_wait(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: click + and wait for the page each time -> qty goes 2, 3, 4, 5, 6
    for expected_qty in ["2", "3", "4", "5", "6"]:
        click_and_wait(guest_page, guest_page.locator(PLUS_BUTTON))
        expect(guest_page.locator(QTY_BOX)).to_have_value(expected_qty)

    # Expected: subtotal RM10.20 (6 x RM1.70) and badge 6
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.20")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("6")


# Verify CART-15: the Maalox cart line shows the same name, image, price and pack size as the product page.
def test_CART_15_maalox_cart_line_matches_product_page(guest_page: Page):
    # Step 1: open the Maalox product page and check name, price, pack and image
    guest_page.goto(MAALOX_URL)
    expect(guest_page.locator(PRODUCT_TITLE)).to_have_text(MAALOX_NAME)
    expect(guest_page.locator(PRODUCT_PRICE).first).to_have_text(MAALOX_PRICE)
    expect(guest_page.locator(PRODUCT_PACK)).to_have_text(MAALOX_PACK)
    assert MAALOX_IMAGE in guest_page.locator(PRODUCT_IMAGE).first.get_attribute("src")

    # Step 2: add it to the cart and open the cart
    guest_page.locator(ADD_QTY_BOX).fill("1")
    guest_page.locator(ADD_TO_CART_BUTTON).click()
    expect(guest_page.locator(CART_BADGE).first).to_have_text("1", timeout=15_000)
    guest_page.goto(CART_URL)

    # Expected: the cart line shows the same name, price, pack and image
    expect(guest_page.locator(LINE_NAME)).to_have_text(MAALOX_NAME)
    expect(guest_page.locator(LINE_PRICE)).to_have_text(MAALOX_PRICE)
    expect(guest_page.locator(LINE_PACK)).to_have_text(MAALOX_PACK)
    expect(guest_page.locator(LINE_IMAGE)).to_be_visible()
    assert MAALOX_IMAGE in guest_page.locator(LINE_IMAGE).get_attribute("src")


# Verify CART-15: the Uphalyte cart line shows the same name, image, price and pack size as the product page.
def test_CART_15_uphalyte_cart_line_matches_product_page(guest_page: Page):
    # Step 1: open the Uphalyte product page and check name, price, pack and image
    guest_page.goto(UPHALYTE_URL)
    expect(guest_page.locator(PRODUCT_TITLE)).to_have_text(UPHALYTE_NAME)
    expect(guest_page.locator(PRODUCT_PRICE).first).to_have_text(UPHALYTE_PRICE)
    expect(guest_page.locator(PRODUCT_PACK)).to_have_text(UPHALYTE_PACK)
    assert UPHALYTE_IMAGE in guest_page.locator(PRODUCT_IMAGE).first.get_attribute("src")

    # Step 2: add it to the cart and open the cart
    guest_page.locator(ADD_QTY_BOX).fill("1")
    guest_page.locator(ADD_TO_CART_BUTTON).click()
    expect(guest_page.locator(CART_BADGE).first).to_have_text("1", timeout=15_000)
    guest_page.goto(CART_URL)

    # Expected: the cart line shows the same name (with '-' instead of '–'), price, pack and image
    expect(guest_page.locator(LINE_NAME)).to_have_text(UPHALYTE_CART_NAME)
    expect(guest_page.locator(LINE_PRICE)).to_have_text(UPHALYTE_PRICE)
    expect(guest_page.locator(LINE_PACK)).to_have_text(UPHALYTE_PACK)
    expect(guest_page.locator(LINE_IMAGE)).to_be_visible()
    assert UPHALYTE_IMAGE in guest_page.locator(LINE_IMAGE).get_attribute("src")


# Verify CART-16: the guest cart (2 x Maalox + 1 x Uphalyte = RM4.30) is unchanged after a page refresh.
def test_CART_16_cart_kept_after_refresh(guest_page: Page):
    # Step 1: add 2 Maalox and 1 Uphalyte, open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=2)
    add_to_cart(guest_page, UPHALYTE_URL, qty=1)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM4.30")

    # Step 2: refresh the page
    guest_page.reload(wait_until="load")

    # Expected: same 2 lines, same quantities, subtotal RM4.30, badge 3
    expect(guest_page.locator(CART_LINE)).to_have_count(2)
    expect(guest_page.locator(CART_LINE, has_text=MAALOX_NAME).locator(QTY_BOX)).to_have_value("2")
    expect(guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME).locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM4.30")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("3")


# Verify CART-16: the cart is kept after logging out and logging back in.
@pytest.mark.skip(reason="logged-in scope")
def test_CART_16_cart_kept_after_relogin():
    pass


# Verify CART-17: a prescription (Rx) product in the cart follows the Rx checkout flow.
@pytest.mark.skip(reason="Rx product not in guest non-Rx scope; needs Rx product")
def test_CART_17_rx_product_checkout():
    pass

# Verify CART-18: + on Maalox in a 2-product cart changes only Maalox (1 -> 2); Uphalyte stays 1 at RM0.90, subtotal RM4.30.
def test_CART_18_plus_changes_only_that_line(guest_page: Page):
    # Step 1: add 1 Maalox and 1 Uphalyte, open the cart
    add_to_cart(guest_page, MAALOX_URL)
    add_to_cart(guest_page, UPHALYTE_URL)
    guest_page.goto(CART_URL)
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)

    # Step 2: click + on Maalox
    click_and_wait(guest_page, maalox_line.locator(PLUS_BUTTON))

    # Expected: Maalox qty 2, Uphalyte still qty 1 at RM0.90, subtotal 2 x 1.70 + 0.90 = RM4.30, badge 3
    expect(maalox_line.locator(QTY_BOX)).to_have_value("2")
    expect(uphalyte_line.locator(QTY_BOX)).to_have_value("1")
    expect(uphalyte_line.locator(LINE_PRICE)).to_have_text("RM0.90")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM4.30")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("3")


# Verify CART-19: - on Uphalyte in a 2-product cart changes only Uphalyte (2 -> 1); Maalox stays 1, subtotal RM2.60.
def test_CART_19_minus_changes_only_that_line(guest_page: Page):
    # Step 1: add 1 Maalox and 2 Uphalyte, open the cart
    add_to_cart(guest_page, MAALOX_URL)
    add_to_cart(guest_page, UPHALYTE_URL, qty=2)
    guest_page.goto(CART_URL)
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)

    # Step 2: click - on Uphalyte
    click_and_wait(guest_page, uphalyte_line.locator(MINUS_BUTTON))

    # Expected: Uphalyte qty 1, Maalox still qty 1 at RM1.70, subtotal 1.70 + 0.90 = RM2.60, badge 2
    expect(uphalyte_line.locator(QTY_BOX)).to_have_value("1")
    expect(maalox_line.locator(QTY_BOX)).to_have_value("1")
    expect(maalox_line.locator(LINE_PRICE)).to_have_text("RM1.70")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM2.60")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("2")


# Verify CART-20: at the maximum qty 9998, + does not raise the quantity (stays 9998, subtotal RM16,996.60).
def test_CART_20_plus_at_max_quantity(guest_page: Page):
    # Step 1: add 1 Maalox, open the cart, type 9998 in the qty box and reopen the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)
    type_quantity(guest_page.locator(QTY_BOX), "9998")
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(QTY_BOX)).to_have_value("9998")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM16,996.60")

    # Step 2: click +, wait, reopen the cart
    guest_page.locator(PLUS_BUTTON).click()
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)

    # Expected: qty still 9998 and subtotal unchanged
    expect(guest_page.locator(QTY_BOX), "BUG: + went above the maximum qty 9998").to_have_value("9998")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM16,996.60")


# Verify CART-21: a qty changed with + and - (1 -> 3 -> 2) is kept after refreshing the cart (qty 2, RM3.40, badge 2).
def test_CART_21_plus_minus_kept_after_refresh(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: click + twice and - once -> qty 2
    click_and_wait(guest_page, guest_page.locator(PLUS_BUTTON))
    click_and_wait(guest_page, guest_page.locator(PLUS_BUTTON))
    click_and_wait(guest_page, guest_page.locator(MINUS_BUTTON))
    expect(guest_page.locator(QTY_BOX)).to_have_value("2")

    # Step 3: refresh the page
    guest_page.reload(wait_until="load")

    # Expected: qty 2, subtotal RM3.40, badge 2
    expect(guest_page.locator(QTY_BOX)).to_have_value("2")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM3.40")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("2")


# Verify CART-22: - at qty 1 + Confirm on Maalox in a 2-product cart removes only Maalox; Uphalyte stays (RM0.90, badge 1).
def test_CART_22_popup_removes_only_that_product(guest_page: Page):
    # Step 1: add 1 Maalox and 1 Uphalyte, open the cart
    add_to_cart(guest_page, MAALOX_URL)
    add_to_cart(guest_page, UPHALYTE_URL)
    guest_page.goto(CART_URL)
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)

    # Step 2: click - on Maalox and Confirm in the 'Remove Item' popup
    maalox_line.locator(MINUS_BUTTON).click()
    expect(guest_page.locator(REMOVE_POPUP_OPEN)).to_be_visible()
    guest_page.locator(REMOVE_POPUP_CONFIRM).click()
    guest_page.wait_for_url("**/cart/?removed_item=1**")

    # Expected: Maalox gone, Uphalyte still there with qty 1, subtotal RM0.90, badge 1
    expect(maalox_line).to_have_count(0)
    expect(guest_page.locator(CART_LINE)).to_have_count(1)
    expect(uphalyte_line.locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM0.90")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("1")


# Verify CART-23: the trash icon on Maalox (qty 2) removes the whole line; Uphalyte stays (RM0.90, badge 1).
def test_CART_23_trash_removes_only_that_product(guest_page: Page):
    # Step 1: add 2 Maalox and 1 Uphalyte, open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=2)
    add_to_cart(guest_page, UPHALYTE_URL)
    guest_page.goto(CART_URL)
    maalox_line = guest_page.locator(CART_LINE, has_text=MAALOX_NAME)
    uphalyte_line = guest_page.locator(CART_LINE, has_text=UPHALYTE_CART_NAME)

    # Step 2: click the trash icon on Maalox
    click_and_wait(guest_page, maalox_line.locator(TRASH_BUTTON))

    # Expected: Maalox gone (both units), Uphalyte still there with qty 1, subtotal RM0.90, badge 1
    expect(maalox_line).to_have_count(0)
    expect(guest_page.locator(CART_LINE)).to_have_count(1)
    expect(uphalyte_line.locator(QTY_BOX)).to_have_value("1")
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM0.90")
    expect(guest_page.locator(CART_BADGE).first).to_have_text("1")
