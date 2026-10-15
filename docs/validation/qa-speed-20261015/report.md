# QA speed and quality evaluation

2026-10-15. The instruction-only speed candidate was rejected after a matched GPT-6.1 Sol high comparison. The change did not alter the runtime, fixtures, detector or dependencies.

## Result

| Measure | Previous skill | Candidate | Change |
| --- | ---: | ---: | ---: |
| Report-save median, two valid repetitions | 11.54 min | 12.02 min | +4.1% |
| Final assistant median, two valid repetitions | 12.43 min | 12.62 min | +1.5% |

The candidate was slower in both measures. Its first repetition produced a complete quality report, but the second report contained four finding cards and omitted two previously corroborated families: missing-sauce recovery feedback and unnamed quantity controls. The candidate fails the quality floor and is not merged. The two instruction files were restored to the last accepted commit.

The ordinary OMO arm is a separate baseline. It is not used to claim a causal skill speedup. The InferHub GLM 5.3 high retry failed with provider 502 before any QA tool call and receives no score. Interrupted runs, server-unavailable runs and provider failures stay in the archive.

## Open-source claims

The supported public story is evidence-backed rendered QA: one installable package, four bundled components, screenshot-linked findings, final-value preservation, keyboard and recovery checks, and explicit uncertainty. The data does not support a faster-QA headline. Do not publish speed, cost, production-readiness, human-preference or accessibility-certification claims from this study.

[Machine-readable summary](verification.json), [timing records](accounting-r1.json), [second repetition records](accounting-r2.json), [blind quality judgment](judgment-r1.md), [second repetition judgment](judgment-r2.md), [GLM failure record](glm-retry.json), and [earlier interrupted/invalid run records](interruption.json).


The second repetition judgment records the same quality boundary: W18 and W77 passed the core coverage, while W31 lacked 320px payment evidence. The candidate remained unaccepted.
