# Skill-on versus skill-off: bounded pilot

2026-10-14. Remorsearch found more seeded issues in this small test and completed one more assigned task. This does **not** establish general superiority, lower cost or faster execution. Both conditions missed important issues, and the treatment did not follow every linked instruction.

The full skill is still one installable package. This comparison isolates instruction use on identical existing browser instrumentation; it does not compare a complete research/remediation service with an unequipped agent.

## Results

Two fresh operators per condition, four existing pages per operator: checkout, booking, and their clean-control variants. Same requested model and effort, same Chromium/Playwright/device profile, same task prompts and limits. No new execution framework or sample product was built.

| Measure | Skill off | Skill on |
| --- | ---: | ---: |
| Tasks completed, driver-measured | 7 / 8 | 8 / 8 |
| Seeded issues matched, all assigned opportunities | 5 / 20 (25%) | 8 / 20 (40%) |
| Observable subset, excluding three predefined model/judgment seeds | 4 / 14 (28.6%) | 6 / 14 (42.9%) |
| Findings reported | 9 | 15 |
| Additional supported findings | 0 | 2 case occurrences of one issue family |
| Unsupported findings | 4 | 5 |
| Established false positives | 0 | 0 |
| Warnings on four clean-control page runs | 3 | 4 |
| Mean end-to-end time per operator, including reporting | 26m 03.5s | 25m 46.5s |

Completion means the existing scenario success selector became visible, corroborated by the recorded final screen. It does not certify every persisted value or a real transaction.

The 17-second average difference is not evidence of a speed advantage. One baseline operator exhausted the observation budget before the defective booking task and also deviated from the prescribed task order. Both conditions had one operator finish its report after the observation cutoff; their complete elapsed time is retained.

“Established false positives: 0” must not be read as perfect precision. Nine warnings had insufficient grounds to establish a defect. Most concerned when validation errors should clear or whether focus must move automatically. Clean-control warnings include these unconfirmed suggestions and one source-supported unseeded issue; they are not automatically false alarms. No population false-positive rate or headline precision is claimed.

The treatment's extra issue concerned checkout controls remaining interactive behind the full-screen completion layer. It occurred in both variants, including a nominal clean control. The independent reviewer confirmed the source mechanism and recorded state; live keyboard activation and screen-reader behavior were not exercised. This is one issue family with two case occurrences, not two unrelated discoveries.

## Per-run results

| Operator | Condition | Repeat | Completed | Seed matches / 10 | Supported extras | Unsupported | End-to-end |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | Off | 1 | 3 / 4 | 2 | 0 | 1 | 28m 27s |
| B | On | 1 | 4 / 4 | 3 | 0 | 1 | 22m 58s |
| C | On | 2 | 4 / 4 | 5 | 2 | 4 | 28m 35s |
| D | Off | 2 | 4 / 4 | 3 | 0 | 3 | 23m 40s |

All four reported `inferhub/combo-deepseek-4-1-flash`, effort `ultra`. Backend identity was not independently attested. The reviewer saw anonymous labels, then the supervisor checked matches and aggregate calculations. An erroneous reviewer note about A's unstarted task having a true completion flag was corrected against the input, which was null; scoring did not change.

## Token accounting

These are provider-reported counters summed across both operators in each condition. They include repeated host instructions, tool schemas, screenshots/state context and report generation. Cached input is a subset of input. The exposed counter did not separately identify reasoning output, so no reasoning-token conclusion is drawn.

| Reported token field | Skill off | Skill on |
| --- | ---: | ---: |
| Input | 13,578,795 | 12,800,546 |
| Cached input | 12,628,224 | 9,897,984 |
| Input minus cached input | 950,571 | 2,902,562 |
| Output | 149,176 | 196,156 |
| Total | 13,727,971 | 12,996,702 |

Total reported tokens were about 5.3% lower with the skill, while output tokens were about 31.5% higher and uncached input was about 3.1 times higher. Cache hit rates differed substantially between operators and were not controlled. Task completion also differed. These numbers do not support a dollar-cost saving or a causal token-efficiency claim. No prices or missing counters were invented.

## What was missed

No operator matched the low-contrast checkout note, overloaded payment-choice hypothesis, left-thumb reach hypothesis, short booking-result toast or low-contrast booking CTA. Missing cases count against the assigned-opportunity denominator. Ergonomic/cognitive seed matches describe agreement with the existing key; they are not measurements of discomfort, gaze, mistap frequency or real-user preference.

The main improvement visible here was broader task coverage and additional detection of color-only availability and delayed payment feedback. The sample contains only two task families and two repetitions. It is too small, and the protocol deviations too consequential, to claim broad quality or speed gains.

## Fidelity and limits

- The experiment used the [preregistered protocol](protocol.md), frozen payload `6d5bd9755b5fb48b4ca7f617dae07d0d7fe8f0344c43003d2025270499f7e3d2` from commit `bda38f67f8ff4b5f56588d487430c282d1483be1`. The installed candidate has the same payload. Installer and README changes are outside the evaluated runtime payload.
- Same existing transport for both sides: Node 22.23.3, Playwright 1.56.1, Chromium 141.0.7390.37, Galaxy S24 viewport/input emulation. Physical devices were not tested.
- A and B were assigned order 1,4,2,3; A actually ran 1,2,4 and did not start 3. C and D followed 3,2,4,1. The incomplete counterbalancing remains a limitation.
- All operators initially encountered a sandbox browser-launch denial and then used the authorized non-sandboxed launch. Those attempts are environmental failures, not UI defects; startup and recovery time remain in totals.
- A and C received a cutoff instruction after the 25-minute observation window. They were allowed report-only closeout; no new product inspection was authorized. End-to-end reporting exceeded that window and is disclosed rather than silently trimmed.
- Treatment adherence was partial. Both read SKILL.md and relevant material; B read only the first 6,000 bytes of the QA workflow, and neither opened the linked generated-UI preflight. No mid-run coaching supplied missing checks. This is observed agent use of the skill, not proof of full workflow execution.
- The command audit found no answer-key, page-source or other-operator reads. This was protocol isolation, not an OS filesystem sandbox guarantee. Source was available to the independent adjudicator after operators finished.
- Known existing fixtures were reused. These are not a newly unseen held-out sample. The experiment does not compare live community research, Figma editing, code-fix loops, real-device ergonomics or production user benefit.
- No automated keyboard walk or reflow sweep was added to either arm. Focus metadata does not establish a keyboard or screen-reader experience.

## Reproducible records

- [Results and exact counters](results.json), [command/read audit](audit.json), [fixture hashes and route mapping](fixture-map.json).
- Frozen operator prompts: [A](prompt-A.txt), [B](prompt-B.txt), [C](prompt-C.txt), [D](prompt-D.txt). Replace the documented path placeholders with local paths; use the existing driver commands. Do not build another coordinator.
- Operator findings: [A](findings-A.json), [B](findings-B.json), [C](findings-C.json), [D](findings-D.json).
- [Blind review input](judgment-input.json), [per-finding adjudication](adjudication.json), and [evidence receipts](evidence-receipts.json).
- Referenced snapshots/inspect records and completed run records are under `local-evidence/`. PNGs are unchanged; JSON copies normalize local paths and retain source/published hashes. No system instructions, hidden reasoning, credentials or unrelated user records are published.

## Installation checks kept separate

The installed driver selftest also passed 561 checks with zero failures.

The single command installed all four components, the bundled search references, portable launcher, manifest, pinned driver dependencies and a usable Chromium browser into an isolated test installation/cache. One discoverable SKILL.md and the unchanged payload hash were verified. The installed browser opened the existing local checkout fixture. Existing offline research/loop smoke checks passed; they use synthetic content and are not live research evidence.

The full local Python suite ran 1,086 tests with no failures and one skip. The skipped painted-state test requires captures supplied by its focused browser group. The 24 installer tests cover guarded destinations, update records/symlinks, private backups, dependency failure, post-install corruption and Node-pinned npm invocation. CI outcomes are reported separately on the PR.
