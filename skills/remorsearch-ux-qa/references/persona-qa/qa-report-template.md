# UX QA Report Template

## Scope

- Product or URL:
- Surface:
- Run date:
- Mode:
- Browser, viewport, and input:
- Tools available and used (browser tools by class, the reader, search tools) and fallbacks:
- Figma URL and version:
- Data mutation permission:
- Unavailable surfaces:

### Reader access table

For community research (`references/research/public-page-access.md`, sections 6 and 16). One row per host or channel.

| Host or channel | Tools | Reads | Rungs used | Stops by class | Unread (untried rungs) | robots / TDM decision | Browser context |
| --- | --- | --- | --- | --- | --- | --- | --- |

- Engine rung R4: off / on (version)
- Search count / budget:
- Signed-in communities authorised in the brief: none / list

## Executive result

Summarize the most consequential verified finding, its root cause, and the highest-value remediation.

## Scenario matrix

| ID | Persona basis or audience ref | Task | Context | Device/input | Claim IDs | Expected outcome | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Community evidence

Grade and gate status come from research mode's gate (`references/research/source-grading.md`). Cite community sources by channel, date and source ID, not by URL.

| Evidence ID | Claim ID | Channel | Date | User situation | Signal | Grade | Gate status | Access (rung or stop) | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Findings

| ID | Severity | Confidence | Area | Short finding | Verified in product | Figma mismatch |
| --- | --- | --- | --- | --- | --- | --- |

For each finding, include the complete format from `references/evidence-and-severity.md`.

## Causal analysis

Complete the causal chain for every P0 or P1 finding. Keep official constraints, product observations, community signals, and inferences distinct.

## Recommendations

| Finding | Fix layer | Change | Expected behavior change | Trade-off | Priority |
| --- | --- | --- | --- | --- | --- |

## Figma comparison

- File URL:
- Version/readback:
- Relevant pages and node IDs:
- Matched flows:
- Mismatched flows:
- Missing states:
- Token or component drift:
- Accessibility drift:

## Validation and regression

- Original scenario rerun:
- Happy path:
- Empty state:
- Error and recovery:
- Permission state:
- Responsive:
- Keyboard or assistive technology:
- New regressions:
- Remaining unknowns:

## Unverified claims and next evidence needed

Community claims that are not gate-supported (`single_voice`, `lead_only`, `conflicting`, `stale`, `needs_product_check`, `unfit`) and findings that are not verified go here, and only here, with the evidence needed next. This heading is an annex for `report-check` (planned).

| ID | Statement | Status | Next evidence needed |
| --- | --- | --- | --- |

## Coverage statement

State what was checked, which tools were used, what was stopped (by class), which public pages stayed unread and which rungs were untried, what was not reproduced, and which conclusions remain hypotheses.
