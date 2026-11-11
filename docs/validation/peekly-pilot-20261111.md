# Peekly discovery and journey receipt admission — 2026-11-11

## Result and scope

Peekly product/user-effect validation is blocked by missing target information. The approved repository contains historical Peekly findings, but no authorized product URL, repository/path, local start command, build binding or owned import fixture with expected outputs. No Peekly interaction, actual-user observation, satisfaction gain or detection superiority is claimed.

The authorized independent fallback repairs one core boundary in the reusable persona journey skill: a receipt must remain inside its original lease through validation and serialization, and the saved receipt must be the exact detached snapshot that was checked. Four regressions failed against the unchanged base. After the fix, all 255 persona regressions and the full permitted Python suite passed (1,311 run, one existing capture-dependent skip). The extracted bundle passed all 17 new admission regressions. Browser validation remains explicitly unavailable and the release report correctly remains ready:false.

## Source and preservation boundaries

- Remorsearch origin: https://github.com/remorser58/Remorsearch_UX_QA_Skill.git.
- Requested base branch rem/public-evidence-pilot-20261111 was remotely verified at 81858b4ac70ca4610f4ef54ad515c2ca1bddeef5 before work.
- WebSynch rem/continuous-sync-20261111 was remotely verified, read-only, at 30f0063aa29739843eb625418c9fa2a05b8fa039.
- New branch: rem/peekly-pilot-20261111. New worktree under the approved Remorsearch root: .ux-loop/web-pro-peekly-pilot-20261111/worktree.
- Before work, 11 other Remorsearch worktrees (one dirty) were inventoried without optional Git writes: status, worktree metadata and content hashes of 7,106 tracked/nonignored files. Existing ignored research/process/ledger state was not inspected or altered.
- The post-validation inventory exactly matches that baseline: all 11 worktree records, the existing dirty status and all 7,106 file hashes are unchanged. No existing process or ledger was inspected.
- No installed skill, existing worktree, external service, real account, browser/Chrome, screen/input/clipboard, model/Codex runtime, research access route or security setting was changed. No deployment or login was attempted. Ordinary push is authorized for this new branch only.

## Peekly discovery

Searches used the exact base README.md, README.ko.md, PRD.md, HANDOFF.md, docs/release.md, tracked docs and then all tracked Peekly references. No personal-directory search or guessed endpoint was used. Existing AGENTS.md, Remorsearch SKILL.md, product-improvement and persona-library guidance were read. The skill-creator guidance was applied only to reuse existing code, document the contract and validate the distributable; no personal skill installation was performed.

The relevant historical source is [persona-upgrade-summary-20261110.md](persona-upgrade-summary-20261110.md). Its findings include missing return guidance, large-list import failure, focus leaving an import dialog after an error and unavailable close/cancel during controlled loading delay. They are prior-session observations, not new reproductions. The summary explicitly says accepted-cancellation late-result behavior was not exercised. The other tracked Peekly mentions describe preservation or non-modification, not an accessible target.

The [frozen protocol](peekly-pilot-protocol-20261111.md) lists four tentative goal hypotheses: resume an interrupted analysis, import a larger owned dataset, recover from invalid input and cancel a stalled import. They remain unexecuted hypotheses pending actual product PRD review. An actual pilot needs an explicitly authorized Peekly URL or exact repository/build and local start instructions, owned fixture data/expected outputs, plus a permitted interface that does not use the user's browser. Supplying only a URL would not remove the current browser/input restrictions.

DC written-permission and authorized YouTube Data API access remain unresolved. This fallback performs no research requests or alternative acquisition. Synthetic fixtures are never promoted to user or product evidence.

## Criteria fixed before the experiment

Protocol ID: peekly-admission-v1. Frozen at 2026-11-11T14:44:43.044978+00:00 (2026-11-11 23:44:43 KST).

SHA256: 2d0d3b9447e69dbae4bf5d446a481a8232e88c02f144b008784aaaffd30081a3.

The protocol is unchanged after results. Its C1–C8 expectations fix valid-before-deadline behavior, rejection during validation/serialization, detached receipt identity, restart/unknown effects, bounded concurrency/quarantine, unchanged permission/evidence gates and permitted offline verification. They do not ask whether the synthetic persona improved Peekly UX.

## Reproduced defect and product change

At base 81858b4, record checked lease expiry when loading state, then validated artifacts and serialized the new state without a final check before atomic publication. It also copied the caller's receipt only after validation. In deterministic owned tests:

| Pre-change regression | Observed failure |
| --- | --- |
| Deadline reached during artifact validation | Record accepted; expected expiry exception was not raised |
| Deadline reached during state serialization | Record accepted; expected expiry exception was not raised |
| Caller replaced checked observations/status after validation | Saved receipt digest differed from the validated input |
| Caller inserted a synthetic email-shaped marker after privacy validation | Unchecked replacement was saved |

These are library/API and storage-boundary reproductions, not proof of real worker timeout or private-data exposure in production. The owned tests advance a controlled clock at validation/serialization boundaries and mutate only their own in-memory input. They do not stall or operate Peekly.

The implementation in skills/remorsearch-ux-qa/uxpersonas/swarm.py now detaches the receipt before identity/binding validation, validates and saves that same snapshot, and checks the unchanged lease deadline after full state serialization immediately before invoking atomic storage. Exact-deadline and later submissions reject all five outcomes with lease_expired and an inspection/recovery diagnostic. Rejection at this new boundary leaves saved state and evidence unchanged. A subsequent read records the existing inconclusive transition and quarantines uncertain owned-fixture writes; explicit current-attempt retry or settlement remains required.

The cutoff is atomic-writer handoff, not completion of fsync/rename or an external action. An admitted write may finish after the deadline. Save failure/acknowledgement loss requires inspecting committed state, not blindly replaying the product action. Already-expired entry behavior, PNG evidence requirements, build/persona/source validity, privacy checks and side-effect permissions remain unchanged. This is not worker termination, evidence authenticity, clock-rollback protection or a schema migration; older compatible readers do not enforce the new boundary.

PRD section 6.2, the installed persona-library contract and both READMEs describe this behavior and its limits.

## Verification

Runtime: Python 3.14.7 selected by the repository's find_runtime.py. No supported Node 22 was found, and no runtime/dependency was installed. Initial host: 14 CPUs, 38,654,705,664 bytes RAM, load 7.19/7.93/8.25, free-memory percentage 43%. Before full validation: load 4.81/5.70/6.60 and free-memory percentage 50%. Resource-heavy checks are sequential; the new contested-writer test has at most two workers. Existing full-suite concurrency remains bounded by its own fixtures.

Measurement uses macOS /usr/bin/time -lp. RSS below is the maximum resident-set value reported by that command, not a summed machine/process-tree memory footprint. Default system TemporaryDirectory fixtures remain outside the source tree.

| Check | Observed result | Wall seconds | Maximum RSS bytes |
| --- | --- | ---: | ---: |
| Unchanged-base focused reproduction | 4 tests, 4 expected failures; exit 1 | 0.21 | 37289984 |
| Initial fixed admission suite | 16 tests passed; exit 0 | 0.38 | 37306368 |
| Final admission plus adjacent persona regression | 255 tests passed, including all 17 new admission tests; exit 0 | 108.23 | 50085888 |
| Full offline release candidate and extraction | 1,311 Python tests run: 1,310 passed, one existing skip; all 13 permitted release checks passed; web-driver skipped; wrapper exit 1 as required | 172.89 | 157138944 |
| Extracted-bundle admission regressions | 17 passed; parent and fresh child verify the extracted module path; exit 0 | 0.55 | 37453824 |
| Source loop smoke | All 18 command expectations matched, including intended refusal/unknown/error cases; exit 0 | 1.83 | 30932992 |
| Source research smoke | merge, gate, report-check, audience export/check and minimization passed on invented data; network_requests:0; exit 0 | 0.54 | 51249152 |

The full suite itself reports 168.740 seconds; the release supervisor measured that check at 169.31 seconds. Its one existing skip is ActualPaintCaptures.test_frozen_browser_captures_feed_real_checks because ERGO_PAINT_CAPTURES was not supplied. It was not enabled or replaced with a synthetic browser result. The web-driver release check is a separate explicit skip. Release-file validation, bundle build/integrity, extracted integrity/runtime/help/reference checks, relocated smoke, current-source match and validation-input stability all passed. Both input inventories contained the same 667 files with no added, removed or changed inputs. Extracted smoke includes both research and loop paths and reports live_integrations_executed:false.

| Frozen criterion | Observed result |
| --- | --- |
| C1 | A receipt admitted just before expiry retained the reviewed task/criteria; product_ready remained false |
| C2 | Exact-deadline and later validation completions rejected; all five terminal outcomes obeyed the cutoff and preserved saved bytes/evidence |
| C3 | Expiry during complete serialization rejected before the atomic writer |
| C4 | Caller changes to identity, outcome, criterion status, observation, references and synthetic privacy marker did not replace the validated snapshot |
| C5 | A new Python process reported one inconclusive attempt, zero passes, the same operation and a quarantined resource; retry required explicit current-attempt inspection |
| C6 | A real competing writer lock refused the contender; expired shared-write uncertainty blocked the shared resource while an independent task could claim |
| C7 | New identity/private-evidence tests and existing build/persona/privacy/evidence/research regressions passed without relaxing a gate |
| C8 | Permitted full regression, smokes, packaging and extracted checks passed; browser checks remain unexecuted and ready:false |

The new tests cover all five late outcomes, serialization boundary, pre-deadline success, validated snapshot preservation, privacy-shaped caller mutation, new-process reload, explicit retry with the same operation, stale receipt rejection, actual writer-lock contention, uncertain shared-resource exclusion, independent-resource progress, wrong identity, missing/unsafe evidence, pre-publication storage failure, lost acknowledgement and admitted-write completion after expiry. They reuse the existing owned fixture (invented log and 2×2 PNG). That image is internal test data, not a capture of Peekly or any browser; a synthetic passed receipt proves a code path only.

### Reproduction commands

Run from the new worktree, with PY set to /opt/homebrew/Cellar/python@3.14/3.14.7/Frameworks/Python.framework/Versions/3.14/bin/python3.14. Each measured command is prefixed with PYTHONDONTWRITEBYTECODE=1 and /usr/bin/time -lp; stdout/stderr are retained under .ux-loop/peekly-pilot-validation-20261111. For the extracted run, REMORSEARCH_TEST_SKILL_ROOT was set to the absolute worktree path plus /dist/peekly-pilot-release-20261111/extracted/remorsearch-ux-qa, with PYTHONPATH=tests.

    PYTHONPATH=tests "$PY" -m unittest -v test_persona_receipt_admission.ReceiptAdmissionTests.test_expiry_during_artifact_validation_is_rejected_before_save test_persona_receipt_admission.ReceiptAdmissionTests.test_expiry_during_state_encoding_is_rejected_before_atomic_handoff test_persona_receipt_admission.ReceiptAdmissionTests.test_saved_receipt_is_the_same_detached_snapshot_that_was_validated test_persona_receipt_admission.ReceiptAdmissionTests.test_caller_mutation_cannot_bypass_the_checked_privacy_boundary
    PYTHONPATH=tests "$PY" -m unittest -v test_persona_receipt_admission
    "$PY" -m unittest discover -s tests -p 'test_persona*.py' -v
    "$PY" scripts/check_release.py --output dist/peekly-pilot-release-20261111 --skip-web
    REMORSEARCH_TEST_SKILL_ROOT="$PWD/dist/peekly-pilot-release-20261111/extracted/remorsearch-ux-qa" PYTHONPATH=tests "$PY" -m unittest -v test_persona_receipt_admission
    "$PY" skills/remorsearch-ux-qa/scripts/smoke_loop.py
    "$PY" skills/remorsearch-ux-qa/examples/research/run_fixture.py

The release checker ran the entire Python suite, required release-file checks, bundle build and verification, extraction verification and relocated launcher smokes. --skip-web deliberately yielded exit 1 and ready:false; this is not a browser-validated release. Product code, tests and contract documents stayed frozen during the checker. This result report alone was finalized afterward; the final source comparison permits only docs/validation/peekly-pilot-20261111.md to differ from that measurement window. It does not relabel the archived validation-input snapshot as a snapshot of the finalized report. The skill payload, test code, PRD, READMEs, contract and frozen protocol remain the validated bytes.

### Retained artifacts and digests

The local archive is dist/peekly-pilot-release-20261111/bundle/remorsearch-ux-qa.zip (4,118,366 bytes), SHA256 f88910e6901ca9a23edebf599e609af7a551c5ae08170d89959df1b948715616. It was extracted into a disposable directory inside this new worktree and was not installed or deployed.

The detailed release report is dist/peekly-pilot-release-20261111/validation.json, SHA256 60befcf2d70011019d8ac6a702a4fbd7eb08f5a93bab1b7ac9add1320c4485b9. It retains ready:false, published:false and all input fingerprints. Raw logs, measurements.json, freeze record and before/after preservation inventories are retained under .ux-loop/peekly-pilot-validation-20261111. These local logs are not collected from another session and are not committed as product/user evidence.

| Retained log | SHA256 |
| --- | --- |
| baseline-admission.log | ffe04125e8ed0cf4748744ced9c01ab0efd85f033f44df2cab130729187ce0ba |
| admission-fixed.log | 939eb0577f78bfde5ef7d2a5f214063ac0fe0a636901a49ca78a05ead2c6a876 |
| persona-regression.log | 1816305d6b9fdc21db6ed6a8df4dd4a03714275c4fc2c078e57244d61b433fbf |
| release.log | 7c86e75bc7c54364a743b707bbceeef8bc770b68f016f00ac46a76685d8badcf |
| extracted-admission.log | 91e84f234a598fddf7aa4adcee4126011d431db84b8061a0fea5ed2873b003dc |
| source-loop-smoke.log | 580d5695655667ebb65e498c2d2ff048db56a12c6672196aeecfcdf72a11374e |
| source-research-smoke.log | 24d48c81b34f214bf65ade9a64d646f01a35cdbfdc5ec72bf828b78c2d2d7024 |

Validated source SHA256: swarm.py f58aff928afb62c5a555986f3f7bdfb4828feb715dcb775c265705c1271c56df; test_persona_receipt_admission.py c73d8fdb26d5873cb40d7393ccbe493801dd1942b306048c2b308ee2aa3be00c.

The final staged git diff --check exits 2 for exactly one formatting warning: peekly-pilot-protocol-20261111.md ends with the blank line present when its SHA was frozen. That byte is deliberately preserved instead of changing the experiment protocol after results. The same check excluding only that immutable protocol exits 0. No whitespace rule, hook or repository setting is changed, and this exception is not reported as an unqualified clean full diff check.

## Remaining boundaries

No actual Peekly product, goal completion, cancellation acceptance, late product effect, real browser/account or participant was exercised. The target route and safe fixture are missing; browser interaction is also explicitly prohibited. No model was called, no provider restriction was bypassed and no research source was collected. A future authorized pilot must review actual goals and freeze its own expected observations before execution. The historical findings and this synthetic regression cannot establish real-user benefit, representativeness, whole-product readiness or comparative effectiveness.
