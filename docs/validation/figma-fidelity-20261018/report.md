# Figma fidelity reconciliation: blind before/after visual QA

Date: 2026-10-18

Three blind reviewers used the current skill to inspect one build each of the portfolio case page against the approved mobile Figma frame. The pre-change build was rejected with 13 P3 findings that covered all six registered difference groups and two desktop alignment offsets nobody had pointed out to the reviewer. The first reconciled build was approved with five P3 follow-ups. After those were fixed, the final build was approved with no defects. This is one product reviewed once per build, not a general detection-rate measurement.

## Reference and builds

- Figma file `ikOHVXrV47diF5hmrympEr`. The original frame `2:2` is preserved. Frame [`14:2`](https://www.figma.com/design/ikOHVXrV47diF5hmrympEr?node-id=14-2) (390 x 3528) is its reconciled copy: section frames widened from 342 to 390 px, real case copy instead of placeholders, the owner's signature purple `#7C4DFF` (directive of 2026-08-21) instead of `#612EC7`, 44 px section links, explicit line heights, disclosure and current-step states, and word-level Korean line breaks. Pretendard is unavailable in this Figma catalog, so the frame uses Noto Sans KR; [the reference notes](reference/reference-notes.md) record that substitution as an approved deviation.
- Builds of the portfolio branch: B = `064d9ba` (before), A = `09fa14e` (Figma rules applied at 820 px and below), C = `a6ec654` (A plus the five follow-ups). The labels did not reveal order or role.
- The same capture scripts served every build: Chromium 141 through Playwright 1.56.1 at 390 x 844, 320 x 568 and 1440 x 900 at DPR 1, and iOS 27.0 Simulator Mobile Safari on a task-owned iPhone 17 through safaridriver at a 402 x 714 CSS viewport and DPR 3. Build B's 390 px top capture is byte-identical to the 2026-10-17 archive (`0d3aba6b...`), so the capture repeats across days.

## Protocol

Each reviewer received only [the frozen skill instructions](skill-frozen/) (PR head `cb9f0af`), the reference package and one build's captures with receipts and computed styles. [The registered key](registered-key.json) lists six expected difference groups and two desktop offsets found by the supervisor. It was written while the first two reviewers ran and before any output was read (sha256 `e3e54d17...`). [Assignment](assignment.json) maps the labels to commits.

## Results

| Build | Verdict | Findings | Six registered groups | Desktop offsets |
| --- | --- | --- | --- | --- |
| [B](reviews/B/report.md), `064d9ba` | REQUEST_CHANGES | 13 P3: 11 implementation, 1 approved deviation, 1 tool limit | 6 of 6 found | 2 of 2 found, uncued |
| [A](reviews/A/report.md), `09fa14e` | APPROVE | 5 P3 follow-ups, 1 approved deviation, 1 tool limit | none remaining | fixed |
| [C](reviews/C/report.md), `a6ec654` | APPROVE | no defects; 1 approved deviation, 2 tool limits | none | none |

Review B also found two defects absent from the key: body headings that did not group with their content, caused by an existing CSS specificity bug (F-06), and a Chromium line beginning with a middle dot (F-07). Review A found the middle-dot break at a new position, a related-case arrow 3 px tighter than Figma and three desktop inconsistencies. All five were fixed in C, and Review C reported none of them.

The reviewers opened 50, 45 and 40 original images respectively, plus their own crops. Review C corrected the reference notes: the Safari screenshots are 1206 x 2622 full-screen images, so page content starts about 63 CSS px below the image top.

## Existing gate

Each reviewer's inspection of the 390 px top region went into a focused `Evidence.visual` slice ([B](gate/B/result.json), [A](gate/A/result.json), [C](gate/C/result.json)).

- B was recorded as failed. The gate accepted it as an observation and rejected it when a pass was required.
- A and C passed all six visual aspects with viewed pixels. Static images cannot show interaction states, so both reviewers reported the comparison as unknown, and the gate stopped it as unknown in both modes. Static evidence alone did not become a pass.

## Final-build interaction and Safari checks

- Safari: seven scroll captures were viewed. Document width stayed at 402 px with no overflow, clipping candidates or text-box collisions, and Pretendard was loaded.
- Touching 요약, 과정 and 본문 at scrollY 0 produced touch and click events and moved to each anchor ([receipt](final-build-qa/safari-interaction.json)).
- After the page had scrolled, Safari automation touch actions and Element Click produced no page event, as in earlier runs, so those steps are unknown. `elementFromPoint` mapped the above-title, title and toggle points of every step to its summary. Chromium touch emulation toggled the disclosure and did not toggle it from body text ([receipt](final-build-qa/chromium-touch-disclosure.json)).
- A Chromium scan found no line starting with `·` at 320, 340, 360, 375, 390, 402, 414, 430, 768 or 1440 px.

## Skill updates

This run added two instruction clarifications. The iOS 27 Safari input limit now covers any scrolled page and points to `elementFromPoint` hit checks, and the typography review names Korean lines that split a word or start with `·` or closing punctuation.

## Limits

- One product was reviewed once per build, and the reviewers ran on the same model family as the supervisor. No general recall, precision or speed claim follows.
- Reviewers knew that a reconciled Figma frame existed but not which build had changed. The supervisor authored both the frame and the fixes.
- Desktop has no Figma frame, so its fidelity is unknown. Reviewers noted desktop text-role differences whose intent is unknown.
- Physical devices, VoiceOver, 200% text, text-spacing overrides and contrast were not tested.
- Reviewer crops and device screenshots are hashed in [the input manifest](input-manifest-sha256.json) but not archived. Safari captures for A and B are archived as 1x previews; the receipts keep the original hashes.

