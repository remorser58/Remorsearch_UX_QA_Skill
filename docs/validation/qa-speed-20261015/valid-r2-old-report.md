# Delivery UX QA

Variant A preserved every requested final value in the three tested pointer-driven flows. Variant B reached the fake order screen at every size, but its missing-address error deleted the allergy note. B also blocks keyboard-only selection of the required chicken part. These failures should be fixed before accepting B's purchase flow.

Priorities are to preserve the allergy note after rejected submission, make the chicken-part choices keyboard operable, and let mobile sauce labels display their full surcharge. `findings.json` contains seven deduplicated findings with reproduction steps, impact, evidence and limits.

Build identity supplied for this run: `66b93b89f5c8bfbd8fc5e485ce55083a23120e88`. The product source and repository were not inspected.

## Flow results

| Viewport | Variant A | Variant B |
| --- | --- | --- |
| 384x832 | Requested final values preserved | Final allergy note becomes `없음` |
| 320x568 | Requested final values preserved | Same note loss; sauce surcharges clipped |
| 1440x900 | Requested final values preserved | Same note loss; required chicken choice skipped by Tab |

Both variants added the configured chicken at 25,000원, displayed quantity 2 and a 50,000원 cart subtotal, rejected `HANKI5000`, accepted `HANKKI5000` for a 5,000원 discount, and displayed 48,000원 including 3,000원 delivery. The final menu options, quantity, delivery request, synthetic detail address and 동네페이 payment matched in both variants.

The allergy note was `땅콩 알레르기가 있어요. 양념에 땅콩가루 빼 주세요`. In B it survived both coupon attempts, then cleared to `0/50` after submission without detail address. Correcting only the address to `302동1104호` produced an order with `가게 요청 없음`. This reproduced at all three sizes. In a separate mobile run, explicitly re-entering the note after the error preserved it in the final order. That workaround requires noticing the silent loss.

Compare `b-mobile-coupon-typo.png`, `b-mobile-address-error.png` and `b-mobile-final.png`. The successful workaround is shown in `b-mobile-manual-note-recovery.png`; A's preserved result is in `a-mobile-final.png`.

## Findings

| ID | Impact | Reproduced behavior |
| --- | --- | --- |
| F1 | High | B deletes the allergy note after missing-address validation. |
| F2 | High | B's required chicken-part choices cannot receive keyboard focus. |
| F3 | Medium | B clips sauce surcharges at both mobile widths. |
| F4 | Medium | B rejects an add with sauce omitted without a visible explanation. |
| F5 | Low | B's typo-coupon error provides `CPN-4003` without spelling guidance. |
| F6 | Medium | B's cart quantity buttons have no accessible names. |
| F7 | Medium | B's visible detail-address error lacks a programmatic association and invalid state. |

The keyboard comparison covered a full option-screen focus cycle. A's boneless and spicy radios worked with arrow keys, and cola worked with Space. B skipped the required chicken-part choices; its accessible tree exposed them as plain text. Neither variant received a complete keyboard-only checkout pass.

## Rendered review and limits

Actual screenshots were viewed for menu, options, selected states, cart, coupon error, address error and final summary at the requested sizes. Short-screen final values were also reviewed after scrolling. Text alignment, Korean wrapping, clipped labels, fixed headers and bottom actions were inspected. Scroll-under-header content remained reachable and was not classified as a failure. B's clipped surcharge labels persisted in a later capture; early captures with missing action text were not promoted to findings because later settled captures showed readable text.

Figma fidelity remains unknown. This was one operator using owned headless Chromium contexts at DPR 1, with synthetic fixture data and fake orders. Final values were checked in the rendered order summary; backend storage and network payloads were not inspected. No source, external websites, accounts, prior reports, memory or real personal data were used, and the product was not modified.

Real devices, Safari/WebKit, screen readers, voice control, 200% text resizing, text-spacing overrides, measured contrast, exhaustive focus behavior, reload/history persistence and desktop sauce-omission validation remain untested. No formal accessibility-conformance or overall readiness claim is made. High-impact findings received a labelled self-review, not independent review.

`evidence.json` holds screenshot receipts and recorded keyboard traversal. `observations.json` holds supporting accessible-DOM observations, state checks, self-review records and the manual-recovery receipt.
