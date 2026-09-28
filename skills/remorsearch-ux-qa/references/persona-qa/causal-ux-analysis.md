# Causal UX Analysis

## Required chain

For every P0 or P1 finding, complete:

```text
Symptom
→ Direct interaction problem
→ Product or service mechanism
→ Organizational or business constraint
→ User behavior change
→ User outcome
→ Product or operational outcome
→ Remediation hypothesis
→ Trade-off
→ Validation
```

## Distinguish the layers

- Symptom: what appears on screen or in the user's statement.
- Direct interaction problem: what the user cannot understand, find, operate, or recover from.
- Product mechanism: state, data, ranking, persistence, permission, policy, or implementation behavior.
- Organizational or business constraint: legacy ownership, conversion pressure, support cost, regulation, or release risk.
- User behavior change: repetition, abandonment, avoidance, unsafe assumption, or help-seeking.
- User outcome: effort, confidence, task success, safety, trust, or accessibility.
- Product outcome: possible conversion, retention, error, support, or operational effect.

## Example

```text
Symptom:
The dashboard displays six charts with equal visual emphasis.

Direct interaction problem:
The user cannot tell which metric answers the primary question.

Product mechanism:
The screen was generated from dataset fields rather than a ranked task model.

Organizational or business constraint:
The request rewarded a complete-looking demo and had no agreed success metric.

User behavior change:
The user scans randomly, opens multiple views, or asks someone else to interpret it.

User outcome:
Comprehension and confidence decrease.

Product outcome:
Decision time and support dependency may increase.

Remediation hypothesis:
Choose one primary question, promote one answer, and move exploration into secondary views.

Trade-off:
Some users lose immediate visibility into less common metrics.

Validation:
Test whether target users find and explain the primary metric within the agreed time.
```

## Root-cause questions

- Is the problem visual, semantic, interactional, service-level, or data-level?
- Is the user confused by the interface or by the service rule itself?
- Does the fix remove work or move it to another step?
- What state, permission, freshness, or recovery path is missing?
- What evidence would disprove this cause?
