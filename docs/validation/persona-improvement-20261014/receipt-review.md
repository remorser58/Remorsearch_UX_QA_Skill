Both reports contain supported core findings from the same completed recording. T73 matches four seed families; T14 matches five. Their nine per-report credits cover five distinct defects in one case.

| Count | T73 | T14 |
| --- | ---: | ---: |
| Raw findings / unique seeded matches | 4 / 4 | 5 / 5 |
| Unique supported extras | 0 | 0 |
| Unsupported core findings | 0 | 0 |
| Core false positives | 0 | 0 |
| Within-report duplicates | 0 | 0 |
| Withheld hypotheses excluded | 4 | 7 |
| Missing citations | 0 | 0 |

Below, Sxxx refers to recording/S-P1-page1-xxx; source lines refer to frozen delivery-b.html.

| Finding | Seed and direct support |
| --- | --- |
| T73 F1: part semantics | D-delivery-02. S004/S007.json contain generic DIV choices with a11y=null; step 2 clicks one. Source :280–287/:591–597 exposes no radio state, tabindex or part keyboard path. Visible text/content names do exist; keyboard/AT behavior was not recorded. |
| T73 F2: quantity names | D-delivery-06. S010/S011.json show empty button names. At quantity 2 both buttons are enabled, still unnamed; source :643–650 renders aria-hidden glyphs only. Both buttons count once. |
| T73 F3: extra-row activation | D-delivery-04. Steps 5–6 show text no-op then native checkbox activation. S005/S006 elements and PNG hashes match; S007.png shows the successful check. Source :187/:301/:606 confirms the 18px input and non-label row. |
| T73 F4: coupon guidance | D-delivery-08. S018.png/json shows generic CPN-4003 rejection; S020.json and steps 16–19 confirm correction and 48,000. Source :819/:832 ignores the failure reason. Human unaided typo recognition is not demonstrated. |
| T14 F1: extra-row activation | D-delivery-04, supported by the same raw steps/captures and source. The 18×18 CSS box is measured; 3.3mm is a catalog-derived estimate, not a physical measurement. P1 escalation beyond key minimum P2 lacks observed blockage/physical impact. |
| T14 F2: part semantics | D-delivery-02. S002/S003/S006.json and source :284–285/:591–597 support the missing control contract. Source :63 and captured font weight also show bolding, so “only color and border” is imprecise. P1 matches the key minimum. |
| T14 F3: quantity names | D-delivery-06. S011.json shows both enabled buttons unnamed, confirmed by source :643–650. Only the plus has a recorded 10×10 paint box; the minus measurement is unsupported. P1 elevation above key P2 is not established by this touch recording. |
| T14 F4: sauce clipping | D-delivery-03. S006.json shows hot 111.77/88.98 and garlic 115.72/89.98 full/visible widths; S004/S006.css.png show truncated prices. Source :183–185 clips the chips. Clipping exists before selection, but its extent changes. P2 exceeds key minimum P3 as a priority judgment; no financial harm is observed. |
| T14 F5: coupon guidance | D-delivery-08. S018.css.png/json, S020.json and source :819/:832 support the generic error and corrected success. Both coupon findings report P3 below key minimum P2. Their guidance assessment is supported; confusion/support-contact effects are untested. |

The part names are generic content names, not selectable-control semantics. Quantity names are DOM measurements, not recorded speech. The extra-row persona note is anchored to step 22/pay rather than the earlier row tap, so it provides no independent corroboration. Those qualifications preserve the supported core findings. Unsupported estimates, factual imprecision and severity grounds are flagged separately; withheld hypotheses receive no false-positive penalty.

Shared-case integrity passes: all 78 receipt entries match, with 24 snapshot PNGs, 24 CSS derivatives and matching dimensions. Final S023.png/json confirms menu/options, quantity 2, exact allergy note, detail address, no utensils, Dongne Pay and 48,000. This is one completed recording reviewed twice. The receipt inventory remains in receipts.json.

Auxiliary analysis is candidate data only. The user-declared common 15-minute limit does not turn this into a live-persona or full-skill performance result. No physical/assistive session, new UI action, alternate case, method assignment or causal method comparison was inspected. All submitted findings are adjudicated.
