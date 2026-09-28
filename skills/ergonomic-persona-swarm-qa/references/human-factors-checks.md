# Human-Factors Checks

Each check reads measured inputs (geometry, colours, timing) and applies a
model. Values and their evidence tags live in `ergoqa/params.py`; the research
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
| RH-01 | model | Thumb reach difficulty `D` for the profile's grip (`thumb-reach-v3-uncalibrated`: polar model around a thumb-base pivot, left hand mirrored; zones natural 0 / mild <0.4 / stretch 0.4–1 / out 1). Evaluated for primary, game-control and on-path targets. | Primary/game control: out → P2, stretch → P2 (D ≥ 0.6) else P3, small target in the cramped near-palm zone → P3. Other on-path controls (fields, tabs): out → P3 only. Never above P2 from the model alone. |
| RH-02 | model | Destructive action (not on the task path) sits in the natural zone. | P3 |
| GM-02 (reach) | model | Landscape two-thumb games: travel from the nearest thumb rest point (assumed 25 × 22 mm inset from lower corners) and top-band placement (Apple HIG: frequent controls near thumbs, menus at the top). | top band → P2; travel > 35 mm → P3 |

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
| PT-01 | measured | WCAG 2.2 SC 2.5.8: ≥ 24 × 24 CSS px, or the 24 px spacing-circle exception, over the whole rendered page. Inline/equivalent/essential exceptions need judgment. | P1 on primary/destructive/path targets, else P2 |
| PT-02 | measured | Physical size of controls the task depends on (primary, destructive, on-path): < 4.4 mm (iOS 28 pt floor) → P1; < 7 mm (44 pt / 48 dp / Windows 7.5 mm) → P2; one-hand grip < 9.2 mm (Parhi) → P3. Small secondary targets are left to PT-01. | as rule |
| PT-04 | model | Dual-Gaussian tap success (Bi & Zhai 2016): σx² = 0.0075·W² + 1.68, σy² = 0.0108·W² + 1.33 (mm²); P(hit) = erf(Wx/2√2σx)·erf(Wy/2√2σy). Severity from the baseline model (k = 1). Profile multipliers (one-hand thumb 1.3, walking 1.4, tremor 1.5/2.25, 60s 1.15, 70s+ 1.3 — declared assumptions) add findings only for targets under 9.2 mm and are capped at P2. | baseline miss ≥ 10 % P1, ≥ 5 % P2, ≥ 3 % P3; profile-only ≤ P2 |
| PT-03 | model | Misfire: probability that a tap aimed at a primary/path target lands in a destructive neighbour (same Gaussian integrated over the neighbour box), plus gap. Same baseline/profile split as PT-04. | baseline ≥ 1 % and neighbour declared `irreversible` → P0; ≥ 5 % → P1; ≥ 1 % → P2; profile-only ≤ P2; gap < 8 dp (1.27 mm) → P3 |
| PT-06 | measured | Pointer devices: a destructive control within 8 CSS px of a primary/path control (Material 8 dp; Win32 separation of destructive commands). | P2 |
| PT-05 | model | Fitts ID between consecutive pointer steps (mouse MT = −107 + 223·ID ms, MacKenzie, Sellen & Buxton 1991). Relative comparison only. | ID > 6 bits → P3 |

Reference values (derived): 3.8 mm (≈ 24 CSS px on a phone) → P(hit) 0.74;
7 mm → 0.975; 9.6 mm → 0.997. Passing WCAG never implies ergonomic adequacy.

## Gaze and attention

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| GZ-01 | model | `gaze-priority-v2`: priority = bottom-up conspicuity + layout prior (upper-left pull for all UI types, UEyes 2023 / Leiva 2020; web left-half ~80 %, NN/g) + element cues, ad-like penalty. 300 Monte Carlo scanpaths with a 5° distance penalty, inhibition of return and right/down bias give P(primary fixated within 4 fixations ≈ 1 s). Free-viewing priors do not model goal-directed search, so this stays a prompt to check hierarchy. | < 0.5 → P3 |
| GZ-02 | model | Feedback noticing: angle θ from the touch/click point to new or changed feedback. Salient change (new object, ≥ 1°, ≥ 3:1 against surroundings): likely ≤ 10°, uncertain ≤ 20°, else likely missed. Non-salient: 2° / 5°. Bands × 0.7 for 70+, low vision or high load (assumption). One-hand grips also test the thumb/hand occlusion wedge (±35° toward the thumb base). | likely missed or occluded: error/critical P2, status P3; uncertain critical P3 |
| GZ-03 | model | Critical information in a desktop right rail, a thin full-width top banner or declared `ad_like` styling (banner blindness: banners found ~58 % vs 94 % for links, Benway & Lane 1998). Needs judgment. | P3 |
| GZ-04 | model | ≥ 4 interactive elements out-prioritise the primary action. | P3 |

Gutenberg/Z-patterns are not encoded (no eye-tracking support). All gaze data
were free viewing of static screenshots in labs; outputs are population-level
hypotheses. A Korean calibration pilot (~20 people × 30 screens) is proposed in
gaze-visual-attention.md.

## Perception

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| PC-01 | measured | WCAG 1.4.3: 4.5:1, or 3:1 for ≥ 24 px / ≥ 18.66 px bold (KWCAG 2.2 same), over the whole rendered page. Disabled controls exempt. | < 3:1 or primary/critical → P1, else P2 |
| PC-02 | measured | WCAG 1.4.11 for components identified by their boundary: form controls (inputs, selects, switches, checkboxes, sliders) and icon-only buttons; border vs background or fill vs container ≥ 3:1. Text buttons are exempt (the text identifies them). | P2 |
| PC-03 | model | Colour-only states: within same-shaped groups, each channel (fill, border, text) that splits into clearly different colours (ΔE00 ≥ 20) is treated as a state code; different labels (times, names) are not a state cue, explicit state words/icons are. After Machado per-severity simulation, ΔE00 < 5 confusable, 5–10 marginal; exempt when the states differ by ≥ 3:1 luminance (G183). Tritan simulation is low confidence. | < 5 → P2; 5–10 → P3 |
| PC-04 | model | Font-size visual angle at the profile's viewing distance: < 16′ (ISO 9241-303 minimum) → P2 (P1 for critical messages), all text; < Hangul critical print size (24.6′ young, 31.2′ 60s+/presbyopic; snippet-level, metric unconfirmed) → P3, continuous text (≥ 12 characters) only. The older-adult value is not combined with a longer viewing distance. | as rule |
| PC-05 | model | Bright-sun profile: primary, status, error and critical text below 7:1 (one ambient model: 2000 nits, 50 klx, ρ 0.02 ≈ WCAG 7.07). | P3 |

Korean CVD prevalence: men 5.9 % (1989) / 6.5 % (KNHANES 2013, 19–49), women
0.44 % / 1.1 %; deutan ≈ 6× protan [snippet]. KRDS body text ≥ 16 px (17 px
default).

## Cognition and timing

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| CG-01 | model | More than 9 same-shaped interactive choices (Hick-Hyman b ≈ 150 ms/bit used only to show relative cost; not a Miller 7±2 rule). | P3 |
| CG-02 | model | Transient text (timing window of kind `transient_text`, declared or inferred from a readable message) shown for less than the reading time of a −1 SD reader (Korean adults ~330, older ~290 syllables/min; mean ~587/410) × 1.5, floor 4 s (Material). Toasts with an action must not auto-dismiss (WCAG 2.2.1). | action toast → P1; too short → P2 |
| CG-03 | measured | First DOM change after a tap/click: > 400 ms (Doherty) P3; > 1 s P2 (needs a progress indicator); > 10 s P1; none within 3 s P2. | as rule |

## Games

| ID | Basis | Rule | Severity |
| --- | --- | --- | --- |
| GM-01 (perception) | measured/model | HUD/subtitle text: XAG 101 floor 26 px at 1080p on console/TV/handheld, 18 px on PC (scaled to the display and DPR); visual angle ≥ 16′. | P2 (P1 for critical prompts) |
| GM-05 | measured | Touch game controls (`game_control`): < 7 mm → P2; < 9.6 mm (serial thumb taps, Parhi) → P3; closer than 2 mm to a screen edge (system gestures, bezel) → P3 (HGR-11). | as rule |
| GM-06 | measured | The run needed ≥ 8 rapid presses on one target to progress (XAG 107 / GAG: avoid mashing; offer hold/toggle/auto). Confirm alternatives by judgment. | P2 |
| GM-03 | model | Timed input (QTE) window vs the profile's choice reaction time 95th percentile (log-normal, CV 0.2 assumption) + 100 ms motor + input latency. | margin < 0 → P1 |
| GM-04 | measured | WCAG 2.3.1 / ITU-R BT.1702 general-flash screening from two sources: (a) sampled frames (> 3 flashes in any 1 s with area > 0.006 sr, i.e. 25 % of a 10° field → P0; IRIS "extended" 2–3 flashes/s over 5 s → P1), and (b) DOM elements that appear and disappear more than 3 times in any second (16 ms in-page polling), cover the WCAG area, and are saturated red (R/(R+G+B) ≥ 0.8) or differ by ≥ 10 % luminance → P0. Frame sampling (~30 fps) aliases fast flashes, which is why (b) exists. Screening only; confirm with EA IRIS or Harding FPA. | as rule |

Game timing must be measured, not inferred from an agent failing in real time.
Photosensitivity, subtitles-for-dialogue and audio-only cues are covered in
game-ux-ergonomics.md; subtitle coverage and audio cues are not automated here.

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
