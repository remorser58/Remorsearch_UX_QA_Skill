# Delivery UX QA

Variant B fails the requested order integrity and keyboard checks. Variant A preserves all requested final values in the tested flows. This is a bounded synthetic-fixture result, with Figma fidelity unknown.

Build identity supplied for this run: `66b93b89f5c8bfbd8fc5e485ce55083a23120e88`.

Prioritize preserving the store note through validation and cart return, making required meat choices keyboard-operable, and exposing complete sauce labels and omission feedback at narrow widths.

## Results

| Variant | Viewport | Full flow and final values | Rendered review |
| --- | --- | --- | --- |
| A | 384x832 | All requested values preserved | Reviewed key states; no reading or action obstruction observed |
| A | 320x568 | All requested values preserved | Reviewed key states and scrolled receipt bottom |
| A | 1440x900 | All requested values preserved; completed by keyboard | Reviewed key states, focus and errors |
| B | 384x832 | Final order reached; allergy note missing | Sauce surcharges clipped |
| B | 320x568 | Final order reached; allergy note missing | Sauce surcharges clipped; receipt bottom reachable |
| B | 1440x900 | Final order reached; allergy note missing; keyboard meat selection blocked | Sauce labels readable |

Both variants calculate the configured item at 25,000 won, quantity two at 50,000 won, and final payment at 48,000 won after the 5,000 won coupon discount and 3,000 won delivery fee. Final receipts show the requested meat, sauce, cola, detail address, bell request and payment method. B shows `가게 요청: 없음`; A shows the exact supplied allergy note.

## Reproduced findings

1. B discards the allergy note when submission fails for a missing detail address. It survives both coupon attempts, then changes from 28/50 to 0/50. Entering the address and submitting leaves the final request empty. A separate replay also loses a re-entered note after cart return. See `b-mobile-coupon-error.png`, `b-mobile-address-error.png`, `b-mobile-final.png` and `b-mobile-back-return.png`.

2. B's required meat choices have no keyboard tab stop. Tab proceeds from the back button to sauce and extras. The choices are non-focusable DIV elements with no control role. A completes selection, quantity, coupon correction and address recovery by keyboard. See `b-desktop-keyboard-options.png` and the actual tab trace in `evidence.json`.

3. B clips the hot and garlic sauce surcharges at 384px and 320px, including selected states. Desktop labels remain readable. See `b-mobile-missing-sauce.png`, `b-short-selected.png` and `b-desktop-selected.png`.

4. B silently blocks Add when sauce is omitted. There is no new error text or error styling, and focus remains on Add. Choosing sauce recovers the flow. A identifies the missing sauce and focuses its control. See `b-desktop-missing-sauce.png` and `a-desktop-missing-sauce.png`.

5. B returns `쿠폰을 적용할 수 없습니다. (CPN-4003)` for the typo without spelling guidance. The supplied correction succeeds. See `b-mobile-coupon-error.png`.

6. B's cart decrement and increment buttons have no accessible names. Their visible icons work with a pointer. See `b-mobile-cart-one.png` and the cart accessibility snapshot in `evidence.json`.

The first two failures received a separate capture-and-trace self-review. No independent reviewer was used. Repeated widths and note-loss transitions are consolidated into the same issue families.

## Design and limits

Reviewed actual screenshots of entry, options, omission, cart, coupon error, address error, final receipt and share overlays. Alignment and wrapping remain readable in the other reviewed states. Fixed controls and headers allow the exercised content to remain reachable; ordinary scroll-under-header behavior is not reported as a defect. Share dialogs fit all requested widths and close successfully.

Testing used owned headless Chromium contexts, CSS viewport sizes and DPR 1. Real devices, Safari/WebKit, assistive-technology speech, software keyboards, 200% text resizing, text-spacing overrides, reload persistence and slow networks were not tested. Formal WCAG/KWCAG conformance remains unassessed.

Product source, server payloads and Figma were unavailable or outside the permitted scope. A checkout rerender causing the note reset is a hypothesis. Real fulfilment harm was not observed. Locator interception and focus-wait failures were automation limitations, not product findings.

Screenshots and DOM traces were captured in this run. Exact capture-clock receipts were not recorded; `evidence.json` retains report-time hashes and separate file creation metadata. `findings.json` contains reproduction steps, severity, coverage and unverified hypotheses.
