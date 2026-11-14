# Independent review of the fresh 32-person cohort

The execution root is `.ux-loop/peekly-completion32-pinned-20261115/stage-32`. Smoke sessions and historical reobservations are excluded from this cohort's denominator. The frozen runtime is the 17-file R6 runtime at `f50d082a197e683b5961d17919fe219dc48c4d55`; documentation commits may advance HEAD without changing it.

## Review ownership and evidence

Partition completed jobs into 001–012 (input/fixture/cancellation paths), 013–024 (storage recovery, relationship lists and legacy UNKNOWN), and 025–032 (search/deletion and retention/PAYWALL). Review only the actually assigned requirements and new admitted evidence. Do not copy old case overrides or turn a cross-criterion product finding into an assigned-criterion failure without its binding.

During execution, reviewers may prepare draft decisions from completed jobs' immutable result/checkpoint/receipt artifacts. Do not promote uncertain, incomplete or current-invalid jobs. After the raw finalizer publishes, reconcile each draft against the final eligible report and use the same plan, raw-summary and artifact-audit hashes for every final decision fragment. Root merges disjoint `(job_id, kind, index)` keys and runs `apply_criterion_review.py` once. The exact input contract is in `review-application.md`.

Every decision must bind the actual result hash, expected raw status, plan requirement, registered artifacts and admitted observation IDs, including an execution log with purpose `result`. PNG visibility claims require the actual captured pixels; returned DOM text outside the capture can support a scoped DOM finding but must not be described as visible in that screenshot. Separate product findings, runner/fixture limitations and judge corrections.

## Conditional recovery

Apply the literal assigned criterion. Its recoverable browser/import failure condition does not add an "unexpected only" exception. A test correctly rejecting a deliberately invalid fixture is a successful negative test, but the import itself was still rejected. If the sequence then proves safe correction/reselection, preserved prior state and a successful persisted valid import, it can support recovery `passed`. R6 024 provides such a case: raw recovery N/A is corrected independently to passed while the original receipt is preserved. Use `judge_missed_execution` for a supported N/A-to-passed correction.

Do not manufacture a failure or assume recovery from a later unrelated success. Keep recovery N/A where the complete evidence has no triggering failure, such as R6 032's acknowledged successful imports. A model sentence claiming all imports succeeded cannot override actual rejection observations.

## Publication and comparisons

The background finalizer owns exactly `summary.json`, `comparison.md`, `not-run-23-baseline.json`, `artifact-audit.json`, and `automated-outcome.json`. Do not stage unrelated files while it publishes. These outputs remain raw and marked pending manual review. The review helper preserves them and produces `reviewed-summary.json`, `comparison-reviewed.md`, and `evidence-review.md`; its scope is always the explicitly listed criteria.

Keep the whole-cohort population, old 23 unique missing criteria, and original 46 weighted / 32 unique mapping distinct. Only matched passed/failed results earn executed-coverage credit. not_run, N/A and unassessed are separate; a smaller assessed denominator must not be presented as coverage improvement. Preserve all four historical columns and report the fresh cohort as the fifth.
