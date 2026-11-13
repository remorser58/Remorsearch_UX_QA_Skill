# Peekly explicit-success verification — 2026-11-14

## Decision and scope

This report uses the current Peekly PRD from product commit `51110f4` (SHA-256 `a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b`) and the 32 saved personas re-derived against that PRD. It does **not** start another persona journey. The final queue state is frozen at 23 operationally completed sessions, one blocked session and one uncertain model send. The uncertain send is preserved and was not replayed.

The final queue's original `resume-report-r1.json` is retained unchanged. The additive `resume-report-rules-r1.json` is a stored-evidence-only overlay. It reads existing observation JSON, screenshot references and the frozen synthetic fixture archive; it does not dispatch a browser action, model decision or review call. Re-judgment ledger: 16 criterion changes; 0 model calls; 0 browser calls. The original observations and screenshots are not rewritten.

The comparison below distinguishes session outcomes from criterion-unit counts. `N/A / 미평가` means no valid UX verdict could be issued (blocked, uncertain or unassessed); it is not a product failure. Recovery criteria are shown separately because `not_applicable` is permitted only for a conditional recovery that had no trigger.

## Three-run comparison

| Measure | First run — `696dbe3` | Verdict revision — `cb0188d` | Current — stored-evidence re-judgment |
| --- | ---: | ---: | ---: |
| Distinct personas in cohort | 32 | 32 | 25 queue entries (23 complete, 2 not assessed) |
| Session UX pass | 0 | 4 | 0 |
| Session UX fail | 2 | 0 | 0 |
| Session UX inconclusive | 30 | 7 | 23 |
| N/A / 미평가 | 0 | 21 | 2 (1 blocked, 1 uncertain) |
| Success criteria — passed | Not recorded in 696dbe3 index | 22 | 2 |
| Success criteria — failed | Not recorded in 696dbe3 index; 3 model-failed candidates were separately listed for review | 0 | 0 |
| Success criteria — not run | Not recorded in 696dbe3 index | 6 | 74 |
| Success criteria — N/A | Not recorded in 696dbe3 index | 0 | 0 |
| Recovery criteria — passed | Not recorded in 696dbe3 index | 2 | 1 |
| Recovery criteria — not run | Not recorded in 696dbe3 index | 0 | 22 |
| Recovery criteria — N/A | Not recorded in 696dbe3 index | Not separately itemized in the old summary | 0 |

**Reading the comparison:** the first run's 32 sessions were operationally complete, but its two failed model verdicts were not two confirmed functional defects. The prior independent review explicitly rejected the obsolete import-shortcut criterion as a product defect and did not independently confirm the former-mutual copy failure. The `cb0188d` attempt is dominated by 21 `engine_conflict` blocks; its four passes and seven inconclusives are the 11 assessed sessions, not a 32-persona product pass. The current 23 completed sessions remain inconclusive because most applicable criteria were not fully executed and 22 completed receipts still carry `host_protocol` execution issues. The two unassessed sessions are not silently counted as UX failures.

The first-run machine index does not retain a complete success/recovery criterion-unit ledger. Those cells are deliberately `Not recorded`, rather than reconstructed from session totals. Its indexed evidence does record three model-failed criteria for independent review and one manually reviewed finding.

## Current queue and stored-evidence re-judgment

Final queue counts from `stage-25/resume-report-r1.json`:

- 23 complete; 1 blocked (`PER-PEEKLY-V2-031`, `tool_context_unavailable`); 1 uncertain (`PER-PEEKLY-V2-011`, TOKENMAXX route failure after a persisted send intent).
- Of the 23 complete entries, 22 carry a `host_protocol` execution problem and one has no recorded problem. These are execution/protocol limitations, not 22 additional product defects.
- No new model or browser calls were made for re-judgment.

Sixteen stored criterion statuses changed under the current-PRD deterministic rules:

| Change | Count | Interpretation |
| --- | ---: | --- |
| failed → passed | 1 | The current More > `이미 받은 자료로 확인하기` path reached the file-selection view; the obsolete request-guide phrase is not required by the current PRD. |
| failed → not_run | 12 | A failure had been inferred without the criterion's own required precondition/fixture/result. This includes malformed HTML/account/missing-list fixture criteria and the sample-export check on a real-data list rather than the sample MatrixTab. |
| passed → not_run | 3 | HTML/JSON parity had been marked passed even though the frozen HTML fixture is not a complete HTML document. The fixture cannot support either a product pass or product failure. |

The frozen `peekly-format-html.zip` contains fragmentary `followers.html` / `following.html` content without a complete `<html><body>…</body></html>` document. Its SHA-256 is `23d5efe57558a95f13ae00615b1a5b8ccc8c597c1b59b877da5e40d8071ae63d`. This is a test-fixture defect. The parser's rejection of this invalid fixture is not evidence of a product parser defect. A valid, complete HTML fixture is required before HTML/JSON parity can be judged.

The corrected rules also bind malformed-HTML, account-mismatch and missing-list outcomes to the exact fixture actually uploaded and its own result observation. A result left over from a previous valid import can no longer make a different criterion fail. `not_run` carries a reason and evidence link in the overlay; it is not promoted to pass.

## Defect classification — keep the causes separate

### Product UX defects

**P3 — The main relationship hint omits the former-mutual inclusion rule (still present in current source).** The PRD definition includes people who used to follow back but no longer do. The visible hint still says only `내가 팔로우하는데 나를 팔로우하지 않아요`, which does not explain that inclusion. The current product worktree at `51110f4` still contains this copy in `src/components/ResultsTab.tsx:272`; the current PRD definition is in `docs/PRD.md` §4. This is a content-accuracy/discoverability gap, not a calculation defect. The earlier persona-020 observation is in `evidence-index-32.json` (`PER-PEEKLY-V2-020`, `obs-2`, screenshot `browser-00019.png`, SHA-256 `af7e9524110ed26fceb8e6deff6023fe2595614fd6542e3ec6feef9939abcdd0`). The finding is still statically reproducible in the current source; this turn did not re-run a browser journey for it.

**Historical P2 — Imported result summary below the visible viewport.** The 2026-11-13 evidence review observed this in 29/32 journeys at 756×413. The current source now calls `heading.scrollIntoView({ block: 'start', behavior: 'instant' })` in `src/components/ResultsTab.tsx:164`, so the old finding appears addressed in code. Current-build runtime behavior was not re-run in this turn; do not claim a new live pass.

**Historical P2 — Manual import entry discoverability.** The earlier 32-persona evidence observed the old disclosure below the fold and repeated More-tab searches. The current PRD/build now exposes `이미 받은 자료로 확인하기` on More. Current persona-007 observations 2–3 show the More entry and its click opening the file-selection flow; see the private evidence path below. This path is confirmed for the observed desktop journey, not certified across all viewports or iOS.

No current 23-session stored-evidence re-judgment remains a confirmed functional product failure. That does not establish product readiness: 74 success criteria remain `not_run`, and the P3 copy issue remains.

### Execution / runner defects

- `cb0188d`: 21 of 32 jobs were blocked by `engine_conflict` after the reviewed engine manifest no longer matched. Those jobs are unassessed, not product failures.
- Current queue: 22 completed receipts still record `host_protocol`; one session is blocked because the owned browser context could not be resumed (`tool_context_unavailable`); one model send is uncertain. The uncertain intent was preserved and not resent.
- The 22 `host_protocol` receipts can still contain useful admitted screenshots/observations, but they cannot be upgraded to full persona passes while the final judgment/host envelope remains unresolved.

### Verdict / criterion misjudgments

- The prior `696dbe3` evidence index lists the obsolete `이미 파일을 받았어요` criterion as a failed model judgment even though the then-current control `받은 파일 바로 넣기` navigated to the file selection step. The prior reviewer marked it not independently confirmed as a product defect.
- Current stored evidence had the same class of obsolete-string failure, plus invalid fixture attribution and a sample-export criterion applied to a real-data MatrixTab. The 16 changes above correct only these affected criterion records; no model decision was regenerated.
- `PRD-SAMPLE-EXPORT` is only judged after entering sample mode and opening More > 관계 목록 (MatrixTab). A real-data list with active `목록 복사` / `목록 저장` controls is not evidence that sample restrictions are broken.
- Product privacy is judged from the product's own visible local-processing notice, not from the test host's external-network block. Search uses the current `아이디나 이름으로 찾기` text input rather than an obsolete `type=search`/placeholder assumption.

## Representative current evidence anchors

All paths below are local private evidence under the worktree's `.ux-loop`; the original bytes were preserved and are not committed to this report.

- Current More entry visible: `.ux-loop/peekly-explicit-success-retry-final-20261114/stage-25/sessions/S-onpcmjcamnllineodknelimf/evidence/S-onpcmjcamnllineodknelimf/1/agent-observation-2.json`.
- Current More entry clicked and file input opened: same directory, `agent-observation-3.json`.
- Current sample-export misclassification: `.ux-loop/peekly-explicit-success-retry-final-20261114/stage-25/sessions/S-eiempjpglicmbhkndcehglln/evidence/S-eiempjpglicmbhkndcehglln/1/agent-observation-13.json`; it shows the ordinary imported relationship list, not a sample-mode MatrixTab.
- HTML fixture rejection and subsequent JSON result: persona-007 session above, `agent-observation-8.json` through `agent-observation-10.json`.
- Full per-session stored-evidence overlay: `.ux-loop/peekly-explicit-success-retry-final-20261114/stage-25/resume-report-rules-r1.json` (SHA-256 `d6436cf3f68c96faa39c1b8e17b1f96a85006042572c618eb8803b00bca4c506`). The pre-overlay report remains `resume-report-r1.json` (SHA-256 `b43f6a8b60e5cd001bc57f1928430e6e4b8af585cea1983a2e84b7d31d6a6866`).

## Validation of the verdict-rule patch

- `PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 -m unittest discover -s tests -v` — **1,604 passed, 21 skipped, 0 failed**. The skipped tests require the optional pinned LangGraph runtime, which is not installed in this environment.
- Focused `test_verdict_quality.py` — **21 passed**.
- `skills/remorsearch-ux-qa/scripts/smoke_loop.py` — **passed**, 18 expected command outcomes.
- `skills/remorsearch-ux-qa/examples/research/run_fixture.py` — **passed**; fixture-only merge/gate/report workflow.
- `git diff --check` — passed before the verdict-rule commit.
- No Peekly persona re-execution, no browser dispatch, no model call, no Instagram login, no iOS runtime test, no purchase and no deployment.

## Commits and limitations

- Verdict-rule implementation/test commit: `51d871f75a6c6e4bc35e5c90f919452a37ca5da1` (`fix: align Peekly verdicts with current PRD evidence`).
- This report and its machine-readable summary are committed separately so the judgment-rule change and its audit record remain distinct.
- Synthetic personas are PRD hypotheses, not research participants. The runs do not establish real-user prevalence, satisfaction, iOS behavior, accessibility conformance or product readiness. The 23 completed current sessions are operationally complete, not UX passes.
