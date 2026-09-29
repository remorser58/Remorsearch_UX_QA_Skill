# Persona Scenario Design

## Purpose

Use personas to widen QA coverage and create realistic test conditions. When research mode has produced an audience file, build personas from its segments first. Otherwise use a small stratified sample of synthetic personas; do not attempt to treat a multi-million-profile dataset as a list of users to impersonate.

## Persona use policy

- A persona is a scenario generator, not a research participant. This holds for personas composed from audience research too.
- When an audience file exists (`ergo-audience.v1`, from `references/research/audience-pipeline.md`), each scenario row is a segment's typical member or a one-facet variant, times a key task. It cites `segment_id`, `task_id`, `facet` and gate-supported claim IDs.
- Synthetic dataset records may add only attributes that do not change the task.
- Composed personas stay `basis: synthetic` and carry `audience_ref` `{audience_id, segment_id, facet, claim_ids}`. They never support claims about real users.
- Raw community text never enters persona or scenario prompts. Only authored, scrubbed segment summaries and task data do.
- Resolve the exact dataset source and revision before reading it; do not assume that a field or value exists because another version had it.
- Inspect the schema first and prefer streaming, bounded sampling, or a local sample over full-dataset download.
- A persona attribute is relevant only when it changes a task, constraint, expectation, or failure risk.
- Do not infer personality, ability, income, or preference from age, region, job, or household alone.
- Keep the original dataset field names and values when they matter to reproducibility.
- Record the dataset name, version or access date, sample rule, and selected fields.
- If neither an audience file nor the dataset is available, use a manually defined scenario and mark population simulation as blocked.

## Dataset access record

Keep this record whenever a synthetic dataset is read, including when it only adds attributes to audience-composed personas.

```text
Dataset:
Source and revision:
Access date:
Schema inspected:
Sampling mode: streaming / bounded / local sample / manual
Sampling rule:
Fields used:
Fields omitted:
Reason for omission:
```

## Sampling strategy

Take strata from the audience file first: its segments, their conditions, contexts, devices and key tasks. Use the table below for dimensions the audience file does not cover, or when there is no audience file.

| Dimension | Example strata | QA value |
| --- | --- | --- |
| Product familiarity | first use, returning, expert | discoverability and efficiency |
| Device | small mobile, large mobile, desktop | reachability and responsive hierarchy |
| Input | touch, keyboard, assistive technology | interaction and accessibility |
| Context | hurried, interrupted, low connectivity | feedback and recovery |
| Goal | browse, compare, complete, recover | information hierarchy |
| Risk | low, financial, safety, privacy | trust and confirmation |
| Data state | normal, empty, partial, stale | state handling |

Use the audience file, or without one the dataset, to select plausible contexts. Create the actual task, with concrete data, from the product surface and the audience file's key tasks.

## Scenario format

```text
Scenario ID:
Audience ref (audience_id, segment_id, facet), or "none" with the reason:
Persona source:
Sample rule:
Relevant attributes:
User segment:
Task ID and concrete data:
Task goal:
Context:
Device and input:
Starting state:
Constraints:
Expected success:
Likely failure:
Claim IDs:
Evidence that motivated the scenario:
```

## Example

The IDs below are illustrative.

```text
Scenario ID: S-03
Audience ref: AU-shop-202609, SEG-evening-reorder, facet: one hand free (CTX-commute)
Persona source: composed from the audience file, basis synthetic; no dataset attributes added
Sample rule: the segment's typical member, varied in one facet (context)
Relevant attributes: evening routine, repeat purchase, one hand free
User segment: SEG-evening-reorder ("퇴근길에 생필품을 다시 주문하는 직장인")
Task ID and concrete data: T-reorder: reorder "생수 2L x 12" from the last order, delivery by Friday
Task goal: reorder a previously purchased item
Context: user is interrupted and has one hand available
Device and input: small mobile, touch
Starting state: signed in with a test account, previous order exists
Constraints: low patience, must confirm delivery date
Expected success: reorder without searching from the beginning
Likely failure: previous order is hard to find or delivery date is hidden
Claim IDs: CLM-7c2e9a41 (pain_point, supported_medium), CLM-0d5f3b18 (context_of_use, supported_high)
Evidence that motivated the scenario: two people in one community report that past orders are hard to find (CLM-7c2e9a41)
```

The example is a test condition. It is not evidence that every member of the segment behaves this way, and the segment's share says nothing about how many users would meet this failure.
