# GM-04 flash screening: live check

Eleven small pages, each recorded three times in real Chromium (Galaxy S24
emulation, `--flash-sample-ms 1500`) and evaluated by GM-04 for the default
profile (300 mm viewing distance). First run at commit `697ce28`; the table below is the re-run after the screen-capture fixes.

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
| `feed-scroll-inner.html` | the same feed in an app-shell scroll box (the page itself does not scroll) | pass |
| `static.html` | static page | pass |
| `slow.html` | full-screen change at 1 Hz | pass |

Before the rework, `box`, `halves`, `red` and `wait-flash` passed (whole-viewport
mean luminance, no red test, no sampling during waits).

## Result: 33 of 33 as expected

Re-run after two driver fixes (September 2026). CDP screenshot clips are in document
coordinates: frames were clipped at 0,0, so once a page scrolled they showed the top of
the document (mostly unpainted) instead of the screen. The earlier `feed-scroll`
passes (30 of 30 table, commit `697ce28`) were therefore measured on nearly blank
frames. With frames of the real screen, a feed of equal cards scrolled at about half a
card per frame made the motion estimate ambiguous, and on a tablet 3 of 8 stress runs
failed GM-04 on plain scrolling. The driver now uses the page's measured scroll between
frames as the motion, and captures whole frames (no downscaling clip, which also
stopped scroll gestures on inner scroll boxes) during gesture steps. Stress runs after
the fix (4 per variant, long and short strokes): tablet window scroll 8/8 pass, tablet
and phone app-shell scroll 16/16 pass, no flash candidate area.

| scenario | rep | driver exit | expected | verdict | kind | flashes/s | area sr | mean fps | max gap ms | sampled ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SC-flash-a-box | 0 | 0 | fail | fail | general | 5.5 | 0.00836 | 27.0 | 51.4 | 3481.9 |
| SC-flash-a-box | 1 | 0 | fail | fail | general | 5.0 | 0.00836 | 27.4 | 49.6 | 3500.7 |
| SC-flash-a-box | 2 | 0 | fail | fail | general | 5.0 | 0.00836 | 26.7 | 57.5 | 3483.0 |
| SC-flash-a2-box-small | 0 | 0 | pass | pass | general | 5.5 | 0.00352 | 27.6 | 50.0 | 3475.3 |
| SC-flash-a2-box-small | 1 | 0 | pass | pass | general | 5.5 | 0.00352 | 27.1 | 50.4 | 3471.6 |
| SC-flash-a2-box-small | 2 | 0 | pass | pass | general | 5.5 | 0.00352 | 27.7 | 50.0 | 3467.8 |
| SC-flash-b-halves | 0 | 0 | fail | fail | general | 5.0 | 0.02457 | 26.8 | 50.4 | 3467.1 |
| SC-flash-b-halves | 1 | 0 | fail | fail | general | 5.5 | 0.02457 | 27.6 | 50.4 | 3479.6 |
| SC-flash-b-halves | 2 | 0 | fail | fail | general | 5.0 | 0.02457 | 28.1 | 50.4 | 3451.4 |
| SC-flash-c-red | 0 | 0 | fail | fail | red | 5.5 | 0.02457 | 27.3 | 52.6 | 3486.0 |
| SC-flash-c-red | 1 | 0 | fail | fail | red | 5.5 | 0.02457 | 27.1 | 51.1 | 3467.6 |
| SC-flash-c-red | 2 | 0 | fail | fail | red | 5.5 | 0.02457 | 26.9 | 48.3 | 3454.7 |
| SC-flash-d-wait | 0 | 0 | fail | fail | general | 5.0 | 0.02457 | 28.1 | 51.0 | 6471.1 |
| SC-flash-d-wait | 1 | 0 | fail | fail | general | 5.0 | 0.02457 | 27.0 | 53.8 | 6472.4 |
| SC-flash-d-wait | 2 | 0 | fail | fail | general | 5.0 | 0.02457 | 27.6 | 51.1 | 6446.5 |
| SC-flash-e-flicker30 | 0 | 0 | fail | fail | general | 4.5 | 0.02457 | 26.5 | 51.1 | 3465.5 |
| SC-flash-e-flicker30 | 1 | 0 | fail | fail | general | 4.5 | 0.02457 | 27.1 | 59.9 | 3466.4 |
| SC-flash-e-flicker30 | 2 | 0 | fail | fail | general | 3.5 | 0.02457 | 27.7 | 56.3 | 3466.5 |
| SC-flash-f-scroll-text | 0 | 0 | pass | pass |  | 1.0 | 0.0 | 26.4 | 60.7 | 4465.9 |
| SC-flash-f-scroll-text | 1 | 0 | pass | pass |  | 1.5 | 0.0 | 26.9 | 52.0 | 4457.0 |
| SC-flash-f-scroll-text | 2 | 0 | pass | pass |  | 1.0 | 0.0 | 26.0 | 69.5 | 4431.2 |
| SC-flash-g-static | 0 | 0 | pass | pass |  | 0.0 | 0.0 | 27.3 | 50.8 | 5426.1 |
| SC-flash-g-static | 1 | 0 | pass | pass |  | 0.0 | 0.0 | 28.5 | 50.2 | 5361.3 |
| SC-flash-g-static | 2 | 0 | pass | pass |  | 0.0 | 0.0 | 26.9 | 50.8 | 5400.0 |
| SC-flash-h-feed-scroll | 0 | 0 | pass | pass |  | 2.5 | 0.0 | 24.3 | 56.3 | 5930.2 |
| SC-flash-h-feed-scroll | 1 | 0 | pass | pass |  | 2.0 | 0.0 | 23.6 | 56.7 | 5902.2 |
| SC-flash-h-feed-scroll | 2 | 0 | pass | pass |  | 2.5 | 0.0 | 23.7 | 56.2 | 5959.4 |
| SC-flash-i-slow | 0 | 0 | pass | pass |  | 1.5 | 0.0 | 26.6 | 53.4 | 4431.3 |
| SC-flash-i-slow | 1 | 0 | pass | pass |  | 1.0 | 0.0 | 27.0 | 52.2 | 4482.4 |
| SC-flash-i-slow | 2 | 0 | pass | pass |  | 1.0 | 0.0 | 26.9 | 52.4 | 4465.2 |
| SC-flash-j-feed-scroll-inner | 0 | 0 | pass | pass |  | 2.0 | 0.0 | 23.8 | 55.8 | 5956.6 |
| SC-flash-j-feed-scroll-inner | 1 | 0 | pass | pass |  | 2.0 | 0.0 | 23.4 | 57.4 | 5952.2 |
| SC-flash-j-feed-scroll-inner | 2 | 0 | pass | pass |  | 2.0 | 0.0 | 23.7 | 58.0 | 5943.9 |

`flashes/s` for `flicker30` is the aliased rate (4-5/s), not the true 30 Hz: the
sampler (~25 fps with 0-15 ms jitter) sees that the region flashes, not how
fast. The verdict does not depend on the exact rate above 3/s.

Limits: frames are downscaled to ~160 CSS px wide, so patterns finer than a
block (22 × 40 CSS px on phones) average out; spatial-pattern rules (IRIS
pattern check) are not screened. This is screening, not certification. EA IRIS
is not a certification either: its defaults need 25 % of the frame to change, so
a local flash that fails here can pass IRIS, and that pass does not clear it.
For broadcast or certification, use a certified process such as Harding FPA.
