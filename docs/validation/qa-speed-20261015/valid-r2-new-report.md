# Delivery variant UX QA

Variant A completed the requested order with every specified value preserved. Variant B reached the final order screen but lost the allergy instruction during recovery, and its required boneless choice could not be selected with keyboard alone. Hold B until those failures are fixed. This is a bounded fixture assessment, not a product-readiness verdict.

Both variants produced a 25,000-won configured item, a two-item cart totaling 50,000 won, and a 48,000-won final payment after the 5,000-won coupon and 3,000-won delivery fee. Final details confirmed boneless chicken, spicy sauce, cola, the requested delivery instruction, detail address 302동1104호 and 동네페이. A retained the exact allergy note. B displayed `가게 요청 없음`.

Prioritize these changes:

1. Preserve the store note through address validation and checkout back/return, then verify it in the final order (F-01).
2. Make both required part choices keyboard-operable and replay the full keyboard order (F-02).
3. Restore complete mobile sauce prices and fit the payment breakdown within 320 pixels (F-03, F-04).

Pointer flows and painted key states were reviewed at 384x832, 320x568 and 1440x900 for both variants. The typo coupon was rejected and the corrected coupon accepted on both mobile flows. A completed the entire keyboard-only flow, including both validation recoveries. B's keyboard flow stopped at the inaccessible required part choice; later keyboard states remain blocked. Address recovery and cart back/return both erased B's note. The final-value mismatch was reproduced at every requested width.

B's sauce surcharge text clips at both mobile widths. Its 320-pixel payment summary extends to 360 pixels: scrolling right reveals the amounts while clipping the labels. The total on the fixed payment button remains correct. Screenshot inspection also cleared an early transient A cart frame after stable recapture; it is not reported as a persistent failure. Scroll-under-header content that remained reachable was not treated as a defect.

The four deduplicated findings, reproduction steps, individual coverage results, screenshot paths and priority capture receipts are in [findings.json](findings.json). Priority findings received a capture-and-text self-review; this was not independent review.

Build identity supplied for this run: `66b93b89f5c8bfbd8fc5e485ce55083a23120e88`. Only rendered local pages, screenshots and accessible DOM were inspected in owned Chromium contexts. The product was not modified.

Figma fidelity is unknown. Other browser engines, physical devices, screen-reader speech, text enlargement/spacing, optional dialogs and network-failure recovery were not tested. Additional viewport runs used the correct coupon without repeating the typo. Backend persistence and real payment were outside this synthetic fixture. No all-QA-pass claim is made for those missing checks.
