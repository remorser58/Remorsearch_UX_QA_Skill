# Causal UX Analysis

## Required chain

For each priority issue, complete every applicable layer:

```text
Observed situation
→ User friction
→ Immediate behavior change
→ Product or service mechanism
→ Organizational or business constraint
→ User outcome
→ Product outcome
→ UX hypothesis
→ Trade-off
→ Validation
```

## Layer definitions

### Observed situation

What the user was doing, with enough context to reproduce the moment.

### User friction

The extra effort, uncertainty, error, delay, or loss of control introduced by the experience.

### Immediate behavior change

What the user does next: repeats input, abandons, asks for help, switches service, waits, or makes an unsafe assumption.

### Product or service mechanism

The direct implementation or policy behavior causing the friction: lost state, unclear label, hidden permission, stale data, missing feedback, or ranking rule.

### Organizational or business constraint

The reason the mechanism may have survived: conversion pressure, advertising inventory, regulatory review, legacy data model, team ownership, support cost, or release risk.

### User outcome

The effect on comprehension, confidence, task success, effort, safety, or trust.

### Product outcome

The possible effect on conversion, retention, support volume, errors, repeat use, or operational cost. Use conditional language when no metric is available.

## Example

```text
Observed situation:
The user opens several product details while keeping a price and delivery filter.

User friction:
Returning to the list removes the active filter and sort state.

Immediate behavior change:
The user repeats the filter, avoids opening details, or abandons comparison.

Product mechanism:
List state is not preserved in navigation history or a stable URL state.

Organizational or business constraint:
The original flow was optimized for a short single-item purchase path.

User outcome:
Comparison becomes slower and less trustworthy.

Product outcome:
Detail visits and completed comparisons may decrease.

UX hypothesis:
Preserving list state will reduce repeated input and support comparison behavior.

Trade-off:
Users may return to stale results unless freshness and reset behavior are visible.

Validation:
Compare task completion time, repeated filter input, and successful selection.
```

## Root-cause checks

Before proposing a visual change, ask:

- Is the real problem missing information, poor ordering, or missing persistence?
- Is the user confused by the interface or by the underlying service policy?
- Does the problem affect new users, expert users, or both?
- Is the proposed fix moving complexity elsewhere?
- What state, error, permission, or recovery path is missing?
- What evidence would disprove this cause?
