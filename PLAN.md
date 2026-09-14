# Implementation and packaging plan

## Environment and scope

Linux sandbox; all authored source lives in `/mnt/data/workdir`. The requested
macOS checkout `/private/tmp/ux-research-qa-pro-auto/worktree` and OMO installation
`/Users/r3m0r5e/.codex/plugins/cache/sisyphuslabs/omo/4.19.4` are unavailable.
Use the supplied repository ZIP as the implementation baseline and read the
supplied OMO ZIP without modifying it. No upstream branch/history is included;
local commits on `sandbox/ux-loop-implementation` are sandbox-only commits, not
commits to the user's original checkout. No push or deployment is authorized.
No visible planning tool is available; this file is the durable checklist.

## Checklist (maximum eight top-level items)

- [x] Inspect all original source, tests, evidence contract, and OMO reference surfaces.
- [x] Define a small versioned composition, browser/visual evidence, and permission contract.
- [x] Implement fail-closed offline validation and durable bounded state transitions.
- [x] Implement one-entry intake, fix/replay orchestration, checkpoint resume, and reporting.
- [x] Add happy, blocked, interrupted, visual-failed, unknown, and regression-failed tests/fixtures.
- [x] Document standalone installation, architecture, OMO provenance, usage, and limitations.
- [x] Run original and new tests/smokes; record output and local implementation commit SHA.
- [x] Complete source-only packaging and verify the sole `/mnt/data/result.zip`.

## Implementation plan

Preserve both independently installable skills and v1 evidence IDs. Add a small
standard-library Python composition layer and a separate versioned loop envelope,
not an autonomous monolith. Keep research ownership of provenance/claims and QA
ownership of real observations. Gate writes explicitly; do not infer permissions
from provider content. Keep synthetic fixture success distinct from live product
success. Use atomic checkpoints with immutable input identity and bounded retries;
accept fixes only after same-scenario replay against the fixed code revision,
pinned Figma readback and explicit visual/accessibility/regression evidence.

## Detailed stage instructions

Inspect OMO hooks, state/checkpoint and stop/continuation logic from the supplied
4.19.4 snapshot. Attempt public primary-source verification, record failures, and
avoid guessing an `omon` repository. No OMO source will be copied into the product.
Run original tests before changes. Add small modules and tests, then perform CLI
smokes from a fresh source-only extraction. Record each live integration that is
not executed and its blocking reason. Never report fixture runs as live evidence.

## Verification commands

Actually executed; detailed output is in IMPLEMENTATION_REPORT.md:

```sh
python3 scripts/validate_bundle.py tests/fixtures/valid-bundle.json
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/ux_loop.py validate examples/loop/packet.json --evidence-root examples/loop
python3 scripts/smoke_loop.py
(cd .ux-loop/fresh-source && python3 -m unittest discover -s tests -p 'test_*.py' -v)
(cd .ux-loop/fresh-source && python3 scripts/smoke_loop.py)
python3 -m compileall -q uxloop scripts tests
python3 scripts/ux_loop.py --help
git diff --check
find /mnt/data -maxdepth 1 -name '*.zip' -print
```

## Packaging criteria

Package authored source, configuration, tests/fixtures, README/docs and this plan.
Exclude `.git`, dependencies, virtual environments, build/runtime outputs, logs,
caches, browser profiles, and raw community data. Remove all pre-existing
`/mnt/data/*.zip` only after source/reference inspection is complete. Create exactly
`/mnt/data/result.zip` with `container.exec`. Check that `PLAN.md` is at the root,
check the exclusion list, and actually run the final `find` command. Mark completed
items before final packaging; do not hide unimplemented external integrations.

## Completed verification record

Original five tests passed before changes. Final suite: 93/93 passed; one of the
new tests exercises 1,332 wrong-JSON-type mutations without validator crashes.
Offline CLI smoke: 15/15 commands returned the expected success/non-success exit
codes. Source-only fresh copy without `.git`: 93/93 tests and 15/15 smokes passed.
Static example/fixture parity, documented patch prediction, compile checks and
Git whitespace checks passed. Original two skill trees, original v1 schema and
original test file are unchanged against the imported snapshot.

Implementation commit: `906ce0afed065e8a8401723d587d843f2f2cbf5d` on
`sandbox/ux-loop-implementation`. This is a sandbox-only commit, not the user's
unmounted macOS checkout/current branch. No upstream push or deployment occurred.
Only authored delivery metadata is updated after this code commit.

Initial `/mnt/data/result.zip` was created with `container.exec` from tracked
source files, after deleting all prior `/mnt/data/*.zip`. ZIP CRC, root PLAN.md,
source-only exclusions and actual final-path enumeration passed (one root ZIP,
`/mnt/data/result.zip`). This completed checklist is then included in the final
regenerated ZIP and the same checks are repeated. Runtime artifacts, caches, Git
metadata and input/reference archives are not packaged. See DELIVERY.md.
