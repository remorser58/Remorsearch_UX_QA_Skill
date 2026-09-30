# UX QA Report Template

For a report written in Korean, use the headings, style rules and tables of `references/research/korea/report-template.md` where it has them (scope, access table, coverage gaps, out of scope, evidence map, cause analysis, recommendations, Figma handoff, verification plan, and the appendix "미확정 / 확인 필요 (부록)"). Translate the scenario matrix, the findings table and the coverage statement with its glossary (section 1.6).

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
- Accessibility standards: KWCAG 2.2 items and WCAG 2.2 success criteria, reported apart (`references/persona-qa/kwcag-2.2.md`); WCAG 2.2 only when the product is not Korean:
- Verification gates not passed and left untested (본인인증, 인증번호, CAPTCHA, payment):

### Reader access table

For community research (`references/research/public-page-access.md`, sections 6 and 15). One row per host or channel.

| Host or channel | Tools | Reads | Rungs used | Stops by class (terms_restricted apart) | Terms restricted | Unread (untried rungs) | robots / TDM decision | Browser context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

- Search count / budget:
- Signed-in communities authorised in the brief: none / list
- Terms checks the user recorded in the brief (`access_policy.terms_checked`): none / list (host, terms_url, checked_on, result)
- Official APIs used with the user's key (route, calls, quota units, earliest `retention_until`): none / list
- Keys missing: none / list (environment variable and the routes that need it)

Show `terms_restricted` stops apart from the other stop classes. Count private channels, search results pages and switched-off discovery routes as out of scope, not as coverage gaps. A missing key for an official route (`official_route_needs_key:<ENV>`) is a coverage gap and a question to the user; the page is not read another way instead.

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

| ID | Severity | Confidence | Area | Short finding | Verified in product | Figma mismatch | KWCAG 2.2 item | WCAG 2.2 SC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

For each finding, include the complete format from `references/evidence-and-severity.md`.

The last two columns are for accessibility findings. They are required on a Korean product and optional elsewhere (then use the WCAG column only). Fill each column on its own: the KWCAG 2.2 numbering (chapters 5 to 8) and the WCAG 2.2 numbering (chapters 1 to 4) differ, and a pass on one is not a pass on the other. Write one of these in a cell:

- the number and title, for example `6.2.1 응답시간 조절` or `2.2.1 Timing Adjustable`;
- `없음(대응 항목 없음)`, when the standard has no counterpart item;
- `일부` with the reason;
- `미검사`, when the step was a stop or outside the tools;
- `미확인`, when the item number or title was not checked against the official text.

Never join two numbers in one cell (5.4.3/1.4.3), never fill one column from the other's result, and write the repository check ID (for example PC-01) in the evidence, not in the standard's column. Severity comes from user and product impact, not from the standard's level. Write "a failure under KWCAG 2.2 6.1.1 and WCAG 2.2 SC 2.1.1 was observed on this screen", not "compliant" or "violates the law" (`references/persona-qa/kwcag-2.2.md`, section 7).

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

State what was checked, which tools were used, what was stopped (by class), which public pages stayed unread and which rungs were untried, what was not reproduced, and which conclusions remain hypotheses. On a Korean product, add the accessibility coverage statement of `references/persona-qa/kwcag-2.2.md` (section 7) and list every identity or payment step that was not passed as untested. The results are coverage of this screen under these conditions, not a share of users and not a finding of legal compliance.
