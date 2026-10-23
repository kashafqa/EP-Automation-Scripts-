# Small order fee requirements

Source prompt: "A small order fee is added to any order whose cart subtotal, before discounts, is below 10.00 RM. The fee is decided only by the subtotal. Coupons and discounts reduce what the customer pays but never trigger or remove the fee." Same rules for guest and logged-in users; guest verified first.

| ID | Requirement | Acceptance criteria |
|----|-------------|---------------------|
| REQ-1 | Subtotal is the sum of item price × quantity before any coupon/discount | Subtotal shown = Σ(price × qty) |
| REQ-2 | Small order fee is shown when subtotal < 10.00 RM | Fee line "Small Order Fee" = RM5.00 visible for subtotal 9.99 RM and below |
| REQ-3 | No small order fee when subtotal ≥ 10.00 RM | No fee line at exactly 10.00 RM and above |
| REQ-4 | Fee updates when the cart changes | Fee appears/disappears immediately when qty or items move the subtotal across 10.00 RM |
| REQ-5 | A coupon never removes the fee | Subtotal < 10 RM + coupon → fee still shown |
| REQ-6 | A coupon never adds the fee | Subtotal ≥ 10 RM + coupon that brings the payable amount below 10 RM → no fee |
| REQ-7 | Same rules for guest and logged-in users | REQ-1 to REQ-6 pass for both |

## Test data

- Coupon: "small order fee coupon", fixed 3.00 RM off, logged-in users only (stored as `DOC_COUPON_CODE` / `DOC_COUPON_AMOUNT` in `.env`).
- REQ-6 check: subtotal between 10.00 and 12.99 RM + coupon makes the payable amount below 10 RM; the fee must still NOT appear.
- Guest check: applying the coupon as a guest must not give the discount (see Q1–Q3).

## Open questions (for dev: Adhi / Hong)

Raised by: Kashaf (QA) · Date: 2026-10-14 · Status: awaiting answer

| # | Question | Why it matters | Answer |
|---|----------|----------------|--------|
| Q1 | **Coupon for guests:** the coupon should work only for logged-in users, but on the cart screen a guest can apply it. Is the discount actually applied for the guest, or is it just accepted in the box? What is the intended behaviour? | If the discount applies, it breaks the "logged-in only" rule and lets anyone use the coupon without an account. | Seen live (2026-10-14): guest coupon field is ENABLED on the cart and a voucher discount is applied there, but at checkout the guest field is disabled and the voucher is silently dropped (cart RM5.00 → checkout RM13.50, no message). CONFIRMED by test `test_guest_cannot_use_logged_in_only_coupon`: "small order fee coupon" (logged-in only) IS applied for a guest on the cart: RM3.00 off, Estimated Total RM10.50 instead of RM13.50 (fee stays RM5.00). Intended behaviour still needed. **Shared with Hong 2026-10-14 (in progress).** |
| Q2 | **Proposed guest behaviour:** guest can type the code, but Apply shows "This coupon is for members. Log in to use it" with a login link; after login the cart is kept and the coupon applies. Can we agree on this? | Clear for the user and encourages sign-up; avoids a coupon that silently disappears at checkout. | **Shared with Hong 2026-10-14 (in progress).** |
| Q3 | **Server-side check:** is the "logged-in only" coupon rule enforced again at payment/order creation, not only on the cart screen? | A cart-screen-only check can be bypassed, so a guest could still pay with the discount. | **Shared with Hong 2026-10-14 (in progress).** |
| Q4 | **Fee amount and label:** how much is the small order fee (RM), and what exact label is shown (e.g. "Small Order Fee")? | Tests cannot assert the correct fee without it. | **CONFIRMED by Kashaf 2026-10-14: fee is RM5.00**, label "Small Order Fee" (cart and checkout). |
| Q5 | **Sale prices:** for products with a crossed-out price (e.g. ~~RM20.19~~ RM17.16), is the subtotal calculated on the sale price or the original price? | "Before discounts" is ambiguous; it decides whether the fee applies near 10 RM. | Seen live: fee follows the SALE price (11 × Uphalyte = RM9.90 sale / RM10.45 original → fee charged). Please confirm intended. |
| Q6 | **Where the fee appears:** cart, checkout, or both? | Tests need to know which screen(s) to check. | Seen live: both cart (`Estimated Total`) and checkout (`Grand Total`). |
| Q7 | **What counts toward the 10 RM:** are shipping, delivery and other fees excluded from the subtotal? | Changes whether a cart near 10 RM gets the fee. | Seen live: no delivery line in cart/checkout for these carts; fee decided on item subtotal only. Please confirm. |
| Q8 | **Exact boundary:** confirm 10.00 RM exactly = no fee, and 9.99 RM = fee. | Boundary cases are the most likely place for a bug. | Tested 2026-10-14: exactly RM10.00 (Gillette Blue II RM3.20 + 4 × Maalox) → no fee; RM9.99 (3 × Dimectal + 5 × Uphalyte) → RM5.00 fee. Matches the rule; please confirm. |
| Q9 | **Prescription (Rx) products:** do Rx items count toward the subtotal, and does the fee apply to Rx orders the same way? | Test cases CART-17 covers Rx checkout but the fee rule does not mention Rx. | |
| Q10 | **Public voucher "200" (RM300 OFF):** it is listed on cart/product pages and the "Auto Apply Vouchers" button applies it for guests, bringing the cart total to RM0.00. Is this voucher meant to be public / usable by guests? | Possible revenue leak. | |
| Q11 | **Test systems linked from production:** "Log in" / "Sign In to Unlock" go to `auth.dev.doctoroncall.com.my` and the payment frame loads from `checkout-demo.airwallex.com`. Is this expected on www.doconcall.com.my? | Real customers may be sent to dev login / demo payment. | |
| Q12 | **Remove confirmation is inconsistent:** − at qty 1 asks "Remove Item" confirmation, but the trash icon and typing 0 / blank / -1 remove the line with no confirmation. Which is intended? | Users can lose items without warning. | |
| Q13 | **Invalid typed quantity (1.5, 9999):** the field keeps showing the typed value while subtotal, fee and badge show the old quantity, with no on-page error. Should it reset or show an error? | Cart looks wrong to the user. | |
| Q14 | **Fast clicks on + / − are lost:** each click reloads the page, so clicks during a reload are dropped (5 × + from 2 gave 4, not 7). Should + / − be disabled during the update, or update without a reload? | Wrong quantity in cart. | |
| Q15 | **Fee not explained before checkout:** the RM5.00 fee and the RM10 threshold are not mentioned on the product page or the free-delivery bar. Should a hint be shown (e.g. "Add RMx more to avoid the small order fee")? | Customer surprise at checkout. | |
| Q16 | **Cart Checkout button (automation):** in automated Chrome, clicking `Checkout` on the cart stays on /cart/; the site's Cloudflare link prefetch gets a 503 "prefetch refused" for /checkout/. Opening /checkout/ directly works. Can you check whether real users are affected? | If real, guests cannot reach checkout from the cart. | |
| Q17 | **Product data:** Terumo Syringe (Slip Tip) has four variants all labelled "5ml" priced RM2.00 / 1.50 / 3.50 / 1.50; product page shows RM2.00 but listings say "from RM1.50". Is this correct? | Customers can't tell variants apart; wrong price shown. | |
| Q18 | **Checkout savings banner:** guest checkout says "You are missing out on up to RM 272.08 in savings!" for a RM26.60 cart. Where does this number come from (the public RM300 voucher?) | Misleading amount shown to customers. | |

## Test cases (automated, guest)

Rewritten 2026-10-14 in simple style (Step / Expected comments).
50 test functions = 55 test cases. Last full run: 45 pass, 8 fail, 2 skip — 3 of the failures were slow page loads / a test fix and passed on re-run, so expected result = 48 pass, 5 fail (real site issues), 2 skip.

| What is tested | File | Test | Last result |
|----------------|------|------|-------------|
| Verify CART-01: + raises the quantity from 1 to 2 and the subtotal becomes RM3.40 (2 x RM1.70). | `test_cart_quantity.py` | `test_CART_01_increase_quantity` | PASS |
| Verify CART-02: - lowers the quantity from 2 to 1, the subtotal drops from RM3.40 to RM1.70 and no Remove popup opens. | `test_cart_quantity.py` | `test_CART_02_decrease_quantity` | PASS |
| Verify CART-03: - at quantity 1 opens the 'Remove Item' popup with the exact texts and Confirm, Cancel and X buttons. | `test_cart_quantity.py` | `test_CART_03_minus_at_qty_1_shows_remove_popup` | PASS |
| Verify CART-04: Confirm in the remove popup removes the item and shows the '"Maalox ..." removed.' notice. | `test_cart_quantity.py` | `test_CART_04_confirm_removes_item` | PASS |
| Verify CART-05: Cancel in the remove popup closes it and keeps Maalox at qty 1 (subtotal RM1.70). | `test_cart_quantity.py` | `test_CART_05_cancel_keeps_item` | PASS |
| Verify CART-06: X in the remove popup closes it and keeps Maalox at qty 1 (subtotal RM1.70). | `test_cart_quantity.py` | `test_CART_06_x_keeps_item` | PASS |
| Verify CART-07: an empty guest cart shows the empty-cart message and no items, summary or checkout button. | `test_cart_quantity.py` | `test_CART_07_empty_cart_page` | PASS |
| Verify CART-08: the empty-cart 'Start Shopping' button opens the All Products page. | `test_cart_quantity.py` | `test_CART_08_start_shopping_button` | PASS |
| Verify CART-09: the header badge counts items: 1 after Maalox, 2 after Uphalyte, 3 after +, 2 after trashing Uphalyte. | `test_cart_quantity.py` | `test_CART_09_header_badge_count` | PASS |
| Verify CART-10: adding Maalox from its page and again via search gives ONE cart line with qty 2 (RM3.40). | `test_cart_quantity.py` | `test_CART_10_same_product_twice_merges` | PASS |
| Verify CART-11: 2 x Maalox (RM1.70) + 1 x Uphalyte (RM0.90) show the right lines and subtotal RM4.30. | `test_cart_quantity.py` | `test_CART_11_two_products_subtotal` | PASS |
| Verify CART-12: the cart qty box allows at most 9998, and typing 9999 does not change the cart (still 1, RM1.70). | `test_cart_quantity.py` | `test_CART_12_max_quantity` | PASS |
| Verify CART-13: typing 0, -1, 'abc' or nothing in the cart qty box removes the line with a 'Basket updated.' notice. | `test_cart_quantity.py` | `test_CART_13_typed_quantity_removes_line` | PASS |
| Verify CART-13: typing 1.5 is not accepted and the qty box goes back to 1 (cart stays RM1.70, badge 1). | `test_cart_quantity.py` | `test_CART_13_typed_decimal_quantity_rejected` | FAIL – site bug: box keeps 1.5 (Q13) |
| Verify CART-13: typing 9999 is not accepted and the qty box goes back to 1 (cart stays RM1.70, badge 1). | `test_cart_quantity.py` | `test_CART_13_typed_too_large_quantity_rejected` | FAIL – site bug: box keeps 9999 (Q13) |
| Verify CART-14: 5 quick + clicks then 3 quick - clicks from qty 1 end at qty 3 (no clicks lost). | `test_cart_quantity.py` | `test_CART_14_rapid_plus_minus_clicks` | FAIL – site bug: quick clicks lost (Q14) |
| Verify CART-14: clicking + five times, waiting for each reload, ends at qty 6, subtotal RM10.20, badge 6. | `test_cart_quantity.py` | `test_CART_14_plus_clicks_with_wait` | PASS |
| Verify CART-15: the Maalox cart line shows the same name, image, price and pack size as the product page. | `test_cart_quantity.py` | `test_CART_15_maalox_cart_line_matches_product_page` | PASS |
| Verify CART-15: the Uphalyte cart line shows the same name, image, price and pack size as the product page. | `test_cart_quantity.py` | `test_CART_15_uphalyte_cart_line_matches_product_page` | PASS |
| Verify CART-16: the guest cart (2 x Maalox + 1 x Uphalyte = RM4.30) is unchanged after a page refresh. | `test_cart_quantity.py` | `test_CART_16_cart_kept_after_refresh` | PASS |
| Verify CART-16: the cart is kept after logging out and logging back in. | `test_cart_quantity.py` | `test_CART_16_cart_kept_after_relogin` | SKIP – logged-in scope |
| Verify CART-17: a prescription (Rx) product in the cart follows the Rx checkout flow. | `test_cart_quantity.py` | `test_CART_17_rx_product_checkout` | SKIP – needs Rx product |
| Verify CART-18: + on Maalox in a 2-product cart changes only Maalox (1 -> 2); Uphalyte stays 1 at RM0.90, subtotal RM4.30. | `test_cart_quantity.py` | `test_CART_18_plus_changes_only_that_line` | PASS |
| Verify CART-19: - on Uphalyte in a 2-product cart changes only Uphalyte (2 -> 1); Maalox stays 1, subtotal RM2.60. | `test_cart_quantity.py` | `test_CART_19_minus_changes_only_that_line` | PASS |
| Verify CART-20: at the maximum qty 9998, + does not raise the quantity (stays 9998, subtotal RM16,996.60). | `test_cart_quantity.py` | `test_CART_20_plus_at_max_quantity` | PASS |
| Verify CART-21: a qty changed with + and - (1 -> 3 -> 2) is kept after refreshing the cart (qty 2, RM3.40, badge 2). | `test_cart_quantity.py` | `test_CART_21_plus_minus_kept_after_refresh` | PASS |
| Verify CART-22: - at qty 1 + Confirm on Maalox in a 2-product cart removes only Maalox; Uphalyte stays (RM0.90, badge 1). | `test_cart_quantity.py` | `test_CART_22_popup_removes_only_that_product` | PASS |
| Verify CART-23: the trash icon on Maalox (qty 2) removes the whole line; Uphalyte stays (RM0.90, badge 1). | `test_cart_quantity.py` | `test_CART_23_trash_removes_only_that_product` | PASS |
| Verify FEE-01 (REQ-2): 1 x Maalox = RM1.70 with no voucher gets the RM5.00 fee, Estimated Total RM6.70. | `test_small_order_fee.py` | `test_FEE_01_fee_below_10` | PASS |
| Verify FEE-02 (REQ-1/2): 11 x Uphalyte = RM9.90 at sale price (RM10.45 at original price) still gets the fee. | `test_small_order_fee.py` | `test_FEE_02_fee_uses_sale_price` | PASS |
| Verify FEE-03 (REQ-3): 6 x Maalox = RM10.20 has no fee, Estimated Total RM10.20. | `test_small_order_fee.py` | `test_FEE_03_no_fee_above_10` | PASS |
| Verify FEE-06 (REQ-3 boundary): exactly RM10.00 (1 x Razor RM3.20 + 4 x Maalox RM1.70) has NO fee. | `test_small_order_fee.py` | `test_FEE_06_no_fee_at_exactly_10` | PASS |
| Verify FEE-07 (REQ-2 boundary): RM9.99 (3 x Dimectal RM1.83 + 5 x Uphalyte RM0.90) gets the fee, total RM14.99. | `test_small_order_fee.py` | `test_FEE_07_fee_at_9_99` | PASS |
| Verify FEE-08 (REQ-4): on the cart screen, - (qty 6 -> 5, RM8.50) adds the fee to the total (RM13.50) and + (5 -> 6, RM10.20) removes it (RM10.20). | `test_small_order_fee.py` | `test_FEE_08_fee_follows_quantity_changes` | PASS |
| Verify FEE-09 (REQ-4): trashing Uphalyte drops the cart from RM10.30 to RM8.50 and the RM5.00 fee appears. | `test_small_order_fee.py` | `test_FEE_09_fee_appears_after_trash_removal` | PASS |
| Verify FEE-10 (REQ-4): removing Maalox with - and Confirm drops RM10.70 to RM9.00 and the RM5.00 fee appears. | `test_small_order_fee.py` | `test_FEE_10_fee_appears_after_popup_removal` | PASS |
| Verify FEE-11 (REQ-4): adding 2 Uphalyte to a RM8.50 cart (fee shown) lifts it to RM10.30 and the fee goes away. | `test_small_order_fee.py` | `test_FEE_11_fee_removed_when_product_added` | PASS |
| Verify FEE-12 (REQ-4): adding the bigger Maalox pack (4.3ml x20, RM26.60) to a RM1.70 cart removes the fee (RM28.30). | `test_small_order_fee.py` | `test_FEE_12_bigger_pack_removes_fee` | PASS |
| Verify FEE-14: with an auto-applied voucher, Estimated Total = RM8.50 + RM5.00 - voucher discount (never below RM0.00). | `test_small_order_fee.py` | `test_FEE_14_estimated_total_with_voucher` | PASS |
| Verify FEE-16: clicking the cart Checkout button opens the checkout page. | `test_small_order_fee.py` | `test_FEE_16_checkout_button_opens_checkout` | FAIL – stays on /cart/ in automation; check by hand (Q16) |
| Verify FEE-18 (REQ-3): checkout for exactly RM10.00 (1 x Razor + 4 x Maalox) has no fee and Grand Total RM10.00. | `test_small_order_fee.py` | `test_FEE_18_no_fee_on_checkout_at_exactly_10` | PASS |
| Verify FEE-19: the fee is a flat RM5.00 charged once (one row) for a 3-line RM7.93 cart, in cart and checkout. | `test_small_order_fee.py` | `test_FEE_19_fee_charged_once` | PASS |
| Verify FEE-20: the free-delivery bar asks for RM111.50 more (RM120.00 - RM8.50); the RM5.00 fee does not count. | `test_small_order_fee.py` | `test_FEE_20_free_delivery_bar_ignores_fee` | PASS |
| Verify FEE-21: the guest cart and its RM5.00 fee are unchanged after refreshing the cart page. | `test_small_order_fee.py` | `test_FEE_21_fee_kept_after_refresh` | PASS |
| Verify COUPON-01: an invalid coupon shows the 'does not exist' error and the cart stays RM1.70 + RM5.00 = RM6.70. | `test_coupon.py` | `test_COUPON_01_invalid_coupon_error` | PASS |
| Verify COUPON-02: the logged-in-only coupon gives a guest no discount (RM8.50 cart stays RM13.50 with the fee). | `test_coupon.py` | `test_COUPON_02_guest_cannot_use_logged_in_coupon` | FAIL – site bug: coupon works for guest (Q1, with Hong) |
| Verify COUPON-03 (REQ-5): an auto-applied voucher on a RM8.50 cart lowers the total but the RM5.00 fee stays. | `test_coupon.py` | `test_COUPON_03_voucher_never_removes_fee` | PASS |
| Verify COUPON-04 (REQ-6): an auto-applied voucher that brings a RM10.20 cart below RM10 never adds the fee. | `test_coupon.py` | `test_COUPON_04_voucher_never_adds_fee` | PASS |
| Verify COUPON-05 (REQ-6): the real coupon on a RM10.20 cart (payable may drop to RM7.20) never adds the fee. | `test_coupon.py` | `test_COUPON_05_coupon_never_adds_fee` | PASS |
| Verify COUPON-06: removing the coupon from a RM8.50 cart brings back Estimated Total RM13.50 with the RM5.00 fee. | `test_coupon.py` | `test_COUPON_06_removing_coupon_restores_totals` | PASS |
| Verify COUPON-07: the coupon in UPPERCASE, Title Case or with extra spaces gives the same discount and total as the exact code. | `test_coupon.py` | `test_COUPON_07_coupon_case_and_spaces` | PASS |

## Requirement results (guest)

| ID | Result | Notes |
|----|--------|-------|
| REQ-1 | PASS | Subtotal = Σ sale price × qty |
| REQ-2 | PASS | RM5.00 fee at RM1.70 … RM9.99 (cart + checkout) |
| REQ-3 | PASS | No fee at exactly RM10.00, RM10.20, RM10.70, RM28.30 |
| REQ-4 | PASS | Fee updates on +/−, trash, popup Confirm, 2nd product, bigger pack |
| REQ-5 | PASS | Voucher/coupon never removes the fee |
| REQ-6 | PASS | Voucher/coupon never adds the fee (RM10.20 − RM3 → no fee) |
| REQ-7 | NOT RUN | Logged-in side not tested yet (needs DOC_EMAIL / DOC_PASSWORD) |

Coupon rule (logged-in only): **FAIL for guest** – see Q1 (with Hong).

## Missing test cases (still to write)

| # | Missing | Blocked by |
|---|---------|------------|
| M1 | REQ-7: all fee tests as a logged-in user | Login in `.env` |
| M2 | Logged-in user can apply "small order fee coupon" (RM3 off) and the fee still follows the subtotal | Login in `.env` |
| M3 | CART-16 re-login: cart kept after log out / log in (also guest cart → after login) | Login in `.env` |
| M4 | CART-17: Rx product needs prescription/consultation before payment | Rx product name |
| M5 | Guest coupon expected behaviour (message / login link) – update TC for guest coupon | Hong's answer (Q1–Q2) |
| M6 | Coupon is rejected again at payment for guests (server-side check) | Q3 answer; needs a safe test order / test payment |
| M7 | Trash icon / typing 0 should (or should not) show the Remove popup | Q12 answer |
| M8 | Pharmacist Screening popup on some non-Rx products before add to cart | Decide if in scope |
| M9 | End-to-end journey: home → search → product → Add to Cart → cart icon → checkout (fee shown) | Nothing – planned for later |
