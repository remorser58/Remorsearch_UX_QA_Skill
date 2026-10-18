# Bounded clipping re-review — 2026-10-15

COMMENT: Both accepted MEDIUM findings are resolved in their exact original reproductions. No blocking finding remains in these scenarios. Final acceptance and full tests belong to main.

## Evaluated versions and execution

Repository: `<repo-root>`.

- Original extractor SHA-256: `254ecb94215c7d7ece0f490a4f0f1aa502611491746852ac7349c0a905d61f02`.
- First two-line patch extractor SHA-256: `388c326ad331dec219e8233800ab487cfd54ff583764057d959dbcb444dd0227`.
- Range repair extractor SHA-256: `003d1d351b7ce5d94d20ad305c98f4ceaec82bf7bffe0bba930f52cf95965c74`.

The original, faulty patch and Range repair were evaluated on the same synthetic page in Chromium `141.0.7390.37`, viewport 384×600. The faulty patch was reconstructed in memory from the archived original by removing its interactive exclusion; its hash matched the previously reviewed source. This re-review modified no product or test file and introduced no harness.

Extractor arguments:

```js
{ key: 'ergoqa.driver.v1', cap: 400, knownRoles: ['primary'] }
```

## Exact synthetic HTML

```html
<style>button{display:block;font:16px sans-serif;margin:12px;width:90px;overflow:hidden;white-space:nowrap}#ripple{position:relative;width:180px;height:48px;text-align:left}#ripple i{position:absolute;top:0;left:0;width:300px;height:100px;opacity:0;pointer-events:none}</style><button id="nested"><span>Continue to secure checkout</span></button><button id="ripple">Continue<i aria-hidden="true"></i></button><button id="tagged">Read <span id="inner" data-ergo-role="primary">complete delivery terms</span></button><label><input id="check" type="checkbox">Agree</label><input id="submit" type="submit" value="Continue to secure checkout" style="width:90px;overflow:hidden">
```

## Before and after evidence

| Candidate | Original | Faulty two-line patch | Range repair |
| --- | --- | --- | --- |
| `#ripple` | No clipping record | `x:true,y:true,by:null,act:"failed"` | No clipping record |
| `#tagged` | No clipping record | `x:true,y:false,by:null,act:"failed"` | No clipping record |
| `#inner` | `x:true,y:false,by:"#tagged",act:"failed"` | Same record | Same record |

All versions emitted seven candidates without truncation. The checkbox, associated label, nested-span button and native submit input remained unchanged.

`#ripple` label Range: x=28, y=63, w=64.046875, h=18. Its client boundary is left=22, top=50, right=198, bottom=94. All label text fits despite scroll dimensions of 300×100 from the invisible child.

`#tagged` owns only `"Read "`: Range x=28, y=111, w=42.703125, h=18, within client boundary left=22, top=110, right=108, bottom=130. `#inner` starts at x=70.703125 and has width=168.953125, so it crosses the parent's clipping boundary. The repaired extractor correctly preserves that child evidence without a parent warning.

The faulty patch's analyzer produced P2 LY-01 for each of `#ripple`, `#tagged`, and `#inner` in the initial review. The repaired extraction supplies clipping evidence only for `#inner` in this exact page. A separate analyzer/full-suite rerun was left to main.

## Direct-text positive controls

The original separate button/link page was replayed against the Range repair. `#cut` and `#link` retain `x:true,y:false,act:"failed"`; `#clean` has no clipping record; `#dots` retains `ellipsis:true,act:"passed"`.

Its existing earlier evidence paths are `<local-evidence>/code-repro/repro.mjs`, `code-repro/results.json`, and `code-repro/interactive-clipping.png`. The JSON and screenshot predate the Range repair. No new screenshot was saved for this re-review; current extraction and Range geometry were recorded in the tool output above and summarized here.

## Snapshot relationship fields

`page_scripts.mjs:1357` emits `ancestor_ids` as up to three raw ID-bearing ancestor values; `#inner` has `["tagged"]`. These are DOM IDs, not CSS selectors or snapshot element IDs. ID-less ancestors are absent. The element's `selector` is a separate field; `clipped.by` is `"#tagged"` for this example, but falls back to a tag name for an ID-less clipping ancestor. Do not treat either relationship field as a general unique ancestor-selector chain.

## Limits and pilot attribution

This review covers the exact accepted reproductions and original positive controls. Untagged labels wholly inside spans and native input-button values remain existing extraction limits. It makes no claim about transform geometry, every icon/control shape, or whole-product QA performance.

JavaScript syntax and `git diff --check` passed. LSP diagnostics were attempted for the revised extractor and analyzer; TypeScript and basedpyright servers are unavailable and previously declined. No server was installed and full suites were not duplicated.

The matched OMO instruction pilot began before the runtime repair. Pilot conclusions must identify the instruction hash actually evaluated and remain scoped to those instructions and recorded conditions. The runtime SHA above must not substitute for that instruction hash; this re-review does not verify the pilot's instruction receipt or claim final runtime gains from it.

Source SHA at report write: `003d1d351b7ce5d94d20ad305c98f4ceaec82bf7bffe0bba930f52cf95965c74` (matches evaluated Range repair).
