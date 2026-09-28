# Subagent setup

Several modes can start subagents: persona agents in ergonomics and persona-qa,
parallel source readers in research, and judges or verifiers in any mode. This
page decides which model and reasoning effort they use. Skip it when the run
starts no subagents.

## 1. Saved choice

Read `${XDG_CONFIG_HOME:-~/.config}/remorsearch-ux-qa/config.json` if it exists:

```json
{
  "version": 1,
  "source": "harness | user",
  "host": "claude-code | codex | other",
  "roles": {
    "operator": {"model": "inherit | haiku | sonnet | opus | fable | <model id>", "effort": "inherit | low | medium | high | xhigh | max"},
    "judge": {"model": "...", "effort": "..."}
  },
  "decided_at": "2026-09-28T00:00:00Z"
}
```

- `operator`: persona agents that drive the real screen, research readers, and
  counter-searchers.
- `judge`: verification (including research verifiers that sample excerpts),
  matching findings to evidence, and severity review.

If the file is valid and the user did not ask to change it, use it and go to
step 4. If the user says something like "change the agent model" or "에이전트
모델 바꿔줘", start again at step 2.

## 2. Existing harness mapping comes first

Check read-only, without changing any setting:

- **Claude Code**: the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable (and
  `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`), agent definitions with `model:` or
  `effort:` front matter in `.claude/agents/` or `~/.claude/agents/`, and agent
  types provided by plugins.
- **Codex**: per-agent or per-profile model settings in the user's Codex
  configuration.
- **Other harnesses** (for example OMO-style plugins): their documented
  agent-to-model mapping.

If any mapping exists:

1. Do not pass a model or effort when starting subagents. In Claude Code a model
   given at call time wins over agent definitions and the environment default,
   so passing one would silently override the user's mapping.
2. If the harness defines role agents, route by role: research readers to its
   research agent, judges to its review or verification agent, persona operators
   to its general worker.
3. Save `"source": "harness"` with `"model": "inherit"` for each role, tell the
   user in one line which mapping is being followed, and do not ask.

`CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` forces one model on every subagent. Any
choice made here then has no effect; say so instead of asking.

## 3. Ask once

Only when no saved choice and no harness mapping exist. Use the host's selection
prompt (in Claude Code, the `AskUserQuestion` tool); if the host has none, ask
with a numbered list. Ask two questions in one prompt:

**Model for persona and research subagents**

| Option | Tell the user |
| --- | --- |
| Same as this session | No extra configuration. |
| Opus | Recommended for persona QA: found the most seeded defects with no false alarms in the benchmark below. About 2x Sonnet per run. |
| Sonnet | Cheaper; reached the task goal but found fewer defects. |
| Haiku | Cheapest; reached the goal but reported almost no UX problems. Not recommended for QA findings. |

**Reasoning effort**: "Same as this session" (default), `high`, or `max`.

Before asking, say that ergonomics mode may start one agent per simulated
profile (16 in the default sample), so the model choice multiplies.

Judges and verifiers default to the strongest model the user allows. Ask about
them separately only if the user raises cost.

In a research audience run, the brief questions (A0 in
`references/research/audience-pipeline.md`) may go in the same selection prompt,
so the user is asked once.

Save the answers with `"source": "user"`. Create the folder if needed. Never
write secrets or tokens to this file.

## 4. Use the choice

- Pass the saved model and effort when starting each subagent, unless the source
  is `harness`.
- A subagent that fails because the model is unavailable falls back to the
  session model; record the fallback in the run report.
- Record in every report which model and effort each role used. Persona agents
  from one model count as one correlated rater
  (`references/ergonomics/persona-agent-protocol.md`, replication rule).

## 5. Research readers

These rules add to the steps above. They do not change how the model is chosen.

- Research readers and counter-searchers use the `operator` settings. Verifiers
  use the `judge` settings.
- Run readers 2-3 per batch, or 5-6 when the host enforces the return schema
  (schema-forced fan-out). Never start 10 or more at once. The research run ledger
  caps the load on each host, whatever the concurrency.
- Readers return `ux-reader-return.v1` (planned schema) and never write their own
  fetch code. They read through `scripts/ux_research.py` and the browser tools in
  `references/research/public-page-access.md`.
- Harvest rule: the orchestrator does not finish until every reader has returned
  or has been recorded as a missing axis. A missing return is re-run in batch mode.
- Readers from one model share blind spots. When the user allows it, prefer a
  different model for verifiers than for readers, and record the choice.

## Evidence for the recommendation

The options above come from a blind benchmark in this repository: each model
drove the same seeded-defect and clean-control pages through the live web
driver, and two blind judges matched the reports against the answer keys. See
the repository document `docs/validation/subagent-model-benchmark.md` for the
method, per-model numbers and limits.
