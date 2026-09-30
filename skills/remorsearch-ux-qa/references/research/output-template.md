# Output Template

For a report in Korean (`report_lang: ko`), use `references/research/korea/report-template.md`: the same sections, with Korean headings and style rules.

Use this structure for a deep research result. Keep the prose compact. Link official and product sources to their original location when the environment provides a usable link. Reports shared outside the team cite community sources by channel, date and source ID (for example `kr-communities, 2026-08-14, SRC-1a2b3c4d`), not by URL; post URLs stay in the bundle's `source_ref`.

## Research boundary

- Product and surface:
- Research date:
- Tools available and used (browser tools by class, the reader, search tools) and fallbacks:
- Search count / budget:
- Channels checked:
- Official sources checked:
- Time windows:
- User segments:
- Signed-in communities authorised in the brief: none / list
- Terms checks the user recorded in the brief: none / list (host, terms URL, checked on, result)
- Ethics review: none / exempt / approved / pending
- Official APIs used (route, calls, quota units, earliest `retention_until`): none / list
- Model provider and processing region, and whether its terms exclude storage and training: (write "unknown" if unknown)
- User groups the public web under-covers:
- Unread after allowed rungs (with untried rungs):
- Stopped by access control or opt-out (by class, `terms_restricted` apart):
- Coverage limitation:

### Reader access table

One row per host or channel (`references/public-page-access.md`, sections 6 and 15).

| Host or channel | Tools | Reads | Rungs used | Stops by class (terms_restricted apart) | Terms restricted | Unread (untried rungs) | robots / TDM decision | Browser context |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

### Coverage gaps

One row per stop class, plus one for missing keys. Write 0 when no URL ended that way.

| Stop class | Hosts or channels | URLs | Reason codes | Next step |
| --- | --- | --- | --- | --- |
| `terms_restricted` | | | | None. A `confirmed` entry is never lifted; a `reported` one only when the user reads the terms and records the check in the brief. |
| `opted_out` | | | | None |
| `auth_gate` | | | | None. Only communities the user authorised in the brief, as summaries. |
| `paywall` | | | | None |
| `human_check` | | | | None |
| `rate_limit` | | | | None. The host stays stopped for this run. |
| `geo_block` | | | | None |
| `legal_block` | | | | None |
| `gone` | | | | None. Never recovered from an archive or a cache. |
| `budget` | | | | Raise within the ceiling, with a recorded reason. A host whose terms restriction was lifted keeps 10. |
| `host_stopped` | | | | None. The host is closed for this run. |
| Key missing | | | `official_route_needs_key` | Ask the user to set the key. Never read the page another way. |

Fill the gaps from other channel families, the team's own data, surveys and interviews. Never fetch what a stop withheld by another route.

### Out of scope

| Kind | Hosts or channels | URLs |
| --- | --- | --- |
| Private channels (`out_of_scope`) | | |
| Search results pages (refused, or stopped on a redirect) | | |
| Switched-off discovery routes (refused) | | |

## Executive finding

State the central UX problem, the most likely root cause, and the highest-value proposal in three short paragraphs.

## Audience segments

Include when the run answered who the users are (`references/audience-pipeline.md`). Shares come only from measured or statistical sources; otherwise write `unknown`.

| Segment | Priority | Share and basis | Confidence | Supporting claim IDs | Key contexts, tasks and pains | Exclusions | Untested |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Evidence map

| ID | Claim ID | User segment | Task and situation | Observed friction | Source (channel, date, source ID) | Evidence type | Grade | Status | Published / observed / valid at | Recurrence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Grade and status come from the gate (`references/source-grading.md`). Until the gate ships, write "graded by hand" next to the table. The label is `observed`, `inferred` or `unknown`. An item read through an official API also shows its `retention_until`, and it is deleted by then. Never restore a scrub placeholder such as `[phone]` in a quote. A community's modelled gender, age or political lean is never attributed to a poster, a claim or a persona.

## Causal analysis

For each priority issue:

```text
Observed situation:
Direct friction:
Immediate behavior:
Structural cause:
Organizational or business constraint:
User outcome:
Possible product outcome:
Counterevidence:
Claim IDs:
Confidence:
```

## UX proposal

For each proposal:

```text
Problem addressed:
Change:
Design layer: copy / interaction / information architecture / service rule / data system
Intended behavior change:
Expected benefit:
Trade-off:
Priority:
Validation:
```

## Figma handoff

- File URL:
- Version or readback:
- Relevant pages and node IDs:
- User flow:
- Component and token decisions:
- States covered:
- Responsive behavior:
- Accessibility behavior:
- Implementation acceptance criteria:

If Figma evidence is unavailable, write `blocked` and state the concrete reason.

## Validation plan

- Happy path:
- Empty state:
- Error and recovery:
- Permission state:
- Mobile:
- Keyboard or assistive technology:
- Measurement:
- Open question:

## 미확정 / Unresolved (annex)

Claims that are not supported go here, and only here: `single_voice`, `lead_only`, `conflicting`, `stale`, `needs_product_check` and `unfit`. For each, give the claim ID, its status, and the evidence needed next. `ux_research.py report-check` (planned) fails a report that cites such a claim outside a heading that contains an annex term: 미확정, 확인 필요, 부록, Unresolved, Unverified, Annex, Appendix or Next evidence needed.

| Claim ID | Statement | Status | Why not supported | Next evidence needed |
| --- | --- | --- | --- | --- |

### Items for counsel

Legal questions this run could not settle, such as whether leaving out authors' names fits a duty to name the source. For Korean law, see `references/research/korea/legal-checklist.md`. This report is not legal advice.

| Item | Provision and version | Default in this run |
| --- | --- | --- |
