# Keep / cut / add decisions

Every change to the check catalogue, the profile plan and the scoring is logged
here with its evidence. Sources used below:

- **Dev ablation:** `ablation-dev-8707b70.json`, leave-one-out on the three
  development suites (53 seeded defects).
- **Adjudication:** `docs/validation/adjudication-round1.json`, 68 sampled findings,
  2 judges, κ 0.72.
- **Reviews:** six Opus cross-reviews (human factors, UX design, QA practice, game
  accessibility, methodology, code correctness).
- **Research:** the briefs in `docs/qa-discipline/`, cited by candidate ID
  (UEM-, STF-, AP-, LAT-).

The development suites are training data, so every decision here is post-hoc for
them. The out-of-sample test is `heldout-2`, pre-registered in
`heldout-2-preregistration.md`.

**Decision rule:**

- **KEEP:** the item finds seeded defects that nothing else finds (unique
  detections), or it is a normative check with a measured basis.
- **CUT or demote to hypothesis:** no unique detection on dev, and either
  adjudicated validity ≤ 1/6 or clean-control noise ≥ 5 findings.
- **CHANGE:** judges named a concrete cause of invalid findings, so the cause is
  fixed rather than the check removed.
- **ADD:** a candidate that research ranks high and that can be measured by the
  driver. It is evaluated on heldout-2 per category, never tuned on it.

## Demoted to hypothesis (computed, listed for review, never counted as defects)

| Item | Evidence | Decision |
| --- | --- | --- |
| GZ-01 primary not fixated early | 0 unique on 53 dev defects; 17 clean-control P3; 0/6 judged valid (wrong state, free-viewing artefact); STF-01, UEM-03 | hypothesis |
| GZ-04 competing emphasis | 0 unique; 7 clean-control P3; 1/6 valid | hypothesis |
| PC-05 bright-sun contrast | 0 unique; 17 clean-control P3; judges split (1 valid, 3 split); the bright-sun stratum adds 31 findings and no defect | hypothesis |
| PT-05 Fitts ID > 6 bits | no normative threshold; no dev finding (STF-22) | hypothesis |
| GM-06 button mashing | counts the presses the script needed, not what the game requires (game review); its one dev detection is a scripting artefact | hypothesis until a press-rate sweep exists |
| PJ-01 persona notes, uncorroborated | an agent's self-declared corroboration is not evidence (STF-23, LAT-03) | hypothesis unless runs of a different model family or input channel note the same anchor |

## Narrowed (cause fixed, check kept)

| Item | Unique dev detections | What was wrong (adjudication or review) | Change |
| --- | --- | --- | --- |
| All position and perception checks | – | findings on elements covered by a sheet or behind a modal | skip elements ≥ 50 % covered by a *painting* layer or inert behind a modal; transparent click layers and `pointer-events:none` overlays do not count |
| RH-01 reach | 6 | phone model applied to tablets; reach scored at the target's centre | tablets use side grips (HGR-9); easiest point of the target |
| RH-02 destructive in easy zone | 0 | a link that opens a confirmation is not a risk (0/2 valid) | only `irreversible` actions |
| PT-02, PT-04 size and miss | 1 (PT-04) | label hit area ignored; 60 × 8.8 mm fields flagged; profile-only P2 on off-path controls | label-extended targets; flag only targets harder to hit than a 9.2 mm square; profile-only P2 only for primary or used controls |
| PC-02 boundary contrast | 2 | container colour measured against the page base; text-labelled radio cards; icon glyph ignored | driver composites the layer below; labelled cards exempt, switches and sliders not; icon glyph at 3:1 passes |
| PC-03 colour-only states | 4 | 입금/출금 and signed amounts not treated as state cues; status severity ignored | state words and signs are cues; status, warning and error encodings ≥ P2 |
| PC-04 text visual angle | 3 (critical print size tier) | critical print size applied to button labels, table cells, Latin text and inherited sizes | Hangul prose only (≥ 12 syllables; not interactive, heading or cell); elements must own their text. Cutting the tier would lose all 3 defects. |
| CG-01 choice overload | 1 | unrelated controls grouped by size; PIN pads; set truncated at the fold | group by container; keypads exempt; whole rendered group |
| CG-02 toast reading time | 4 | 4 000 ms toast measured as 3 995 ms; game pop-ups treated as messages; off-screen toasts not recorded | 50 ms tolerance; undeclared game pop-ups are decorative; off-screen appearances are recorded and flagged |
| CG-03 feedback latency | 1 | taps on closed QTEs or on focused fields; target resolved in the wrong snapshot | skip non-actionable targets and text fields; resolve in the before snapshot |
| GZ-02 feedback noticing | 4 | eccentricity to the centroid; salience from box fill only; redundant feedback; screen replacement | nearest point; bold or icon text at 4.5:1 is salient; redundancy and screen-replacement rules; off-screen feedback flagged (P1 for errors) |
| GM-02 landscape reach | 2 | pause flagged in the top band, where Apple HIG puts it | secondary controls (pause, menu, settings) exempt by name |
| GM-03 QTE window | 2 | model-only P1; declared QTE chains routed to flash screening | P1 only when a typical young adult misses the window, else P2; declared QTEs are always scored by GM-03 |
| GM-05 game control size | 1 | 9.6 mm serial size applied to pause | serial size for gameplay controls only |
| GM-04 flash | 1 | whole-frame mean luminance misses local, counter-phase and red flashes; no sampling during waits; a 3 Hz flicker counted as 3.5 flashes; red tested on gamma-encoded values | per-block tracking summed within 10° fields, sampling during waits, capture jitter, half-open 1 s window with 50 ms sampling tolerance, linear red test, `inconclusive` on poor sampling. Live check 30/30 (`docs/validation/flash-screening/`) |

## Profile plan

| Item | Evidence | Decision |
| --- | --- | --- |
| Floors: left hand (per input kind), deutan, presbyopia, walking | removing each lost unique defects in ≥ 2 dev suites (left one-hand 3–5, deutan 4, presbyopia 3 via PC-04, walking 2); AP-02 | keep as floors |
| Fallback strata: bright sun, first use, protan, large hand | 0 unique; bright sun +31 findings; no deterministic check reads familiarity (AP-03, AP-04) | removed from the fallback plan; audience composition adds them only with evidence |
| Tremor | 0 unique on dev, but an edge condition that has a model (AP-02) | kept |
| Touch σ multipliers (walking 1.4, tremor 1.5/2.25, age) | multipliers off: 0 dev defects lost, 29 fewer findings; judges: profile-only P2 too high off-path | kept, but profile-only severity is limited (see PT-04). Calibration brief pending. |
| Bottom-up conspicuity in gaze | the "gaze disabled changes nothing" toggle ran with a stale cache (code review) | **decision withdrawn**; rerun with the cache fix |
| Stratified vs random sampling | same recall at about a third of the profiles (dev); UEM-12 | keep stratified as the fallback; audience composition is the default |
| Audience composition, one facet per variation, presbyopia not tied to age facets | AP-01, AP-14 | adopted |

## Scoring and reporting

| Item | Evidence | Decision |
| --- | --- | --- |
| Coverage denominators | 203/225 held-out findings had tested == triggered (UEM-01) | the denominator is every evaluated profile the check applies to; the differential counts out-of-scope profiles as untriggered (AP-05) |
| Problem units | 225 findings → about 63 units (UEM-02, STF-03) | reports lead with units |
| Viewport wildcard matching | page-level findings matched any selector (UEM-10) | exact matching is available and is the heldout-2 headline |
| Precision "lower bound" | excluded unlabelled findings (methodology review) | `validity_lb_units` counts all units; labelled-subset precision is reported under its own name |
| Condition identification, recall by operating point, unconditioned recall | methodology review | added to `bench.score` |
| Held-out result | the id-prefix scorer rule was added after the freeze | reported with both scorers (0.60 / 0.80) |

## Pending additions (evaluated on heldout-2 per category, not tuned on it)

- Semantics and layout checks (accessible name, clipped text, focus, reflow):
  waiting for `automated-ui-accessibility-testing.md`.
- Deterministic twins for agent notes (dead end, unclear error):
  `llm-agents-as-test-users.md` LAT-09.
- GM-03 acceptance-window measurement and a GM-06 press-rate sweep (game review).
- Browser chrome offset for mobile web viewports (human-factors review).

## Development-suite effect of the changes so far

| Recording | Detector | Strict recall (53) | Findings | Clean-control findings | Units | Clean-control units |
| --- | --- | --- | --- | --- | --- | --- |
| exp (before fixes) | `8707b70` | 0.906 | 518 | 213 | – | – |
| exp2 (round 1) | `782a15c` | 0.811 | 354 | 143 | 148 | 57 |
| exp3 (round 2) | `4dbdc37` | 0.849 | 186 | 51 | 96 | 26 |

Rounds 3 and 4 (the fixes after exp3) are re-recorded together with the flash
rework and added here.
