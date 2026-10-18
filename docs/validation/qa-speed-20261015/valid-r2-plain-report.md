# Delivery UX QA

Both variants were exercised through the requested order at 384x832, 320x568 and 1440x900. Variant A preserved the requested values throughout recovery. Variant B completed the order but silently lost the allergy note after rejecting a missing detail address. Five deduplicated findings are recorded in `findings.json`.

The configured chicken cost 25,000 won in both variants. Quantity 2 produced a 50,000 won subtotal. Correcting HANKI5000 to HANKKI5000 applied a 5,000 won discount; adding the 3,000 won delivery fee produced a final payment of 48,000 won with 동네페이. Final details were inspected, including the options, quantity, delivery request and synthetic address 302동1104호.

## Findings

1. B clears the allergy note on the missing-address error. The first final order showed `가게 요청: 없음` at every viewport. `b-mobile-coupon-typo.png` shows the entered note; `b-mobile-address-error.png` shows the emptied textarea, and `b-mobile-final.png` shows its absence in the order. Re-entering the note after the error restored it in a separate run, recorded in `b-mobile-recovery-final.png`.

2. B's required part choice cannot be reached through Tab navigation. Focus jumps directly from the back button to the sauce choices. The boneless control is a rendered DIV with no role or tabindex. Its cart quantity buttons also have empty accessible names. A exposes part radios, supports ArrowRight/Space selection and names its quantity controls. The observed Tab sequence, active elements and accessibility excerpts are saved in `accessible-dom-evidence.json`.

3. B silently rejects adding an item without sauce. It leaves the same screen and keyboard focus on the add button without explaining the missing choice. Selecting spicy sauce permits recovery. A highlights the sauce group, displays an instruction and focuses a sauce radio. Compare `b-mobile-missing-sauce.png` with `a-mobile-missing-sauce.png`. B displays the later address error, but keyboard focus remains on the payment button.

4. B clips prices at narrow widths. Sauce surcharges are clipped at both 384 and 320 pixels, as shown in `b-mobile-selected-options.png` and `b-short-selected-options.png`. At 320 pixels its checkout amount panel extends to 360 pixels and clips the right-hand amounts. A fresh-context reproduction is in `b-short-totals-fresh.png`. Horizontal scrolling recovers the amounts while clipping the labels (`b-short-totals-horizontal-recovery.png`); the payment button still shows the correct total. Desktop values were readable.

5. B rejects the typo coupon with `쿠폰을 적용할 수 없습니다. (CPN-4003)` and provides no spelling guidance. The corrected code works. A explains that the entered code is unknown and asks for a spelling check. See `b-mobile-coupon-typo.png` and `a-mobile-coupon-typo.png`.

## Coverage and limits

Reviewed screenshots cover menu, product options, selected states, omitted-sauce attempts, two-item carts, coupon errors, address errors, payment totals and final-order details at all three requested sizes. The coverage entries in `findings.json` identify the actual reviewed files. Keyboard checks included Tab navigation, ArrowRight/Space selection, Enter activation and validation focus. B's inaccessible part choice prevents an entirely keyboard-only order.

Text alignment, Korean wrapping, clipping and fixed headers/footers were inspected in the captured states. Ordinary scrolling exposed the final details and form content. Scroll-under-header behavior, broad desktop whitespace and synthetic product images were not reported as failures.

Figma fidelity is unknown. These were owned headless Chromium contexts using the existing Playwright package, with CSS-pixel viewport sizing and device scale factor 1. Physical-device touch, virtual keyboards, IME, screen readers, alternate browsers, zoom and dark mode remain unverified. No product source, prior reports, memory, other operator output or external sites were read, and the product was not modified. The supplied build identity was not independently verified through repository inspection. No unsupported implementation hypothesis is presented as a finding.
