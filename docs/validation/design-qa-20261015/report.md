# Design QA repair and OMO comparison

2026-10-15. Rendered mobile/desktop QA is now a required part of the existing skill. A passing task cannot override missing visual coverage or unreadable required text. The existing extractor also now screens directly owned button/link text for clipping. No execution harness, service or dependency was added.

## Final access-matched Astra medium comparison

A fresh pair fixed the ordinary-OMO guidance access mismatch described below. Both runs allowed the same OMO bundled skill directories, existing Playwright/Node installation and task skill-reference directories. The plain operator read its normal browser guidance. Final tool logs recorded zero permission denials in either condition. Both reported `gpt-6-astra` at `medium`, used the same task and 15-minute cap, and exited with code 0. These are single-operator OMO runs with no delegation, not a comparison of every possible OMO configuration.

| Measure | Ordinary OMO | OMO + Remorsearch |
| --- | ---: | ---: |
| Raw finding cards | 6 | 5 |
| Supported distinct issue families | 5 | 6 |
| Unsupported-as-defect suggestions | 1 | 0 |
| Established false factual observations | 0 | 0 |
| Primary 384×832 pointer flows reaching the final state | 2 / 2 | 2 / 2 |
| Primary flows preserving every requested final value | 1 / 2 | 1 / 2 |
| Report saved after launch | 5m 07s | 10m 08s |
| Last assistant message after launch | 6m 23s | 11m 00s |
| Reported total tokens, including cache/context | 1,682,184 | 3,798,125 |

Both identified the high-impact allergy-note and keyboard failures. The blind adjudication found five supported families in the plain report and six in the skill report, with no supported exclusive family missed by the skill. Its additional finding was payment-summary reflow at 320px. No separate billed-cost result is available.

The treatment combines sauce-price clipping and payment-summary overflow in one finding card. They concern distinct components, states and repairs, so normalized family counts separate them consistently. Raw card counts are also shown. The coupon correction succeeds in the plain report; absent a requirement or measured recovery failure, its spelling-hint recommendation remains a suggestion rather than a supported defect.

The skill adds direct proof of the 320px payment-summary overflow and a complete keyboard flow on A. Plain OMO also exercises the key widths and reports additional full resized replays. Both find the known high-impact failures. The result supports a scoped improvement in useful findings and noise, with substantially more time and reported tokens. It does not establish general superiority, faster QA, billed-cost savings or an exhaustive no-miss guarantee.

The plain operator disclosed accidental inline-script exposure when its keyboard probe serialized `document.body.textContent`; it repeated the probe with bounded fields. Full source-blind compliance cannot be claimed. The skill reports no build-version proof and uses a mixed-width secondary replay. The comparison remains based on known synthetic pages and one repetition. A copying omission initially left the plain operator's original `interaction-evidence.md` out of the blind review folder; it was restored byte-for-byte before final adjudication and is present in the published archive.

[Final blind judgment](parity-judgment.md), [individual adjudications](parity-judgment.json), [protocol](astra-parity-protocol.json), [timing/token counters](astra-parity-accounting.json), and [access audit](astra-parity-audit.json) separate claims from evidence. [Final comparison captures](parity-captures.tar.gz) contain 113 files with [hash receipts](parity-receipts.json); P83 is plain OMO and P24 is the skill condition. The final pilot exercised instructions through native OMO/browser tools; no analyzer invocation was observed, so the runtime clipping repair is validated separately.

The additional narrow-width failure is visible here: the payment amounts extend beyond the right edge.

![Final comparison: clipped payment amounts at 320 CSS pixels](payment-summary-320.png)

## Exploratory OMO comparison (access mismatch; superseded)

Both conditions used OMO `omo-ai 5.1.28`, Astra `gpt-6-astra` at `medium`, the same task, browser installation and 15-minute wall limit. The only intended treatment was loading Remorsearch. Ordinary OMO kept its normal extensions and tools. The plain condition attempted to read OMO's bundled browser/visual guidance, but those paths were denied by the task permission preset. Remorsearch references were available to the treatment. This access mismatch invalidates the table as a fair performance comparison; a fresh matched run grants the ordinary OMO guidance to both conditions. Remorsearch was absent from the plain condition. The local OpenAI endpoint override was identical and temporary, using the already-running model proxy. No global provider configuration was changed.

The task covered both delivery variants: the complete 384×832 order/recovery flow, plus key states at 320×568 and 1440×900. Each condition ran once. These are known development fixtures, not unseen products. Results were adjudicated from anonymous reports, actual PNGs and DOM/action receipts. R46 was plain OMO; R17 used the skill.

| Measure | OMO | OMO + Remorsearch |
| --- | ---: | ---: |
| Supported unique defect families | 5 | 6 |
| Unsupported-as-defect suggestions | 1 | 0 |
| False factual observations established | 0 | 0 |
| Complete primary mobile pointer flows recorded | 2 / 2 | 2 / 2 |
| Primary flows preserving every requested final value | 1 / 2 | 1 / 2 |
| Report saved after launch | 6m 27s | 11m 17s |
| Reported total tokens, including cache/context | 2,716,627 | 4,685,741 |

Both found lost allergy instructions after address validation, required part selection skipped by keyboard, mobile sauce-price clipping, missing-sauce feedback, and unnamed quantity buttons. The skill condition additionally proved that the 320px payment summary cropped amounts; panning exposed the amounts while hiding their labels. The plain condition's coupon-copy suggestion accurately described the wording but did not establish a defect or failed recovery.

The skill condition supplied stronger keyboard and bottom-of-screen coverage, including a full keyboard checkout on A. Neither condition passed B: its receipt lost the allergy request despite showing the expected 48,000 won. Secondary viewports were sampled states, not independent complete flows. The supplied artifacts favor the skill in this run, with longer reporting time and more reported tokens. Because ordinary OMO guidance was blocked, this is exploratory only and cannot satisfy the OMO performance criterion. The blind review's broader task-benefit verdict remains inconclusive. No population, speed, cost or general quality superiority is established.

The plain OMO process remained idle after writing its report and was terminated by the 15-minute wrapper (exit 124); its final assistant message was at 6m 49s. The skill process exited normally; its last assistant message was at 12m 35s. Report-time and process termination are separate. Token counters come from the host; cached context is substantial, cumulative token/cost ceilings were not enforced by this invocation, and no billed dollar cost was measured.

The skill operator accidentally exposed inline page script through `BODY.textContent` during focus inspection and disclosed this. Its initial two PNGs lacked adjacent receipts; 67 later PNGs had matching hashes. The plain operator used consolidated notes rather than adjacent receipts. These limitations remain in the [blind adjudication](astra-judgment.md) and [per-finding JSON](astra-judgment.json). No benchmark-key file read or analyzer invocation was found in the inspected tool calls. The comparison evaluates observed instruction use, not the later extractor repair's causal effect.

The requested follow-up used InferHub `combo/glm-5-3`, effort `high`, with the same access-corrected prompts and limits. The plain run ended with `upstream stream interrupted`; the skill run exhausted provider retries with five 502 errors and one 524 error. Neither produced a valid QA report. They receive no quality score. [Failure receipts](glm-result.json) distinguish service failure from product findings.

Earlier attempts are also retained locally: Z.ai Flash hit a weekly/monthly limit; Kimi runs were cancelled when the user selected Astra. Initial Astra/GLM attempts lacked permission for OMO's `eval` and external skill references. Fresh matched runs corrected only those task permissions. Blocked/cancelled attempts are not successes and are excluded from the comparison table. See [Astra conditions](astra-access-protocol.json), [GLM conditions](glm-access-protocol.json), and [usage/timing](astra-accounting.json).

## Mobile and full-flow verification

The original six evaluation pages remain byte-for-byte unchanged ([hashes](source-hashes.json)). Fresh checks cover delivery, civil-service application and course/quiz, each with two variants. Scripted execution and manual rendered review are recorded separately.

- Delivery: both 40-step mobile flows reached a receipt. A preserved the allergy request; B lost it. The B desktop flow also reached a receipt. Screenshots confirm sauce-label clipping and the independent OMO review confirms the short-width payment overflow.
- Civil: initial authored runs failed because `Control+A` did not replace phone/query text in this macOS environment. Owned scenario copies changed only that chord to `Meta+A`; both 65-step runs then completed. Original runs remain failures in the evidence. A's first failed submit clears the identity fields, while B preserves them. A places the missing-name error at y=54 beneath the fixed header/stepper; the recorded occlusion fraction is 1 and the capture hides the error. Scrolling recovers it. These are input/recovery and error-visibility failures, not mere rectangle intersections.
- LMS: both 35-step existing scenarios reached 100-point results. The preliminary scripted review's suspicion that A never registered answers was not confirmed by this replay and is not a final defect. End-of-video progress was not verified at the exact endpoint. Initial rendering/key-state captures cover 384×832, 320×568 and 1440×900 on the civil/LMS pages.
- iOS: Safari 27 on an iOS 27 iPhone 17 simulator was separately exercised. WebDriver touch was unreliable; direct Device Hub clicks/drags after ending that session reproduced B's clipped price labels and reached cart/checkout with the correct 25,000-won item and 50,000-won quantity-two subtotal. This is a scoped Safari check, not a completed Safari payment flow or physical-device evidence. Initial page viewport was 402×714 at DPR 3; browser chrome changed during scrolling.

Full-flow completion does not mean these intentionally defective pages passed QA. Required tasks now include rendered review at entry, scroll, selection, error and overlay states. Alignment claims need a Figma or established component reference; visible obstruction needs actual screenshots and reproducible conditions. The sampled scrolled-under headers and horizontally scrollable fee table were not automatically marked defective. Figma fidelity, physical devices, screen-reader speech and production/backend outcomes remain unverified.

## Extractor repair

The old snapshot collector and LY-01 analyzer explicitly skipped interactive elements. A narrow reproduction showed two clipped direct-text controls (button and link) omitted before the repair and detected afterward; a readable button remained clean and deliberate ellipsis retained its lower-severity exception.

Independent review found two problems in the first two-line patch: invisible decorative children could create false clipping, and a tagged child label could be counted through its parent. The final collector checks the owning control's direct text Range against clipping boundaries. It ignores decoration and leaves tagged descendants to their own captures. The exact two review reproductions now pass; see [review and source hashes](code-review.md).

This is bounded screening. Untagged labels wholly inside spans and native input-button values remain existing limits. Geometry does not certify visual alignment, layering, painting or every transformed control. Mandatory rendered review covers those gaps.

## Verification and evidence

- Python: 1,088 tests, no failures, one environment-dependent skip.
- Final web driver: 629 passed, zero failed. Shared-browser handshake and Python captured-font analysis remain environment-dependent skips.
- Focused checks: 44 semantics, 14 reflow and 13 reading-budget checks pass. Existing limits were not raised.
- Earlier full web run: 626 passed and one analysis timeout at the unchanged 30-second limit. The same analysis group then passed 65 checks; the final full run passed. The failed log is retained.
- One-command isolated installation passed with Node 22.23.3 and Playwright 1.56.1. All four modes and bundled search are present; 232 files and changed source/installed-file equality were verified. Payload SHA-256: `ee58b34a415486def2274f09218b2ff28f0592b401eb0db77ea458ef1f1e7c76`.

[Verification records](verification.json) list individual runs and test boundaries. [Captured artifacts](captures.tar.gz) contain 332 selected files; extract locally with `tar -xzf captures.tar.gz`. [Receipts](receipts.json) provide original/published hashes. PNGs are unchanged; text normalizes local paths. Original complete captures and failed-run logs remain in the local task archive. Raw model events, hidden reasoning, credentials and unrelated browser state are excluded.
