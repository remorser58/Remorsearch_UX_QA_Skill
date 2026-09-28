# GM-04 flash screening: live check

Ten small pages, each recorded three times in real Chromium (Galaxy S24
emulation, `--flash-sample-ms 1500`) and evaluated by GM-04 for the default
profile (300 mm viewing distance). Commit `697ce28`.

    python3 docs/validation/flash-screening/validate.py --repeat 3

| Page | What it shows | Expected |
| --- | --- | --- |
| `box.html` | 190 × 120 CSS px box, white/black at 5 Hz (~0.0085 sr) | fail |
| `box-small.html` | the same flash on a smaller box (~0.0035 sr) | pass |
| `halves.html` | two halves swapping black/white at 5 Hz; the mean luminance stays constant | fail |
| `red.html` | full screen `#ff0000` ↔ `#7f7f7f` at 5 Hz (almost equal luminance) | fail (red flash) |
| `wait-flash.html` | a full-screen flash that starts while the script waits | fail |
| `flicker30.html` | 30 Hz full-screen flicker (aliases to a still image without capture jitter) | fail |
| `scroll-text.html` | high-contrast text scrolling | pass |
| `feed-scroll.html` | the user scrolls a feed | pass |
| `static.html` | static page | pass |
| `slow.html` | full-screen change at 1 Hz | pass |

Before the rework, `box`, `halves`, `red` and `wait-flash` passed (whole-viewport
mean luminance, no red test, no sampling during waits).

## Result: 30 of 30 as expected

| scenario | rep | driver exit | expected | verdict | kind | flashes/s | area sr | mean fps | max gap ms | sampled ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SC-flash-a-box | 0 | 0 | fail | fail | general | 5.0 | 0.00836 | 27.2 | 60.7 | 3456.5 |
| SC-flash-a-box | 1 | 0 | fail | fail | general | 5.0 | 0.00836 | 27.5 | 49.9 | 3451.0 |
| SC-flash-a-box | 2 | 0 | fail | fail | general | 5.0 | 0.00836 | 26.9 | 51.2 | 3451.9 |
| SC-flash-a2-box-small | 0 | 0 | pass | pass | general | 5.0 | 0.00352 | 26.2 | 53.1 | 3472.6 |
| SC-flash-a2-box-small | 1 | 0 | pass | pass | general | 5.5 | 0.00352 | 27.2 | 51.4 | 3454.4 |
| SC-flash-a2-box-small | 2 | 0 | pass | pass | general | 5.0 | 0.00352 | 27.3 | 59.2 | 3474.4 |
| SC-flash-b-halves | 0 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.3 | 50.7 | 3465.0 |
| SC-flash-b-halves | 1 | 0 | fail | fail | general | 5.5 | 0.02457 | 24.9 | 79.3 | 3457.7 |
| SC-flash-b-halves | 2 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.0 | 51.0 | 3466.6 |
| SC-flash-c-red | 0 | 0 | fail | fail | red | 5.5 | 0.02457 | 26.8 | 51.8 | 3429.7 |
| SC-flash-c-red | 1 | 0 | fail | fail | red | 5.0 | 0.02457 | 25.7 | 90.4 | 3469.6 |
| SC-flash-c-red | 2 | 0 | fail | fail | red | 5.0 | 0.02457 | 26.8 | 58.0 | 3502.8 |
| SC-flash-d-wait | 0 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.4 | 52.0 | 6446.8 |
| SC-flash-d-wait | 1 | 0 | fail | fail | general | 5.0 | 0.02457 | 27.0 | 58.6 | 6439.9 |
| SC-flash-d-wait | 2 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.6 | 53.1 | 6471.3 |
| SC-flash-e-flicker30 | 0 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.7 | 66.6 | 3443.7 |
| SC-flash-e-flicker30 | 1 | 0 | fail | fail | general | 4.0 | 0.02457 | 26.2 | 60.7 | 3466.7 |
| SC-flash-e-flicker30 | 2 | 0 | fail | fail | general | 4.0 | 0.02457 | 26.4 | 63.2 | 3449.9 |
| SC-flash-f-scroll-text | 0 | 0 | pass | pass |  | 1.0 | 0.0 | 25.6 | 67.6 | 4456.3 |
| SC-flash-f-scroll-text | 1 | 0 | pass | pass |  | 1.5 | 0.0 | 25.1 | 65.9 | 4468.6 |
| SC-flash-f-scroll-text | 2 | 0 | pass | pass |  | 1.0 | 0.0 | 25.8 | 67.1 | 4416.8 |
| SC-flash-g-static | 0 | 0 | pass | pass |  | 0.0 | 0.0 | 27.0 | 58.2 | 5397.6 |
| SC-flash-g-static | 1 | 0 | pass | pass |  | 0.0 | 0.0 | 26.1 | 58.0 | 5440.1 |
| SC-flash-g-static | 2 | 0 | pass | pass |  | 0.0 | 0.0 | 26.3 | 52.7 | 5429.8 |
| SC-flash-h-feed-scroll | 0 | 0 | pass | pass |  | 1.0 | 0.0 | 24.8 | 71.2 | 5889.1 |
| SC-flash-h-feed-scroll | 1 | 0 | pass | pass |  | 1.0 | 0.0 | 24.5 | 70.9 | 5848.3 |
| SC-flash-h-feed-scroll | 2 | 0 | pass | pass |  | 0.5 | 0.0 | 25.1 | 71.1 | 5908.0 |
| SC-flash-i-slow | 0 | 0 | pass | pass |  | 1.5 | 0.0 | 26.6 | 52.0 | 4442.3 |
| SC-flash-i-slow | 1 | 0 | pass | pass |  | 1.5 | 0.0 | 26.7 | 56.0 | 4492.8 |
| SC-flash-i-slow | 2 | 0 | pass | pass |  | 1.5 | 0.0 | 26.4 | 53.0 | 4474.8 |

`flashes/s` for `flicker30` is the aliased rate (4-5/s), not the true 30 Hz: the
sampler (~25 fps with 0-15 ms jitter) sees that the region flashes, not how
fast. The verdict does not depend on the exact rate above 3/s.

Limits: frames are downscaled to ~160 CSS px wide, so patterns finer than a
block (22 × 40 CSS px on phones) average out; spatial-pattern rules (IRIS
pattern check) are not screened. This is screening, not certification: confirm
failures with EA IRIS or Harding FPA.
