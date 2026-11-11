# Peekly target discovery and fixed fallback protocol — 2026-11-11

Protocol ID: peekly-admission-v1. Freeze this file before the first regression experiment. Record its SHA256 before running tests; do not edit this protocol after seeing results. Record outcomes separately.

## Verified starting point

- Remorsearch origin: https://github.com/remorser58/Remorsearch_UX_QA_Skill.git
- Requested and observed remote base: rem/public-evidence-pilot-20261111, 81858b4ac70ca4610f4ef54ad515c2ca1bddeef5.
- WebSynch reference: rem/continuous-sync-20261111, 30f0063aa29739843eb625418c9fa2a05b8fa039; read-only verification only.
- Independent work branch: rem/peekly-pilot-20261111.
- Only this new worktree may be changed. Existing worktrees, research, processes, ledgers and installed skills remain unchanged.

## Peekly discovery result and required access

The exact base's README, PRD, HANDOFF, release guide, tracked documents and tracked Peekly references were inspected. The only concrete product observations are the historical summary in docs/validation/persona-upgrade-summary-20261110.md: missing return guidance, large-list import failure, focus escaping an import dialog after an error, and unavailable close/cancel during a controlled loading delay. That summary says product files were not modified and accepted-cancellation late-result behavior was not exercised.

The approved source tree supplies no Peekly URL, product repository/path, local start command, build binding or safe import fixture. Do not invent any of them, search personal directories, reuse a running session, or turn the historical summary into a new observation.

Possible goals inferred from that summary, pending actual Peekly PRD review:

| Goal hypothesis | Observable result needed | Current status |
| --- | --- | --- |
| Resume an interrupted analysis | Reach the saved task and preserve prior selection/data | Not executed; product and fixture missing |
| Import a larger owned dataset | Complete import and inspect the resulting analysis without losing existing data | Not executed; fixture shape/expected values missing |
| Recover from invalid input | Preserve input and reach the corrective action after a real error | Not executed; safe route missing |
| Cancel a stalled import | First reach and receive cancellation, then inspect late effects and retained records | Not executed; prior report did not reach accepted cancellation |

These are inferred task hypotheses, not validated personas, representative user needs, new defects or measured effects. A genuine future pilot needs an authorized Peekly URL or exact repository/build, documented local execution, owned fixture and expected outputs, and a permitted non-user-browser interface. Browser/Chrome, keyboard/clipboard, login, account mutation, deployment and security changes remain prohibited for this task.

## Independent fallback selected before experiment

Inspect and repair the final admission boundary for persona journey receipts. The current record path checks lease expiry while loading state, then validates artifacts and serializes state without a final deadline check immediately before the atomic state handoff. It also copies caller-owned receipt data after validation. Reproduce with the existing owned SwarmTests fixture; no model, browser, real account or actual Peekly behavior is involved.

The frozen goal is: only the validated, detached receipt may be accepted while the original lease is still valid at the final write boundary. Expiry or mutation must not invent a pass, renew a lease, retarget a journey, discard evidence or reset a retry budget.

## Fixed acceptance criteria

| ID | Expected result fixed before testing |
| --- | --- |
| C1 | A valid receipt whose final write handoff is strictly before its deadline preserves existing accepted outcome and goal/criteria semantics. |
| C2 | If artifact/receipt validation crosses the exact deadline or finishes later, all five terminal outcomes are rejected with an expiry diagnostic; the saved run bytes and evidence stay unchanged. |
| C3 | If complete state serialization crosses the deadline, reject before atomic state publication. A check only before serialization is insufficient. |
| C4 | Caller mutation after validation cannot replace the checked observations, outcome, criterion statuses or references in the saved receipt. Validate and save one detached snapshot. |
| C5 | A fresh read after a refused late receipt exposes the existing inconclusive/unknown behavior, no passed goal/requirement, the same attempt/operation and unchanged criteria. Existing explicit inspection, retry and settlement rules remain required. |
| C6 | A competing worker cannot claim through the current writer lock; after expiry, an uncertain fixture-write resource remains quarantined while independently authorized resources can proceed. Bound test concurrency at two workers. |
| C7 | Wrong identity, unsafe evidence, privacy violations, changed builds/personas and existing missing-evidence rules still reject; no permission, screenshot or research gate is relaxed. |
| C8 | Full Python regression, required offline smokes, package integrity and extracted-bundle checks succeed for permitted routes. Browser checks are explicitly skipped and release ready remains false. |

## Execution and interpretation

- First run the new focused regressions against the unchanged base implementation and retain the failing result.
- Apply the smallest source change for the admission boundary, then rerun focused and adjacent tests.
- Use Python 3.14.7 discovered by the repository helper. No Node 22 was found. Do not install runtimes or browser dependencies.
- Run resource-heavy verification sequentially. Keep default system temporary fixtures outside the source tree and never reuse an existing release output directory.
- Use the existing check_release.py with --skip-web for the full Python suite, extraction and relocated smoke checks; preserve its ready:false result. Do not claim the Chromium suite passed.
- Run the new regressions or equivalent actual CLI path against the extracted code and verify its module path. Freeze code/doc inputs before the full release checker.
- Record exact commands, exit codes, elapsed time, maximum RSS, hashes and intermediate failures. Do not retune these criteria after observing results.
- Synthetic fixtures establish admission/recovery mechanics only. No new Peekly interaction, participant observation, real-user completion rate, satisfaction, detection superiority or measured UX improvement is claimed.
- DC written-permission restrictions and the absent authorized YouTube API route remain gaps. No research request, alternate route, login or personal-data transmission is needed for this fallback.

