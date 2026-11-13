# Peekly live-model browser scale validation — 2026-11-13

## Stage checkpoint: 4 personas

Four saved v2 PRD-hypothesis personas completed their own browser journey,
final judgment and same-persona review. All four uploaded the allowlisted
synthetic current ZIP. The four independent browser contexts shut down.
The read-only audit revalidated the queue event chain, original persona/build
bindings, observation receipts, 39 PNG hashes, and 39 execution logs.

| Cumulative endpoint | New personas | Operationally complete | Model attempts | Accepted decisions/reviews | Input tokens | Output tokens | Failed model responses | HTTP 429 | Stage wall seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 4 | 4/4 | 49 | 47 | 342,179 | 29,618 | 2/49 (4.08%) | 0 | 253.298 |

The two failed responses were schema/criterion validation rejections, recovered
within the attempt limit before any action was dispatched. No browser action
or capture-integrity failure occurred in this stage. Token totals include
both rejected replies.

The four overall UX outcomes are **inconclusive**, not product passes: the
persona-specific PRD criteria include conditions not exercised by this bounded
sample/import journey. Operational completion and evidence validity must not
be confused with satisfying the whole product PRD.

## Model and cost

All 49 requests used `TOKENMAXX/deepseek-v4.1-flash-free`; all served names were
`deepseek-v4.1-flash`. No InferHub, other fallback or `flash-1m` call was made.
The user-confirmed free-route policy cost is USD 0. All 49 responses omitted
`usage.cost` and `billing_source`; their raw receipt fields remain null. This
is not an independently verified invoice or a provider-reported zero charge.

## Evidence and reproducibility

- [Scope, fixed inputs and limits](scope.md).
- [Stage 4 audit and evidence index](stage-4-audit.json).
- [Read-only audit recipe](audit_run.py).
- Frozen implementation: `b5e03ea` on `rem/peekly-scale-evidence-20261113`.
- Run root in that private worktree: `.ux-loop/peekly-verified-20261113-r3`.
- Local raw PNGs remain private; the committed index contains relative paths
  and hashes, not account images or credentials.

The live cohort continues only after each expansion gate passes. A future
16- or 32-persona result is not asserted by this four-persona checkpoint.
Synthetic tests, earlier failed attempts and the one diagnostic model probe
are excluded from the cohort's four distinct persona count.
