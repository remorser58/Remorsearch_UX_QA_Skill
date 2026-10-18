# Visual QA: build A, case detail page

**Build in the captures:** 09fa14e (footer text, matching both receipts).
**Verdict:** APPROVE, with five non-blocking P3 follow-ups.

The mobile page matches the approved Figma frame (node 14:2) closely in Chromium at 390 and 320 px and in iOS Safari at 402 px. No text is cut off and nothing covers text or controls at any width. Every issue found is a small polish item. The verdict covers static visual quality only.

I viewed all 45 original images, then measured edges, gaps and colors in the pixels; all 31 capture hashes match their receipts. Each item is marked observed (seen in pixels or receipts), inferred (reasoned from them) or unknown.

## Defects

- **F1 (P3, 390 Chromium, observed):** in process step 03 a line starts with a middle dot: "·공백 확인, 지식팩 제안, 리포트 순서로 움직이도록" (web-390-02, x 52, y 798). The compound "충돌·공백" breaks before the dot. Figma keeps it whole, and 320 and Safari do not break it this way.
- **F3 (P3, 1440, observed):** the RESULT label sits 108 px below the first line of its text, centered in the purple band, while OUTPUT, INPUT and PIN each sit 3 px below theirs (web-1440-01).
- **F4 (P3, 1440, observed):** the 요약 / 과정 / 본문 links start at x 276, 12 px inside the 264 px edge that every other header element uses (web-1440-00). The likely cause is the mobile link padding left in place after the border is removed (inferred).
- **F5 (P3, 1440, observed):** "관련 자료" sits 28 px below the previous paragraph and 31 px above its own link, so it groups weakly with its content (web-1440-05). The mobile frame uses 32 px between blocks and 12 px under a heading.

## Figma differences

- **F2 (P3, 390, 320 and Safari, observed):** the arrow after each related-case title sits 4-5 px from the last letter ("프로토타입↗"), against 7-8 px in Figma, where a word space precedes it (nodes 14:55, 14:58, 14:61).
- Everything else measured in the mobile frame matches within 1-3 px: the x 24 left edge, section gaps, hairlines, the square #7C4DFF result card with identical line breaks, step numbers, minus icons, and the body and related-case spacing. The Figma frame itself showed no clipping or overlap.

## Approved deviations

- **A1 (observed):** Pretendard replaces Noto Sans KR, as recorded in the reference notes. Line breaks move (the question breaks after "내용과" instead of "어긋난"; the meta line, step paragraphs and the step 03 title also differ), link widths shrink slightly (48.5 vs 50 px, 161 vs 168 px), and the middle dot and arrow glyphs look different. Size, weight, line height and color still match.

## Unknowns

- Interaction states (collapse and expand, hover, focus, pressed, section jumps) cannot be judged from static captures.
- On mobile the purple step number moves with scrolling (02, 04 and 05 light up in later captures). Figma shows only 01 as current, so the intended behavior is unknown.
- Desktop has no Figma frame. Its text roles also differ from mobile: the meta line is dark while the question is light gray, the body paragraph is dark while process paragraphs are gray, the body section has no "본문" label, and every step number is purple. These may be intentional.
- The Figma readback has no version or branch, so fidelity is tied to the export hash (1d7321d5…d93e). The site footer lies outside the frame.
- Chromium font loading is not recorded. Its glyph extents equal Safari's, where Pretendard is reported loaded, which suggests it loaded too (inferred).
- Safari capture limits (T1): the strip under the status bar is blurred by the system, and the floating toolbar covers painted content outside the layout viewport. At the end of the page the footer stays above the toolbar.
- Not reviewed: scroll positions between captures, 200% text, text-spacing overrides, contrast and screen-reader output.
