# Stage 0: Audience Research

Before any persona exists, find out **who uses the product under test**. The
output is one `ergo-audience.v1` file (contract: repository `docs/ergonomic-swarm-spec.md`
section 13). Personas are then composed from it with `ergo_qa.py personas
--audience`, so every persona can be traced to a segment and to the evidence
behind it. Nothing is sampled at random.

## Why not random personas

On the development suites, a stratified set of 14 profiles per device found as
many seeded defects (0.91 strict recall) as a random draw of 40, and with less
noise. At 8 profiles the numbers were 0.87 (stratified) against 0.79
(random). Source: `docs/validation/experiments/ablation-dev-8707b70.json`.
Composition decides what the swarm can find. Audience research decides which
compositions matter for this product.

## Questions Stage 0 must answer

Frame the answers with ISO 9241-11 context of use: users, goals and tasks,
resources, environment.

1. **Segments.** Who buys or uses the product, and in which groups whose needs
   differ: age, digital familiarity, abilities, devices, contexts. Name each
   group by what they do ("출퇴근 중 충전하는 직장인"), not by demographics alone.
2. **Weight.** How large each group is. Use `share` with its `basis`: measured
   (analytics, a survey with n), estimated (market data, a comparable product),
   or unknown. Unknown is a valid answer; do not invent a number.
3. **Priority.**
   - `primary`: the product is built for them.
   - `secondary`: they use it regularly.
   - `edge`: a small group for whom failure is costly or exclusionary, such as
     low vision, tremor or first-time older users of a public-service app.
4. **Devices and grips.** Which phones, tablets or desktops, and how they are
   held. Default grip mix and left-handedness come from `ergoqa/params.py`.
   Override them only with evidence.
5. **Abilities and conditions.** Presbyopia, low vision, colour-vision
   deficiency, tremor, first use, time pressure, hand size. Give the share inside
   the segment when known. Mark `stakes: high` when a failure costs money, health,
   legal standing or access.
6. **Contexts of use.** Seated, standing, walking or on transit; indoor, bright
   sun or dark; one hand free or both; interruptions.
7. **Key tasks with concrete data.** The jobs the segment hires the product
   for, written as JTBD ("When …, I want to …, so I can …"), with frequency,
   criticality and the exact values an agent will type or pick (amounts, dates,
   names, menu options). Tasks without data leave branches untested.
8. **Known pain points.** What these users already complain about. These become
   hypotheses to check on the real screen, not findings.

## Evidence sources, in order of preference

| Source type (`sources[].type`) | Use for | Caveat |
| --- | --- | --- |
| `product_analytics`, `survey`, `interview`, `usability_test`, `support_tickets` | Real segment sizes, devices, tasks, failures | Best evidence. Ask the team; cite version and date. |
| `official_statistics` | Age/sex structure, disability, digital divide. Korean sources: 행정안전부 주민등록 인구, KOSIS, 과기정통부·NIA 디지털정보격차 실태조사, 방송통신위원회 방송매체 이용행태조사, 보건복지부 장애인 실태조사, 한국콘텐츠진흥원 게임이용자 실태조사 | Population-level. It bounds a segment; it is not the product's user base. |
| `app_store_reviews`, `community` | Who complains, in which context, about what. Use the research mode (`references/research/workflow.md`) for public communities. | Self-selected and skewed toward problems. Firsthand quotes support existence, never size. |
| `competitor`, `market_report` | Audience of comparable products, device mix | Estimated; state the comparable product and its date. |
| `official_docs`, `product_brief` | Intended users, legal duties (accessibility law, 전자상거래법) | Intent, not evidence of actual use. |
| `research_paper` | Condition effects and prevalence (CVD, presbyopia, handedness) | Check the country and year. |
| `expert_judgment` | Last resort, labelled as such | Low confidence. |

Rules:

- Every segment has at least one evidence item. Every share, condition,
  context and task cites a `source_id`.
- Keep `firsthand` (a user said it), `statistic`, `official` and `inference`
  apart. An inference never becomes a statistic by repetition.
- Record access dates. Community sources keep their access basis and public
  scope, as in the evidence-bundle contract.
- Synthetic personas and LLM output are **never** sources for the audience file.

## Workflow

1. Read the product (brief, store listing, website, onboarding) and list the
   candidate groups and tasks.
2. Search official statistics for size bounds, reviews and communities for
   contexts and pain points, and comparable products for device mix. Ask the
   team for analytics before estimating.
3. Write `audience.json`. Validate it:
   `python3 scripts/ergo_qa.py audience-check audience.json`.
4. Compose personas under a budget, and read the plan:
   `python3 scripts/ergo_qa.py personas --audience audience.json --budget 12 --plan work/persona-plan.md --out work/profiles.json`
5. Write scenarios from the key tasks:
   `python3 scripts/ergo_qa.py scenario-stubs --audience audience.json --out scenarios/`.
   Fill in the URL, roles, steps and timing windows.
6. Report which segments, facets and floors the budget did not reach (the
   `untested` list). Those are untested, not "fine".

## How composition uses the file

See spec section 13 for the exact rules.

- Each segment gets one **typical member**: modal age, top device, dominant
  grip, modal context, and every condition shared by at least half the segment.
- Extra profiles go to segments by weight (D'Hondt). Each varies **one facet**:
  a minority condition, the left-hand mirror, another device, a context, first
  use, another age band or another grip. Changing one thing at a time keeps
  "which condition caused this finding" answerable.
- **Inclusive floors** are coverage guarantees for conditions whose removal
  lost unique defects in at least two of the three development suites: a
  left-hand profile per input kind, deuteranomaly, presbyopia, and walking (touch
  devices). They attach to the most plausible segment and are labelled as
  floors, not as segment evidence. Change them with `floors` in the file or
  `--floors` on the command line.
- Segment weights steer allocation only. The report states, per finding, which
  segments' profiles triggered it (`segments_affected`), never what share of
  users is affected.

## What this stage does not do

- It does not prove how many users are affected by a finding. That needs
  analytics or a study with real users.
- It does not replace usability testing with real people from the segments,
  especially edge segments.
- It does not simulate assistive technology (screen readers, switch access).
  Record such users in `exclusions` and test them separately.
