# Instruction review

**Verdict: APPROVE — instruction content only.** No critical coverage loss or instruction blockers found; minimum fix: none. Files reviewed: 2. Issues: 0 (CRITICAL/HIGH/MEDIUM/LOW: 0 each).

Scope: working-tree diff against `eb193f1`, plus full context of `skills/remorsearch-ux-qa/references/persona-qa/workflow.md` and `qa-report-template.md`. References below use those filenames.

| Requirement | Evidence and result |
| --- | --- |
| Intermediate observations and batching | `workflow.md:16` requires bounded inspection, capture/receipt and stopping on unexpected transitions. `workflow.md:55` retains verification after every step; `workflow.md:63` retains inspection after each step/failed submit. Batching changes host-call overhead without authorizing end-only observation. |
| Blind pass | `workflow.md:63` preserves screenshot-first operation, separate accessibility inspection and refusal of DOM inspection in screenshot-only sessions. |
| Keyboard and recovery | `workflow.md:18` separates full keyboard execution from pointer diagnosis and records downstream blockage. `workflow.md:51` and `workflow.md:52` retain recovery transitions and the whole primary keyboard task. Blocked steps cannot become passes. |
| Visual coverage | `workflow.md:16` includes bottom content/overlays; `workflow.md:47` retains mobile/desktop, short-height and state coverage. `qa-report-template.md:26` requires inspected rendered evidence for every screen/state/viewport. |
| Provenance | `workflow.md:67` requires receipts during capture; `workflow.md:73` separates build identity from PNG integrity. `qa-report-template.md:86` rejects reconstructed receipt provenance. Capture reuse remains subject to current-build, state and run requirements. |
| Persona and bundle contracts | `workflow.md:20`, `workflow.md:28` and `workflow.md:39` preserve audience gates, unchanged profiles, matched-pair attribution and separation of actual executions from shared-recording analysis. `workflow.md:109` and `workflow.md:117` retain bundle validation, exact bindings, second-pass IDs and unknown unreached checks. |
| P0/P1 review | `workflow.md:87` and `qa-report-template.md:88` retain capture/text-only review without the draft, frozen assessments, every finding's review record and written disagreement resolution. |
| Compact JSON + Markdown | `qa-report-template.md:3` establishes one authoritative record. Required finding fields remain at `workflow.md:85` and `qa-report-template.md:40`; report-level method/provenance remains at `qa-report-template.md:118`. Markdown can summarize and link without repeating cards, receipts or cause narratives. |

Validation: scoped `git diff --check` passed. LSP diagnostics were requested for both files but rejected because the checkout lies outside the tool's request cwd; no successful diagnostics or runtime/type-safety approval is claimed. The reported 13 passing reading checks and unchanged runtime/caps were supplied context, not independently rerun or inspected. No new tests, harness, benchmark outputs, sessions, delegation or router were used. Review is complete within the requested instruction scope.
