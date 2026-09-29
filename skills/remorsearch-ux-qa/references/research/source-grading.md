# Source Grading

This page says how much a source can prove, for which kind of claim, and how a
claim's status is computed. It is used by research mode's audience run
(`references/audience-pipeline.md`), by persona-qa community research, and by
ergonomics Stage 0.

A grade belongs to a pair: one source and one kind of claim. The same forum post
can be good evidence that a situation exists and no evidence at all of how many
users are in it.

`python3 scripts/ux_research.py gate` (planned) applies these rules. The data file
`uxresearch/data/grading.json` (planned) holds the same tables and is keyed by a
rules version. Until the gate ships, apply the rules by hand, keep research claims
`unverified` unless they meet the supported rules in section 7, and label the
report "graded by hand; the gate has not run".

## 1. Claim kinds

| Claim kind | Says | Type |
| --- | --- | --- |
| `segment_exists` | A group of users with shared needs exists | existence |
| `segment_share` | How large a segment is | size |
| `device_mix` | Which devices a segment uses, and in what proportion | size |
| `condition_presence` | A condition (presbyopia, tremor, first use, time pressure) occurs in a segment | existence |
| `condition_share` | What share of a segment has a condition | size |
| `context_of_use` | A segment uses the product in a context, such as walking, on transit, in bright sun or with one hand | existence |
| `task` | A segment does this task with the product | existence |
| `pain_point` | Some users report this difficulty | existence |
| `workaround` | Some users get around a problem this way | existence |
| `product_behavior` | The product does this | product |
| `intended_behavior` | The product is meant to do this | intent |
| `prevalence` | How common an experience is among users | population |
| `user_preference`, `real_user_preference` | What users prefer | population |
| `discomfort` | How many users find something uncomfortable | population |

Use `pain_point` for "some users report X". Keep `discomfort` and the preference
kinds for population claims, which need measured support.

## 2. Source families

The bundle's `source_type` uses the `ergo-audience.v1` source types, plus `news`,
`llm_output` and `synthetic`.

| Family | Source types | What it is |
| --- | --- | --- |
| measured | `product_analytics`, `survey`, `interview`, `usability_test`, `support_tickets` | The team's own data about its users |
| statistical | `official_statistics`, `research_paper` | Population-level data. It bounds a segment; it is not the product's user base. |
| estimate | `market_report`, `competitor` | Estimates from comparable products or markets. State the comparable product and its date. |
| intent | `official_docs`, `product_brief` | What is intended, not what happens |
| voice | `community`, `app_store_reviews` | People who chose to post. Self-selected and skewed toward problems. |
| secondary | `news` | A report of someone else's evidence. Go to the original when you can. |
| expert_judgment | `expert_judgment` | A last resort, labelled as such |
| none | `llm_output`, `synthetic` | Never evidence. Always E. |

## 3. Fit table

Grades:

- **A**: fits the claim kind directly. One A can support the claim.
- **B**: a good fit. It needs another independent unit to support the claim.
- **C**: a partial fit. It can back up a B from another channel family, never lift a
  claim alone.
- **D**: a lead or context. It never counts toward a status.
- **E**: unfit. It must not be cited as support.

Maximum grade for each claim kind and source family:

| Claim kind | measured | statistical | estimate | intent | voice | secondary | expert_judgment |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `segment_exists` | A | B | C | C | B | C | D |
| `segment_share` | A | B | C | E | E | D | E |
| `device_mix` | A | B | C | E | E | D | E |
| `condition_presence` | A | B | C | D | B | C | D |
| `condition_share` | A | B | C | E | E | D | E |
| `context_of_use` | A | C | C | D | B | C | D |
| `task` | A | D | C | C | B | C | D |
| `pain_point` | A | C | C | E | B | C | D |
| `workaround` | A | E | D | D | B | C | D |
| `product_behavior` | D | E | D | D | D | D | D |
| `intended_behavior` | D | E | D | A | D | C | D |
| `prevalence` | A | B | C | E | E | D | E |
| `user_preference` | A | B | C | E | E | D | E |
| `real_user_preference` | A | B | C | E | E | D | E |
| `discomfort` | A | B | C | E | E | D | E |

Notes:

- Statistical sources reach B for shares only as a bound: a population figure limits
  a segment's size, it does not measure the product's users.
- A device named in a post is a device cue. Keep it as a lead for finding measured
  device data, never as `device_mix` support.
- `product_behavior` is confirmed only on the product surface. It needs linked
  product observations (section 7), never sources alone.

## 4. Downgrades

Start from the fit grade, then apply these. Apply the one-grade steps first, then
the caps. A grade never goes below E.

| Condition | Effect |
| --- | --- |
| No publication date | One grade lower |
| Secondhand ("a friend said", "I heard") | One grade lower |
| Unclear context: the task or the situation cannot be told | One grade lower |
| Member-only content from an authorised community (`references/public-page-access.md`, section 3) | One grade lower, because outsiders cannot re-check it |
| Promotion or affiliate disclosure | At most D |
| Snippet, teaser or summarising fetch (a tool that returns model-written text) | At most D |
| Injection flag not yet cleared by a verifier | E |
| The source hit a stop, or it was deleted or withdrawn | E |
| LLM output or a synthetic source | E |
| The same text appears in several sources | Counts once, as one unit, flagged `copypaste` |

Promotion and affiliate disclosures to look for, in the form a disclosure takes:

- Korean: 체험단 (체험단 후기, 체험단으로 참여), 협찬 (#협찬, [협찬], 협찬을 받아),
  원고료 (소정의 원고료를 받아), 제품을 제공받아 (무상으로 제공받아), 업체로부터
  지원받아, 광고 (#광고, [광고], 유료 광고 포함), 쿠팡 파트너스 활동의 일환으로,
  수수료를 제공받, 서포터즈 활동.
- English: sponsored, #ad, paid partnership, affiliate link, "I received this
  product for free", "I may earn a commission".

A word alone is not a disclosure. A review that complains "광고가 너무 많다" (too
many ads in the app) is a user complaint, not promotion. The reader's marker file
(`uxresearch/data/markers.json`) holds the full lists, compiled for this skill.

## 5. Independence

Count independent units, not URLs.

| Unit | One unit is | Used for |
| --- | --- | --- |
| Person | One author key (a salted key, never the handle). On anonymous boards, one thread key per thread. | Voice sources |
| Channel family | One kind of channel, as the route table's `platform_family` names it: blogs (`blog`), forums and communities (`community`), Q&A boards (`qna`), video comments (`video`), app-store reviews (`app_store_reviews`) or microblogs (`microblog`). A source outside the route table uses its source type. | Corroboration across channels |
| Organisation | One registrable domain, with Korean second-level suffixes (`co.kr`, `or.kr`, `go.kr`, `ac.kr`, `ne.kr`, `re.kr`, `pe.kr` and the regional ones such as `seoul.kr`). Blogs hosted by path or subdomain count per author. An explicit `org` value overrides. | Institutional sources: statistics, docs, market reports, news |

Korean examples:

- `blog.naver.com/alice` and `blog.naver.com/bob`: 2 people, 1 channel family
  (`blog`). Counting by organisation alone would wrongly merge them into
  `naver.com`.
- `alice.tistory.com` and a Naver blog author: 2 people, still 1 channel family
  (`blog`).
- A Naver blog author and an App Store reviewer: 2 people, 2 channel families
  (`blog`, `app_store_reviews`).
- A DCInside poster and a Naver Cafe member: 2 people, 1 channel family
  (`community`).
- Five anonymous replies in one DCInside thread: 1 unit, the thread.
- Two news articles that repeat one press release: 1 unit (copy-paste), and news is
  secondary.
- Statistics Korea's site and KOSIS: set `org` to Statistics Korea, so they count
  as one organisation.

Thresholds:

- **Repeated**: 2 or more people.
- **Corroborated**: 2 or more people across 2 or more channel families, or one
  measured or statistical source.
- **Per-person cap**: one author key contributes at most 3 sources or 5 excerpts
  per run. Going over is a process violation (gate exit 1). This stops one loud
  voice from dominating a claim, and it stops the run from profiling a person.

## 6. Neutral denominators for sizes

A size claim (`segment_share`, `device_mix`, `condition_share`, `prevalence`) and a
population claim (`user_preference`, `real_user_preference`, `discomfort`) need a
neutral denominator:

- the product's users, from analytics;
- a sampled population with a stated n, from a survey or official statistics;
- a defined population, from a study.

The people who chose to post are never a denominator. Post counts, review counts,
like counts and the share of posts that mention something are not sizes. A number
from a party with a stake, such as a vendor's own marketing survey, is an estimate
at best. A voice source cited for a size value is a hard error (gate exit 2).

## 7. Statuses

Each independence unit contributes its best grade after downgrades. Only A-C
evidence counts toward a status. D and E evidence may stay on a claim as context:
`gate --write-bundle` (planned) moves it to `context_evidence_ids`.

The first matching row sets the status:

| Status | Rule |
| --- | --- |
| `needs_product_check` | A `product_behavior` claim with no linked product observations. With observed observations from completed runs, the claim is `supported_high`. |
| `unfit` | Every evidence item is E for this claim kind. |
| `lead_only` | Nothing is graded A or B. |
| `stale` | The claim is about the current version and all counting evidence predates the release date (section 10). |
| `conflicting` | Counter evidence, or a counter-search with outcome `contradicts`, and no resolution (section 8). |
| `supported_high` | One A; or B evidence from 2 or more units that is corroborated: the units span 2 or more channel families, or one of the B items is measured or statistical. |
| `supported_medium` | B evidence from 2 or more people in one channel family; or one B plus a C from another channel family. |
| `single_voice` | B-grade support from only one person or thread. |

What each status means downstream:

| Status | Bundle `verification_status` | `ergo-audience.v1` confidence | Use |
| --- | --- | --- | --- |
| `supported_high` | `verified` (epistemic status `observed`) | `high` | May motivate P0/P1 scenarios; exported |
| `supported_medium` | `verified` (epistemic status `observed`) | `medium` | May motivate P0/P1 scenarios; exported |
| `single_voice` | `unverified` | not exported | Exploratory scenarios only |
| `lead_only` | `unverified` | not exported | Exploratory only; read the sources first |
| `conflicting` | `unverified` | not exported | Report both sides in the annex |
| `needs_product_check` | `unverified` | not exported | Becomes a persona-qa scenario |
| `stale` | `unverified` | not exported | Research again for the current version |
| `unfit` | `unverified` | not exported | Find another source family |

Evidence kind in `ergo-audience.v1`:

| Source | `evidence[].kind` |
| --- | --- |
| voice | `firsthand` |
| measured: `product_analytics`, `survey` | `statistic` |
| measured: `interview`, `usability_test`, `support_tickets` | `firsthand` |
| statistical | `statistic` |
| estimate | `statistic` when the quote carries the number, otherwise `inference` |
| intent | `official` |
| expert_judgment | `inference` |
| secondary (`news`) | Not exported until the ergonomics contract accepts `news` |

Share basis in `ergo-audience.v1`:

| Supported share claim from | `share.basis` |
| --- | --- |
| measured | `measured` |
| statistical or estimate | `estimated` |
| no supported share claim | `unknown`, with `share.value` null |

Voice sources never set a share, a condition share or a device weight.

## 8. Counter-search

A counter-search looks for evidence against a claim before the claim is used. It is
required for:

- claims about primary segments;
- claims with `stakes: high`;
- any claim that sets a share value;
- claims that motivate P0 or P1 scenarios.

Record it on the claim:

```json
{
  "counter_search": {
    "query": "[product] 편해요",
    "lang": "ko",
    "tool": "web_search",
    "read_source_ids": ["SRC-1a2b3c4d"],
    "summary": "Two reviewers say the flow is fine on large phones.",
    "outcome": "qualifies"
  }
}
```

- `outcome` is `none_found`, `qualifies` (the claim holds only for some users,
  versions or contexts) or `contradicts`.
- Every source in `read_source_ids` must be registered in the bundle, read through
  the reader. Unregistered URLs are a hard error (gate exit 2).
- `contradicts` makes the claim `conflicting` unless `counter_search.resolution`
  explains the difference, such as another version or another segment.
- A missing counter-search where one is required is a process violation (gate
  exit 1).
- Useful counter queries: [product] 편해요, 만족, 문제없음, 잘 돼요; "[product] works
  fine", "no problems".

## 9. Per-person cap

One author key contributes at most 3 sources or 5 excerpts per run. Section 5
explains why. When a person has more to say, keep the clearest excerpts and note
the rest as context.

## 10. Time

| Field | Meaning | From |
| --- | --- | --- |
| `published_at` | When the author published | The page. Null when unknown, which costs one grade. |
| `observed_at` | When the reader read it | The run ledger |
| `valid_at` | When the content was true: the product version or period it describes, or an archive capture's date | The page or the claim |

A claim about the current product sets `about_current_version: true`. When all of
its counting evidence predates the brief's `release_date` (or the date of the
current version), the status is `stale`. Reports show `observed_at` and
`valid_at` next to each piece of evidence.

## 11. The gate

`python3 scripts/ux_research.py gate` (planned) computes every claim's status.
Agents never write a status themselves.

| Exit | Meaning | Examples |
| --- | --- | --- |
| 0 | Pass | `gate.json` is written and any old `gate_failed.json` is removed. |
| 1 | Process violation | A required counter-search is missing; an excerpt is over 300 characters; personal data is left after scrubbing; the per-person cap is exceeded. |
| 2 | Hard error | A voice source supports a size value; a stopped, lead-only, LLM or synthetic source supports a verified claim or an exported value; counter-search URLs are not registered sources; a reference is broken. |

- On exit 1 or 2 the gate deletes `gate.json` and writes `gate_failed.json` with
  the exit code, the kind of failure, the reasons and the next step.
- `gate.json` (`schemas/ux-research-gate.v1.schema.json`, planned) records the
  rules version, process violations, warnings, a count per status, and for each
  claim its status, grade, units, channel families, organisations, reasons, a hash
  of its inputs (`input_sha256`), and the `ergo-audience.v1` mapping (confidence,
  evidence kind, share basis).
- `gate --write-bundle` is the only writer of `verification_status` for research
  claims. It sets supported claims to `verified` and the rest to `unverified`, and
  it moves evidence that did not count to `context_evidence_ids`, so every
  `evidence_ids` entry of a verified claim is eligible support. The result passes
  `scripts/validate_bundle.py`.
- The data-flow lock: `export-audience` and `report-check` (planned) refuse to run
  without `gate.json`, or when a claim's input hash no longer matches the bundle.
  A change to one record invalidates only the claims that use it.
- A pass certifies process and referential integrity, not truth. The thresholds
  (2 people, 2 channel families, 300 characters) are research judgment, and
  `gate.json` records the rules version they came from.

`report-check` (planned) then checks the report body. A heading is an annex when it
contains one of the annex terms below; its sub-headings stay in the annex until a
heading of the same or a higher level. Claim IDs that are not supported may appear
only inside an annex. Unknown claim IDs fail as phantom citations. A warning follows
when fewer than half of the supported claims are cited.

## 12. Vocabulary

Shared by the gate, the bundle and the reports. The contract test (planned) checks
that code and data use the same lists.

```text
claim kinds: segment_exists, segment_share, device_mix, condition_presence, condition_share, context_of_use, task, pain_point, workaround, product_behavior, intended_behavior, prevalence, user_preference, real_user_preference, discomfort
source families: measured, statistical, estimate, intent, voice, secondary, expert_judgment
grades: A, B, C, D, E
statuses: supported_high, supported_medium, single_voice, lead_only, conflicting, needs_product_check, stale, unfit
counter-search outcomes: none_found, qualifies, contradicts
annex terms: 미확정, 확인 필요, 부록, Unresolved, Unverified, Annex, Appendix, Next evidence needed
```

## 13. Credit

The gate's design comes from studying insane-research
(github.com/fivetaku/insane-research, MIT License, Copyright (c) 2026 fivetaku):
claim status computed by code rather than written by an agent, a data-flow lock
between the gate and the report, independence counting, time validity, and a report
gate with an annex. No code or text was copied. Two things were changed on purpose.
Grades depend on the claim kind, so community posts can support existence claims
instead of being set aside as uncitable. And people, not only organisations, are
the independence unit, because one portal hosts many independent authors.
