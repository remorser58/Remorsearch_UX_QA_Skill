# ergoqa live web driver (`drivers/web/`)

Drives a real Chromium page with Playwright, emulating one catalogued device, and
writes the evidence that `ergoqa analyze` consumes: `ergo-snapshot.v1` files
(screenshot + measured element geometry/colour) and one `ergo-run.v1` per run.
The contract is [`docs/ergonomic-swarm-spec.md`](../../docs/ergonomic-swarm-spec.md)
sections 3, 5 and 10. The driver measures; it never scores ergonomics and never
role-plays a user.

Requirements: Node.js 22 and `playwright@1.56.1` with its Chromium. Install once:

```sh
cd drivers/web
npm install                 # playwright 1.56.1 into drivers/web/node_modules
npx playwright install chromium
node selftest.mjs           # ~1 minute; expects "138 passed"
```

The package is resolved by normal module resolution (so `drivers/web/node_modules`
or a global install both work), then each `NODE_PATH` entry, then
`/opt/node22/lib/node_modules/playwright` (a pre-installed cloud container path).
The driver itself never installs anything.

## Commands

```sh
# Scripted: execute scenario.steps
node drivers/web/ergo_drive.mjs run --scenario sc.json --profile p.json --out runs/ \
  [--run-id R-x] [--base http://127.0.0.1:8765] [--flash-sample-ms 1000]

# Interactive: an LLM persona agent looks at each screenshot and picks the next action
node drivers/web/ergo_drive.mjs serve --scenario sc.json --profile p.json --out runs/ --port 9477

# Self-test (local fixture server, ~1 minute)
node drivers/web/selftest.mjs [--keep]
```

| Option | Meaning |
| --- | --- |
| `--profile P.json` | `ergo-profile.v1`; uses `profile_id`, `attributes.device_id`, `attributes.orientation` |
| `--device ID` | override the profile's device (or run without a profile: `profile_id` becomes `no-profile`) |
| `--device-json F` | a device object (`ergoqa.devices.Device.to_dict()`) instead of the built-in table |
| `--orientation O` | `portrait`/`landscape`; only phones, tablets and foldables rotate (width/height swap) |
| `--base URL` | replaces `{BASE}` in `surface.url` and `success.url_contains` |
| `--flash-sample-ms N` | sample the viewport for N ms after page load, after each input and during snapshot steps, and for the whole of each wait step |
| `--feedback-timeout-ms N` | max wait for the first feedback after an input (default 3000; per-step `feedback_timeout_ms`) |
| `--settle-ms N` | wait after the first feedback before the after-snapshot (default 300; per-step `settle_ms`) |
| `--allow-origin O` | extra origin the page may load (repeatable). Default: only the scenario's origin |
| `--continue-on-error` | scripted: continue after a failed step (default: stop, status `failed`) |
| `--no-auto-scroll` | never scroll a target into view; an off-screen target is `no_target` |
| `--no-visual-feedback` | only DOM mutations/navigation count as feedback |
| `--timeout-s`, `--idle-timeout-s` | scripted run limit / serve idle limit (default 900 s each; ends `blocked`) |
| `--locale`, `--timezone` | default `ko-KR`, `Asia/Seoul` |
| `--headed` | visible browser window (needs a display) |

Exit codes: **0** run completed and `success` is true; **3** run.json written but not
successful (success false or unknown, or a scripted step failed); **2** usage/input
error (nothing is run; an existing non-empty run directory is never overwritten);
**4** driver/browser failure or a `blocked` run (run.json is still written when the
run directory exists). `run` and `serve` print one JSON line per event on stdout
(`ready`, `finished`).

## Devices

`devices.mjs` mirrors `ergoqa/devices.py` (ids, CSS viewport, DPR, input,
form factor); the self-test fails if they drift. Viewport and DPR always come from
the catalog; a named Playwright descriptor (`Galaxy S24`, `iPhone 15`,
`iPhone 15 Pro Max`, `Desktop Chrome`) only supplies its user agent, otherwise a
reduced Chrome UA is used. `hasTouch`/`isMobile` follow `Device.has_touch` /
`Device.is_mobile`. Screenshots are viewport-only PNGs in device pixels
(`viewport x dpr`, e.g. 1080x2340 for galaxy-s24).

## Actions and real input

Every action is dispatched as real browser input (CDP `Input.dispatchTouchEvent`,
Playwright touchscreen/mouse/keyboard), never as synthetic DOM events or `el.click()`.

| action | fields | touch devices | mouse devices |
| --- | --- | --- | --- |
| `tap`, `click` | `target`, `offset?` | touchStart/End | click |
| `double_tap` | `target` | two taps 120 ms apart | dblclick |
| `long_press` | `target`, `ms?` (800) | touch held `ms` | button held `ms` |
| `swipe` | `target?` (start, default centre), `to` or `dx/dy` or `direction`+`distance`, `duration_ms?` (200) | finger path (fling allowed) | drag path |
| `drag` | `target`, `to`/`dx/dy`/`direction`, `hold_ms?` (250), `duration_ms?` (600) | hold, move, hold 100 ms | same with mouse |
| `scroll` | `dx/dy` or `direction`+`distance` (content direction), `target?` | slow finger strokes, slop-compensated, corrected | mouse wheel |
| `type` | `text`, `target?` (tapped/clicked first), `clear?`, `delay_ms?` | keyboard | keyboard |
| `press` | `key`, `hold_ms?`, `repeat?` | keyboard | keyboard |
| `gamepad` | `key` or `keys` (the keyboard mapping), `button?` (label), `hold_ms?` | keyboard | keyboard |
| `wait` | `ms` | | |
| `snapshot` | | | |

Common optional fields: `settle_ms`, `feedback_timeout_ms`, `timeout_ms` (target
wait, default 5000), `auto_scroll`, and metadata (`note`, `label`, `comment`,
`description`, `id`, `intent`, `expected`). A remote (TV) device has no pointer:
pointer actions fall back to mouse events and a warning is recorded
(`input: "mouse(fallback)"`). The Switch-style handheld has a touchscreen and uses touch.

Targets: a Playwright selector (`#pay`, `text=결제하기`, `role=button[name="..."]`),
`hotspot:<id>` (from `scenario.hotspots` or the page's
`window.__ergoqa__.hotspots()`, which wins because it is live), or `{x, y}` viewport
CSS px. The pointer point is the element centre unless `offset` (from the
element's top-left) is given. The step records `point`, `target_element_id` (id in
the `before` snapshot), `hit_element_id` and `target_hit` (is the target the
top-most element at the point, i.e. not covered by an overlay).

If a target appears only after the last snapshot, or its point is outside the
viewport, the driver (unless `--no-auto-scroll`) scrolls it into view
programmatically and takes a **pre-action snapshot** (note
`pre_action_auto_scroll` / `pre_action_target_appeared`) that becomes the step's
`before`, so geometry always matches what was on screen when the input happened.
Snapshot ids are `S-<run_id>-<nnn>` in capture order; `step_index` is the step
they belong to (0 = initial load), so a step can own two snapshots.

## What is measured

- **Elements** (per snapshot, max 400: scenario-role and `data-ergo-role` elements
  first, then interactive, then `role=alert|status`, then visible text blocks):
  box (viewport CSS px), visible/in_viewport/enabled, accessible name
  (aria-labelledby, aria-label, alt, label, text, title), ARIA role (explicit or
  implicit, `generic` when none), tag, unique selector (`#id` preferred),
  font size/weight, `color_fg`, `color_bg`, `container_bg` (behind the element),
  `border_color` for controls, cumulative `opacity`, `roles[]` (scenario targets +
  `data-ergo-role`; unknown role names are dropped with a warning, never guessed),
  `source: "dom"`. Hotspots become `source: "manual"`, `role: "hotspot"`,
  `selector: "hotspot:<id>"`.
- **Colours**: the layers under the element's centre (`elementsFromPoint`, or the
  ancestor chain when off-screen) are composited over the page canvas with group
  opacity; `color_bg` is `null` when an image, video, canvas, SVG or
  background-image/gradient is underneath (unknown, not guessed).
- **Feedback latency**: an init-script `MutationObserver` timestamps DOM changes;
  `feedback_latency_ms` = first DOM mutation or main-frame navigation after input
  dispatch, `null` if none within 3000 ms (`feedback_window_ms` says how long was
  observed). Only when neither occurs does a visual change of the viewport count
  (`feedback_source: "visual_change"`, ~30 ms resolution; covers canvas and
  CSS-only feedback). `feedback_ambient_mutations` / `feedback_visual_ambient` flag
  pages that were already changing before the input (latency then is ambiguous).
- **Timing windows**: each selector is polled in the page every 16 ms; a window
  reports `visible_ms` (shortest completed visible interval, the tightest window a
  user got; null if none completed), `intervals_ms`, `min/max_visible_ms`,
  `appearances`, `open_interval_ms` (still visible at the end, a lower bound, not
  counted), and the text seen. "Visible" = rendered, non-zero box, intersecting
  the viewport. Non-CSS selectors fall back to Playwright polling (`method`).
- **Flash sampling** (`--flash-sample-ms`): CDP screenshots of the viewport
  downscaled to ~160 CSS px wide, as fast as possible (~30 fps here), decoded by
  the built-in PNG decoder (`png.mjs`). Each sample has `t_ms`, `mean_luminance`
  (WCAG relative luminance, 0..1), `frame_index`, `step_index`,
  `changed_fraction` (share of pixels whose luminance changed by >= 0.10 vs the
  previous frame of the burst), `flash_fraction` (same, with the darker state <
  0.80: the WCAG 2.3.1 pair condition) and `red_fraction` (saturated red).
  Each sample also carries a block grid for local and counter-phase flashes:
  `block_lum` and `block_red` (base64, one byte per block: mean relative
  luminance and share of saturated-red pixels, linear R/(R+G+B) >= 0.8 and
  (R-G-B) x 320 > 20), and `block_moved` + `motion_css` when the content moved
  (scrolling is motion, not flashing). Blocks are at least 22 x 40 CSS px and at
  most 820 per frame; the layout is in `run.flash_sampling.block_grid`. A random
  0-15 ms pause between captures breaks phase lock with fast flicker, and
  `flash_sampling` records `sampled_ms`, `mean_fps`, `max_gap_ms`, `bursts` and
  `truncated` (sampling stops at about 6 MB of samples so `run.json` stays below
  ergoqa's input limit).
- **Keyboard focus walk** (mouse and keyboard devices by default; `--focus-walk`
  / `--no-focus-walk`): after the task, when the run ended normally, the driver
  Tabs through up to 40 stops of the end state and then of the initial screen (in a
  separate browser context with the same network policy), each walk within 8 s. It
  resets the sequential focus starting point to the top, turns smooth scrolling off
  and waits for scrolling to settle, and follows focus into open shadow roots and
  same-origin iframes. Per stop, `run.focus_walks[].stops[]` records the focused
  element (`selector`, `dom_id`, `role`, `name` — never a field's value — `box`,
  `frame`), `indicator_px` (pixels that change by >= 24/255 in the element box, its
  small wrappers and 4 px around them, between the focused state and the same
  element blurred at the same scroll position) and `obscured_fraction` /
  `obscured_by` (share of nine sample points covered by a painting fixed or sticky
  layer that does not contain the element). `ended` says why a walk stopped
  (`cycle`, `left_document`, `max_stops`, `time_budget`, `opaque_frame`).
- **Console**: `console.error` and uncaught page errors, per snapshot (since the
  previous one) and in `run.json`. Errors caused by the driver's own network block
  are counted separately, not reported as page errors.
- **Success**: `scenario.success` keys `selector_visible`, `url_contains`,
  `text_present` (string or list; all must hold) are measured at the end
  (`success_basis: "measured"`). Unknown keys make success unknown (`null`). In
  serve mode the persona's `/finish {"success": ...}` is kept as
  `persona_claimed_success` and used only when the scenario declares no criteria
  (`success_basis: "judgment"`).
- Times (`t_start_ms`, `t_end_ms`, `t_ms`) are ms since the initial navigation
  started; page timestamps are converted with a measured clock offset.

## Serve API (interactive persona sessions)

`serve` prints `{"event":"ready","url":"http://127.0.0.1:PORT",...,"snapshot":...,"png":...}`
after the initial snapshot. `--port 0` picks a free port.

| Endpoint | Body | Reply |
| --- | --- | --- |
| `GET /health` | | `{ok, run_id, steps, last_snapshot_id, finished}` |
| `GET /snapshot` | | new snapshot without acting: `{snapshot, png, snapshot_id, step_index, url, title, result}` |
| `POST /act` | one action object (table above) | same plus `result` (`ok`/`no_target`/`error`), `error`, `point`, `target_element_id`, `target_hit`, `feedback_latency_ms`, `feedback_source`, `before`, `auto_scrolled` |
| `POST /note` | `{intent, expected, observed, confusion: bool, step_index?, severity?}` | `{ok, note_index, step_index}`; stored as `persona_notes` with `basis: "judgment"` |
| `POST /finish` | `{success?: bool}` | writes run.json, replies `{run, status, success, success_basis, exit_code}`, then exits |

Requests run one at a time in arrival order. A `no_target` action does not end the
session; the persona can try something else. `status` is `completed` after
`/finish`, `blocked` after an idle timeout, signal or browser crash.

## Security and scope

- The HTTP server binds **127.0.0.1 only**, checks `Host` (DNS rebinding) and
  rejects any foreign `Origin`/`Sec-Fetch-Site` (cross-site POSTs from a browser);
  POST bodies must be `application/json`, at most 64 KiB, JSON objects.
- Unknown actions and unknown action keys are rejected (400). **No endpoint
  evaluates JavaScript**, navigates to a request-supplied URL, or reads/writes a
  request-supplied path. Selectors go to Playwright's selector engines as data.
  There is no token: any local process can reach the port while a session runs,
  so use it on a single-user machine.
- Network policy: the page may load only from the scenario URL's origin (plus
  `data:`/`blob:` and any `--allow-origin`); everything else is aborted and listed
  in `run.json.driver.network_policy`. Service workers are blocked.
- The driver only performs the declared actions on the declared surface. Keep it on
  local fixtures or staging builds; do not point it at production accounts,
  payments or real user data. Screenshots and typed text are written to the run
  directory unredacted.
- Files are written atomically (temp file, fsync, rename); run directories are
  never overwritten.
- The page runs in the main world next to a small driver state object
  (`Symbol.for('ergoqa.driver.v1')`) and, when timing windows exist, a binding named
  `__ergoqaDriverTimingWindow`. A hostile page could read or spoof these; the page
  under test is trusted to that extent.

## Not exercised here (honest limits)

- **Only Chromium device emulation.** No real Android/iOS device, no Safari/WebKit
  or Firefox engine, no native apps, no desktop OS widgets. Android
  (uiautomator) and vision/annotation snapshots are separate drivers (spec
  section 11), not part of this one. An iPhone profile is Chromium with an iPhone
  user agent and viewport, not WebKit.
- No browser UI: the viewport is the full catalog screen (no address bar, system
  bars, notch/safe areas) and no on-screen keyboard (typing does not shrink the
  viewport). No pinch zoom, multi-touch, stylus, hover on touch, haptics or sound.
- Emulated touch in Chromium: a long press does not open a native context menu and
  a click still follows the release; touch slop and fling differ from devices.
- Elements inside iframes and closed shadow roots are not extracted (open shadow
  roots are, with selectors relative to their root). Text colour is the element's
  computed colour (mixed-colour children are separate elements only when they have
  their own direct text). Placeholder colour, text shadows, filters and blend modes
  are ignored; `color_bg` under non-ancestor translucent layers is approximate.
- Feedback latency counts any DOM mutation (including unrelated timers; see the
  ambient flags); CSS-only or canvas feedback is detected only visually at ~30 ms
  resolution; the `:active` state of a touch tap is usually too brief to capture.
- Flash sampling is ~25 fps with capture jitter, on a downscaled frame, and only
  during the sampled windows (after inputs, snapshot steps, whole waits); flicker
  faster than ~12 Hz is seen as flashing at an aliased rate, not its true rate.
  It is an input to the WCAG 2.3.1 check, not a certification.
- `window.__ergoqa__.hotspots()` and scenario hotspots are trusted as declared;
  scenario hotspot boxes are fixed viewport coordinates (only page-provided
  hotspots follow scrolling).
- Tested on Linux with Node 22.22 and Playwright 1.56.1 / Chromium 141 (headless).
  `--headed`, macOS and Windows have not been executed here.
