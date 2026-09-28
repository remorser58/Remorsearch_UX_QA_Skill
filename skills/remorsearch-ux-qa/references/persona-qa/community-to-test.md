# Community Signal to Test

## Conversion chain

```text
Gate claim ID (pain_point, workaround or context_of_use)
→ community statement (scrubbed excerpt, with its grade and status)
→ user situation
→ task or decision
→ suspected friction
→ browser scenario
→ verified observation
→ UX finding
```

Start from a claim that research mode's gate has graded (`references/research/source-grading.md`). A `supported_high` or `supported_medium` claim may motivate a P0/P1 scenario. A `single_voice` or `lead_only` claim gives an exploratory scenario only. Until the gate ships, grade by hand and label the claim "graded by hand".

## Example

The IDs below are illustrative.

```text
Claim:
CLM-4e1b20c9 (pain_point), supported_medium: two people in one channel family.

Community statement (EV-7d3a5b12, grade B, read by the reader at R2, ok_strong):
“상세 페이지를 보고 돌아오면 검색 조건을 다시 넣어야 한다.”

User situation:
The user compares several results under a price and delivery filter.

Task:
Select one result after checking details.

Suspected friction:
List state is lost during list-detail navigation.

Browser scenario:
Apply a filter, open two details, return through browser back, and inspect
filter, sort, scroll position, and result order. The scenario cites CLM-4e1b20c9.

Verified observation:
Record which state was preserved and which state was reset.

UX finding:
State loss is a P1 issue only if it blocks or materially slows the task.
Otherwise classify it as P2 friction.
```

## Community source checklist

- Is this firsthand or secondhand?
- Is the task and context clear?
- Is the product version or date known?
- How was the page read: which tool, which rung, which verdict? Was anything stopped?
- Does the same issue appear in another channel?
- Does corroboration come from other people and other channel families, not from other URLs on one host?
- Is the claim `single_voice` or `lead_only`? Then the scenario is exploratory only.
- Is the post promotional, coordinated, or emotionally amplified?
- Is there a counterexample?
- Can the scenario be reproduced in the actual product?

## Search channel roles

Reader routes and stops are starting points. Verify them live (`references/research/public-page-access.md`, channel notes).

| Channel | What it shows | Reader route | Typical stop |
| --- | --- | --- | --- |
| YouTube comments | Natural language, immediate reactions, setup and expectation gaps | R0 Data API with the user's key, or R3 render (first comments only) | Usually none; long threads are only partly read |
| DC Inside and open forums | Strong dissatisfaction, workarounds, edge cases, and version reactions | R2 mobile twin | `human_check` or `rate_limit` on busy boards |
| Naver Cafes | Focused user groups, local context, recurring practical workflows | R2 mobile twin or R3, public boards only | `auth_gate` on member-only boards, unless the user authorised that cafe |
| Reddit and product forums | Expert workflows, comparisons, shortcuts, and migration reasons | R0 `.rss` feeds | `rate_limit`; robots.txt opt-outs |
| App reviews | Onboarding, reliability, permissions, crashes, and broad sentiment | R0 App Store reviews feed; Google Play R3 or the team's export | Google Play renders show only the first reviews |
| Support and policy pages | Intended behavior, limits, and recovery paths | R1 | Rarely any |

No channel represents all users. Use channel differences as part of the finding.
