# Peekly verdict-quality rerun — same 32 saved personas

Date: 2026-11-13, Mac mini. Product build: Peekly preview from isolated
`insta-tracker` worktree at commit `58214441`. The original product worktree
was not modified. The same saved `peekly-persona-library-v2` identities
`PER-PEEKLY-V2-001` through `PER-PEEKLY-V2-032` were used; no personas were
cloned or renamed to inflate coverage.

## Before / after verdict comparison

| Verdict | Previous run | New run | Change |
|---|---:|---:|---:|
| Passed | 0 | 6 | +6 |
| Failed | 2 | 4 | +2 |
| Inconclusive | 30 | 22 | -8 |
| Distinct personas with a final current run | 32 | 32 | 0 |

The new run has 32/32 distinct personas with a completed execution and current
evidence. The result is a more decisive verdict distribution, not a product
pass: 6 pass, 4 fail and 22 remain inconclusive. The 21 `engine_conflict`
records in the first rerun queue were execution-integrity stops caused by a
code-manifest change during that attempt. They were not treated as UX failures;
all affected identities were subsequently executed in separate queues with a
frozen engine per queue. No `engine_conflict` remains in the final 32-persona
cohort.

## Platform-scope N/A and criterion ledger

| Criterion status / scope | Count |
|---|---:|
| Passed criteria | 56 |
| Failed criteria | 4 |
| Applicable but not executed / insufficient evidence (`not_run`) | 42 |
| Desktop-only N/A: native OS share-sheet preview | 7 |
| Conditional recovery N/A: no triggering failure occurred | 27 |

The 7 desktop N/A items concern checking the native share-sheet image preview
for account ID and aggregate-count content. A desktop browser cannot open the
native mobile share sheet. These items are separated from applicable `not_run`
criteria; they are not counted as passes. The 27 recovery N/A criteria are
also separate: no recoverable failure was triggered, so a recovery action was
not applicable. Neither category is silently promoted to passed.

The remaining 42 applicable `not_run` criteria are grouped in
`verdict-quality-summary.json`: required fixture/upload not executed (15),
persona subflow not executed (11), other evidence gaps (14), precondition or
account mismatch (1), and fixture/platform capability missing (1). These
remain explicit coverage gaps.

## Confirmed failures — not model hallucinations

1. **P2 — Import progress/cancellation feedback absent (1 persona).** Three
   ZIP attempts returned directly to result/error states without a distinct
   read-versus-analysis progress state or an in-progress close/cancel control.
   Evidence: `PER-PEEKLY-V2-014` in the machine-readable evidence index.
2. **P3 — Relationship list is not alphabetically sorted (3 personas).** The
   list appeared in `JU, IN, TA, AT, MI` order rather than the criterion's
   alphabetic ID order. Search itself worked and narrowed `JU` to one entry.
   Evidence: `PER-PEEKLY-V2-025`, `026`, and `027`.

The earlier wording-drift false positive was not repeated: a button that
worked despite different copy was not failed. The earlier unexecuted-list
false positive was also prevented: a condition with no execution/evidence
cannot be marked failed. The 4 current failures above each cite observations
and screenshots from actually executed UI actions.

## Verdict-quality changes

- `not_applicable` is accepted only for conditional recovery criteria when no
  triggering failure occurred. Success criteria cannot use this status.
- Applicable but unexecuted success criteria remain `not_run` and cannot
  contribute to a pass.
- A `failed` judgment is rejected if its observation describes a condition as
  untested, unopened or unobserved, or reports only wording drift while the
  action succeeded.
- Model-authored narrative steps with no evidence IDs are omitted from the
  evidence-step list; they cannot be used as evidence. Empty evidence is
  accepted only for explicitly unassessed criteria.
- Per-persona tasks now include actions mapped from their saved PRD
  requirements, including the specific v3 synthetic ZIP fixtures.
- The CDP file-input lookup now traverses the full owned DOM tree. A rejected
  pre-dispatch upload is reconciled only with evidence that no file was
  selected; the old tool request is never resent. A fresh model decision must
  choose a new action from the current page.

## Actual model and usage

- Provider/model requested: `TOKENMAXX/deepseek-v4.1-flash-free` only.
- Served model observed: `deepseek-v4.1-flash` (recorded as returned).
- Model calls: 691; dispatch attempts: 731; browser actions: 621.
- Known usage: 6,828,146 input tokens and 670,543 output tokens.
- HTTP 429: 0. Paid fallback / InferHub / Haiku: 0.
- Policy cost: USD 0 under the user's free TOKENMAXX authorization.
- Provider cost and billing-source fields were null; no invoice verification is
  claimed. Timed-out attempts without usage are unknown, not zero-token calls.

## Execution integrity and limitations

- All 32 final identities have a current result and evidence set; each stage's
  browser shutdown was confirmed.
- Initial 21 `engine_conflict` statuses were preserved as historical failed
  attempts and the same personas were retried in fresh isolated queues after
  the engine was frozen. The old queues were not edited to make them appear
  complete.
- One persona (`017`) required a fresh isolated rerun after a model-only
  timeout and a pre-dispatch upload-target rejection. The old model call was
  reconciled without resending; the rejected upload was not replayed. The
  final successful execution is recorded separately.
- No Instagram login, credentials, real Instagram data, or live account
  connection was used. Only the owned local preview and synthetic ZIPs were
  tested.
- This is synthetic persona QA, not real-user research, native iOS testing,
  accessibility certification, or product-readiness approval.
- Final full Python regression: **1,587 passed, 21 skipped**. Focused verdict,
  queue, receipt and criterion-binding suites also passed; `node --check`, JSON
  validation and `git diff --check` passed.

## Machine-readable evidence

- `verdict-quality-summary.json`: before/after comparison, status totals,
  N/A scopes, token usage and attempt accounting.
- `evidence-index-32.json`: one final result per saved persona, with the exact
  run report path, evidence root, result digest, and criterion statuses.
- Raw browser evidence and provider ledgers remain in the private local
  `.ux-loop/peekly-verdict-quality-*` trees; credentials are not included.
