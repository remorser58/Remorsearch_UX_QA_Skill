# Peekly action deadline follow-up — offline validation

Date: 2026-11-15 (Asia/Seoul).

## Source and scope

- Isolated branch: `rem/peekly-action-deadline-20261115`.
- Base: `74d9288b29e54060bd223edc6e2168587df3f3d5`.
- Worktree: `.worktrees/peekly-action-deadline-20261115` inside the completion worktree.
- The running R5 source and its old queue, observations, uncertainty and process ownership are unchanged. Integration requires the coordinating run to become terminal first.
- No provider, actual model, real browser, product fixture target or existing process was invoked by this follow-up. Authored fixture callbacks and owned Python test subprocesses are separate from actual UX execution.

The coordinating R5 record reports a host `TimeoutError` for 022's upload of `peekly-missing-followers.zip`, while the driver had already written a screenshot. The prior code's action exchange ceiling is confirmed to be 25 seconds. Screenshot existence and modification time do **not** identify the blocking step or prove that a full response reached the host. Synchronous fixture reads, capture writing, pipe backpressure and parent event-loop delay remain possible explanations; this change does not assert which occurred.

## Deadline and response contract

| Layer | Budget | Boundary |
| --- | ---: | --- |
| Node startup | 60 seconds | Full fixture validation, Chrome startup and initial observation |
| Python startup exchange | 70 seconds | Includes the startup reply margin |
| Node action | 80 seconds | One action, its observations and capture write |
| Node normal reply flush | 5 seconds | Exactly one packet write; no replacement packet after uncertain flush |
| Python action window | 90 seconds | Original action plus any allowed new observation after a known nondispatched click rejection |
| Queue tool call | 180 seconds | Startup plus action uses at most 160 seconds of configured host windows |
| Python close exchange | 12 seconds | Existing owned cleanup fallback and exact close response preserved |

The remaining 20-second Queue margin is for host admission and surrounding work. The deadline test reads the actual Node export, Python host values and `live_limits()`; it does not infer them from prose. Parent synchronous receipt processing and a system-wide I/O stall are not eliminated by these budgets.

The separate five-second reply-flush bound can stop a command if the parent or pipe remains stalled beyond that limit, even after a screenshot was written. It is an explicit fail-closed bound, not proof that the unobserved R5 bottleneck has been removed.

The known nondispatched click recovery remains one rejected click followed by a distinct observation. Both exchanges now share one 90-second window, so they cannot consume 90 seconds each after a 70-second startup. An uncertain click is never retried.

Independent review identified an event-loop ordering edge in that shared timer. A total monotonic postcheck now rejects the response before admission even when each individual exchange was within its own deadline but the combined action window was exceeded. The regression controls only the host clock, leaving asyncio's timer clock real, and exercises two actual exchanges of 60 simulated milliseconds each against a 90-millisecond total window. A separate check before the recovery observation prevents even that read-only follow-up from being dispatched after the shared window has already expired; its regression verifies exactly one original click packet.

## Implementation

### Abort-aware actions and diagnostics

- A per-action controller starts before action execution, with a fixed 80-second deadline.
- Phase records include command ID, action, phase, elapsed time and preceding phase duration. DOM observation, storage observation, upload fixture validation, target resolution, dispatch, screenshot capture/write and response writing are distinguishable.
- Clock checks occur before further CDP dispatch, even if a blocked event loop has delayed the timer callback.
- A timeout or action abort preserves its poisoned signal. A late asynchronous continuation cannot obtain a fresh, un-aborted action context.
- The host records dispatch start, expected deadline, elapsed time and error class. A response returned after the exchange deadline is not admitted because of event-loop callback ordering.
- Driver timeout/abort/CDP-timeout errors poison the host channel. Existing owned process-group teardown remains responsible for cleanup; none of these paths resend the original action.
- Driver phase files are bounded diagnostic records, not admitted UX evidence or delivery acknowledgements. A pipe write callback proves that the driver wrote its response, not that the queue accepted it.

### Fixture and capture integrity

Every selected upload entry still undergoes full name, regular-file, symlink, real-path, byte-count and SHA-256 validation before `DOM.setFileInputFiles`. File reads are asynchronous and receive the action abort signal. No fixture integrity check was removed or moved after upload.

Capture creation uses an exclusive `wx` open with mode `0600`, private-file checks, the full byte count and SHA-256. A delayed open that completes after cancellation is closed before writing. A write that was already in flight may leave an unadmitted partial file; it is never counted as a completed capture, overwritten or retried. The host still independently validates admitted capture paths, permissions and exact bytes.

The legacy seed's fresh-owned-profile, first-mutation, full storage digest, one-shot latch and synchronous intent-before-write sequence are unchanged. The action deadline cannot authorize a second seed.

### Close contract

The host wire response remains exactly `{"stopped": true}` or `{"stopped": false}`. Rich cleanup details stay in the lifecycle record. Existing tests exercise the real host `call()` and `_exchange()` through Queue and ScaleExecution; confirmed group closure completes current-valid receipts, while unconfirmed closure remains blocked with ownership retained.

## Offline regression

Command, run from the isolated worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests \
/Users/m4mini/.local/bin/python3.11 -m unittest \
  test_scale_browser_action_deadline \
  test_scale_browser_lifecycle \
  test_scale_browser_close_contract \
  test_scale_browser_guardrails \
  test_scale_run
```

Final result after independent review: **35 Python test cases passed, zero failures, zero skips; exit 0; 55.958 seconds.** The driver wrapper also ran the Node guardrail, scroll, legacy, lifecycle and new action-deadline suites. Earlier 33-case and 34-case passing runs are preserved as intermediate records rather than substituted for this final run.

- Preserved final log in the main completion worktree: `.ux-loop/peekly-action-deadline-regression-final-20261115.log`.
- Log bytes: 73,898.
- SHA-256: `f8e52810d1666fc389c77d81cf1607398c281bd7ef34f90b780b25d1c8b68b36`.
- Intermediate logs are also preserved there as `peekly-action-deadline-regression-20261115.log` (SHA `bdb61ebbbbac891c06ef6703478d51a675d64c9e0a2ff767f64c0c0eb69f1902`) and `peekly-action-deadline-regression-v2-20261115.log` (SHA `f8f82b417eca34f073a9af3a39b8db002c3f04d1ffdad75ac9ae0b21b1b93a19`).
- `git diff --check` passed.

Final tested runtime bytes: Node driver SHA `8d758a9b1f7fc8f4e09ffba37a78897db4caedc2bb04476ce3ea20cc9dc31e97`; Python host SHA `510923c6f62a625d0299187ab1b86fa7fce68fb81c3c2c4d7063ab461ea3a636`.

The focused cases cover a single delayed response, the scaled old 25-second deadline versus the new 90-second budget, late response after event-loop delay, shared click/observe budget, driver timeout poisoning, unchanged single dispatch, late file reads, late capture open/write, capture permissions and overwrite refusal, pipe backpressure, uncertain reply flush without replacement, exact close shape, real SQLite receipt completion and real owned-child process-group exit.

These are offline checks. A new smoke must independently demonstrate actual execution improvement after integration. No remaining-not-run reduction, R5 completion, release readiness or 32-person coverage is claimed by this document.
