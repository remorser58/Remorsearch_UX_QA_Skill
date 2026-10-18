# Visual-layout benchmark, 2026-10-18

The rendered-layout checks were measured on `benchmarks/visual-layout`, a suite of four Korean product pages with 28 seeded defects in nine families, 11 decoys and a clean twin of every page. A separate agent wrote the suite from the benchmark spec and one example suite without reading the detector, driver or analyser code. Its README records the authoring model, date and how every number in the key was measured.

## Results

Strict scoring (`bench.score` with exact page-level matching): a finding counts when its scenario, category and element (or the element's container) match a seeded defect.

| Detector | Measured checks only | With one default profile | Decoys flagged, measured / profile | Findings on clean twins, measured / profile |
| --- | ---: | ---: | ---: | ---: |
| Before the layout checks | 3 / 28 | 6 / 28 | 3 / 4 | 6 / 18 |
| First blind score | 19 / 28 | 22 / 28 | 3 / 4 | 6 / 18 |
| After fixes made on seeing the misses | 25 / 28 | 28 / 28 | 3 / 4 | 6 / 18 |

The suite has 11 decoys and four clean twins. The decoy and clean-twin counts did not change: the new checks added no finding on a decoy or a clean page. The first blind score is the held-out number. The last row is a development fit; four fixes followed the misses (an `overflow-x: hidden` wrapper read as a scroll container, a cell whose text had already run past the edge, a ribbon over one word, a list too long for one screen).

By family at the final score, measured checks find all of cut text (own box, clipping ancestor, past the screen edge), text under fixed bars, badge and margin overlap, overlapping heading lines, near-miss alignment and uneven list spacing. Text below 11 px is found only by the profile-based reading-size check (PC-04), since whether small print matters (a coupon condition versus a legal footer) needs judgment.

## No regression on the earlier suites

Same command, same scorer, before and after:

| Suite | Recall, measured / profile swarm | Findings on clean controls, measured / swarm |
| --- | --- | --- |
| mobile-commerce | 0.353 / 0.824, unchanged | 7 / 23, unchanged |
| game-desktop | 0.375 / 0.938, unchanged | 19 / 28, unchanged |
| heldout-mixed | 0.150 / 0.900, unchanged | 31 / 50, unchanged |

## Reproduce

```sh
python3 skills/remorsearch-ux-qa/scripts/ergo_bench.py --suite benchmarks/visual-layout --out .ergo-bench/visual-layout
```

The command serves `benchmarks/` on 127.0.0.1, records every scenario in Chromium with the pinned Playwright 1.56.1 driver, analyses it and scores it. `summary.json` holds the three configurations; `score-measured_only.json` lists each defect. Expect small differences on another machine: the suite was measured with macOS system fonts, and the smallest seeded cut and overlap (16.8 px and 9.6 px) leave room for font metrics.

## Limits

One suite of four products written by one agent, with families chosen in advance. It shows that the checks find these defect kinds on unseen pages; it says nothing about how often such defects occur or how many other defect kinds exist. Chromium only.
