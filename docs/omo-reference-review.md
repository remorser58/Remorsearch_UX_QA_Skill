# OMO reference inspection and provenance

## What was accessible

Inspection was performed in the Linux sandbox from the supplied archives. The
requested macOS checkout and plugin installation were not mounted here:
`/private/tmp/ux-research-qa-pro-auto/worktree` and
`~/.codex/plugins/cache/sisyphuslabs/omo/4.19.4`. No file in that
installation or another repository was edited. This does not assert that the
user's current installed plugin or remote HEAD matches the supplied snapshot.

Input archive SHA-256 values, calculated from their actual mounted bytes:

| Supplied archive | SHA-256 |
| --- | --- |
| `ux-research-qa-skills-source(2).zip` | `e2844a61612c286acfdf4c53274a1c2859f4e7b1d820b391cafa1800205434e3` |
| `omo-reference.zip` | `4797a55fc974f3e7a55eb9284cab7bb68875cbfd9ffc724c26eedc41fa9887bd` |
| `gpt-dev-agent-context.zip` | `6dd85e14886c783caf8404ba53477ff3fdf98e4b6eb5dfe09f9d7dd5dad64523` |

OMO paths below are relative to `4.19.4/` inside `omo-reference.zip`. The manifest
identifies `omo` version `4.19.4` and the requested `sisyphuslabs/omo` repository.
The snapshot includes isolated component source and skill/hook surfaces; its
package metadata also references a local cache dependency. It was inspected as
reference source, not installed or asserted to be a complete buildable release.
Source: `.codex-plugin/plugin.json`, `package.json` in the supplied snapshot.

## Inspected mechanisms and adaptation

| Local primary source | Observed mechanism | Deliberate implementation choice |
| --- | --- | --- |
| `.codex-plugin/plugin.json`; `hooks/stop-checking-ulw-loop-resume.json` | Plugin surfaces remain components; Stop delegates to a component CLI. | One optional coordinator over two untouched independent skills. No hook installation. |
| `components/ulw-loop/src/domain-types.ts` | Explicit goal/criterion state, attempts, reasons, evidence and quality-gate fields. | Versioned goal, typed run/evidence records, stable references and non-success states. |
| `components/ulw-loop/src/plan-io.ts` (locks near line 19; atomic rename at 115–116; ledger append near 130) | Scoped in-process locks, temporary JSON replacement, separate appended ledger. | POSIX process locks and a single atomic checkpoint with embedded hash-chained ledger, avoiding two-file checkpoint/ledger commit skew. |
| `components/ulw-loop/src/checkpoint.ts`; `checkpoint-reconciliation.ts` | Reconcile checkpoint criteria and quality gates before objective completion. | Revalidate concrete linked receipts, exact scenario/revision identities and required checks, not keyword-based assertions. |
| `components/ulw-loop/src/checkpoint-continuation.ts` | Completion and explicit advance control next-goal continuation; blocked outcomes retain handoff state. | Explicit foreground resume/retry, same IDs/grants, no hidden continuation. |
| `components/ulw-loop/src/stop-resume-hook.ts` (68–87) | Pending/in-progress resumption and a two-strike no-ledger-progress guard. | Fixed maximum iterations and invocation step budget; blocked/unknown/failed never auto-loop. |
| `hooks/pre-tool-use-enforcing-unlimited-goal-budget.json` | A separate unlimited-budget hook surface is present in this snapshot. | Not copied: user-requested finite budgets take precedence. |
| `components/ulw-loop/src/spawn-guard.ts`; `quality-gate-verdicts.ts` | Reviewer dispatch requires prerequisite code/manual-QA artifacts; gate verdicts distinguish passing from missing/inapplicable evidence. | No agent fanout; apply/accept separation, missing comparison evidence cannot pass. |
| `components/start-work-continuation/src/boulder-reader.ts`; `plan-checklist.ts`; `codex-hook.ts` | Plan/checklist-derived continuation; stop-hook and context-pressure guards; rendered worktree/ledger context. | Durable user-visible PLAN.md for implementation and a machine checkpoint for product runs. No transcript parsing or automatic session resumption. |
| `skills/visual-qa/SKILL.md`; associated image-diff/PNG helper surfaces | Actual/reference comparison, stable viewport, recent evidence, separate read-only review and explicit failure reporting. | Versioned Figma-first reference and actual captures plus comparison/accessibility receipts; local integrity/dimension checks, not an invented visual judgment. |

This is a design adaptation, not copied OMO code or a redistributed installation.
No OMO dependency, agent command, telemetry or auto-resume hook was added.
The limited source changes are standard-library Python, JSON contracts, tests and
documentation in the target snapshot.

Selected source SHA-256 fingerprints make these observations reproducible:

```text
.codex-plugin/plugin.json
  94c7e4cccca5948e7349d4824e8570925b8a9733c3e2fc1f59ed2f9b9eb5e686
components/ulw-loop/src/domain-types.ts
  8368992760f12ccf36fc489aeb69b41054258e194e37e4dc26ec0e1a237e9810
components/ulw-loop/src/plan-io.ts
  805ce01d975fd9460f847040f7ce9686d00daf7790570ea5f6ea47f08d267329
components/ulw-loop/src/stop-resume-hook.ts
  847ac4d6ec511bc3aaee564f03cf5e31d5e1d485da13dfcd919b67d00da24ad5
components/ulw-loop/src/checkpoint-continuation.ts
  baa472cd04fa8f174d0c0784d2785d2febd3584a3c49d580b334cede937a151a
components/ulw-loop/src/spawn-guard.ts
  36469bca1f9dc6a913251b3f7659ff1ceeb301aefda77e014efc70acf2ba9c60
components/ulw-loop/src/quality-gate-verdicts.ts
  4448cfec9f6fee89241b4c5f9f18d2e3b4e607cf99129698266f2627205832cd
components/start-work-continuation/src/codex-hook.ts
  1bcfa0bb1dadacb7d01af5151fce0036ccbec78d4e06c050962be3dc5921dc9d
skills/visual-qa/SKILL.md
  1a8b119581fcf558989fd006dc6b1c676a62def1f6473a6b83638c5d99f657c0
```

## Public-source verification, not silent substitution

On 2026-09-15 (Asia/Seoul), the web tool failed to fetch the specifically requested
`https://github.com/sisyphuslabs/omo` and
`https://raw.githubusercontent.com/sisyphuslabs/omo/main/README.md` with
`DisabledError`. Therefore its live public HEAD, availability, current release
and exact source identity were **not verified**. The local archive is the primary
reference for the implementation. A fetch failure does not prove the repository
is private, missing or renamed.

A related public distribution's own README describes an `omo` namespace with
isolated components, durable goals, continuation hooks and read-only specialist
roles. This corroborates only the broad separation pattern; it is explicitly a
Claude Code distribution, not proof of the requested Codex snapshot's identity.
[Source: code-yeongyu/lazyclaudecode README, Components and Skills & subagents](https://github.com/code-yeongyu/lazyclaudecode).

That README links to the public Codex distribution, LazyCodex. Its own README
separates planning, start-work execution and evidence-verified looping, and says
hook approval precedes execution while autonomous permissions remain an explicit
choice. This supports separating planning/authorization/verification; its current
distribution and defaults were **not substituted** for the supplied 4.19.4
source. No installer, plugin hooks or agent configurations were executed.
[Source: code-yeongyu/lazycodex README, marketplace installation and workflow sections](https://github.com/code-yeongyu/lazycodex).

No supplied source or retrieved primary evidence establishes a distinct project
called `omon`. It remains unresolved, not an invented repository and not a silent
alias for OMO, LazyCodex, OpenCode or another project.
