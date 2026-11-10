# Keyboard recovery after asynchronous state changes

Use this focused task recipe for dialogs, imports and forms whose active
controls become disabled, disappear or are replaced during work. It supplements
the product task, not a separate screenshot audit. Record build, PRD obligations,
start state and expected behavior before execution. If task assignment happened
after an exploratory run, report that run separately; do not invent a prior claim.

## Exercise the transition

1. Start in an isolated approved state. Use actual Tab/Shift+Tab and Enter/Space
   to reach and invoke the task. Record the focused role/name and visible state.
2. Provide a safe invalid input through the invoked control. Observe the busy
   phase, including whether the focused initiating control becomes disabled.
3. When the error appears, record active focus and whether it is inside the
   still-open dialog. Check subsequent Tab and Shift+Tab destinations. Do not
   programmatically focus a control to hide the product's recovery behavior.
4. Retry using valid approved data and actual keyboard invocation. Compare
   storage/results with expected values; an error must not replace prior valid
   state. Record whether reselecting the same input is possible where applicable.
5. Verify close/Escape and focus return. If the opener was removed on success,
   inspect the next meaningful action and declared navigation behavior. BODY
   focus alone does not establish severity; document task impact and the next
   keyboard destinations.

Keep a still-open dialog's focus containment separate from closing it and
restoring focus. A successful retry does not erase a failure in the error state.
Never substitute a pointer-only test for keyboard recovery.

## Cancellation during processing

Start with a nonempty approved synthetic record. While loading/processing,
check whether close, Escape and any promised cancel control are available.
Record cancellation acceptance separately from dismissal and later commits.
If cancellation cannot be invoked, mark late-result-after-cancel checks not_run,
not another failure. Compare prior stored bytes before/after incomplete work.
A bounded delayed local response can expose a transient phase; document exactly
what was delayed, preserve served product bytes and do not report natural timing
or worker execution that the delay prevented. Release owned delays and close
the test browser/server, including on failure.

## Evidence and limits

Record each action, resulting UI state, focused element, outcome and time.
Screenshots cannot establish focus isolation on their own. Include actual
runtime/build hashes and distinguish an existing built artifact from a fresh
source build. Preserve failed harness attempts separately from product findings.
For visible labels, handle rendered nonbreaking spaces deliberately without
altering the product text or accepting a different control.

If a browser filechooser was opened by Enter but automation supplied the files,
that proves application-level invocation, not native OS picker keyboard use.
State screen reader, real-device, native UI and other excluded checks explicitly.
Keep setup errors, unavailable controls and unvisited states as not_run/blocked.

For every outcome, separate:
- PRD-linked obligation and its actual result.
- Technical focus/recovery observation, expected behavior and impact.
- Synthetic persona assumptions and unmeasured real-user effects.

Changes still require product-edit authority and the project's design/intent
checks. A verified defect in a QA target does not authorize changing that target.
