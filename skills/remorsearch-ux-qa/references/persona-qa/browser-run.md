# Run saved-persona tasks in an owned local product build

This is the bounded browser alternative to [local-run.md](local-run.md).
The host prepares it from the user's product folder and ordinary-language goal.
The user does not write a scenario, manifest, receipt, runtime path or lease.

## 1. Choose the supported surface

Read the PRD, relevant source and existing persona/research evidence first.
Use this path for reviewed, owned static HTML/CSS/JavaScript and synthetic inputs.
An actual SPA production build is supported when it is self-contained in those
reviewed assets. Preserve its exact bytes and source/build manifest; do not replace
it with a lookalike page. Build only an authorized owned copy, reusing inspected
dependencies, and record that separate build's command, hashes and source boundary.
Reuse the original Library and current research gates. The installed driver
operates fixed tasks; it does not invent research or role-play an autonomous user.

A production account, backend, arbitrary URL, existing localhost service, user
browser, persistent profile or unreviewed executable is outside this path.
If a product requires those surfaces, report that exact gap and continue the
authorized analysis. Do not turn a backend into a fake successful fixture.

Review the actual page behavior and every included file. The runtime serves only
the frozen file bytes at https://remorsearch.invalid/. HTTP/WebSocket requests
have no forwarding fallback, RTC/WebTransport constructors are disabled before
page code, and unexpected popups/downloads block the session. The document guard
does not cover Worker realms. Worker plans additionally require the process
network restriction below. Neither path grants execution of unreviewed code.
No package installation happens inside a journey.

## 2. Prepare and execute

Use the existing start/run/status commands. The host selects each exact relative
file through repeated --include options, chooses current saved persona versions
and writes the plan from the inspected product goal. Keep source, original
Library, optional reviewed research and execution workspace separate.

The browser plan has the same five fields as the Python plan:

- schema_version: ux-journey-browser-plan.v1
- product_id: current Library product
- runner: reviewed copied JSON adapter, not a command or executable
- timeout_seconds: integer 1–30
- tasks: existing swarm task records, including predeclared PRD obligations

The adapter is ux-journey-browser-adapter.v1 with a journeys array. Each item has
exactly task_id, scenario, device_id and criteria. Every task appears once.
Optional uploads and workers declare the additional reviewed inputs; omit them
for the original static-page contract.

Reuse the existing ergo-scenario.v1 schema. Set a reviewed static HTML URL at the
fixed origin, one device ID, the exact task goal and 1–16 explicit actions.
Omit surface.build_id; the host engine injects the current prepared-build hash.
Only measured success.task_checks are accepted. Each check has an explicit
1-based after_step, and every success/recovery criterion maps one-to-one through
{kind, index, check_id}. Unmapped checks and criteria are rejected before claim.
Action input and check values must be owned synthetic data.

The existing driver defines exact value/text/checked comparisons, from_step,
redaction and capture timing. Native success is reconstructed from those
checkpoints. A later successful recovery never erases an earlier mismatch.
Text checks may explicitly set normalize_whitespace: true to compare visible
text with NBSP/line wrapping folded to ordinary spaces. This option is forbidden
for value and checked; it does not change screenshots, product state or wording.
Missing targets, unvisited checkpoints and targets absent/offscreen/obscured or
with unsupported visible geometry remain not_run. A DOM match alone does not
prove the user saw a successful result, understood it or found the task easy.

The host's --allow-reviewed-local-runner flag records existing source/input
review authority. It does not grant new permissions or require another user
approval when that scope is already authorized.

## 3. Runtime and finite ownership

Use already prepared Node 22, Playwright 1.56.1 and its matching Chromium.
The host can select an existing Node binary with REMORSEARCH_JOURNEY_NODE and
existing package/cache locations with NODE_PATH and PLAYWRIGHT_BROWSERS_PATH.
Canonicalize those locations at preflight. The initial probe launches no browser.

Freeze the resolved Node, driver, Chromium executable, Playwright/core package
roots and hashes before dispatch. Each execution loads the exact pinned package
and core, with a sanitized environment; it does not inherit browser attachment
endpoints, Node options, credentials or the user's home. Runtime changes block
new dispatch without consuming a new attempt. Historical readback validates the
saved evidence without requiring the old runtime to remain installed.

The existing limit is 1–16 tasks, serial dispatch, one attempt per task and at
most 240 seconds of configured browser time. One owned headless Chromium is
closed before another task starts. Browser close and process termination are
required; parent timeout allows up to five seconds for graceful cleanup.
If closure cannot be confirmed, keep the intent and stop subsequent dispatch.
Never signal stored PIDs after restart or reset attempts through a new workspace.

Limits also include 64 static files, 2 MiB per file, 16 MiB total, 64 task checks,
256 KiB request/pipe output and 64 MiB native browser evidence per task.
Typing defaults to zero per-character delay in this finite scripted path.

### Owned uploads and module Workers

Declare uploads as up to 32 objects with exactly id, path, name and mime_type.
The path must be one of the reviewed files copied under product/. The engine
freezes its byte count and SHA-256. Each action names up to 16 unique IDs:

```json
{
  "action": "upload",
  "target": ".sheet-body > button.btn-hero",
  "input": ".sheet-body input",
  "files": ["ZIP-PREVIOUS"],
  "timeout_ms": 5000
}
```

The visible target activates the product's actual file input. The driver arms a
Playwright filechooser before pointer dispatch, verifies the owned page/input,
then transfers only the frozen in-memory buffers. It never accepts an action
path, reads a user-selected personal file, opens an OS picker or assigns a
fabricated FileList. Generic CLI/serve sessions have no upload registry.
Limits are 16 MiB per upload file, 32 MiB for the whole registry/selection and a
5-second chooser timeout. File selection is input evidence; product parsing,
errors, preservation and comparison require separate measured checkpoints.

Declare workers as up to eight exact reviewed .js/.mjs asset paths. The CSP
permits only those entry URLs and keeps connect-src 'none', with no HTTP fallback,
service workers or SharedWorker. Original Worker bytes are never rewritten.
Worker plans currently require macOS /usr/bin/sandbox-exec with the literal policy
`(version 1)(allow default)(deny network*)`. Freeze the launcher hash and policy
hash, and use the same launcher for preflight and every dispatch. Unsupported
platforms, policy changes or failed denial probes stop before a claim; there is
no plain-Node fallback. Each execution also requires an explicit OS refusal of
an owned ephemeral loopback bind before it can launch a Worker-capable browser.
That refusal is an execution check, not independent kernel attestation of the
whole policy. The security boundary is the frozen Python launcher together with
the network-denial capability validation; direct bridge calls are not a substitute.

Use the matching, already-installed Chromium headless shell resolved by the
pinned Playwright registry for Worker plans. The full macOS Chromium app needs
ProcessSingleton sockets outside its profile and cannot run under this policy.
Do not widen the network policy to make that app start. This is a process network
restriction, not a general filesystem sandbox. Both the native browser close
acknowledgement and direct child termination remain mandatory.

## 4. Evidence, failure and readback

The engine binds each native run to task, operation, attempt, build, scenario
and exact persona/profile/PRD revision. Step before/after anchors, measured
checkpoints, snapshot identities, reviewed page URLs and PNG hashes are checked.
The existing swarm receipt gate decodes PNGs and requires log/capture evidence.
Successful upload steps must also match the current fixture IDs, sizes, hashes,
MIME types and selected input. Display names obey the existing redaction rules.
Native owned-input metadata omits upload paths/names, and observed served assets
and Worker starts carry the corresponding reviewed hashes. These records show
this isolated product execution; they do not establish participant behavior.
The independent deterministic audit reconstructs the receipt from stored native
evidence; it is not an independent human/model evaluation of the product.

Confirmed-cleanup timeout or cancellation may preserve earlier valid checkpoint
failures. An incomplete tail action and unvisited recovery remain unobserved.
A stopped/partial run cannot pass, even if its earlier checks passed.

Completed run/start/status calls read back the same content-derived reports
without browser execution or file rewrites. The current report lists exact saved
personas, criterion outcomes, reproduction actions, evidence paths, duplicates,
conflicts, gaps and next steps. It sets real_user_evidence and product_ready to
false. ui_observed means admissible owned static browser observations exist.

run exits 0 only when the measured task scope, declared requirements and audit
are all complete and passing; this is not product readiness. Failure, conflict,
partial or Python-only scope exits 1. Invalid input/runtime/preparation exits 2.
Status exits 0 for a generated report regardless of the QA verdict.

## 5. Installed diagnostic

Run examples/journey/run_browser_fixture.py --out NEW_DIRECTORY with an already
prepared runtime. Add --research to reuse the bundled invented research export
through the real merge/gate/Library path. Existing directories are refused.

The diagnostic uses an intentionally defective input-retention path and a normal
control. Expected product-task outcomes are failure 1 / pass 1. It verifies
the earlier failure survives final recovery, original source/Library/research
preservation, and identical readback with no redispatch.

This is real browser execution of an authored synthetic page with known answers.
It is not Peekly execution, public community acquisition, actual participants,
an effectiveness comparison or measured real-user UX improvement.
