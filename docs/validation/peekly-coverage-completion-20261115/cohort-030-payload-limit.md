# Cohort 030 — local model-payload limit

**Diagnosis:** after admitting browser observation 68, the frozen runner's next model payload exceeded its 256 KiB bound before dispatch. This is a known local runner limit, not a product failure, uncertain delivery, screenshot timeout, or the 80-turn ceiling. This document records diagnosis only; no payload fix is implemented.

## Bound result

- Stage: `.ux-loop/peekly-completion32-pinned-20261115/stage-32`.
- Persona/job: `PER-PEEKLY-V2-030` / `S-dhjdnlebpigdchpmkmnblafj`.
- Frozen runtime: `f50d082a197e683b5961d17919fe219dc48c4d55`.
- Result SHA-256: `204b3b42d12402b6235f4cfbf722518994f1584896ee19699a19596984c5c98e`.
- Checkpoint SHA-256: `263e446abe61e93b3a8e6d004e41a01d19a8019e915e88a132da9f9a91d1c216`.

Queue status is complete because diagnostic finalization finished. The sealed result nevertheless has `operational_completed=false`, `problem=host_protocol`, `ux_outcome=inconclusive`, and no sealed first judgment. Its native fallback P/P/NR and recovery NR are not eligible completed-execution verdicts. **All three success criteria and one recovery criterion remain unassessed/excluded.**

## Exact size calculation

| Payload | Canonical UTF-8 bytes |
|---|---:|
| Last sent model payload, slot 67 | 261,027 |
| Next payload derived from admitted obs-1 through obs-68 | 265,147 |
| Frozen bound | 262,144 |
| Excess | 3,003 |

The reconstruction used saved checkpoint observations, the frozen pure `_project_model_observations` function, the identical checklist rows with frozen `_criterion_progress` updates, and `remaining_model_turns=80-turn`. Canonical serialization uses NFC-normalized strings/keys, integral floats normalized to integers, sorted compact UTF-8 JSON, and no NaN.

As an anchor, reconstructing the preceding payload from obs-1 through obs-67 matched the actual saved request **byte-for-byte**. The next derived payload SHA-256 is `0d80bb191059128da8a65c3702f4ee0859771682498697e71ae0adf9bd8c0d30`. **This digest describes a calculated, never-sent payload, not an outbound operation.** Projected facts and text/action/check bundles stayed below their separate 65,536-byte bounds (maxima 12,397 and 3,175 bytes). Twelve of 80 model turns remained.

## Frozen source path to finalization

These source bytes were checked against the frozen commit:

- `skills/remorsearch-ux-qa/uxpersonas/scale_run.py`: `payload()` line 590 calls `_data(payload, 262144, privacy=False)`. Worker lines 691–692 evaluate that payload argument before entering `dispatch()`; `q.begin` is inside dispatch at line 594.
- `skills/remorsearch-ux-qa/uxpersonas/agent_run.py`: `_data`, lines 57–63, raises `host_protocol` with “Host payload exceeds its bound.”
- `scale_run.py`: `_code` retains only the code. Worker lines 783–803 record the known failure and enter owned close; lines 751–776 confirm close and seal a diagnostic result with operational completion false.
- `skills/remorsearch-ux-qa/uxresearch/canonical.py`: lines 24–54 define the canonical normalization/bytes used above.

The checkpoint/result preserve only `host_protocol`, not a full exception message. The specific size-bound cause is established by the frozen branch and anchored reconstruction, rather than inferred from the missing final judgment alone.

## Settled dispatch and response history

All **68 admitted model decisions are tool decisions**, and all **68 browser-tool operations have acknowledged, sealed replies**. There is no next model slot 68 or review operation.

The last model operation is `op-34a8b26a1424e301722359ba1561420c932e38a9`; it returned a scroll decision. The last tool is `op-45953a84d3abb66d53577a56d922f555498a16ce`, a dispatched modal scroll with observation/capture admitted. Close `op-71e4ab4051bc61ec4118e5e406554bd503096d85` is done and returns exactly `{"stopped":true}`. That close confirms this context's cleanup; it does not claim whole-cohort terminal cleanup.

## Earlier quality repairs are distinct

The saved router ledger records **68 logical model calls / 70 received attempts, plus two quality diagnostic markers**. Each marker duplicates an already-received response ID; it is not another attempt. All calls end `reply_received`, solely on the approved free route.

| Model slot | Received invalid content | Admitted repaired decision |
|---|---|---|
| 9 — `op-13a7a741814a1e883cd23cd10a74a9e4d69b5f46` | Upload used generic `input[type=file]`, violating structural-selector grammar | Valid More click |
| 51 — `op-b1833291893ce144c78afdccb9e5971b379b3bce` | Final used nonempty observation IDs for success[1] not_run | `wait(ms=800)` |

Frozen `skills/remorsearch-ux-qa/uxpersonas/model_router.py`, lines 338–358 and 508–518, rejects received invalid content before returning an admitted decision, then performs bounded contract repair. The malformed final never reached the execution completion guard. Thus `completion_attempts=[]`, `completion_guard={}`, and no accepted/sealed final are consistent. Terminal slot 67 has one successful received response and no quality rejection.

There is **no uncertain resend or paid fallback**. No actual new model/browser request, Queue construction/write, source change, test execution, or rerun was performed for this diagnosis. The four excluded criteria earn no coverage reduction credit.
