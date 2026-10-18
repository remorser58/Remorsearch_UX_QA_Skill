# Blind QA adjudication

## Verdict

PARTIAL — task-benefit comparison INCONCLUSIVE. R17 has the stronger evidence-backed artifact set in this supplied run: six valid unique defect families, versus five in R46. Both identified the two known high-impact failures. R17 additionally demonstrates cropped payment amounts at 320px and provides broader keyboard and bottom-state coverage. R46's coupon wording item is a supported observation and an unsupported defect claim.

This comparison concerns anonymous labels only. Two product variants plus one repeat are too small to establish a robust task-benefit win or general superiority. Start times and accounting are outside this review.

## Evidence

| Arm | Submitted | Valid unique | Unsupported as defect | False factual findings | Supported exclusive |
| --- | ---: | ---: | ---: | ---: | ---: |
| R17 | 6 | 6 | 0 (0%) | 0 | 1 |
| R46 | 6 | 5 | 1 (16.7%) | 0 | 0 |

R46 IDs below are assigned by source order. Each arm's six findings are reviewed separately in the JSON; the table merges overlap without double-counting viewport repetitions.

| Family | Members | Status / severity | Direct evidence and qualification |
| --- | --- | --- | --- |
| Allergy note loss | R17 F01; R46 F01 | Supported, high / P1 | Both arms' coupon PNGs show the entered note and 28/50; address-error PNGs show empty note / 0/50; mobile finals show no store request. R17 adjacent DOM receipts and R46 consolidated observations corroborate the transition. Explicit persistence failure; no real harm or backend omission is claimed. |
| Required part unreachable by keyboard | R17 F02; R46 F02 | Supported, high / P1 | Tab sequences skip part controls; DOM identifies non-focusable DIVs. R17 `b-keyboard-blocked-add.png` plus receipt shows sauce/cola selected, part unset and 23,000-won add still on options. R46 option-focus PNG and DOM notes support unreachable selection, with less direct blocked-task proof. |
| Sauce prices cropped | R17 F03; R46 F04 | Supported, medium / P2 | `R17/b-mobile-sauce-error.png`, `R17/b-short-sauce-selected.png`, `R46/b-missing-sauce.png` and `R46/b-options-short-keyboard.png` visibly crop surcharges at card edges. Desktop labels fit. This is actual painted clipping, not geometry alone. Complete accessible names do not resolve the visual loss. |
| Payment summary overflow | R17 F04 | Supported, medium / P2 | `R17/b-short-payment-bottom.png` crops amounts; `b-short-payment-right-edge.png` reveals amounts while cropping left labels. DOM reports 360px width at a 320px viewport, row right edge 344px. A's corresponding summary fits. The isolated one-item/no-coupon total is correctly 28,000 won; no arithmetic failure is asserted. |
| Missing-sauce feedback | R17 F05; R46 F03 | Supported, medium / P2 | Part and cola selected, sauce unchecked, failed add leaves no new message. R17 receipt and R46 fresh-repeat observation corroborate the PNGs; selecting sauce recovers. Static required labeling gives a partial cue. This is weak rejection feedback, with successful recovery and no bypass claim. |
| Unnamed quantity buttons | R17 F06; R46 F05 | Supported, medium / P2 | Cart PNGs locate minus/plus and show correct quantity changes. R17 accessible snapshot and R46 button inventory establish empty names. PNGs alone cannot prove this finding. Screen-reader speech was not exercised. |
| Coupon correction hint | R46 F06 | Unsupported as a defect; optional suggestion | `R46/b-coupon-error.png` accurately shows a generic message and CPN-4003. `b-checkout-short-payment.png` shows corrected HANKKI5000, 5,000-won discount and 48,000 total. The frozen task supplies the correct code; no failed recovery or required spelling hint is established. No low defect severity is assigned. |

All accepted families concern product B. Product A's sampled final receipts preserve the allergy note, bell delivery request, corrected address and payment. Both arms corroborate a 25,000-won configured item, 50,000-won quantity-two cart and 48,000-won final payment (50,000 + 3,000 - 5,000). B reaches the receipt with the correct money, address, delivery preset and payment, but fails task integrity by losing the allergy note. The address was intentionally empty before validation; filling it afterward proves recovery rather than preservation of a previously entered address.

## Coverage

| Target | R17 | R46 | Strict interpretation |
| --- | --- | --- | --- |
| A/B 384x832 pointer task | Recorded full task, errors, correct amounts and final state; B note loss identified. | Same recorded task and endpoints; B note loss identified. | Full primary-flow coverage is corroborated by state evidence. A passes the scoped outcome; B fails it. Saved captures are not immutable complete event replays. |
| A/B 320x568 | Menu, options/error/selection, cart, coupon/address replay, payment summary, deletion dialog and actual viewport final top/bottom frames. | Menu, option Tab checks, cart, coupon/payment selection, address error and full-page final. | Key-state coverage only in both; neither is an independent full flow at fixed short size. R46's final images are 320x808 and 320x784, so they do not establish 568px fixed-viewport occlusion. |
| A/B 1440x900 | Options, cart, address error, recovered/original final, lower payment summary and deletion overlay. | Options, cart, address error and final. | Key states only; initial desktop menu and invalid-coupon rendering remain gaps. |
| Keyboard | A complete mobile task recorded in `a-keyboard-flow.json` and corroborated by error/final PNGs and receipts; B blocked add captured; short focus cycles. | Option focus-order checks with a consolidated 384px repeat; no full keyboard checkout proof. | R17 demonstrates materially deeper keyboard coverage. Neither establishes physical mobile keyboard or screen-reader behavior. |

R46 misses the supported medium-severity payment-summary family. Its short payment screenshot ends among payment choices and never displays the lower amount summary. R17 misses no supported exclusive R46 family; it already records the coupon-copy observation as unproven. Neither misses the two known high-impact families in the combined finding set. The combined set is not an exhaustive defect oracle.

## Quality comparison

R17 improves meaningful QA in these artifacts with one additional visual defect, lower unsupported rate and broader proof of keyboard and bottom states. No reduction of the frozen-task coverage is demonstrated. This supports a local artifact preference for R17. A task-benefit quality win remains inconclusive because the sample is tiny and does not establish causal attribution or an exhaustive no-critical-miss condition.

R17 discloses an accidental BODY.textContent read returning non-rendered script text and two initial PNGs without adjacent receipts. These qualify procedural quality. The accepted defect evidence is independent of the missing initial receipts: all 67 available PNG receipt hashes match, with zero mismatches; there are 69 PNGs total. R46 supplies 34 PNGs and consolidated DOM/action notes rather than per-capture receipts. Artifact quantity alone is not treated as quality.

## Gaps

No live replay, Figma design source, verified build identity, physical device/OS keyboard, screen-reader application, backend payload, real payment or fulfilment proof. Secondary viewports remain key-state samples. Consolidated action notes support observations but do not prove every input action in an uninterrupted recording.

No compliance mapping is invented. Header/footer scroll-under, partial scrollable navigation and full-page image height are not automatically counted as product defects. Sauce-price clipping and payment-summary overflow are separately confirmed in actual images.

## Risks

High severity reflects the demonstrated synthetic task-data loss and keyboard exclusion. Physical harm, production prevalence, implementation cause and broader accessibility conformance remain unknown. Report/model conditions remain unknown and were not inferred.

Stop condition met: all twelve submitted findings reviewed against PNGs and DOM/trace evidence, seven overlapping/candidate families reconciled, coverage and unresolved proof limits recorded. Only the two assigned judgment artifacts were written.
