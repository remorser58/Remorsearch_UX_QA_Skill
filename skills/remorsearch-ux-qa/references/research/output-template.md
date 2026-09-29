# Output Template

Use this structure for a deep research result. Keep the prose compact. Link official and product sources to their original location when the environment provides a usable link. Reports shared outside the team cite community sources by channel, date and source ID (for example `kr-communities, 2026-08-14, SRC-1a2b3c4d`), not by URL; post URLs stay in the bundle's `source_ref`.

## Research boundary

- Product and surface:
- Research date:
- Tools available and used (browser tools by class, the reader, search tools) and fallbacks:
- Engine rung R4: off / on (version)
- Search count / budget:
- Channels checked:
- Official sources checked:
- Time windows:
- User segments:
- Signed-in communities authorised in the brief: none / list
- Unread after allowed rungs (with untried rungs):
- Stopped by access control or opt-out (by class):
- Coverage limitation:

### Reader access table

One row per host or channel (`references/public-page-access.md`, sections 6 and 16).

| Host or channel | Tools | Reads | Rungs used | Stops by class | Unread (untried rungs) | robots / TDM decision | Browser context |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Executive finding

State the central UX problem, the most likely root cause, and the highest-value proposal in three short paragraphs.

## Audience segments

Include when the run answered who the users are (`references/audience-pipeline.md`). Shares come only from measured or statistical sources; otherwise write `unknown`.

| Segment | Priority | Share and basis | Confidence | Supporting claim IDs | Key contexts, tasks and pains | Exclusions | Untested |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Evidence map

| ID | Claim ID | User segment | Task and situation | Observed friction | Source (channel, date, source ID) | Evidence type | Grade | Status | Observed at / valid at | Recurrence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Grade and status come from the gate (`references/source-grading.md`). Until the gate ships, write "graded by hand" next to the table.

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
