# Peekly headless user-task pilot

This pilot connects four frozen tasks to a fresh build of the actual copied
Peekly application. It reuses the prior pilot's four saved PRD-hypothesis persona
profiles, the product's `buildSampleExportZip`, and the prior
`expanded(rows)` synthetic-data construction. It does not create public-community
research evidence, real participants, or a claim about general UX effectiveness.

The product checkout is never the execution or generation root. Its approved
64-file copy and one build have a separate preservation receipt. No dependency
installation, product-source edit, dev server, existing browser connection,
account login, user-input device, clipboard, or model API is used here.

## Frozen tasks

| Task | Reused profile | User goal and measured boundary | Actions |
| --- | --- | --- | --- |
| T-SAMPLE | P-EXPLORE | Enter the built-in sample; read the 7/10 relationship counts, five-person nonreciprocal list title, six-person comparison title and limitation; exit the sample. | 6 |
| T-RECOVER | P-RETURN | Import the previous ZIP; reject missing following data; retain 12/12 results; import the current ZIP; read 7/10 results and six departures with the limitation. | 11 |
| T-LARGE-ZIP | P-ARCHIVE | Import the fixed 150,000-row ZIP inside the documented byte limits; observe the actual goal result or error; retain the earlier record and recover with the small current ZIP. | 10 |
| T-LARGE-JSON | P-ARCHIVE | Exercise the same fixed goal with all 12 loose JSON files through the visible file-selection flow. | 10 |

P-KEEP remains unchanged in the saved profile set. This pilot does not execute its
storage-fault, retention, or folder-provider tasks. T-RECOVER observes in-session
error recovery, not app-reopen onboarding resume.

The two large tasks still require **150,000 followers and 150,000 following**.
A product rejection is a goal failure even if the subsequent small-file recovery
succeeds. The generator never calls the product parser, so fixture generation
cannot establish acceptance or failure.

### Exact measurement contract

`run_pilot.py` splits each composite protocol criterion into independent
`task_checks`. Every resulting success/recovery index maps one-to-one to a
native check at a fixed action index. `criterion-map-v2.json` retains the original
protocol criterion kind and index.

Text checks use explicit `normalize_whitespace: true`: trim and collapse Unicode
whitespace, including NBSP, to one space. The words, numbers, original text and
PNGs are preserved. Input-value checks do not receive this option.

Selectors are plain CSS. Counts use
`.result-hero-meta > :nth-child(1 of .stat)` and its second-child counterpart.
This selects by the `.stat` class even when the application's Korean-line-break
observer inserts other spans.

Each scenario also declares its deduplicated check selectors in `targets.status`.
This retains the measured element ID and geometry in captures even when the
Korean-line-break observer wraps the element's direct text in child spans. The
expected values and pass rules are unchanged.

The large-input checkpoint follows a fixed 1,000 ms wait. Its selector chooses
one visible result count when no sheet is open, or the actual notice in an open
sheet. The expected text stays `팔로워 150000명` or `팔로잉 150000명`.
Missing, ambiguous, obscured, changing, or unfinished observations remain
unobserved; the harness does not replace them with a pass.

Before execution, click actions are fixed at a 500 ms settling interval and upload
actions at 1,000 ms so Worker startup and React transitions have a bounded chance
to complete before capture. The large-input task retains its additional fixed
1,000 ms wait. These are checkpoint settling times, not a human-performance
measurement or an adaptive wait selected after seeing an outcome.

The recovery sequence is fixed to the suspected error branch. If the large input
unexpectedly succeeds, there is no error-dialog close target. That recovery
sequence remains unvisited instead of adapting, retrying, or changing the input.

Automatic list checks cover the title/count and comparison-limit message. The
existing privacy gate rejects literal handle expectations and is not weakened.
Individual row/name identity can be compared separately using actual PNGs and the
source-based expected sets in `protocol.json`; that comparison is not included
in automatic receipt success. Synthetic handles must never be visited as URLs.

## Synthetic fixtures

The generator reads the reviewed **copied** `src/core/sampleData.ts` and copied
TypeScript 5.7.3 / fflate 0.8.3 packages after checking their recorded hashes. It
transpiles only that sample module in memory. The sample module sees a fixed
Date; the ZIP writer receives a fixed mtime and UTC. No compiled helper is written
into the product copy.

The 17 fixtures total **24,573,378 bytes**, below the 32 MiB registry budget:

- Built-in previous and current sample ZIPs.
- The current ZIP with its following entry removed.
- A 5,000-row ZIP control, generated for reuse but not an executed UI control in
  this four-task pilot.
- A fixed 150,000-row ZIP: **816,720 bytes**.
- All 12 corresponding loose JSON files, including the synthetic account metadata.
  The two relationship files are **11,850,001** and **11,850,029** bytes;
  the complete uncompressed bundle is **23,712,900 bytes**.

The large rows exactly reuse the earlier construction:
`owned_fixture_` plus a six-digit zero-padded index and timestamp
`1700000000`. Every other built-in sample entry remains unchanged. The original
account archive data is never read.

`protocol.json` freezes every fixture ID, path, upload filename, MIME type, size,
and SHA-256. `fixture-manifest.json` has SHA-256
`2d713311b2bb742c886cbad450fd587862fd0b4d71143257d08bf45998234a2d`.
A later generation refuses a different byte set. The output directory must be
new; the generator never overwrites or deletes previous files.

For this pilot generation used pinned Node v22.16.0 in a restricted environment,
with an unprivileged `sandbox-exec` policy denying all network operations and
reads/writes under the original Peekly checkout. ZIP timestamps are fixed only in
the generator. Do not hold the application's browser clock at one millisecond:
its snapshot IDs include import time.

## Prepare, run once, read back

All mutable records belong under an approved ignored stage. The stage must
already contain:

- `product-build/`, the reviewed fresh product copy and its dist.
- `product-build-receipt.json`, `product-dist-manifest.json`, and their source /
  dependency provenance manifests.
- `synthetic-fixtures/fixture-manifest.json`, `generation-receipt.json`, and the
  17 frozen fixture files.

Use the repository's existing Python environment and the explicit absolute stage:

```sh
python3 -B benchmarks/peekly-headless-pilot/run_pilot.py prepare --stage /absolute/owned/stage
```

Preparation refuses an existing `ui-pilot/`. It verifies the frozen build receipt,
the exact six dist files, PRD and fixture hashes. It creates only a small reviewed
UI source set, an existing-format persona Library, the measured adapter/plan and
a workspace:

- `ui-pilot/source/`: six build files, PRD, 17 fixture inputs and browser adapter.
- `ui-pilot/persona-library/`: the four profiles.
- `ui-pilot/operations/`: a separate real CLI process for each import/list/reuse.
- `ui-pilot/reviewed-plan-v2.json` and `criterion-map-v2.json`.
- `ui-pilot/work/`: the existing workspace's reviewed copy.
- `ui-pilot/prepared.json`: benchmark, source, Library, workspace, plan and adapter
  hashes; it explicitly records that no browser or attempt was created.

The persona import is repeated identically to demonstrate revision reuse.
Profiles differ from the original protocol only in the required `PER-` library
ID prefix and the union of requirement IDs actually assigned to that profile.
P-KEEP is stored and reused but receives no task.

The first preparation in this session stopped before Library import because the
terminal's default Python was below 3.10. Its exact rejection remains in
`ui-pilot/operations/001-import.json`; no browser, Library, workspace or attempt
existed at that point. The approved interpreter is
`/opt/homebrew/opt/python@3.14/bin/python3.14`.

The explicit `resume_prepare` mode is limited to that known prerequisite
rejection. It requires the exact partial-root allowlist, unchanged product and
fixture bytes, frozen original adapter/plan/criterion-map hashes, identical
persona-input bytes, and no Library, workspace,
prepared marker or run intent. Existing regular files with one link and identical
bytes are left untouched; any mismatch is refused. It records one preparation
resume request and appends new CLI logs. It neither deletes nor copies the
product/fixture inputs again. A completed preparation or task execution cannot
use this recovery mode.

Before any execution, independent review identified that the large tasks also
needed visible 12/12 baseline measurements immediately after their first upload.
Revision v2 adds those two checks to each large task's same preservation
criterion; the 10 actions and all fixture bytes stay fixed. Each large task now
has eight automatic checks. This is an authoring correction without a product
outcome. The earlier `source/browser-adapter.json`, `reviewed-plan.json` and
`criterion-map.json` remain byte-identical at their original paths. The new
`source/browser-adapter-v2.json`, `reviewed-plan-v2.json` and
`criterion-map-v2.json` are selected for execution. The old source adapter is
excluded from `workspace.prepare`'s reviewed file list, and its frozen hash is
retained in `protocol.json` and the preparation receipt.

Preparation performs Python schema, binding and privacy checks, followed by the
real bridge's pure `--validate` path under network denial. It creates no runtime
probe, browser or execution attempt. The normal driver still validates inputs
and freezes its exact runtime before the first claim.

Only after the protocol, runner, adapter, plan and runtime have been reviewed and
frozen should the authorized host invoke:

```sh
python3 -B benchmarks/peekly-headless-pilot/run_pilot.py run --stage /absolute/owned/stage
```

The host supplies the already approved isolated Node/Playwright/Chromium runtime
through the existing local-run environment. The runner performs no runtime
download or install. It calls `local_run.execute(..., approved=True)` exactly
once, writes a first-run intent before calling it, and refuses another run request
if the intent or execution ownership marker exists. A failed or uncertain launch
is not an invitation to reset or redispatch.

The adapter lists the exact reviewed module Worker path. Worker execution is
subject to the existing process network-denial requirement. Upload actions click
the owned page's visible file button and fulfill that page's Playwright
filechooser with frozen buffers. They do not invoke an OS file picker.

For subsequent inspection:

```sh
python3 -B benchmarks/peekly-headless-pilot/run_pilot.py readback --stage /absolute/owned/stage
```

Readback calls `workspace.status` only. It cannot launch a browser or create
another attempt. Keep per-check failures, unobserved checks, recovery results,
actual file-selection receipts, module Worker activity, screenshots and cleanup
acknowledgements separate in any result report.

On successful command completion, `prepare`, `resume_prepare` and `readback` exit
0. `run` exits 0 only when the returned `task_scope_passed` is exactly true;
otherwise it exits 1 even if report generation completed normally. A produced
report is not automatically a passed user task.

The source and fixture bindings prove what was supplied. Only the eventual
native run and its admitted evidence prove what the application did. Neither
constitutes a real-user study or a measured comparison of persona methods.
