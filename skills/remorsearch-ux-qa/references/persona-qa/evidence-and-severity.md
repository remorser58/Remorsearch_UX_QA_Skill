# Evidence and Severity

## Evidence levels

### Verified product observation

The behavior was reproduced in the actual product or connected app with recorded steps.

### Verified design mismatch

The implementation differs from the current Figma or specification in a way that changes the intended task, state, hierarchy, or accessibility.

### Repeated user signal

Independent users describe a similar situation or workaround across one or more channels.

### Official constraint

Product documentation, policy, design system, or platform behavior explains the intended rule or limitation.

### Inference

The analyst connects evidence into a probable cause or outcome. Keep the supporting items visible.

### Unverified

The claim depends on inaccessible material, an unreproduced screen, a stale report, or ambiguous context.

## Severity

### P0

Blocks a critical task, causes serious data loss, creates a safety or privacy risk, or makes a high-stakes action misleading.

### P1

Causes repeated task failure, major confusion, lost work, inaccessible controls, or material trust damage for an important user segment.

### P2

Adds meaningful effort, slows comparison or completion, hides useful information, or causes avoidable support contact.

### P3

Minor inconsistency, visual polish issue, copy refinement, or low-impact deviation without meaningful task harm.

Severity describes user and product impact. Confidence describes how well the finding is supported. Do not use one as a substitute for the other.

## Finding format

```text
Finding ID:
Severity:
Confidence:
Affected scenario:
Persona basis:
Source evidence:
Reproduction steps:
Expected:
Observed:
User impact:
Possible product impact:
Root-cause hypothesis:
Fix layer:
Trade-off:
Validation:
```
