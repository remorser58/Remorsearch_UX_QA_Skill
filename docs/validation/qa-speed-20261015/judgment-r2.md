# BlindQA adjudication r2

## Verdict

**PARTIAL.** W18 and W77 pass the quality floor. W31 fails because one core viewport behavior is unverified.

## Evidence

The six core areas were final-value integrity, allergy-note preservation, required-part keyboard access, omitted-sauce recovery feedback, mobile sauce-price clipping, and 320px payment-summary overflow.

- **W31 — FAIL.** Seven raw cards normalize to six defect families plus one coupon-wording suggestion. `evidence.json` and `observations.json` give strong screenshot, DOM, and keyboard-trace support. The 25,000원 item, quantity 2, 50,000원 subtotal, 5,000원 discount, 3,000원 delivery, and 48,000원 final payment are evidenced. The allergy note loss, keyboard block, omitted-sauce silence, sauce clipping, unnamed quantity controls, and address-error semantics are supported. Payment-overflow coverage is missing, and omitted-sauce validation was not separately run at desktop.

- **W18 — PASS, with a carding gap.** Four raw cards cover note loss, required-part keyboard access, sauce clipping, and payment overflow. The omitted-sauce silent rejection is recorded in `recovery_observations` and visible in screenshots, so the core behavior is covered, but it is not promoted to a finding card. The inline `priority_receipts` tab sequence plus `b-keyboard-recheck.png` directly support the required-part keyboard claim, although the trace is stored inside the report JSON. Final values and the note-loss transition are directly visible.

- **W77 — PASS.** Five raw cards normalize to six defect families: F2 splits into required-part keyboard access and unnamed quantity controls; F4 splits into sauce clipping and payment overflow. Screenshots plus `accessible-dom-evidence.json` directly support the state transitions, keyboard sequence, omitted-sauce behavior, and 320px geometry. The B final screen proves the initial allergy-note failure; the separate recovery capture proves re-entry restores it.

Coupon typo wording is suggestion-only in W31 and W77; correction works and the 5,000원 discount is applied. It is not counted as a core defect.

## Gaps

The scope is one known synthetic A/B fixture pair with repeated rendered Chromium runs. W31 needs a 320px payment-summary capture and desktop omitted-sauce evidence. W18 should add a distinct card for the observed omitted-sauce recovery failure. W77’s combined cards should be split for triage clarity.

## Risks

No source cause, backend persistence, Figma fidelity, real-device or screen-reader behavior, alternate browser behavior, independent review, or real allergy/payment outcome is proven.
