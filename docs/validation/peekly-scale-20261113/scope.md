# Peekly saved-persona scale execution — scope and gates

This run follows the user's 2026-11-13 request to repair the two interrupted
sessions, verify four sessions, then expand to 16 and 32. It is a new execution
of the existing saved Peekly v2 PRD-hypothesis personas, not a new persona
generation or a replay of old successful observations. Earlier failed queues
and receipts remain untouched in the original integration worktree.

## Fixed inputs

- Frozen cohort code: `b5e03ea`, based on `d86ba1a` (which includes `5e9dc89`).
  Recovery commits `d6a5b2c` and `2bb4575` remain separately reviewable.
- Code worktree/branch: `peekly-scale-evidence-20261113` /
  `rem/peekly-scale-evidence-20261113`, isolated from the earlier running worker.
- Peekly source: `58214441`, built in its separate `peekly-swarm-20261113` worktree.
  All six production build files are checked against its saved build manifest.
- Runtime target: the owned loopback production preview at port 4173.
- Library: the existing 32 saved `PER-PEEKLY-V2-001` … `032` records.
  Their provenance is `prd_hypothesis`, not verified research participants.
- Fixture manifest SHA-256:
  `92620658e3364b0c963c1a956e473370fe3ffb1a519fddbffc73255c8e8517de`.
- Exact request selector: `TOKENMAXX/deepseek-v4.1-flash-free`. No paid
  fallback, InferHub, Haiku, or `flash-1m` route is configured.
- User-confirmed free-route policy cost is zero. Provider `served_model`,
  `usage.cost`, and `billing_source` are preserved separately; absent fields
  are not rewritten as provider-reported zero. No invoice verification is claimed.

## Execution and expansion

Cumulative endpoints are 4, 16, and 32: new batches contain 4, 12, and 16
distinct saved personas. Concurrency is two, with a 30-request/minute route
limit and bounded retries including HTTP 429 backoff. Each session has a
maximum of 16 model decisions plus same-persona review.
Each HTTP attempt has a 50-second limit, at most three attempts per logical
operation, and a 180-second total queue deadline. Up to 4096 output tokens
per attempt allow the model to return its complete criterion judgment.

Expansion requires every assigned session to terminate normally, an admitted
judgment, valid current evidence, confirmed owned-browser shutdown, and no
queued/running/uncertain/blocked/cancelled task. UX criteria may legitimately
be `failed` or `not_run`; product success is not an expansion prerequisite.
The queue's `complete` state alone is insufficient because a turn-limit exit
can be complete but not operationally completed.

Every model attempt, including rejected responses and retries, contributes to
reported token use and failure rate. Diagnostic probes and historical attempts
are reported separately from the final 32-persona cohort. Captures are matched
to observation logs and rehashed from disk rather than accepted on model claims.

## Repairs established before expansion

1. A privacy scrubber treated a numeric portion of a valid SHA-256 as a card
   number and changed the capture metadata. Raw capture digests are now checked
   unchanged; only free observation content is scrubbed. The regression also
   verifies that genuinely altered file bytes are still rejected.
2. The prior provider adapter re-appended whole checkpoints, duplicating every
   earlier observation on each turn. The model now receives one current
   checkpoint, previous observed text, and the latest control metadata.
3. JSON mode explicitly disables unrelated native tool selection. Invalid
   decisions are retried within the existing attempt limit, not executed.
   Native error diagnostics retain names/usage without any credential values.
4. The model receives remaining-turn information and the final-judgment
   contract. All criteria, including unobserved ones, must be accounted for.
5. Cumulative continuation loads the last endpoint, not start-index plus that
   endpoint (which previously made 16→32 demand 48 saved personas).
6. The first corrected run exposed final-JSON truncation and review references
   attached to `not_run`. Those attempts remain in `peekly-verified-20261113-r1`.
   The next preflight (`r2`) rejected a 240-second call limit before dispatch.
   The frozen `r3` cohort uses the unchanged queue maximum of 180 seconds and
   explicitly validates final observation references within bounded retries.

## Interpretation limits

Models see scrubbed text and DOM control metadata, not screenshot pixels.
The driver uses CDP actions, assisted scrolling, and programmatic summary
activation; this is not a human timing or accessibility experiment.
Raw PNGs stay in the private local evidence tree. No real Instagram login,
account data, third-party page access, purchase, or product-source modification
is part of this run. A same-persona review is not an independent rater.

Valid synthetic observations can establish specific behavior in this fixed
web build. They do not establish population prevalence, satisfaction, native
iOS behavior, production privacy guarantees, or overall product readiness.
