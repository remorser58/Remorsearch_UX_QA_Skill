# Applying independent criterion review

This offline utility runs after the durable finalizer has published the new cohort's five raw files. It never calls a model/browser, resumes a queue, changes a raw receipt, or edits historical comparison columns.

## Validation

The final helper and tests passed **26 offline cases in one run, 4.746 seconds, zero failures/skips**. An independent code review checked eligibility, history pins, artifact admission, coverage mapping and output preservation. Actual R2 log-17/PNG-17 admission was also checked read-only; those are historical fixtures for the validator, not new-cohort verdicts.

- `apply_criterion_review.py` SHA-256: `43256fa19c0324f9f81dac95b4f05fbaa329a3ade6eb020fb1d0a5a1dc4a6d25`.
- `test_apply_criterion_review.py` SHA-256: `180276d7dcd647b50ff02c92a352e845329c6d0477c249577a41adeb05669659`.

The actual evidence log precedes checkpoint artifact-registration metadata. The utility verifies that admission metadata and receipt registration, then checks the remaining full observation body; it does not require byte equality between different representation layers.

## Command

Only after the actual raw cohort and artifact audit exist:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/m4mini/.local/bin/python3.11 \
  docs/validation/peekly-coverage-completion-20261115/apply_criterion_review.py \
  --stage .ux-loop/peekly-completion32-pinned-20261115/stage-32 \
  --output docs/validation/peekly-coverage-completion-20261115 \
  --review docs/validation/peekly-coverage-completion-20261115/criterion-review.json
```

Outputs: `reviewed-summary.json`, `comparison-reviewed.md`, `evidence-review.md`. Existing outputs are never overwritten. The raw five files and first four historical columns remain unchanged.

## Review input

Schema: `peekly-completion-criterion-review.v1`. Required top-level fields are `stage_root`, `plan_sha256`, `raw_summary_sha256`, `artifact_audit_sha256`, a truthful `scope`, `raw_receipts_modified:false`, `new_model_calls:0`, `new_browser_calls:0`, `queue_writes:0`, and nonempty `decisions`.

Each decision binds actual `job_id`, `persona_id`, `kind`, `index`, `requirement_id`, `result_sha256`, `expected_raw_status`, `reviewed_status`, `reason`, `classifications`, and cited `evidence`. Each evidence row uses the actual registered `artifact_id`, receipt-relative `path`, `sha256`, `observation_id`, and `purpose` (setup/action/result/context). At least one result-purpose execution log is required per decision. PNG evidence must also match that admitted observation's capture registration.

Permitted classifications: product_defect, runner_limitation, fixture_precondition, judge_false_pass, judge_false_failure, judge_missed_execution, judge_unfounded_execution, conditional_not_applicable, confirmed_raw_verdict. An unchanged verdict may be explicitly reviewed. Success N/A is forbidden; conditional recovery N/A earns no execution credit.

Uncertain, incomplete and current-invalid sessions cannot be reviewed into eligibility. No old job override is transferred. Unlisted criteria and session outcomes remain unchanged. A changed criterion cannot silently resolve an independent session-level problem or missing judgment; inconsistent metadata preserves the original outcome with an `outcome_review_constraint`. Normal runtime problem results are already excluded, so this defense is not evidence of a new product/run defect.

## Reading the output

- Whole new cohort: `candidate`.
- Old 23: `reviewed_coverage.baseline_23.weighted.counts` separates passed/failed/not_run/not_applicable/unassessed. `executed` counts only passed+failed.
- `independently_reviewed_executed` reports the part explicitly checked in this independent review.
- Original 46 weighted rows and unique mappings: `reviewed_coverage.baseline_46.weighted` and `.unique`.
- Actual decision changes: `independent_review.decisions`, `session_changes`, `delta`.

Review status remains `listed_criteria_reviewed`, never an unsupported claim that every criterion received independent semantic review. Smoke participants are not added to the new 32-person denominator.

