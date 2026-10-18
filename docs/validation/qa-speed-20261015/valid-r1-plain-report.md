# Delivery UX QA

Both variants were exercised through the requested order flow at 384x832, 320x568 and 1440x900. Variant A preserved all requested final values in these runs. Variant B reached the correct payment total but lost the allergy note after the missing-address error. Seven issue families were reproduced in B.

## Findings

1. High: submitting without a detail address clears the allergy note. Correcting only the address produces a final order with `가게 요청 없음`. This happened at all three sizes. Compare `b-mobile-coupon-typo.png`, `b-mobile-note-after-error.png` and `b-mobile-final.png`. Re-entering the note after the error restores it, as shown in `b-384-manual-note-recovery-final.png`.
2. High: the required part selector is absent from the accessible controls and skipped by Tab. Keyboard-only selection can choose spicy sauce and cola but cannot choose boneless chicken or add the requested item. See `b-mobile-keyboard-options-result.png` and `dom-evidence.json`. The equivalent keyboard sequence adds the correct 25,000-won item in A.
3. Medium: the phone-width sauce controls clip their surcharge text. Selection does not restore the missing text. See `b-mobile-options-selected.png` and `b-short-options-selected.png`; desktop text fits.
4. Medium: the 360-pixel payment summary overflows the 320-pixel viewport. Horizontal scrolling alternately cuts the amounts or their labels. See `b-320-total-left.png` and `b-320-total-right.png`.
5. Medium: required-field recovery feedback is incomplete. Adding without sauce gives no error message. The address error is visible, but focus remains on the payment button and the field has no accessible invalid/error association. See `b-mobile-sauce-error.png`, `b-desktop-address-error.png` and `dom-evidence.json`.
6. Medium: cart quantity buttons have blank accessible names, despite being keyboard-focusable. See `b-384-cart-recheck.png` and `dom-evidence.json`.
7. Low: typo coupon feedback gives only `쿠폰을 적용할 수 없습니다. (CPN-4003)`. It supplies no spelling or cause guidance. Correction succeeds when the user already knows the right code. See `b-mobile-coupon-typo.png`.

## Verified values and coverage

Both variants showed one configured item at 25,000 won, quantity 2 at 50,000 won, a 5,000-won coupon discount and 3,000-won delivery, giving 48,000 won through 동네페이. Final orders retained the requested chicken options, quantity, `문 앞에 두고 벨 눌러주세요` and `302동1104호`. A also retained the exact allergy note.

Actual entry, option/error/selection, cart, coupon, address-error, payment-summary and final-order screenshots were reviewed across the requested sizes. Keyboard checks covered option selection and cart focus/name behavior. Full keyboard-only checkout was not exhaustively tested. `findings.json` records coverage and evidence per variant and viewport.

## Limits

Figma was unavailable, so design fidelity is unknown. Scroll-under-header content that remained accessible was not counted as a defect. No calculation defect was observed. Initial blank B cart captures were preserved as an unverified capture/state anomaly; fresh reproductions showed complete carts.

This was a local synthetic fixture audit using owned Chromium contexts and existing Playwright, with no product changes. Physical phones, native soft keyboards, screen readers, alternate engines and optional theme/zoom/offline states were not tested. The supplied build identity was not independently verified through source inspection. These results apply to the exercised states and do not establish a global QA pass.
