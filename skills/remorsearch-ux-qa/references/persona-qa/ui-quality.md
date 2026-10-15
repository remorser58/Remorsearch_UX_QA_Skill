# UI quality and reference analysis

Use this card when the request includes UI quality, component quality, screen polish, a design-system comparison, or a question such as “how do mature products build this control?”. It extends persona QA; it does not replace task, recovery, keyboard, accessibility, or Figma checks.

## What mature product teams check

Treat a component as a small public system, not a screenshot. Inspect the component and the screen that composes it.

| Area | Inspect | Evidence required |
| --- | --- | --- |
| System | token roles for type, color, spacing, radius, elevation and motion; repeated values; component API/variants | source token or Figma readback, plus the rendered instance |
| Anatomy | label, icon, container, helper/error text, affordance and hit area | screenshot and DOM/a11y snapshot for the same state |
| State matrix | default, hover where applicable, focus, pressed, selected, disabled, loading, error, empty and long content | reached states with viewport and input recorded; unreached states stay untested |
| Hierarchy | one clear primary action, lower-emphasis alternatives, action versus navigation semantics, destructive separation | screen capture and task step that establishes the decision |
| Content | action labels, sentence case or local writing convention, long Korean/English strings, plural and currency formatting | exact visible text, source/spec, long-content capture |
| Responsive | narrow width, short height, mobile adaptation, safe-area/fixed bars, table/list/card changes | same component at each scoped viewport and engine |
| Interaction | focus indicator, tooltip for icon-only controls, keyboard activation, loading feedback, error association, focus return | action trace, capture before/after, accessibility fields; screen-reader speech remains separate |

Do not turn a design-system recommendation into a defect automatically. A finding needs a task consequence, a stated product intent, a Figma/spec conflict, or a directly verified component rule. Keep taste, brand preference and untested states in the annex.

## Component and screen matrix

Create one row per meaningful component instance, not per DOM wrapper:

```json
{
  "component_key": "checkout.primary-action",
  "primitive": "button",
  "variant": "primary",
  "state": "loading",
  "screen": "checkout",
  "viewport": "320x568 CSS px",
  "input": "touch",
  "source": "Figma node or public design-system URL",
  "capture": "captures/checkout-loading.png",
  "status": "pass | fail | untested",
  "reason": "exact observation or missing state"
}
```

For screens, add a second matrix with hierarchy, container/grid alignment, repeated spacing, fixed-layer behavior, responsive changes, and the primary decision. A screenshot count is not coverage. A screen passes UI review only when every required component state and every scoped viewport has a row.

## Optional REA-assisted reference analysis

REA means [Reverse Engineer Anything](https://rea.tools/). It gives an agent local tools for inspecting an authorized app, website or runtime and returns code references, runtime observations, screenshots and limitations. Its public README describes the flow as decompile/inspect → understand → recreate, and explicitly says it does not recover original source or automatically clone an app. Its browser observation is passive unless a separate authorized action is requested.

Use REA only when it is already installed or the user explicitly authorizes setup. The Remorsearch package does not vendor REA, install Hopper/Ghidra, or add a second execution runtime. Detect it first (`rea doctor --json` or the configured MCP capability); if unavailable, continue with public design-system documentation and the existing browser evidence path.

For a reference comparison:

1. Define the target component or screen, the user decision, the exact state and the allowed target. Prefer a public design-system page or an app the user owns or is authorized to inspect.
2. Inspect two or three relevant references. Capture the state, component anatomy, interaction rule, responsive change and evidence location. Do not collect a whole product catalogue.
3. Normalize each observation into `observed`, `inferred` or `unknown`. Separate a design-system rule from a single product implementation.
4. Map the reference to the local component matrix: `reuse principle`, `local adaptation`, `reason`, `risk`, `Figma node`, `replay state`.
5. Apply only a reversible, intent-compatible change after the local product reproduces a concrete problem. Replay the original state and adjacent states.

Never copy private source, proprietary assets, hidden endpoints, user data or a vendor's visual identity. “Similar” means the interaction principle or component contract is useful; it does not mean a pixel clone. Record the target URL/build, REA version or provider, capture hashes, license/terms boundary, and unresolved questions.

## Reference principles used by this card

- [Salesforce Lightning base components and blueprints](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds): use an existing base component or documented blueprint, expose a stable public shape, use documented variants/hooks and account for adaptive versus responsive support.
- [Salesforce component accessibility](https://developer.salesforce.com/docs/platform/lwc/guide/base-components-accessibility.html): keyboard behavior, focus, ARIA state updates, labels, error association and non-text alternatives belong in the component contract.
- [IBM Carbon button guidance](https://www.carbondesignsystem.com/building-blocks/core/components/button/guidelines): establish action hierarchy, use clear verb-plus-noun labels, do not truncate labels, provide keyboard activation/loading feedback, and explain icon-only buttons with tooltips.
- [GitHub Primer introduction](https://primer.github.io/design/guides/introduction/): cohesive, accessible and responsive behavior is considered from the start and supported by reusable patterns and tokens.
- [GitHub Primer button guidance](https://primer.github.io/brand/components/Button/): keep labels concise, preserve visible focus, use sentence case and use accessible names for icon-only buttons.
- [Atlassian link icon button guidance](https://atlassian.design/components/button/link-icon-button/usage): distinguish URL-changing links from on-page actions and give icon-only buttons a clear name.

These references are comparison material, not a universal visual style. Record the local product's approved Figma and intent before applying any principle.

