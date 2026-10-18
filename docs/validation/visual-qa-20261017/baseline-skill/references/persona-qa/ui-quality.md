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
| Text geometry | text bounds wider than the parent content box, fixed-height text parents, `nowrap`, hidden/clip overflow, or a wrapped line colliding with the next block | Figma readback or DOM geometry plus the painted screenshot; record `text_clipping` separately from general layout |
| Layer geometry | a component, overlay, sticky/fixed layer or transparent hit target covers required text or a control | same-state painted screenshot, layer/stack evidence and task consequence; record `component_occlusion` separately |
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

For screens, add a second matrix with hierarchy, container/grid alignment, repeated spacing, fixed-layer behavior, responsive changes, text geometry, component occlusion and the primary decision. A screenshot count is not coverage. A screen passes UI review only when every required component state and every scoped viewport has a row, with explicit text-clipping and component-occlusion results.

## REA reverse-engineering pass

REA means [Reverse Engineer Anything](https://rea.tools/). Use it to recover how an authorized app, website or runtime works: code references, module and route relationships, component boundaries, runtime transitions, screenshots and unresolved questions. The goal is to explain the mechanism and the design reason, then rebuild that behavior in the user's project with its own Figma, tokens and components.

Use REA when it is already installed or the user explicitly authorizes setup. The Remorsearch package does not vendor REA or add another execution runtime. Detect it first (`rea doctor --json` or the configured MCP capability); if unavailable, use the same investigation record with public design-system documentation and the existing browser path.

For each feature or screen:

1. Define the user decision, target state, allowed target and the local project feature that should benefit from the investigation.
2. Inspect the target's static structure and runtime behavior where the provider supports it: entry point, modules/routes, component boundaries, state variables, event handlers, network or storage relationships, responsive branches, error and recovery transitions.
3. Replay the important states and record the causal chain: input → state change → render/update → feedback → persistence or recovery. Mark every item `observed`, `inferred` or `unknown`.
4. Explain why the reference likely uses the pattern: task priority, error prevention, information hierarchy, latency, responsive constraint, accessibility or maintainability. Keep this as a hypothesis until the evidence supports it.
5. Create a local transfer record: reference mechanism, local component/screen, Figma node, adaptation, implementation path, trade-off, replay state and acceptance evidence. Apply the change through the existing Figma-first and loop workflow, then rerun the original and adjacent states.

Inspect only the feature slice needed to answer the question. Record the target URL/build, REA version/provider, evidence hashes, access boundary and unresolved questions. Transfer the mechanism and rationale; use the user's project components, tokens, assets and content for implementation.

## Reference principles used by this card

- [Salesforce Lightning base components and blueprints](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-slds): use an existing base component or documented blueprint, expose a stable public shape, use documented variants/hooks and account for adaptive versus responsive support.
- [Salesforce component accessibility](https://developer.salesforce.com/docs/platform/lwc/guide/base-components-accessibility.html): keyboard behavior, focus, ARIA state updates, labels, error association and non-text alternatives belong in the component contract.
- [IBM Carbon button guidance](https://www.carbondesignsystem.com/building-blocks/core/components/button/guidelines): establish action hierarchy, use clear verb-plus-noun labels, do not truncate labels, provide keyboard activation/loading feedback, and explain icon-only buttons with tooltips.
- [GitHub Primer introduction](https://primer.github.io/design/guides/introduction/): cohesive, accessible and responsive behavior is considered from the start and supported by reusable patterns and tokens.
- [GitHub Primer button guidance](https://primer.github.io/brand/components/Button/): keep labels concise, preserve visible focus, use sentence case and use accessible names for icon-only buttons.
- [Atlassian link icon button guidance](https://atlassian.design/components/button/link-icon-button/usage): distinguish URL-changing links from on-page actions and give icon-only buttons a clear name.

These references are comparison material, not a universal visual style. Record the local product's approved Figma and intent before applying any principle.

