# Persona Scenario Design

## Purpose

Use synthetic personas to widen QA coverage and create realistic test conditions. Use a small stratified sample; do not attempt to treat a multi-million-profile dataset as a list of users to impersonate.

## Persona use policy

- A synthetic persona is a scenario generator, not a research participant.
- Resolve the exact dataset source and revision before reading it; do not assume that a field or value exists because another version had it.
- Inspect the schema first and prefer streaming, bounded sampling, or a local sample over full-dataset download.
- A persona attribute is relevant only when it changes a task, constraint, expectation, or failure risk.
- Do not infer personality, ability, income, or preference from age, region, job, or household alone.
- Keep the original dataset field names and values when they matter to reproducibility.
- Record the dataset name, version or access date, sample rule, and selected fields.
- If the dataset is unavailable, use a manually defined scenario and mark population simulation as blocked.

## Dataset access record

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

Prefer a matrix that varies task-relevant dimensions:

| Dimension | Example strata | QA value |
| --- | --- | --- |
| Product familiarity | first use, returning, expert | discoverability and efficiency |
| Device | small mobile, large mobile, desktop | reachability and responsive hierarchy |
| Input | touch, keyboard, assistive technology | interaction and accessibility |
| Context | hurried, interrupted, low connectivity | feedback and recovery |
| Goal | browse, compare, complete, recover | information hierarchy |
| Risk | low, financial, safety, privacy | trust and confirmation |
| Data state | normal, empty, partial, stale | state handling |

Use the dataset to select plausible contexts. Create the actual task from the product surface and reported user problem.

## Scenario format

```text
Scenario ID:
Persona source:
Sample rule:
Relevant attributes:
User segment:
Task goal:
Context:
Device and input:
Starting state:
Constraints:
Expected success:
Likely failure:
Evidence that motivated the scenario:
```

## Example

```text
Scenario ID: S-03
Persona source: Nemotron-Personas-Korea, sampled for one-person household and mobile use
Relevant attributes: mobile context, evening routine, repeat purchase
Task goal: reorder a previously purchased item
Context: user is interrupted and has one hand available
Device and input: small mobile, touch
Starting state: signed in, previous order exists
Constraints: low patience, must confirm delivery date
Expected success: reorder without searching from the beginning
Likely failure: previous order is hard to find or delivery date is hidden
Evidence that motivated the scenario: repeated community reports about lost order history
```

The example is a test condition. It is not evidence that every one-person household behaves this way.
