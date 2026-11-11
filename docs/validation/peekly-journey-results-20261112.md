# Peekly core journey pilot results — 2026-11-12

## What ran

Web Pro authored and ran the frozen core pilot in an isolated copy of Peekly, bound to the dirty-source manifest recorded in the protocol. Four synthetic PRD-hypothesis personas were persisted in the real Remorsearch library and reused across fresh CLI processes. Five tasks produced actual execution receipts: **1 failed, 4 inconclusive, 0 passed; product_ready=false**. No browser, DOM, React App, native UI, real account, or independent participant was exercised. This was directed reproduction of a prior large-import hypothesis, not blind discovery or proof of improved UX.

## Confirmed user-goal blocker

The fixed 150,000-row-per-list input is within documented byte limits: ZIP 816,720 bytes, largest JSON 11,850,029 bytes, total files 23,712,900 bytes. Both actual aggregate ZIP and loose-JSON entry points reject it with `InstagramExportFormatError: followers_1.json 파일 형식이 맞지 않아요`. The standalone JSON parser returns all 150,000 rows. The 5,000-row control succeeds. Two independent attempts reproduce the failure; previously stored bytes remain identical and small-input recovery succeeds. A valid large export therefore appears malformed to the user. Spread-based aggregation exists in the inspected source, but a production fix has **not** been applied or validated here.

Other core checks cover built-in sample comparison, interrupted onboarding state, invalid import rejection, storage-error recovery, and folder-export deduplication. Their core criteria succeed, but whole UX outcomes remain inconclusive because interface obligations were not observed.

## Measured evidence

See the adjacent minimized JSON for exact commands, measurements and hashes. Existing Peekly tests: 105 passed, 3.39 seconds, maximum RSS 374,358,016 bytes. Typecheck and build succeeded. The second large-input reproduction took 1.00 second and maximum RSS 404,586,496 bytes. RSS is macOS time's process measurement, not the sum of every child or total machine memory.

The baseline schema/authoring repairs were retained: requirement obligation IDs were made unique before dispatch, and PER-KEEP gained the existing R-IMPORT binding, without changing frozen goals or criteria. Repeated identical imports did not create additional persona revisions. The observation files distinguish core execution from UI and real-user evidence.

## Handoff and limits

After the Web Pro observation tab disappeared, automated review rejected reopening it because of the user's screen/tab restriction. No bypass or new model execution was used. REM reviewed the four existing Web Pro-authored harness files via the terminal, checked Python/Node syntax and verified all 64 bound copied-source files unchanged. The current original Peekly HEAD and index remain unchanged; its PaywallModal.tsx changed externally since the experiment baseline, so this report does not claim the entire original checkout remained unchanged. The original checkout was not modified during this handoff.

This commit preserves the experiment and its failure, not a product fix. It does not claim a new full Remorsearch release gate, installed skill, browser acceptance, or measured persona advantage. The harness expects the specifically prepared, byte-bound owned copy; it is not a general automatic installer or complete cold-start setup. The process-local network guard is an experiment guard, not a security sandbox against arbitrary hostile code. Raw profiles, claims, source copies, synthetic archives and private run logs are not published.

Next: repair the aggregate importer in a separate authorized Peekly worktree, preserve all existing user changes, rerun this frozen input and adjacent limits, then validate ordinary-user recovery and messaging in a permitted isolated browser. Preserve the failed baseline instead of replacing it.
