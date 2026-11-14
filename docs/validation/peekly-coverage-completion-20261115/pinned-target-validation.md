# Pinned target recovery and pre-smoke validation

Recorded 2026-11-15 (Asia/Seoul). These checks prepare a new live smoke; they do not establish new UX coverage.

## Why a separate target was required

After R1 ended, another task changed the original product PRD, code and preview build. Normal Library validation rejected all 32 original bindings as `stale_prd`. The original worktree and its port 4174 server were preserved. This task uses an owned archive of product commit `51110f4c569673faa8d242d5b85c4b47afb54cbb` at `.ux-loop/peekly-pinned-product-51110f4-20261115/source`, served at `http://127.0.0.1:4175/`.

All 319 archived files match the source commit's Git blobs and modes. All 8,777 copied dependency files match their prepared local source; no install was performed. TypeScript and Vite builds exited successfully. The archived PRD SHA is `a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b`.

The index SHA exactly reproduces the historical value `848b334a6affa5c6a578911819aaf127da34bc2e6ae2f04899022872b7d0f6f5`. The historical main JavaScript did not have an independently retained hash, so identity of every historical dist byte is not claimed. All 13 new dist files are pinned in build manifest SHA `c8adccb882b4bba6592e11f3792b8779809f771e66ea169118b5db84a7100d17`.

The new library uses the public `Library.import_profiles()` API and normal `list()`/`get()` validation. Its 32 IDs, profile contents, requirement IDs and 25 exact PRD citations match the prior library. Only `context.prd_path` changed to the archived file. All are revision 1 and reusable. Library SHA: `02c728a1b750d86164e035d88c096ffa7feca42f363cb68ed697a3beec7fa616`. Old library bytes remain unchanged; importing the stale old context still fails. Full provenance and binding hash correspondence are retained in `pinned-inputs.json`.

## Runtime gates and regression

The completion launcher binds the new Library, target URL and manifest through the actual host arguments. It rechecks every archived source file and every dist file. The generated TypeScript cache is frozen separately, rather than counted as an archived source file. It does not use the enclosing QA repository's Git HEAD as a product source identity.

Immediately before and after actual execution it checks HTTP bytes for the index and its five referenced entry assets. Proxy use, redirects, other origins and changed sizes/digests are rejected. A matching HTML file cannot hide changed JavaScript. The smoke-to-cohort gate and finalizer require both saved HTTP verification receipts and the identical input freeze.

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests /Users/m4mini/.local/bin/python3.11 -m unittest test_peekly_completion_target test_peekly_completion_launcher test_peekly_completion_finalizer test_peekly_coverage_launcher test_peekly_history_navigation
```

| Module | Passed |
| --- | ---: |
| New target admission and mutation checks | 12 |
| Completion launcher | 9 |
| Finalizer | 15 |
| Prior coverage launcher | 18 |
| History navigation | 7 |
| Total | 61 |

Exit 0, no skipped or failed tests. Log `.ux-loop/peekly-pinned-target-preflight-20261115/regression.log`, SHA `f01311bb071d5501a881167f4e065f1be6ab2d880922db0b5729a69fb89421de`; command/environment/counts are in its sibling `regression.json`. Independent review reran the target, completion launcher and finalizer modules: 36 passed. Those are overlapping tests, not an additional 36 unique cases.

The actual local archive/library freeze check passed. Actual HTTP GETs verified the index and five referenced assets. `smoke --check-only` passed with the exact 32 reusable personas, 33 prior queues, 329 forbidden old job IDs and 40 preserved old uncertain rows. All prior queues were opened read-only. No model or browser was invoked for these checks. All 32 generated goals pass length and privacy constraints. `git diff --check` passed.

The earlier merged runtime `2e41a0b` also passed 245 affected tests, recorded in STATUS. The previous full release check's Node 22 requirement remains unresolved: this is not a release-ready claim. See `implementation-validation.md` for that distinct gate and its optional skips.

After the user confirmed recovery of the Mac disk/tool stall on 2026-11-15, the same 61-case command passed again in 0.545 seconds. Normal CLI preflight, all 319 archived source files, the frozen library, and the actual six HTTP files were reverified. No R2/cohort result directory or live completion launcher existed. The earlier launch wrapper had failed on its first Python import, before spawning the runner or sending any model/browser operation.

## Fresh execution roots

- R2 smoke: `.ux-loop/peekly-completion-smoke-pinned-20261115` — personas 021 and 029; their six success criteria include two prior not_run.
- New 32: `.ux-loop/peekly-completion32-pinned-20261115` — starts only after the valid two-session smoke gate passes with all six success criteria executed.
- Existing failed R1 remains `.ux-loop/peekly-completion-smoke-20261115`; no resume or receipt rewrite.

Only the authorized free TOKENMAXX route may run, with concurrency two and no uncertain resend. The exact old-23 matching and semantic evidence rules are in `semantic-review-checklist.md`.
