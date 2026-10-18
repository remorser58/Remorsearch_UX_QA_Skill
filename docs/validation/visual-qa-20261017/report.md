# Visual QA regression and Figma comparison

Date: 2026-10-17

The updated skill, operated by a vision-capable host, found all six registered clipped-text locations in the supplied portfolio screenshot. It left the three readable control titles unflagged. An independent run of the previous instructions found the same six locations. This is a successful known-failure replay, not evidence of improved general detection accuracy.

## What was exercised

- The original supplied image is preserved byte-for-byte as [screen A](input/screen-a.png), 689 by 1317 image pixels. Its source version, CSS viewport and capture time are unknown; findings describe its visible pixels.
- [Screen B](input/screen-b.png) is a fresh export of the actual [Figma frame](https://www.figma.com/design/ikOHVXrV47diF5hmrympEr?node-id=2-2), 390 by 1818. [Readback](input/figma-readback.json) records node geometry, font and layout properties. The provider supplied no version ID; exported bytes and readback hashes identify this snapshot.
- The standalone portfolio build at commit `064d9bae628fdf4a1f8f9fb4e8a14c5b22a13748` was captured at 320 by 568, 390 by 844 and 1440 by 900 CSS pixels, DPR 1. [Thirty captures and their receipts](input/web/receipt.json) record overlapping scroll positions, computed typography, the rendered commit label and hashes. These are Chromium captures, not Safari or physical-device evidence.
- Existing host image tools, Figma tools and the installed Playwright package were used. Aside was attempted first; its page interface did not support the requested viewport-resize call. No new browser service, agent harness or dependency was added to the skill.

## Original image replay

Both reviewers received the same neutral request, one image and a frozen subset of the relevant skill references. They did not receive defect locations, prior conclusions, the other review or the [registered key](registered-key.json). The task was to inspect the image, not to infer missing source or perform a browser flow. The two native reviewer roles requested GPT-6.1 Sol at max effort. Returned image-view calls and observations are recorded in their reports; the final matching was performed by the supervising agent.

| Inspection | Matched clipped locations | Readable controls incorrectly flagged | Finding cards |
| --- | ---: | ---: | ---: |
| Previous instructions at `d93c393` | 6 of 6 | 0 of 3 | 5 |
| Updated instructions | 6 of 6 | 0 of 3 | 6 |

The six locations are PIN, RESULT, process step 02, the body heading, the related-cases heading and the OGC title. The previous reviewer grouped the last two into one card. Counting cards as detection improvements would therefore be misleading. Both reviewers correctly left unobserved Figma fidelity and interactions unknown, and did not invent an overlapping layer to explain clipping.

The [baseline report](baseline-result.json), [candidate report](candidate-result.json), [matching record](adjudication.json), [protocol](protocol.json) and frozen instruction folders preserve this distinction. Three readable control titles are OUTPUT, INPUT and INPRO. They are a small negative control, not a general false-positive estimate.

## Current web and Figma review

An independent reviewer opened all 30 web images and the Figma export with image-viewing tools. The [region and component report](web-comparison-result.json) contains six-axis results, coordinates, exact visible strings, source nodes and measured styles. The full scroll sequences overlap; ordinary viewport cutoffs are checked in adjacent images. No persistent clipping or painted occlusion was established in those captured default/expanded states.

The reviewer found six groups of source differences. At 390px, the title is 42px/600 in the web receipt versus 36px/700 in Figma. The question has different emphasis; section-link gaps are 22px versus 8px; identical one-line summary values repeat approximately every 112.83px versus 80px. RESULT is full-width in the web capture and inset in the Figma export. Process and copy differ substantially, including five expanded steps versus three summary rows. These are observed differences against the supplied source; approval history is absent, so remedies require confirming the intended rules before changing Figma or code. The supervisor corrected the first draft's unconditional restore recommendation; the measured differences remain.

The reviewer did not invent a desktop Figma, infer loaded font identity from a CSS font stack, or equate longer content with broken spacing. Exact pixel comparison was not used for these mismatched page compositions. Captured text readability and source fidelity remain separate outcomes.

## Existing gate verification

The runtime change extends the existing visual-evidence check. Both review methods now require regional observations and viewed actual/reference artifact IDs, with coverage of alignment, spacing, typography, clipping, occlusion and Figma fidelity. Contradictory, missing and out-of-bounds observations cannot support a passed result. A named tool and written observation are not cryptographic proof that an image was viewed; the image-capable host still owns semantic judgment.

For the explicit `pixel_diff` method, the gate now decodes the existing PNG artifacts with the bundled decoder and recomputes changed pixels within bounded tolerances. It does not launch a model or add a visual-QA service.

| Synthetic negative control | Previous gate | Updated gate |
| --- | --- | --- |
| No inspection, declared pass | Accepted | Rejected: missing image inspection |
| Solid red actual and solid blue reference, declared pass | Accepted | Rejected: changed fraction 1.0 |
| Identical pixels and complete synthetic observations | Accepted | Accepted |

[Before](gate-before.json) and [after](gate-after.json) preserve the same probe. These synthetic tests prove gate behavior, not live detection accuracy.

The [real header comparison](real-review/result.json) separately uses the actual 390px web capture and the first 844px of the real Figma export, with the source hash and crop coordinates preserved. The existing gate accepts its failed comparison as an observation and rejects it when a passed result is required. This is a focused call to `Evidence.visual`; the saved slice is not a complete improvement-loop packet or a whole-product approval. The [regional inspection](real-review/visual-report.json) records the actual measured mismatch without pretending the two compositions match.

## Package verification

The final full Python suite ran 1,108 tests in 59.093 seconds: no failures or errors, one environment-dependent skip. Focused loop and boundary checks, reading-budget checks, README/packaging parity and the existing skill validator passed. The 233-file bundle passed integrity verification and its synthetic installed smoke run. No dependencies or agent/browser harness were added. [Verification details](verification.json) distinguish these engineering checks from visual-review outcomes.

## Interpretation

The prior miss occurred despite instructions that already called for screenshot inspection. The new procedure makes image viewing and per-region comparison explicit for every product UI QA. It does not replace the host's visual reasoning with a numeric score. The original failure image must not be relabelled as a browser reproduction or proof of a CSS root cause. A document-width measurement of zero overflow cannot establish that the Figma artifact is readable.

Scope remains one known portfolio artifact and one current local build. Repeated widths, crops and findings are not independent products or user participants. No speed advantage, general superiority, accessibility certification, complete Safari replay or whole-product release approval follows from this exercise.
