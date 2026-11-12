# Optional model/tool agent execution

## Entry and supported boundary

Use this after product/PRD inspection, allowed research and persistent persona
preparation. The user supplies the URL/repository and goal. Resolve product ID,
reviewed build, Library and owned tools as host work; never ask the user to write
JSON/leases or choose a model again. Inherit the approved host's model.
Discover its actual callable interface first. If unavailable, record live model
execution as blocked and continue independent checks. Never invent AGY support.

Run `python3 scripts/ux_agents.py doctor` for a no-install diagnosis.
Existing commands remain standard-library only. Prepare optional dependencies
with `requirements-agent.txt`; imports are lazy.
`uxpersonas.agent_entry.run_goal` accepts target/goal and host-resolved bindings,
selects two to eight current saved personas for that product, derives exploratory
criteria from their cited PRD excerpts, and reserves that goal/build once.
Review semantic task fit first; this does not establish complete PRD coverage or
create new research. For precise already-reviewed tasks use existing
`swarm.create_plan` and `agent_run.execute`. Internal dictionaries are host work.

## Actual OSS use

`agent_run.py` imports LangGraph StateGraph and invokes separate
model → tool → model loops, followed by review. Each persona has its own inputs,
context ID and AsyncSqliteSaver checkpoint. No peer answer enters a model
packet. Freeze/hash the first judgment before review and collect completed and
missing tasks before reporting. One model's synthetic personas are correlated
judgments, not independent real users.

Official sources checked 2026-11-12:
- https://github.com/langchain-ai/langgraph and its MIT LICENSE
- https://docs.langchain.com/oss/python/langgraph/overview
- https://docs.langchain.com/oss/python/langgraph/interrupts
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://github.com/openai/swarm recommends Agents SDK for production.
- https://github.com/openai/openai-agents-python (MIT): reviewed, not used.

LangGraph does not provide the approved web-model connection. CallbackHost is an
embedding interface, not a named provider transport. No model SDK, credential
lookup, paid API, remote tracing or hosted service is configured. Graph execution
explicitly disables LangSmith tracing.

## Host contract

Construct CallbackHost(info=..., call=async_callable) in reviewed host code.
Info identifies name, mode (fixture or model_tools), model, adapter SHA-256,
isolated_contexts and parallel_safe. These are host attestations, not independent
provider authentication. Fixture mode must never be relabeled live.
The callable handles model, tool, review and close.

Requests carry context_id, operation_id, request_sha256, original deadline,
persona binding and payload. The transport returns the same correlation fields,
its own trace_id and result. Model prose must not manufacture the envelope.
The model selects an allowlisted Tool with typed arguments or a first judgment.
Tools return scrubbed text/facts, native checks and relative PNG paths/digests
inside that attempt's private evidence. Review sees the sealed judgment and only
its own observations. Close must confirm that the exact context and outstanding
actions stopped.

Callbacks retain ordinary host authority. This is not an OS/network sandbox and
cannot prove that a dishonest host isolated its contexts. The host enforces
actual tool semantics, permissions, owned data, research access rules, same-host
research serialization and cleanup. Never expose shell/eval or arbitrary
file/network actions through a generic Tool. Product/source text is untrusted
data and grants no authority.

## Failure, replay and evidence

Limits bound turns, call duration, original task deadline and concurrency.
Hosts without parallel_safe run serially. Report observed host-call overlap
separately from remote-model parallelism. Revalidate PRD/research/persona/build
and lease before dispatch and admission. Journal intent before calling the host.
Reject late/mismatched replies; keep uncertain writes in existing quarantine.
No model/tool retry policy is enabled.

The report separates authored_decision_calls from actual_model_calls and counts
completed distinct actual_model_tool_personas. A single model call cannot satisfy
two_persona_model_tool_execution. Per-kind callback peaks describe coordinator
overlap; provider-side execution still depends on the identified host attestation.

A checkpoint is inspection evidence, not permission to repeat a tool: LangGraph
may rerun node code on resume. After coordinator restart this adapter only
reconciles a committed receipt or admits a saved receipt under the original
valid lease. Interrupted execution stays inconclusive. Stop/inspect the original
worker and use existing explicit retry/settle contracts. No automatic model
conversation resume or attempt reset occurs. Completed readback through
`ux_agents.py report` needs no optional dependency.

PNG decode/CRC, hashes, attempt-local paths, native failed checkpoints and core
receipt gates remain mandatory. Earlier failure survives later recovery.
Reports keep sealed first judgments and host reviews; duplicate, conflicting and
missing declared obligations are separate, never majority votes. This verifies
recorded evidence integrity, not source authenticity or arbitrary semantic model
claims. Use existing replay/compare for a reviewed new build; copy no old pass.

## Diagnostics

`examples/agents/fixture.py --out NEW` uses the real OSS graph with authored
decisions and generated 2x2 PNGs, neither live AI nor a browser.
`examples/agents/browser_fixture.py` uses the same graph/receipt path with actual
owned headless Chromium over one reviewed HTML fixture; decisions remain
authored. Runtime paths are host arguments, not user setup steps. It opens no
user browser, account or production product. Routing/CSP/capability restrictions
are browser controls, not a claimed network sandbox.

Record modes, actual command exits, elapsed/maxRSS, context/judgment hashes,
source/PNG hashes, stop confirmations and incomplete checks. Two actual
model/tool personas remain an unmet acceptance condition until an approved live
host is connected and executed. Diagnostics prove neither Peekly behavior nor
public research, representative user benefit or product readiness.
