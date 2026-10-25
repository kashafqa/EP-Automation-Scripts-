# Coupons and vouchers on the guest cart: invalid code, the logged-in-only coupon, and REQ-5 / REQ-6
# (a coupon never removes or adds the RM5.00 Small Order Fee). The coupon code comes from .env (see config.py).
import pytest
from playwright.sync_api import Page, expect

from cart_helpers import (
    AUTO_APPLY_VOUCHERS_BUTTON, CART_URL, ERROR_MESSAGE, ESTIMATED_TOTAL, FEE_ROW, MAALOX_URL, SUBTOTAL,
    VOUCHER_AMOUNTS, VOUCHER_ROWS, add_to_cart, apply_coupon, get_amount, remove_coupons,
)
from config import DOC_COUPON_AMOUNT, DOC_COUPON_CODE

# Skip the tests that need the real coupon code when it is not filled in .env.
NEEDS_COUPON = pytest.mark.skipif(not DOC_COUPON_CODE, reason="Fill in DOC_COUPON_CODE in .env to run the coupon tests")


# Verify COUPON-01: an invalid coupon shows the 'does not exist' error and the cart stays RM1.70 + RM5.00 = RM6.70.
def test_COUPON_01_invalid_coupon_error(guest_page: Page):
    # Step 1: add 1 Maalox and open the cart
    add_to_cart(guest_page, MAALOX_URL)
    guest_page.goto(CART_URL)

    # Step 2: apply the coupon INVALIDTEST123
    apply_coupon(guest_page, "INVALIDTEST123")

    # Expected: error message, no voucher, totals unchanged
    expect(guest_page.locator(ERROR_MESSAGE).first).to_contain_text(
        'Coupon "invalidtest123" cannot be applied because it does not exist.', timeout=15_000
    )
    expect(guest_page.locator(VOUCHER_ROWS)).to_have_count(0)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM1.70")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM6.70")


# Verify COUPON-02: the logged-in-only coupon gives a guest no discount (RM8.50 cart stays RM13.50 with the fee).
@NEEDS_COUPON
def test_COUPON_02_guest_cannot_use_logged_in_coupon(guest_page: Page):
    # Step 1: add 5 Maalox (RM8.50) and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    guest_page.goto(CART_URL)

    # Step 2: apply the logged-in-only coupon and reload the cart
    apply_coupon(guest_page, DOC_COUPON_CODE)
    guest_page.wait_for_load_state("load")
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)

    # Expected: fee still RM5.00, no discount, Estimated Total RM13.50
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    discount = get_amount(guest_page, VOUCHER_AMOUNTS)
    total = get_amount(guest_page, ESTIMATED_TOTAL)
    assert discount == 0 and total == 13.50, (
        f"BUG: logged-in-only coupon applied for guest - discount RM{discount:.2f} "
        f"(coupon value RM{DOC_COUPON_AMOUNT:.2f}), Estimated Total RM{total:.2f} instead of RM13.50"
    )


# Verify COUPON-03 (REQ-5): an auto-applied voucher on a RM8.50 cart lowers the total but the RM5.00 fee stays.
@pytest.mark.skip(reason="Turned off for now: the automation coupon is not shown on the front end yet, so Auto Apply has nothing to apply")
def test_COUPON_03_voucher_never_removes_fee(guest_page: Page):
    # Step 1: add 5 Maalox (RM8.50) and open the cart -> fee RM5.00
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")

    # Step 2: click 'Auto Apply Vouchers'
    guest_page.locator(AUTO_APPLY_VOUCHERS_BUTTON).click()
    expect(guest_page.locator(VOUCHER_ROWS).first).to_be_visible(timeout=15_000)
    guest_page.wait_for_load_state("load")

    # Expected: a discount is shown, subtotal still RM8.50, fee still RM5.00
    discount = get_amount(guest_page, VOUCHER_AMOUNTS)
    assert discount > 0
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM8.50")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")

    # Expected: Estimated Total = 8.50 + 5.00 - discount (RM0.00 if the discount is bigger)
    total = get_amount(guest_page, ESTIMATED_TOTAL)
    assert total == max(round(13.50 - discount, 2), 0), (
        f"BUG: Estimated Total RM{total:.2f} != RM8.50 + fee RM5.00 - discount RM{discount:.2f}"
    )

    # Step 3: remove the voucher -> Expected: fee still RM5.00
    remove_coupons(guest_page)
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")


# Verify COUPON-04 (REQ-6): an auto-applied voucher that brings a RM10.20 cart below RM10 never adds the fee.
@pytest.mark.skip(reason="Turned off for now: the automation coupon is not shown on the front end yet, so Auto Apply has nothing to apply")
def test_COUPON_04_voucher_never_adds_fee(guest_page: Page):
    # Step 1: add 6 Maalox (RM10.20) and open the cart -> no fee
    add_to_cart(guest_page, MAALOX_URL, qty=6)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)

    # Step 2: click 'Auto Apply Vouchers'
    guest_page.locator(AUTO_APPLY_VOUCHERS_BUTTON).click()
    expect(guest_page.locator(VOUCHER_ROWS).first).to_be_visible(timeout=15_000)
    guest_page.wait_for_load_state("load")

    # Expected: discount shown and the amount to pay is below RM10, but subtotal RM10.20 and still no fee
    discount = get_amount(guest_page, VOUCHER_AMOUNTS)
    total = get_amount(guest_page, ESTIMATED_TOTAL)
    assert discount > 0
    assert total < 10
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.20")
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)

    # Expected: Estimated Total = 10.20 - discount (RM0.00 if the discount is bigger)
    assert total == max(round(10.20 - discount, 2), 0), (
        f"BUG: Estimated Total RM{total:.2f} != RM10.20 - discount RM{discount:.2f}"
    )

    # Step 3: remove the voucher -> Expected: still no fee
    remove_coupons(guest_page)
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)


# Verify COUPON-05 (REQ-6): the real coupon on a RM10.20 cart (payable may drop to RM7.20) never adds the fee.
@NEEDS_COUPON
def test_COUPON_05_coupon_never_adds_fee(guest_page: Page):
    # Step 1: add 6 Maalox (RM10.20) and open the cart -> no fee
    add_to_cart(guest_page, MAALOX_URL, qty=6)
    guest_page.goto(CART_URL)
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)

    # Step 2: apply the coupon and reload the cart
    apply_coupon(guest_page, DOC_COUPON_CODE)
    guest_page.wait_for_load_state("load")
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)

    # Expected: subtotal still RM10.20 and no fee row
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM10.20")
    expect(
        guest_page.locator(FEE_ROW),
        "BUG: coupon added the small order fee - subtotal RM10.20 is >= RM10 but the fee row is shown",
    ).to_have_count(0)

    # Expected: Estimated Total = 10.20 - discount
    discount = get_amount(guest_page, VOUCHER_AMOUNTS)
    total = get_amount(guest_page, ESTIMATED_TOTAL)
    assert total == max(round(10.20 - discount, 2), 0), (
        f"BUG: Estimated Total RM{total:.2f} != RM10.20 - discount RM{discount:.2f}"
    )

    # Step 3: remove the coupon -> Expected: no fee and Estimated Total back to RM10.20
    remove_coupons(guest_page)
    expect(guest_page.locator(FEE_ROW)).to_have_count(0)
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM10.20")


# Verify COUPON-06: removing the coupon from a RM8.50 cart brings back Estimated Total RM13.50 with the RM5.00 fee.
@NEEDS_COUPON
def test_COUPON_06_removing_coupon_restores_totals(guest_page: Page):
    # Step 1: add 5 Maalox (RM8.50) and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    guest_page.goto(CART_URL)

    # Step 2: apply the coupon and reload the cart
    apply_coupon(guest_page, DOC_COUPON_CODE)
    guest_page.wait_for_load_state("load")
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)
    if get_amount(guest_page, VOUCHER_AMOUNTS) == 0:
        pytest.skip("coupon was not applied for the guest, so there is nothing to remove")

    # Step 3: remove the coupon
    remove_coupons(guest_page)

    # Expected: no voucher, subtotal RM8.50, fee RM5.00, total RM13.50
    expect(guest_page.locator(VOUCHER_ROWS)).to_have_count(0)
    expect(guest_page.locator(SUBTOTAL)).to_have_text("RM8.50")
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
    expect(guest_page.locator(ESTIMATED_TOTAL)).to_have_text("RM13.50")


# Verify COUPON-07: the coupon in UPPERCASE, Title Case or with extra spaces gives the same discount and total as the exact code.
@NEEDS_COUPON
@pytest.mark.parametrize("style", ["uppercase", "title-case", "extra-spaces"])
def test_COUPON_07_coupon_case_and_spaces(guest_page: Page, style: str):
    # Step 1: add 5 Maalox (RM8.50) and open the cart
    add_to_cart(guest_page, MAALOX_URL, qty=5)
    guest_page.goto(CART_URL)

    # Step 2: apply the exact coupon code and note the discount and total
    apply_coupon(guest_page, DOC_COUPON_CODE)
    guest_page.wait_for_load_state("load")
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)
    exact_discount = get_amount(guest_page, VOUCHER_AMOUNTS)
    exact_total = get_amount(guest_page, ESTIMATED_TOTAL)

    # Step 3: remove it and apply the same code written differently
    remove_coupons(guest_page)
    if style == "uppercase":
        code = DOC_COUPON_CODE.upper()
    elif style == "title-case":
        code = DOC_COUPON_CODE.title()
    else:
        code = "  " + DOC_COUPON_CODE + "  "
    apply_coupon(guest_page, code)
    guest_page.wait_for_load_state("load")
    guest_page.wait_for_timeout(3_000)
    guest_page.goto(CART_URL)

    # Expected: same discount and same total as the exact code, fee still RM5.00
    discount = get_amount(guest_page, VOUCHER_AMOUNTS)
    total = get_amount(guest_page, ESTIMATED_TOTAL)
    assert discount == exact_discount and total == exact_total, (
        f"BUG: coupon code ({style}) gives discount RM{discount:.2f} / total RM{total:.2f}, "
        f"but the exact code gives RM{exact_discount:.2f} / RM{exact_total:.2f}"
    )
    expect(guest_page.locator(FEE_ROW)).to_have_text("RM5.00")
