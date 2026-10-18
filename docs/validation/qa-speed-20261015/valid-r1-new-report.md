# Delivery variant UX QA

## Conclusion

Variant B needs fixes before the requested flow can be considered intact. Its final order omits the entered allergy note, and the required boneless choice cannot be reached by keyboard. Variant A completed the requested pointer and keyboard flows with the correct displayed values. No reproduced failure was found in A within this scope; this is not a general readiness or accessibility certification.

The supplied build identity is `66b93b89f5c8bfbd8fc5e485ce55083a23120e88`. Product source was not read or changed.

Priorities are to preserve the store request through validation and cart return, make the portion choices keyboard-operable, and keep sauce prices and the payment breakdown readable on narrow screens.

## Results

Both variants showed 25,000원 for one configured item and 50,000원 for quantity two. Correcting HANKI5000 to HANKKI5000 applied 5,000원 off. With 3,000원 delivery, both final displays showed 동네페이 and 48,000원, the requested delivery instruction and 302동1104호. A also retained the exact allergy note. B showed 가게 요청: 없음 after the missing-address error cleared that note; returning through the cart reproduced the same loss. Coupon application itself retained the note.

The five deduplicated findings in [findings.json](findings.json) cover B's note loss, inaccessible keyboard portion choice, clipped prices, missing sauce-validation feedback, and unnamed quantity buttons. The generic CPN-4003 coupon message and missing address-error DOM associations are documented separately as observations.

## Coverage and evidence

Screenshots were inspected for all six requested variant/viewport combinations: 384x832, 320x568 and 1440x900. Review included option selection and error states, cart quantity, coupon/address recovery, checkout totals, final summaries, wrapping, price alignment, and fixed headers/footers. Lower content was reached by vertical scrolling. Sauce surcharges are clipped in B at both mobile widths; its payment-summary amounts are also cut off at 320px. The fixed payment button still displays the full total. Ordinary scroll-under-header behavior was not classified as a defect.

Complete pointer submissions were run at 384x832 for both variants. Fresh short-screen flows reached address validation; desktop states and final summaries were also reviewed by resizing existing flows. These are key-state checks, not separate complete submissions at every width. A completed the full keyboard flow; B stopped at the required portion blocker, so its later keyboard steps remain untested. Checkout-to-cart-to-checkout preservation was checked in both.

Screenshot files are cited per finding and coverage row. Capture-time hashes, dimensions and visible text are in the three `capture-receipts*.json` files. [interaction-evidence.json](interaction-evidence.json) records keyboard navigation, observed field values, error semantics, and the priority self-review. No independent reviewer or other model was used.

## Limits

Figma fidelity is unknown. This was owned Chromium viewport emulation with synthetic data and fake orders. Real devices, on-screen keyboard occlusion, Safari/WebKit, screen readers, voice control, 200% text resizing, contrast and formal KWCAG/WCAG conformity were not tested. Final rendered values were verified; backend persistence, real payment and fulfilment were not. Source-level causes and unsupported hypotheses remain explicit in the JSON.
