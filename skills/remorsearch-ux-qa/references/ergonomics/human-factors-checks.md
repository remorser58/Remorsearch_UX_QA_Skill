# Human-Factors Checks

Each check reads measured inputs (geometry, colours, timing) and applies a
model. Elements that are ≥ 50 % covered (bottom sheet, scrim) or inert behind an
open modal are skipped in that snapshot and judged where they are usable. A
finding's coverage counts every evaluated profile the check applies to, and
findings with the same scenario, check and differential condition are reported
as one **problem unit**. Checks marked *hypothesis* are listed for review and
never counted as defects. Values and their evidence tags live in `ergoqa/params.py`; the research
behind them is in `docs/human-factors/`. Evidence tags used below:
**[standard]** normative text, **[paper]** peer-reviewed value, **[snippet]**
seen only in search excerpts (verify before treating as a gate), **[derived]**
computed from a cited model, **[policy]** team-tunable threshold,
**[assumption]** declared scenario assumption.

Unit conversion is always physical: `mm = css_px × display_mm / display_px ×
dpr` from the device catalog (`ergoqa/devices.py`), never a nominal dp/pt size.

## Reach and handedness

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| RH-01 | model | Thumb reach difficulty `D` for the profile's grip (`thumb-reach-v3-uncalibrated`: polar model around a thumb-base pivot, left hand mirrored; zones natural 0 / mild <0.4 / stretch 0.4–1 / out 1). Evaluated for primary, game-control and on-path targets at the **easiest point of the target** (inset 3 mm), not its centre. Tablets and unfolded foldables (short side > 120 mm) never use the one-hand model; their two-thumb pivots sit at mid-height of the sides (HGR-9). | Primary/game control: out → P2, stretch → P2 (D ≥ 0.6) else P3, small target in the cramped near-palm zone → P3. Other on-path controls (fields, tabs): out → P3 only. Never above P2 from the model alone. |
| RH-02 | model | Destructive action declared `irreversible` (no confirmation or undo), not on the task path, sits in the natural zone. A destructive link that opens a confirmation dialog is not flagged. | P3 |
| GM-02 (reach) | model | Landscape two-thumb games, gameplay controls (not secondary controls named pause, menu, settings, options, help, close, back or their Korean equivalents): travel from the nearest thumb rest point (assumed 25 × 22 mm inset from lower corners) and top-band placement (Apple HIG: frequent controls near thumbs, secondary controls such as pause and menus at the top, so those are not flagged; a scripted run's tap counts do not decide this). | top band → P2; travel > 35 mm → P3 |

Sources: Parhi, Karlson & Bederson 2006 [paper]; Bergstrom-Lehtovirta &
Oulasvirta 2014 (coefficients not retrieved); Trudeau et al. 2012/2014 [snippet];
Xiong & Muraki 2016 [snippet]; Hoober 2013 grip shares [snippet]. Thumb length L
uses Parhi's landmark (US mean 115 mm); Korean values are scaled by hand length
and are assumptions until calibrated (handedness-grip-reach.md §4.5).

The differential condition (`profile_specific`) shows whether a reach finding is
left- or right-hand specific. Korea has low left-handedness (5.8 % left + 7.9 %
mixed, 2009; 7 % in 2025 with 12–13 % in teens/20s) but ~33–37 % of one-handed
phone use is left-thumb, so always keep a left-grip profile.

## Pointing

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| PT-01 | measured | WCAG 2.2 SC 2.5.8: ≥ 24 × 24 CSS px, or the 24 px spacing-circle exception, over the whole rendered page. The target includes an associated `<label>` (it accepts the same click). Inline/equivalent/essential exceptions need judgment. | P1 on primary/destructive/path targets, else P2 |
| PT-02 | measured | Physical size (label-extended target) of controls the task depends on (primary, destructive, on-path): < 4.4 mm (iOS 28 pt floor) → P1; < 7 mm (44 pt / 48 dp / Windows 7.5 mm) → P2; one-hand grip with a side < 9.2 mm **and** harder to hit than a 9.2 mm square (Parhi) → P3, so a full-width 60 × 8.8 mm field passes. Small secondary targets are left to PT-01. | as rule |
| PT-04 | model | Dual-Gaussian tap success (Bi & Zhai 2016): σx² = 0.0075·W² + 1.68, σy² = 0.0108·W² + 1.33 (mm²); P(hit) = erf(Wx/2√2σx)·erf(Wy/2√2σy), on the label-extended target. Severity from the baseline model (k = 1). Profile multipliers (one-hand thumb 1.3, walking 1.4, tremor 1.5/2.25, 60s 1.15, 70s+ 1.3 — declared assumptions) add findings only for targets harder to hit than a 9.2 mm square; profile-only severity is at most P2 for the primary action or a control the task used, otherwise P3 (MP-02). | baseline miss ≥ 10 % P1, ≥ 5 % P2, ≥ 3 % P3; profile-only ≤ P2 (path/primary) or P3 |
| PT-03 | model | Misfire: probability that a tap aimed at a primary/path target lands in a destructive neighbour (same Gaussian integrated over the neighbour box), plus gap. Same baseline/profile split as PT-04. | baseline ≥ 1 % and neighbour declared `irreversible` → P0; ≥ 5 % → P1; ≥ 1 % → P2; profile-only ≤ P2; gap < 8 dp (1.27 mm) → P3 |
| PT-06 | measured | Pointer devices: a destructive control within 8 CSS px of a primary/path control (Material 8 dp; Win32 separation of destructive commands). | P2 |
| PT-05 | model | Fitts ID between consecutive pointer steps (mouse MT = −107 + 223·ID ms, MacKenzie, Sellen & Buxton 1991). Relative comparison only. | ID > 6 bits → P3 |

Reference values (derived): 3.8 mm (≈ 24 CSS px on a phone) → P(hit) 0.74;
7 mm → 0.975; 9.6 mm → 0.997. Passing WCAG never implies ergonomic adequacy.

## Gaze and attention

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| GZ-01 (hypothesis) | model | Reported as a **hypothesis**, not a defect: no unique detection on 53 seeded defects and 0/6 judged valid. `gaze-priority-v2`: priority = bottom-up conspicuity + layout prior (upper-left pull for all UI types, UEyes 2023 / Leiva 2020; web left-half ~80 %, NN/g) + element cues, ad-like penalty. 300 Monte Carlo scanpaths with a 5° distance penalty, inhibition of return and right/down bias give P(primary fixated within 4 fixations ≈ 1 s). Free-viewing priors do not model goal-directed search, so this stays a prompt to check hierarchy. | < 0.5 → P3 |
| GZ-02 | model | Feedback noticing: angle θ from the touch/click point to the **nearest point** of new or changed feedback. Salient change (new object ≥ 1° with ≥ 3:1 box contrast, or bold/icon-led text at ≥ 4.5:1): likely ≤ 10°, uncertain ≤ 20°, else likely missed. Non-salient: 2° / 5°. Bands × 0.7 for 70+, low vision or high load (assumption); the scaled bands are stored. One-hand grips also test the thumb/hand occlusion wedge (±35° toward the thumb base). Not flagged when another salient message appeared where the user was looking (redundant), or when the action replaced the screen (except declared transient messages). Feedback rendered outside the viewport is flagged directly. | off-screen: error/critical P1, else P2; likely missed or occluded: error/critical P2, status P3; uncertain critical P3 |
| GZ-03 | model | Critical information in a desktop right rail, a thin full-width top banner or declared `ad_like` styling (banner blindness: banners found ~58 % vs 94 % for links, Benway & Lane 1998). Needs judgment. | P3 |
| GZ-04 (hypothesis) | model | ≥ 4 interactive elements out-prioritise the primary action. Reported as a hypothesis (no unique detection; 1/6 judged valid). | – |

Gutenberg/Z-patterns are not encoded (no eye-tracking support). All gaze data
were free viewing of static screenshots in labs; outputs are population-level
hypotheses. A Korean calibration pilot (~20 people × 30 screens) is proposed in
gaze-visual-attention.md.

## Perception

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| PC-01 | measured | WCAG 1.4.3: 4.5:1, or 3:1 for ≥ 24 px / ≥ 18.66 px bold (KWCAG 2.2 same), over the whole rendered page. Disabled controls exempt. | < 3:1 or primary/critical → P1, else P2 |
| PC-02 | measured | WCAG 1.4.11 for components identified by their boundary: native form controls, switches and sliders (their track or thumb is the state indicator, even with a label), and unlabelled custom controls; border vs the layer below, or fill vs container ≥ 3:1. Icon-only buttons pass when the glyph has ≥ 3:1. Text buttons and text-labelled custom radio/checkbox cards are exempt (the text identifies them; 1.4.11 then concerns the state indicator). | P2 |
| PC-03 | model | Colour-only states: within same-shaped groups, each channel (fill, border, text) that splits into clearly different colours (ΔE00 ≥ 20) is treated as a state code; different labels (times, names) are not a state cue, explicit state words (including 입금/출금, 승인/취소) and signed amounts (+/−) are. After Machado per-severity simulation, ΔE00 < 5 confusable, 5–10 marginal; exempt when the states differ by ≥ 3:1 luminance (G183). Tritan simulation is low confidence. | < 5 → P2; 5–10 → P3, but P2 when the colour encodes a status, warning or error |
| PC-04 | model | Font-size visual angle at the profile's viewing distance: < 16′ (ISO 9241-303 minimum) → P2 (P1 for critical messages), all text; < Hangul critical print size (24.6′ young, 31.2′ 60s+/presbyopic; snippet-level, metric unconfirmed) → P3 for running Hangul prose only (≥ 12 Hangul syllables; not buttons, links, headings or table cells). Only elements that own their text are measured. The older-adult value is not combined with a longer viewing distance. | as rule |
| PC-05 (hypothesis) | model | Reported as a hypothesis (no unique detection; judges split). Bright-sun profile: primary, status, error and critical text below 7:1 (one ambient model: 2000 nits, 50 klx, ρ 0.02 ≈ WCAG 7.07). | P3 |

Korean CVD prevalence: men 5.9 % (1989) / 6.5 % (KNHANES 2013, 19–49), women
0.44 % / 1.1 %; deutan ≈ 6× protan [snippet]. KRDS body text ≥ 16 px (17 px
default).

## Cognition and timing

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| CG-01 | model | More than 9 same-shaped interactive choices in one container, counted over the whole rendered group (below the fold or under a sticky bar still count; only a modal hides them) (Hick-Hyman b ≈ 150 ms/bit used only to show relative cost; not a Miller 7±2 rule). Numeric keypads are exempt (recall of a known code). | P3 |
| CG-02 | model | Transient text (timing window of kind `transient_text`, declared or inferred from a readable message; on game surfaces only declared or message-role windows) shown for less than the reading time of a −1 SD reader (Korean adults ~330, older ~290 syllables/min; mean ~587/410) × 1.5, floor 4 s (Material), with 50 ms measurement tolerance. Toasts with an action must not auto-dismiss (WCAG 2.2.1). A message that only ever appeared outside the viewport fails. | action toast or off-screen error → P1; too short → P2 |
| CG-03 | measured | First DOM change after a tap/click: > 400 ms (Doherty) P3; > 1 s P2 (needs a progress indicator); > 10 s P1; none within 3 s P2. Not evaluated when the target was disabled, hidden or covered, when a timed control was tapped after its window closed, or for text fields (their feedback is the caret and focus ring). | as rule |

## Games

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| GM-01 (perception) | measured/model | HUD/subtitle text: XAG 101 floor 26 px at 1080p on console/TV/handheld, 18 px on PC (scaled to the display and DPR); visual angle ≥ 16′. | P2 (P1 for critical prompts) |
| GM-05 | measured | Touch game controls (`game_control`): < 7 mm → P2; < 9.6 mm (serial thumb taps, Parhi) → P3 for gameplay controls, not for secondary controls such as pause or menu (discrete taps); closer than 2 mm to a screen edge (system gestures, bezel) → P3 (HGR-11). | as rule |
| GM-06 | measured | The run needed ≥ 8 rapid presses on one target to progress (XAG 107 / GAG: avoid mashing; offer hold/toggle/auto). Confirm alternatives by judgment. | P2 |
| GM-03 | model | Timed input (QTE) window (measured) vs the profile's choice reaction time 95th percentile (log-normal, CV 0.2 assumption; per-age values provisional) + 100 ms motor + input latency. | margin < 0 → P2; P1 only when even a typical young adult (median, 20s) misses the window |
| GM-04 | measured | WCAG 2.3.1 / ITU-R BT.1702 flash screening from two sources. (a) Sampled frames on a block grid: per block, transitions are opposing luminance changes ≥ 10 % with the darker state < 0.80 (general) or ≥ 10 % of the block moving into or out of saturated red (red); a block flashes while it has more than 6 transitions in any 1 s (50 ms sampling tolerance, so a 3 Hz flicker passes); the areas of concurrently flashing blocks are summed within any 10° field with the device pixel pitch and the profile viewing distance. More than 0.006 sr → P0; IRIS "extended" (≥ 2 flashes/s sustained over 5 s on that area) → P1. Blocks whose change is explained by content motion (scrolling) are not flashing. A pass is reported as `inconclusive` (not clean) when mean capture rate < 20 fps, a wait step had no samples or sampling was truncated. Runs without a block grid fall back to the whole-viewport mean. (b) DOM elements that appear and disappear more than 3 times in any second (16 ms in-page polling), cover the WCAG area, and are saturated red (linear R/(R+G+B) ≥ 0.8) or differ by ≥ 10 % luminance → P0. Live check: `docs/validation/flash-screening/`. Screening only; confirm with EA IRIS or Harding FPA. | as rule |

Game timing must be measured, not inferred from an agent failing in real time.
Photosensitivity, subtitles-for-dialogue and audio-only cues are covered in
game-ux-ergonomics.md; subtitle coverage and audio cues are not automated here.

## Semantics and layout (profile-independent, web DOM)

These are measured once per screen and reported as profile-independent. They
matter most to people the swarm does not simulate (screen-reader, voice-control
and keyboard users), so the report names them. The rules are kept narrow for
precision; a full audit still needs axe-core or a manual WCAG review.

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| SM-01 | measured | A control (button, link, role control) has no accessible name (WCAG 4.1.2; axe `button-name`/`link-name`). Name order: aria-labelledby, aria-label, alt, value, own text, title. | P1 on the task path or primary, else P2 |
| SM-02 | measured | The control's name comes from aria-label/labelledby and does not contain its visible text (WCAG 2.5.3 Label in Name). Only labels of 2+ letters, ≤ 40 characters and ≤ 6 words count as labels (card links with long content are not checked). | P2 on the path, else P3 |
| SM-03 | measured | A form field has no programmatic label: name from placeholder or title only, or none (WCAG 1.3.1, 3.3.2, 4.1.2). | none: P1 on the path, else P2; placeholder/title: P2 on the path, else P3 |
| SM-04 | measured | An error message (declared `error_message` or `role=alert`) is more than 48 CSS px from every field on the screen and no field points to it with aria-describedby or aria-errormessage (WCAG 3.3.1; LAT-09 ER-01). An error next to its field passes. | P2 |
| SM-05 | measured | Keyboard focus walk (desktop and keyboard devices; at load in a separate browser context and at the end of the run): focusing the element changes fewer than 4 pixels in its box + 4 px (WCAG 2.4.7). | P2 |
| SM-06 | measured | The focused element is behind a fixed or sticky layer at all nine sample points (WCAG 2.4.11); partly covered is P3 (2.4.12). Not also reported as SM-05. | P2 / P3 |
| LY-01 | measured | Text is cut off by its own box (overflow hidden or clip and scroll size > client size; XCTest `textClipped`, a symptom for WCAG 1.4.4 and 1.4.12). Boxes under 4 px (screen-reader-only text) are skipped. | P2; P3 with an ellipsis |

## Judgment (not automated)

- WCAG 2.5.8 exceptions; whether an action is irreversible; whether a
  destructive button reads as primary; ad-like appearance.
- Heuristic evaluation with the 24 UXD checks in
  `docs/human-factors/ux-design-discipline.md` (Nielsen, Norman, Shneiderman,
  ISO 9241-110/112). Persona agents record expected vs. observed per step.
- Korean dark patterns (전자상거래법 제21조의2, in force 2025-02-14: 순차공개
  가격, 사전선택, 잘못된 계층, 취소 방해, 반복간섭; 개인정보보호법 제22조 separate
  consents). Run these as a separate auditor pass: agents can be manipulated by
  the patterns they are checking.
- Game intent (QTE/mashing as design), left-handed HUD options, motion comfort.
