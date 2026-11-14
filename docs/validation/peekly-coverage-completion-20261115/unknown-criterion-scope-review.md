# UNKNOWN criterion scope — independent review

**Recommendation:** known-empty is a classification guard, not an additional required live scenario. Retain 021/022 UNKNOWN passed if their admitted migration/current/exclusion proof stands; this interpretation supplies no execution evidence.

## Bound requirement

Personas 021–024 share success[2], `PRD-IMPORT-SNAPSHOT-UNKNOWN`, mapped to `O-PRD-3`:

> 목록이 실제로 비어 있었는지 알 수 없는 과거 백업은 비교 대상에서 제외한다. [PRD-IMPORT-SNAPSHOT-UNKNOWN] a legacy snapshot with unknown included-file provenance is excluded; a recognized empty import is known-empty

The pinned product PRD, `.ux-loop/peekly-pinned-product-51110f4-20261115/source/docs/PRD.md`, §3, line 82, contains the original Korean legacy-exclusion requirement. Its SHA-256 matches the plan binding: `a014a85b7523928f693cd4422793929631f033176715f31409412e95e1d7432b`.

The fresh plan is `.ux-loop/peekly-completion32-pinned-20261115/stage-32/plan.json`, with envelope hash `59f2c770425f85dd834542349f1915f084ca8fc6129c421cc907b4127d0212d8`. All four bound task goals have SHA-256 `d4e32b906f27d5d3fa7211624bae2565f0f26e7bf03992a570b6a739c370deb0`.

## Why this is a guard

The original obligation concerns unknown historical provenance. The bound goal and required-step checklist specify exactly two UNKNOWN fixtures: validated legacy-state JSON and current ZIP. They require the seed first, then only current, then the actual retained-record exclusion/next-record explanation before another known import. After that checkpoint, they direct execution to other criteria's normal pair. They expressly say a known-empty ZIP cannot substitute.

Read alone, the semicolon could join two assertions. The explicit executable contract resolves its purpose: distinguish recognized empty input from unknown legacy provenance, preventing empty input from falsely satisfying UNKNOWN. There is no separate empty-import obligation or required step to waive.

## Frozen sources and tests inspected

The following implementation/tests were read and verified byte-identical to runtime `f50d082a197e683b5961d17919fe219dc48c4d55`; tests were not rerun.

- `skills/remorsearch-ux-qa/uxpersonas/peekly_criteria.py`: UNKNOWN definition and `legacy_scope_evidence` require validated migration, one current import and actual exclusion; known-empty input is insufficient setup.
- `skills/remorsearch-ux-qa/uxpersonas/scale_entry.py`: required fixtures and UNKNOWN steps define the same checkpoint, without an empty-upload step.
- `tests/test_peekly_result_scope.py`, `test_definition_separates_recognized_empty_input_from_unconfigured_legacy_state`: explicitly requires “known-empty” in the expected value while excluding `upload peekly-empty-previous.zip` from the action.
- `tests/test_peekly_completion_scope.py`, `legacy_rows` and `test_validated_migration_and_actual_product_exclusion_pass`: the positive contract contains only seed/current/exclusion observations.
- `tests/test_coverage_planning.py`, `LegacyUnknownPlanningTests`: asserts the exact two fixtures and absence of an empty-upload instruction.
- `tests/test_peekly_legacy_seed.py`: requires a nonempty legacy seed without provenance. `tests/test_peekly_completion_launcher.py` checks the `known_empty_is_known` preflight attestation; it supplies no fresh cohort UI coverage.

The semantic review checklist's “Legacy UNKNOWN — 4 rows, 021–024” section independently specifies this same PASS boundary.

## Coverage limit

`known_empty_fixture_exercised: false`

No separate known-empty behavior is credited as freshly executed. Later negative-file or normal-pair imports cannot replace the preserved UNKNOWN checkpoint. Apply this interpretation to 023/024 only with their own complete, admitted proof; missing execution remains not_run, and uncertain jobs remain excluded. No new model/browser call, queue write or test execution was made for this interpretation.
