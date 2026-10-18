# Build C visual QA: portfolio case detail, build a6ec654

**Verdict: APPROVE** for static visual quality and mobile Figma fidelity. The build matches Figma node 14:2 at 390, 320 and Safari 402, and the 1440 desktop is internally consistent (observed). The approval covers the captured static states only and makes no readiness claim.

The build commit a6ec654 appears in the page footer at every viewport and in both receipts (observed). I opened all 40 images listed in result.json plus eight zoomed crops. Each viewport group was graded on alignment, spacing, typography, text clipping, component occlusion and Figma fidelity.

## Defects

None found in the viewed pixels (observed). Text stays inside its boxes at every width: step copy ends by x=330 inside a 332px box at 390, and by x=260 inside 262px at 320. Nothing overlaps, and no page scrolls sideways.

## Figma differences

Apart from the approved font change below, the 390 build tracks the frame within 1 to 3px (observed). Summary hairlines sit at y=413/494/603 against 415/495/604, and the large vertical gaps match almost exactly (71/72, 35/35, 52/52). Size, weight, line height and colour equal the Figma readback for every text role checked, including the purple #7C4DFF result card.

The purple "current step" number follows scroll position: '02' is purple at scrollY 1214, then '04' and '05' further down (observed). Figma shows only the top-of-page state, where the build matches, so the scrolled behaviour has no reference (unknown intent).

## Approved deviations

F-01: the browser renders Pretendard where Figma uses Noto Sans KR, as recorded in the reference notes (observed). The narrower glyphs move three line breaks and shrink two widths. The meta line breaks after '선정·' instead of '문제'. The problem statement breaks after '내용과' instead of '어긋난'. The step 03 title '흩어진 문서 수집부터 감사 리포트까지' fits on one line instead of two. The section links are 48.5px wide instead of 50. Size, weight, line height and colour are unchanged.

## Unknowns

- Interaction states: collapsed disclosures, hover, focus and pressed states are absent from the static captures (F-02, unknown).
- Desktop has no Figma frame, so fidelity at 1440 is unknown. Three desktop choices need a design decision before anyone can judge them: the body section has no '본문' label, the problem statement turns regular gray, and the body paragraph is near-black while process copy is gray (observed pixels, unknown intent).
- The site footer ('GitHub 프로필 ↗', 'a6ec654') sits outside the Figma frame and has no reference.
- The Safari images are 1206x2622 full-screen captures, while the notes describe a 402x714 viewport. Page content starts about 63 CSS px below the image top (F-03, inferred from the H1 position). The amber Safari toolbar colour can't be traced to a cause from pixels.
- Accessibility, text resize, reduced motion and real-device Safari were not assessed.
