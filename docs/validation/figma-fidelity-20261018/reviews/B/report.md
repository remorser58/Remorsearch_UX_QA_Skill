# Build B visual QA: case detail page (commit 064d9ba)

**Verdict: REQUEST_CHANGES.** At 320, 390 and Safari 402, nothing is clipped, covered or blocking, but the page departs from the approved Figma frame 14:2 in type, spacing and several components. Desktop has two alignment breaks of its own. Every finding is P3. Pixel rects and Figma node values for each item are in `result.json`, and the 390 top comparison is in `inspection-390-top.json`.

Suggested order of work:

1. Restore the 14:2 header roles: a bold, dark problem statement, a 36px title, gray 13px meta text and outlined section chips.
2. Fix the body heading spacing and add the missing "본문" label.
3. Put the desktop RESULT row and MORE CASES block back on the content grid.

## Defects (problems even without Figma)

- **F-06, every width.** The body headings don't group with their content. "관련 자료" sits 28px below the previous paragraph, while "검증 범위" sits 30px above its own paragraph. Figma uses 42px and 20px.
- **F-07, Chromium 390.** A line starts with a middle dot: "·후보·공백이 0건이었습니다." (web-390-05). Safari keeps the dot at the end of the previous line, and 320 and 1440 keep the phrase on one line.
- **F-08, 1440.** The RESULT label and copy sit 80px left of the OUTPUT, INPUT and PIN columns, and the label is centered in the band instead of top-aligned.
- **F-09, 1440.** MORE CASES starts 132px right of every other section and the footer.

## Figma differences (frame 14:2, approved up to 820px)

- **F-01.** The problem statement is 17px regular gray instead of 18px bold #1D1D1F, so the case question loses its lead role.
- **F-02.** The section links render as plain text in a ruled strip followed by an empty band, instead of three outlined chips.
- **F-03.** The result block is a full-width band with a pill button, instead of an inset card with a 6px-radius button.
- **F-04.** The process steps add a progress rail with dots, indent the copy 70px instead of 28px and use larger type. At 320 the step titles wrap to three lines.
- **F-05.** The "본문" section label is missing, so the "본문" link leads to an unlabeled section.
- **F-10.** The type scale and gray text colors differ throughout: title 42px versus 36px, summary values 22px versus 24px, body 17px versus 14-16px, and gray secondary text rendered dark. The page is 5034px tall at 390 versus 3528px in Figma.
- **F-11.** The related cases put a purple arrow in a separate right column with row separators, instead of an inline arrow after each title.

## Approved deviations

- **F-12.** The build uses Pretendard where Figma uses Noto Sans KR, and line breaks differ as a result. No change needed.

## Unknowns

- Interaction states were not captured: collapsed steps, focus, hover and pressed states, section-link jumps, and rail behavior between screenshots (F-13).
- It is unclear whether Figma's purple 01 and gray 02-05 step numbers mark an active step, and whether weight 600 is the intended Pretendard match for Bold.
- Desktop fidelity cannot be judged because no desktop frame exists. 200% text, text-spacing overrides and short heights were not captured.
- The process rail is a vertical rail at the left of the step list. The skill reports bars in existing-product QA only when a task shows harm. Static captures show none, so the rail is logged as a Figma difference.

## What passed

Text clipping and component occlusion pass in all four viewport groups. Mobile alignment holds to the 24px content edge. Safari's toolbar covers content only while the page is scrolled, and at the end of the page the footer sits clear above it.

Coverage: every Chromium capture (8 at 390, 15 at 320, 7 at 1440), all 10 Safari web-view captures, 4 of the 10 device frames, the Figma top image and segments 01-05, plus 8 crops listed in `crops/crops-manifest.json`. The full Figma export was not opened because its six segments cover it. Device frames 02-04 and 06-08 were not opened, and no finding relies on them.

