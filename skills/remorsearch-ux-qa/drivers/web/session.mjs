// WebSession: one emulated device, one page, one run directory.
//
// Produces ergo-snapshot.v1 files and ergo-run.v1 (docs/ergonomic-swarm-spec.md
// sections 3, 5 and 10) from real Playwright/CDP input events. Everything the
// page reports is treated as data; nothing from the page or from HTTP requests
// is evaluated as code.

import fs from 'node:fs';
import path from 'node:path';

import { resolveDevice } from './devices.mjs';
import { STATE_KEY, TW_BINDING, extractSnapshot, hitTest, idAtPoint, idForElement, pageInit } from './page_scripts.mjs';
import {
  BLOCK_MIN_H_CSS, BLOCK_MIN_W_CSS, MOTION_MATCH, RED_EXCESS, RED_RATIO,
  blockStats, cssScaleCopy, decodePng, frameFromImage, frameStats, indicatorPixels, makeBlockGrid, visualDiffFraction,
} from './png.mjs';
import { KNOWN_ROLES } from './validate.mjs';
import {
  DriverFailure, epochNow, isoNow, pngSize, round1, sha256, sleep, truncate, writeFileAtomic, writeJsonAtomic,
} from './util.mjs';

export const ELEMENT_CAP = 400;
export const FEEDBACK_WINDOW_MS = 3000;
const FRAME_WIDTH = 160; // downscaled CSS-px width for flash/visual probe frames
const VISUAL_LEVEL = 16; // per-channel change (0-255) that counts as a changed pixel
const TW_POLL_MS = 16;
const DEFAULT_TARGET_TIMEOUT_MS = 5000;
const MAX_FLASH_SAMPLES = 50000;
// Flash samples carry a block grid (~0.4-2.2 KB of base64 each): sampling stops
// (flash_sampling.truncated) once they would push run.json towards ergoqa's
// 8 MB input limit. ~4,500 phone or ~2,000 desktop samples (1.5-3 min at ~24 fps).
const MAX_FLASH_BYTES = 6_000_000;
// Random pause between flash captures: CDP captures are otherwise phase-locked
// to the compositor (~33 ms), so a 30 Hz flicker would alias to a still image.
const FLASH_JITTER_MS = 15;
const MAX_CONSOLE = 500;
// Keyboard focus walk (WCAG 2.4.7 focus visible, 2.4.11 focus not obscured): Tab
// through up to this many stops; a stop's indicator is the pixel change inside its
// box (+4 px) between focused and unfocused states.
const FOCUS_WALK_MAX = 40;
const FOCUS_DIFF_LEVEL = 24;
const FOCUS_SETTLE_MS = 80;
const FOCUS_WALK_BUDGET_MS = 8000;
// Fewer changed pixels than this near the element sends a stop to the viewport-wide
// comparison (an indicator drawn away from the element, ACT oj04fd); at most
// FOCUS_VIEWPORT_MAX such comparisons per walk (full-viewport captures are slow).
const FOCUS_LOCAL_MIN_PX = 4;
const FOCUS_VIEWPORT_MAX = 6;
const FOCUS_VIEWPORT_WIDTH = 480; // viewport-wide captures are downscaled to about this many px wide
// Gap between the two unfocused captures whose difference masks animation, and the
// per-channel change between them that marks a pixel as animated.
const FOCUS_ANIM_GAP_MS = 40;
const FOCUS_MASK_LEVEL = 4;

// Reflow (WCAG 1.4.10, AUT-06): each distinct screen's DOM is copied as the run goes
// and re-rendered after the run at 320 CSS px wide with scripts off (a static copy,
// so the run itself is never resized). At most REFLOW_MAX_SCREENS per run.
const REFLOW_WIDTH = 320;
const REFLOW_MAX_SCREENS = 12;
const REFLOW_BUDGET_MS = 20000;

const MEASURED = new Set(['tap', 'click', 'double_tap', 'long_press', 'swipe', 'drag', 'type', 'press', 'scroll', 'gamepad']);
const POINTER = new Set(['tap', 'click', 'double_tap', 'long_press', 'swipe', 'drag', 'scroll']);

function firstLine(msg) {
  return truncate(String(msg || '').split('\n')[0], 500);
}

function r4(n) {
  return Math.round(n * 10000) / 10000;
}

function stripQuery(url) {
  try {
    const u = new URL(url);
    return `${u.origin}${u.pathname}`;
  } catch {
    return truncate(url, 200);
  }
}

/**
 * In-page: the deepest focused element (through open shadow roots and same-origin
 * iframes), its identity, box in top-viewport CSS px, and how much of it a painting
 * fixed or sticky layer that does not contain it covers (9 sample points). Null when
 * focus is on the document itself. The name never reads a field's value.
 */
/** In-page, on a static copy at 320 px: does the page scroll sideways, and which outermost
 * elements stick out past the right edge (1.4.10; two-dimensional content exempt)? */
function reflowInfo(limit) {
  const se = document.scrollingElement || document.documentElement;
  const cw = se.clientWidth;
  const sw = se.scrollWidth;
  const clipX = (n) => ['hidden', 'clip'].includes(getComputedStyle(n).overflowX);
  const rootClips = clipX(document.documentElement) || (document.body ? clipX(document.body) : false);
  const out = { client_width: cw, scroll_width: sw, root_clips: rootClips, offenders: [] };
  if (sw <= cw + 1 && !rootClips) return out;
  const TWO_D = new Set(['table', 'canvas', 'video', 'iframe', 'svg', 'pre', 'code', 'map', 'object', 'embed', 'math']);
  const exempt = (n) => {
    for (let m = n; m && m.nodeType === 1 && m !== document.body; m = m.parentElement) {
      const tag = m.tagName.toLowerCase();
      const role = m.getAttribute('role') || '';
      if (TWO_D.has(tag) || ['img', 'application', 'grid', 'treegrid', 'table', 'toolbar'].includes(role)) return true;
      if (m !== n) {
        const ox = getComputedStyle(m).overflowX;
        if (ox === 'auto' || ox === 'scroll') return true; // scrolls inside its own box
        if ((ox === 'hidden' || ox === 'clip') && m.getBoundingClientRect().right <= cw + 1) return true; // clipped by a container that fits
      }
      if (m.getAttribute('aria-hidden') === 'true') return true;
    }
    return false;
  };
  const sel = (n) => {
    if (n.id) return `#${CSS.escape(n.id)}`;
    const parts = [];
    for (let m = n; m && m.nodeType === 1 && m !== document.body && parts.length < 5; m = m.parentElement) {
      if (m.id) {
        parts.unshift(`#${CSS.escape(m.id)}`);
        break;
      }
      const sib = m.parentElement ? [...m.parentElement.children].filter((c) => c.tagName === m.tagName) : [];
      parts.unshift(sib.length > 1 ? `${m.tagName.toLowerCase()}:nth-of-type(${sib.indexOf(m) + 1})` : m.tagName.toLowerCase());
    }
    return parts.join(' > ');
  };
  const hits = [];
  const all = document.body ? document.body.getElementsByTagName('*') : [];
  for (let i = 0; i < all.length && i < 6000; i++) {
    const n = all[i];
    const r = n.getBoundingClientRect();
    if (r.width <= 1 || r.height <= 1 || r.right <= cw + 1) continue;
    const cs = getComputedStyle(n);
    if (cs.display === 'none' || cs.visibility !== 'visible' || parseFloat(cs.opacity) === 0) continue;
    if (!(n.innerText || '').trim() && !['img', 'input', 'button', 'select', 'textarea'].includes(n.tagName.toLowerCase())) continue;
    if (exempt(n)) continue;
    hits.push(n);
  }
  const set = new Set(hits);
  for (const n of hits) {
    let outer = true;
    for (let m = n.parentElement; m; m = m.parentElement) if (set.has(m)) { outer = false; break; }
    if (!outer) continue;
    const r = n.getBoundingClientRect();
    const ids = [];
    for (let m = n.parentElement; m && ids.length < 6; m = m.parentElement) if (m.id) ids.push(m.id);
    out.offenders.push({ selector: sel(n), dom_id: n.id || null, ancestor_ids: ids, tag: n.tagName.toLowerCase(),
      box: { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) },
      text: (n.innerText || n.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 60) });
    if (out.offenders.length >= limit) break;
  }
  return out;
}

function focusInfo() {
  let el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  let ox = 0;
  let oy = 0;
  let doc = document;
  const chain = [];
  for (let depth = 0; depth < 8; depth++) {
    chain.push(el);
    if (el.shadowRoot && el.shadowRoot.activeElement) {
      el = el.shadowRoot.activeElement;
      continue;
    }
    if (el.tagName === 'IFRAME') {
      let inner = null;
      try {
        inner = el.contentDocument && el.contentDocument.activeElement;
      } catch (e) {
        inner = null; // cross-origin frame: stop at the frame element
      }
      if (inner && inner !== el.contentDocument.body) {
        const fr = el.getBoundingClientRect();
        ox += fr.left + el.clientLeft;
        oy += fr.top + el.clientTop;
        doc = el.contentDocument;
        el = inner;
        continue;
      }
    }
    break;
  }
  const view = doc.defaultView || window;
  const r0 = el.getBoundingClientRect();
  const r = { left: r0.left + ox, top: r0.top + oy, width: r0.width, height: r0.height };
  r.right = r.left + r.width;
  r.bottom = r.top + r.height;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const esc = (v) => (window.CSS && CSS.escape ? CSS.escape(v) : v);
  let sel = el.id ? `#${esc(el.id)}` : null;
  if (!sel) {
    const parts = [];
    for (let n = el; n && n.nodeType === 1 && n !== doc.body && parts.length < 6; n = n.parentElement) {
      const tag = n.tagName.toLowerCase();
      if (n.id) {
        parts.unshift(`#${esc(n.id)}`);
        break;
      }
      const sib = n.parentElement ? [...n.parentElement.children].filter((c) => c.tagName === n.tagName) : [];
      parts.unshift(sib.length > 1 ? `${tag}:nth-of-type(${sib.indexOf(n) + 1})` : tag);
    }
    sel = parts.join(' > ');
  }
  const pathOf = (n) => {
    const out = [];
    for (let m = n; m && m.nodeType === 1; m = m.parentElement) out.unshift(m.parentElement ? [...m.parentElement.children].indexOf(m) : 0);
    return out.join('.');
  };
  const path = chain.map(pathOf).join('/');
  const inVp = r.width > 0 && r.height > 0 && r.right > 0 && r.bottom > 0 && r.left < vw && r.top < vh;
  const paints = (n) => {
    const cs = view.getComputedStyle(n);
    const bg = cs.backgroundColor || '';
    const alpha = /rgba\(.*,\s*([\d.]+)\)/.exec(bg);
    if (bg && bg !== 'transparent' && !(alpha && parseFloat(alpha[1]) === 0)) return true;
    if (cs.backgroundImage && cs.backgroundImage !== 'none') return true;
    if (['IMG', 'SVG', 'CANVAS', 'VIDEO'].includes(n.tagName.toUpperCase())) return true;
    for (const c of n.childNodes) if (c.nodeType === 3 && c.nodeValue.trim()) return true;
    return false;
  };
  // Content the user disclosed (WCAG 2.4.11 note): a layer tied to an expanded
  // trigger (aria-expanded="true" + aria-controls) or to a popovertarget button.
  const disclosed = [];
  for (const t of document.querySelectorAll('[aria-expanded="true"][aria-controls]')) {
    for (const id of (t.getAttribute('aria-controls') || '').split(/\s+/)) {
      const target = id && document.getElementById(id);
      if (target) disclosed.push(target);
    }
  }
  for (const t of document.querySelectorAll('[popovertarget]')) {
    const target = document.getElementById(t.getAttribute('popovertarget'));
    let open = false;
    try {
      open = !!target && target.matches(':popover-open');
    } catch (e) {
      open = false;
    }
    if (open) disclosed.push(target);
  }
  const userOpened = (layer) => disclosed.some((d) => d.contains(layer) || layer.contains(d));
  let covered = 0;
  let coveredBy = null;
  let coveredUserOpened = true;
  if (inVp && doc === document) {
    for (const fx of [0.15, 0.5, 0.85]) {
      for (const fy of [0.2, 0.5, 0.8]) {
        const px = Math.min(vw - 1, Math.max(0, r.left + r.width * fx));
        const py = Math.min(vh - 1, Math.max(0, r.top + r.height * fy));
        let hit = document.elementFromPoint(px, py);
        while (hit && hit.shadowRoot) {
          const inner = hit.shadowRoot.elementFromPoint(px, py);
          if (!inner || inner === hit) break;
          hit = inner;
        }
        if (!hit || hit === el || el.contains(hit) || hit.contains(el) || chain.includes(hit)) continue;
        let layer = null;
        for (let n = hit; n && n.nodeType === 1; n = n.parentElement) {
          const pos = getComputedStyle(n).position;
          // Fixed or sticky layers, and non-modal dialogs placed with position:absolute.
          const dialog = n.tagName === 'DIALOG' || ['dialog', 'alertdialog'].includes(n.getAttribute('role'));
          if (pos === 'fixed' || pos === 'sticky' || (pos === 'absolute' && dialog && n.getAttribute('aria-modal') !== 'true')) {
            layer = n;
            break;
          }
        }
        // A fixed dialog or sticky header that contains the focused element is its own
        // layer, not a cover; transparent click-catchers do not hide anything.
        if (layer && !layer.contains(el) && !chain.some((c) => layer.contains(c)) && (paints(hit) || paints(layer))) {
          covered += 1;
          if (!coveredBy) coveredBy = layer.id ? `#${esc(layer.id)}` : layer.tagName.toLowerCase();
          if (!userOpened(layer)) coveredUserOpened = false;
        }
      }
    }
  }
  const tag = el.tagName.toLowerCase();
  const field = ['input', 'select', 'textarea'].includes(tag);
  const txt = (n) => (n ? (n.innerText ?? n.textContent ?? '') : '').replace(/\s+/g, ' ').trim();
  const lb = (el.getAttribute('aria-labelledby') || '').split(/\s+/).map((id) => id && (el.getRootNode().getElementById
    ? el.getRootNode().getElementById(id) : doc.getElementById(id))).filter(Boolean).map(txt).join(' ').trim();
  const labels = el.labels && el.labels.length ? [...el.labels].map(txt).join(' ').trim() : '';
  const name = (lb || (el.getAttribute('aria-label') || '').trim() || labels || (el.getAttribute('title') || '').trim()
    || (field ? (el.getAttribute('placeholder') || '').trim() : el.isContentEditable ? '' : txt(el))).slice(0, 80);
  // Wrappers that draw the focus style (:focus-within borders): the nearest ancestors
  // up to 4x the element's area, so the indicator region includes them.
  const wraps = [];
  for (let n = el.parentElement, i = 0; n && n.nodeType === 1 && i < 3; n = n.parentElement, i++) {
    const a = n.getBoundingClientRect();
    if (a.width * a.height > 4 * Math.max(1, r0.width * r0.height)) break;
    wraps.push({ x: a.left + ox, y: a.top + oy, w: a.width, h: a.height });
  }
  return {
    selector: sel, dom_id: el.id || null, tag, role: el.getAttribute('role') || tag, name, path,
    frame: doc === document ? null : 'iframe',
    box: { x: Math.round(r.left * 100) / 100, y: Math.round(r.top * 100) / 100, w: Math.round(r.width * 100) / 100, h: Math.round(r.height * 100) / 100 },
    wrap_boxes: wraps,
    in_viewport: inVp, obscured_fraction: inVp && doc === document ? Math.round((covered / 9) * 1000) / 1000 : null, obscured_by: coveredBy,
    obscured_user_opened: covered > 0 ? coveredUserOpened : null, vw, vh,
  };
}

export class WebSession {
  constructor({ pw, pwInfo, scenario, deviceRequest, profileId, runId, runDir, mode, options, warnings }) {
    this.pw = pw;
    this.pwInfo = pwInfo;
    this.scenario = scenario;
    this.deviceRequest = deviceRequest;
    this.profileId = profileId;
    this.runId = runId;
    this.runDir = runDir;
    this.mode = mode;
    this.opts = options;
    this.warnings = [...(warnings || [])];
    this.warned = new Set();
    this.steps = [];
    this.snapshots = [];
    this.snapElements = new Map();
    this.personaNotes = [];
    this.consoleAll = [];
    this.consolePending = [];
    this.navEvents = [];
    this.navRequestPending = false;
    this.flashSamples = [];
    this.flashBytes = 0;
    this.flashTruncated = null;
    this.flashGrid = null;
    this.flashPrev = null; // last flash frame (across bursts) for block motion
    this.focusWalks = [];
    this.reflowScreens = [];
    this.reflowSeen = new Set();
    this.reflow = [];
    this.frameIndex = 0;
    this.blocked = [];
    this.blockedCount = 0;
    this.blockedConsole = 0;
    this.blockReasons = [];
    this.snapSeq = 0;
    this.lastSnapshotId = null;
    this.focusPoint = null;
    this.lastActive = null;
    this.clockOffset = 0;
    this.clockRtt = null;
    this.needCalibrate = false;
    this.crashed = false;
    this.finished = null;
    this.startedAt = isoNow();
    this.runStartEpoch = epochNow();
    this.httpStatus = null;
    this.twPollers = [];
    this.tw = new Map(scenario.timing_windows.map((w) => [w.id, {
      def: w, cur: null, intervals: [], starts: [], appearances: 0, firstVisible: null, text: null, method: 'in-page-poll', fallback: false, error: null,
    }]));
    const allowed = new Set(['http:', 'https:'].includes(scenario.origin.protocol) ? [scenario.origin.origin] : []);
    for (const o of options.allowOrigins || []) allowed.add(o);
    this.allowedOrigins = allowed;
  }

  warnOnce(key, msg) {
    if (this.warned.has(key)) return;
    this.warned.add(key);
    this.warnings.push(msg);
  }

  block(reason) {
    this.blockReasons.push(reason);
  }

  rel(epoch) {
    return Math.max(0, round1(epoch - this.runStartEpoch));
  }

  // ------------------------------------------------------------------ lifecycle

  async start() {
    try {
      this.browser = await this.pw.chromium.launch({ headless: !this.opts.headed, timeout: 60000 });
    } catch (err) {
      throw new DriverFailure(`cannot launch Chromium: ${firstLine(err.message)}`);
    }
    this.browserVersion = this.browser.version();
    const dev = resolveDevice({
      ...this.deviceRequest,
      pwDevices: this.pw.devices,
      chromeMajor: parseInt(this.browserVersion, 10),
    });
    this.dev = dev;
    for (const w of dev.warnings) this.warnOnce(`dev:${w}`, w);
    this.vw = dev.contextOptions.viewport.width;
    this.vh = dev.contextOptions.viewport.height;
    this.context = await this.browser.newContext({
      ...dev.contextOptions,
      locale: this.opts.locale,
      timezoneId: this.opts.timezoneId,
      colorScheme: 'light',
      reducedMotion: 'no-preference',
      serviceWorkers: 'block',
      acceptDownloads: false,
    });
    await this.context.route('**/*', (route) => this.onRoute(route));
    await this.context.routeWebSocket(/.*/, (ws) => this.onWebSocket(ws));
    const windows = this.scenario.timing_windows;
    if (windows.length) {
      await this.context.exposeBinding(TW_BINDING, (source, payload) => this.onTimingWindow(source, payload));
    }
    await this.context.addInitScript(pageInit, {
      key: STATE_KEY,
      binding: windows.length ? TW_BINDING : null,
      windows: windows.map((w) => ({ id: w.id, selector: w.selector })),
      pollMs: TW_POLL_MS,
    });
    this.page = await this.context.newPage();
    this.cdp = await this.context.newCDPSession(this.page);
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') this.pushConsole('console', msg.text(), msg.location());
    });
    this.page.on('pageerror', (err) => this.pushConsole('pageerror', err && err.message ? err.message : String(err), null));
    this.page.on('crash', () => {
      this.crashed = true;
      this.block('page crashed');
    });
    this.page.on('request', (req) => {
      try {
        if (req.isNavigationRequest() && req.frame() === this.page.mainFrame()) {
          this.navEvents.push(epochNow());
          this.navRequestPending = true;
        }
      } catch { /* request without frame (service worker) */ }
    });
    this.page.on('framenavigated', (frame) => {
      if (frame !== this.page.mainFrame()) return;
      const t = epochNow();
      this.navEvents.push(t);
      if (this.navRequestPending) {
        // A new document replaced the old one: its timed elements are gone.
        this.navRequestPending = false;
        for (const w of this.tw.values()) if (w.cur) this.applyTransition(w, false, t, null);
        this.needCalibrate = true;
      }
    });

    this.runStartEpoch = epochNow();
    this.startedAt = isoNow();
    let response = null;
    try {
      response = await this.page.goto(this.scenario.url, { waitUntil: 'load', timeout: 30000 });
    } catch (err) {
      this.block(`initial navigation failed: ${firstLine(err.message)}`);
    }
    this.httpStatus = response ? response.status() : null;
    if (response && response.status() >= 400) this.block(`initial navigation returned HTTP ${response.status()}`);
    await this.calibrate().catch(() => {});
    this.needCalibrate = false;
    await sleep(this.opts.settleMs);
    if (this.opts.flashSampleMs > 0) {
      await this.probeFrames({ dispatch: epochNow(), stepIndex: 0, flashMs: this.opts.flashSampleMs, visual: null, fb: { done: true } });
    }
    await this.snapshot(0, []);
  }

  reflowEnabled() {
    if (this.opts.reflow === false) return false;
    return this.scenario.surface_kind !== 'game';
  }

  /** Keep a static copy of a screen for the reflow pass (distinct DOMs only). */
  async keepForReflow(snapshotId) {
    if (!this.reflowEnabled() || this.reflowScreens.length >= REFLOW_MAX_SCREENS) return;
    try {
      const html = await this.page.content();
      const key = sha256(Buffer.from(html));
      if (this.reflowSeen.has(key)) return;
      this.reflowSeen.add(key);
      this.reflowScreens.push({ snapshot_id: snapshotId, url: this.page.url(), html });
    } catch { /* navigating: the next snapshot keeps the screen */ }
  }

  /** Re-render the kept screens at 320 CSS px, scripts off, and record what sticks out. */
  async reflowPass() {
    if (!this.reflowScreens.length) return;
    let context = null;
    const deadline = epochNow() + REFLOW_BUDGET_MS;
    try {
      const touch = this.dev.snapshotDevice.input === 'touch';
      context = await this.browser.newContext({
        viewport: { width: REFLOW_WIDTH, height: touch ? 568 : 256 }, deviceScaleFactor: 1, javaScriptEnabled: false,
        locale: this.opts.locale, timezoneId: this.opts.timezoneId, colorScheme: 'light', serviceWorkers: 'block', acceptDownloads: false,
      });
      await this.installNetworkPolicy(context, false);
      const page = await context.newPage();
      for (const screen of this.reflowScreens) {
        if (epochNow() > deadline) {
          this.warnings.push(`reflow pass stopped at its ${REFLOW_BUDGET_MS} ms budget`);
          break;
        }
        const base = `<base href="${screen.url.replace(/"/g, '&quot;')}">`;
        const html = /<base\s/i.test(screen.html) ? screen.html
          : /<head[^>]*>/i.test(screen.html) ? screen.html.replace(/<head[^>]*>/i, (m) => `${m}${base}`) : `${base}${screen.html}`;
        try {
          await page.setContent(html, { waitUntil: 'load', timeout: 8000 });
          const info = await page.evaluate(reflowInfo, 20);
          this.reflow.push({ snapshot_id: screen.snapshot_id, url: screen.url, width: REFLOW_WIDTH, ...info });
        } catch (err) {
          this.reflow.push({ snapshot_id: screen.snapshot_id, url: screen.url, width: REFLOW_WIDTH, error: firstLine(err.message) });
        }
      }
    } catch (err) {
      this.warnings.push(`reflow pass failed: ${firstLine(err.message)}`);
    } finally {
      if (context) await context.close().catch(() => {});
      this.reflowScreens = [];
    }
  }

  focusWalkEnabled() {
    if (this.opts.focusWalk === true || this.opts.focusWalk === false) return this.opts.focusWalk;
    return !!this.dev && ['mouse', 'keyboard'].includes(this.dev.base.input);
  }

  /** Network policy for a context: HTTP and WebSocket. `count` = add blocks to run.json. */
  async installNetworkPolicy(context, count) {
    if (count) {
      await context.route('**/*', (route) => this.onRoute(route));
      await context.routeWebSocket(/.*/, (ws) => this.onWebSocket(ws));
      return;
    }
    await context.route('**/*', (route) => (this.isAllowed(route.request().url()) ? route.continue() : route.abort('blockedbyclient')).catch(() => {}));
    await context.routeWebSocket(/.*/, (ws) => {
      if (this.isAllowed(ws.url().replace(/^ws/, 'http'))) ws.connectToServer();
      else ws.close({ code: 1008, reason: 'blocked by ergoqa network policy' }).catch(() => {});
    });
  }

  /** Focus walk of the initial screen in a separate context, so the run's page keeps its state. */
  async focusWalkFresh() {
    let context = null;
    try {
      context = await this.browser.newContext({
        ...this.dev.contextOptions, locale: this.opts.locale, timezoneId: this.opts.timezoneId, colorScheme: 'light',
        reducedMotion: 'no-preference', serviceWorkers: 'block', acceptDownloads: false,
      });
      await this.installNetworkPolicy(context, false);
      const page = await context.newPage();
      await page.goto(this.scenario.url, { waitUntil: 'load', timeout: 30000 });
      await sleep(this.opts.settleMs);
      await this.focusWalk(page, 'load', this.snapshots.length ? this.snapshots[0].snapshot_id : null);
    } catch (err) {
      this.warnings.push(`focus walk (load) failed: ${firstLine(err.message)}`);
    } finally {
      if (context) await context.close().catch(() => {});
    }
  }

  /** Clip of the page (or the whole viewport) at CSS scale, decoded (focus indicator comparison). */
  async clipFrame(page, clip) {
    const opts = { scale: 'css', animations: 'disabled', caret: 'hide', timeout: 5000 };
    const buf = await page.screenshot(clip ? { ...opts, clip } : opts);
    return frameFromImage(decodePng(buf));
  }

  /** The whole viewport downscaled to about FOCUS_VIEWPORT_WIDTH px wide (CDP; fast). */
  async viewportFrame(cdp, vw, vh) {
    const scale = Math.min(1, FOCUS_VIEWPORT_WIDTH / vw);
    const r = await cdp.send('Page.captureScreenshot', {
      format: 'png', clip: { x: 0, y: 0, width: vw, height: vh, scale }, captureBeyondViewport: false, optimizeForSpeed: true,
    });
    return frameFromImage(decodePng(Buffer.from(r.data, 'base64')));
  }

  /** Blur the deepest focused element (kept for refocus); false when nothing is focused. */
  async blurFocused(page) {
    return page.evaluate(() => {
      let el = document.activeElement;
      while (el && el.shadowRoot && el.shadowRoot.activeElement) el = el.shadowRoot.activeElement;
      if (!el || el === document.body) return false;
      el.blur();
      window.__ergoFocusEl = el;
      return true;
    });
  }

  async refocus(page) {
    await page.evaluate(() => {
      const el = window.__ergoFocusEl;
      if (el) el.focus({ preventScroll: true });
    });
  }

  /**
   * Tab through the page from the top: per stop, the focused element, how many pixels
   * its focus changes (focused vs blurred, same scroll position, animation masked) in
   * its box and its small wrappers (indicator_px) and, when that is nearly nothing, in
   * the whole viewport (indicator_any_px), and whether a painting fixed or sticky layer
   * or a non-modal absolute dialog covers it (and, in the end state, whether Escape
   * reveals it when the user opened that layer). Bounded by FOCUS_WALK_MAX stops and
   * FOCUS_WALK_BUDGET_MS.
   */
  async focusWalk(page, phase, snapshotId) {
    const stops = [];
    let ended = 'max_stops';
    const deadline = epochNow() + FOCUS_WALK_BUDGET_MS;
    // Smooth scrolling would leave focused elements mid-animation when measured.
    await page.addStyleTag({ content: 'html, body { scroll-behavior: auto !important; }' }).catch(() => {});
    // Reset the sequential focus navigation starting point to the top of the document
    // (blur alone keeps it at the last focused or autofocused element).
    await page.evaluate(() => {
      window.scrollTo(0, 0);
      const b = document.body;
      if (!b) return;
      const had = b.getAttribute('tabindex');
      b.tabIndex = -1;
      b.focus({ preventScroll: true });
      b.blur();
      if (had === null) b.removeAttribute('tabindex');
      else b.setAttribute('tabindex', had);
    });
    const seen = new Set();
    let lastPath = null;
    let repeats = 0;
    let viewportChecks = 0;
    let cdp = null;
    for (let i = 0; i < FOCUS_WALK_MAX; i++) {
      if (epochNow() > deadline) {
        ended = 'time_budget';
        break;
      }
      await page.keyboard.press('Tab');
      await this.settleScroll(page);
      const info = await page.evaluate(focusInfo);
      if (!info) {
        ended = 'left_document';
        break;
      }
      if (info.path === lastPath) {
        // Focus moved inside a cross-origin frame (the frame element stays active).
        if (++repeats >= 3) {
          ended = 'opaque_frame';
          break;
        }
        continue;
      }
      repeats = 0;
      lastPath = info.path;
      if (seen.has(info.path)) {
        ended = 'cycle';
        break;
      }
      seen.add(info.path);
      const boxes = [info.box, ...(info.wrap_boxes || [])];
      const x0 = Math.max(0, Math.floor(Math.min(...boxes.map((b) => b.x)) - 4));
      const y0 = Math.max(0, Math.floor(Math.min(...boxes.map((b) => b.y)) - 4));
      const x1 = Math.min(info.vw, Math.ceil(Math.max(...boxes.map((b) => b.x + b.w)) + 4));
      const y1 = Math.min(info.vh, Math.ceil(Math.max(...boxes.map((b) => b.y + b.h)) + 4));
      const stop = { ...info, path: undefined, wrap_boxes: undefined, vw: undefined, vh: undefined, indicator_px: null, clip_px: null,
        indicator_any_px: null };
      if (info.in_viewport && x1 - x0 >= 2 && y1 - y0 >= 2) {
        // ACT oj04fd: focused vs blurred (blur, not Shift+Tab, so the previous stop's
        // indicator is not mixed in); pixels that change between two blurred captures
        // are animation and are masked.
        const clip = { x: x0, y: y0, width: x1 - x0, height: y1 - y0 };
        const on = await this.clipFrame(page, clip);
        const blurred = await this.blurFocused(page);
        let off = null;
        let off2 = null;
        if (blurred) {
          off = await this.clipFrame(page, clip);
          await sleep(FOCUS_ANIM_GAP_MS);
          off2 = await this.clipFrame(page, clip);
        }
        stop.indicator_px = off ? indicatorPixels(on, off, off2, FOCUS_DIFF_LEVEL, FOCUS_MASK_LEVEL) : null;
        stop.clip_px = [clip.width, clip.height];
        if (blurred && stop.indicator_px !== null && stop.indicator_px < FOCUS_LOCAL_MIN_PX && viewportChecks < FOCUS_VIEWPORT_MAX
            && (info.obscured_fraction || 0) < 0.999) {
          // Nothing near the element: look for an indicator anywhere in the viewport.
          // Focus is restored by keyboard (Shift+Tab, Tab from the blurred starting point)
          // so :focus-visible styles apply as they did; the comparison is kept only when
          // the same element is focused at the same scroll position.
          viewportChecks += 1;
          if (!cdp) cdp = await page.context().newCDPSession(page);
          const scroll = () => page.evaluate(() => [window.scrollX, window.scrollY]);
          // The focused capture is bracketed by two unfocused ones, so an animation
          // changes the pair and is masked.
          const before = await scroll();
          const allOff = await this.viewportFrame(cdp, info.vw, info.vh);
          await page.keyboard.press('Shift+Tab');
          await page.keyboard.press('Tab');
          await this.settleScroll(page);
          const back = await page.evaluate(focusInfo);
          const after = await scroll();
          if (back && back.path === info.path && before[0] === after[0] && before[1] === after[1]
              && Math.abs(back.box.x - info.box.x) < 1 && Math.abs(back.box.y - info.box.y) < 1) {
            const allOn = await this.viewportFrame(cdp, info.vw, info.vh);
            const reblurred = await this.blurFocused(page);
            const allOff2 = reblurred ? await this.viewportFrame(cdp, info.vw, info.vh) : null;
            if (reblurred) await this.refocus(page);
            stop.indicator_any_px = allOff2 ? indicatorPixels(allOn, allOff, allOff2, FOCUS_DIFF_LEVEL, FOCUS_MASK_LEVEL) : null;
            stop.indicator_any_scale = Math.round(Math.min(1, FOCUS_VIEWPORT_WIDTH / info.vw) * 1000) / 1000;
          } else if (!back || back.path !== info.path) {
            await this.refocus(page);
          }
        } else if (blurred) {
          await this.refocus(page);
        }
        await page.evaluate(() => {
          window.__ergoFocusEl = null;
        });
      }
      if (phase === 'end' && info.obscured_user_opened === true && (info.obscured_fraction || 0) >= 0.999) {
        // WCAG 2.4.11 note: content the user opened may cover the focused element if the
        // user can reveal it without moving focus (for example with Escape).
        await page.keyboard.press('Escape');
        await this.settleScroll(page);
        const again = await page.evaluate(focusInfo);
        stop.escape_reveals = !!again && again.path === info.path && (again.obscured_fraction || 0) < 0.999;
      }
      stops.push(stop);
    }
    if (cdp) await cdp.detach().catch(() => {});
    this.focusWalks.push({ phase, snapshot_id: snapshotId, url: page.url(), ended, stops });
  }

  /** Wait until the page stops scrolling after a focus move (max ~600 ms). */
  async settleScroll(page) {
    let prev = null;
    for (let i = 0; i < 12; i++) {
      await sleep(i === 0 ? FOCUS_SETTLE_MS : 50);
      const pos = await page.evaluate(() => [window.scrollX, window.scrollY]).catch(() => null);
      if (pos && prev && pos[0] === prev[0] && pos[1] === prev[1]) return;
      prev = pos;
    }
  }

  /** Run a walk with a hard deadline; a hung page cannot stop run.json from being written. */
  async boundedWalk(fn, phase) {
    let timer = null;
    try {
      await Promise.race([fn(), new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('deadline')), FOCUS_WALK_BUDGET_MS + 5000);
      })]);
    } catch (err) {
      this.warnings.push(`focus walk (${phase}) stopped: ${firstLine(err.message)}`);
    } finally {
      clearTimeout(timer);
    }
  }

  async calibrate() {
    let best = null;
    for (let i = 0; i < 5; i++) {
      const t0 = epochNow();
      const pageEpoch = await this.page.evaluate(() => performance.timeOrigin + performance.now());
      const t1 = epochNow();
      if (!best || t1 - t0 < best.rtt) best = { rtt: t1 - t0, offset: pageEpoch - (t0 + t1) / 2 };
    }
    this.clockOffset = best.offset;
    this.clockRtt = best.rtt;
  }

  pushConsole(type, text, location) {
    const msg = String(text ?? '');
    if (this.blockedCount > 0 && msg.includes('ERR_BLOCKED_BY_CLIENT')) {
      this.blockedConsole++;
      return; // caused by the driver's network policy, not by the page
    }
    const entry = {
      t_ms: this.rel(epochNow()),
      type,
      text: truncate(msg, 1000),
      url: location && location.url ? stripQuery(location.url) : null,
    };
    if (this.consoleAll.length < MAX_CONSOLE) this.consoleAll.push(entry);
    if (this.consolePending.length < 100) this.consolePending.push(`[${type}] ${truncate(msg, 500)}`);
  }

  isAllowed(url) {
    let u;
    try {
      u = new URL(url);
    } catch {
      return false;
    }
    if (['data:', 'blob:', 'about:'].includes(u.protocol)) return true;
    if (u.protocol === 'file:') {
      const s = this.scenario.origin;
      if (s.protocol !== 'file:') return false;
      const dir = s.pathname.slice(0, s.pathname.lastIndexOf('/') + 1);
      return u.pathname.startsWith(dir);
    }
    return this.allowedOrigins.has(u.origin);
  }

  onRoute(route) {
    const req = route.request();
    const url = req.url();
    if (this.isAllowed(url)) return route.continue().catch(() => {});
    this.blockedCount++;
    if (this.blocked.length < 50) this.blocked.push({ t_ms: this.rel(epochNow()), url: stripQuery(url), resource_type: req.resourceType() });
    return route.abort('blockedbyclient').catch(() => {});
  }

  onWebSocket(ws) {
    const url = ws.url();
    const asHttp = url.replace(/^ws/, 'http');
    if (this.isAllowed(asHttp)) {
      ws.connectToServer();
      return;
    }
    this.blockedCount++;
    if (this.blocked.length < 50) this.blocked.push({ t_ms: this.rel(epochNow()), url: stripQuery(url), resource_type: 'websocket' });
    ws.close({ code: 1008, reason: 'blocked by ergoqa network policy' }).catch(() => {});
  }

  // ------------------------------------------------------------------ timing windows

  onTimingWindow(source, payload) {
    try {
      if (!source || source.frame !== this.page.mainFrame()) return;
    } catch {
      return;
    }
    if (!payload || typeof payload !== 'object' || typeof payload.id !== 'string') return;
    const w = this.tw.get(payload.id);
    if (!w || w.fallback) return;
    if (payload.v === null) {
      this.startFallbackPoll(w);
      return;
    }
    if (typeof payload.v !== 'boolean' || typeof payload.t !== 'number' || !Number.isFinite(payload.t)) return;
    const text = typeof payload.text === 'string' ? payload.text.slice(0, 500) : null;
    const b = payload.box;
    if (payload.v && b && [b.x, b.y, b.w, b.h].every((n) => typeof n === 'number' && Number.isFinite(n))) {
      const area = b.w * b.h;
      if (!w.appearBox || area > w.appearBox.w * w.appearBox.h) {
        w.appearBox = { x: Math.round(b.x * 100) / 100, y: Math.round(b.y * 100) / 100, w: Math.round(b.w * 100) / 100, h: Math.round(b.h * 100) / 100 };
        w.appearBg = typeof payload.bg === 'string' ? payload.bg.slice(0, 64) : null;
      }
    }
    if (payload.v && payload.off === true && !w.cur) w.offscreenAppearances = (w.offscreenAppearances || 0) + 1;
    this.applyTransition(w, payload.v, payload.t - this.clockOffset, text);
  }

  applyTransition(w, visible, t, text) {
    if (visible && !w.cur) {
      w.cur = { since: t };
      w.appearances++;
      if (w.starts.length < 2000) w.starts.push(t);
      if (w.firstVisible === null) w.firstVisible = t;
      if (text && !w.text) w.text = text;
    } else if (!visible && w.cur) {
      w.intervals.push(Math.max(0, t - w.cur.since));
      w.cur = null;
    }
  }

  startFallbackPoll(w) {
    // Not a CSS selector (e.g. "text=..."): poll with Playwright every 16 ms.
    w.fallback = true;
    w.method = 'playwright-poll';
    let busy = false;
    const timer = setInterval(async () => {
      if (busy || this.finished || this.crashed) return;
      busy = true;
      try {
        const t0 = epochNow();
        const n = await this.page.locator(w.def.selector).filter({ visible: true }).count();
        const t1 = epochNow();
        let text = null;
        if (n > 0 && !w.cur && !w.text) {
          text = await this.page.locator(w.def.selector).filter({ visible: true }).first().innerText({ timeout: 200 }).catch(() => null);
        }
        this.applyTransition(w, n > 0, (t0 + t1) / 2, text ? text.replace(/\s+/g, ' ').trim() : null);
      } catch (err) {
        w.error = firstLine(err.message);
      } finally {
        busy = false;
      }
    }, TW_POLL_MS);
    this.twPollers.push(timer);
  }

  timingWindowsOut(endEpoch) {
    const out = [];
    for (const w of this.tw.values()) {
      const closed = w.intervals.map(round1);
      const open = w.cur ? round1(endEpoch - w.cur.since) : null;
      out.push({
        id: w.def.id,
        selector: w.def.selector,
        measure: w.def.measure,
        ...(w.def.kind ? { kind: w.def.kind } : {}),
        ...(w.def.text || w.text ? { text: w.def.text || w.text } : {}),
        // Shortest completed visible interval (the tightest window a user got);
        // null when the element never both appeared and disappeared.
        visible_ms: closed.length ? Math.min(...closed) : null,
        intervals_ms: closed,
        min_visible_ms: closed.length ? Math.min(...closed) : null,
        max_visible_ms: closed.length ? Math.max(...closed) : null,
        appearances: w.appearances,
        // Appearances whose whole box was outside the viewport (could not be read there).
        offscreen_appearances: w.offscreenAppearances || 0,
        // Appearance start times relative to run start (flash-rate estimation).
        starts_ms: w.starts.map((t) => round1(this.rel(t))),
        ...(w.appearBox ? { appear_box: w.appearBox, appear_bg: w.appearBg } : {}),
        open_interval_ms: open,
        first_visible_t_ms: w.firstVisible !== null ? this.rel(w.firstVisible) : null,
        poll_interval_ms: TW_POLL_MS,
        method: w.method,
        error: w.error,
      });
    }
    return out;
  }

  // ------------------------------------------------------------------ page state helpers

  async firstMutation(t0, t1) {
    try {
      const v = await this.page.evaluate(({ key, a, b }) => {
        const s = window[Symbol.for(key)];
        return s && s.firstMutationAfter ? s.firstMutationAfter(a, b) : null;
      }, { key: STATE_KEY, a: t0 + this.clockOffset, b: t1 + this.clockOffset });
      return v === null ? null : v - this.clockOffset;
    } catch {
      return null;
    }
  }

  async countMutations(t0, t1) {
    try {
      return await this.page.evaluate(({ key, a, b }) => {
        const s = window[Symbol.for(key)];
        return s && s.countMutations ? s.countMutations(a, b) : 0;
      }, { key: STATE_KEY, a: t0 + this.clockOffset, b: t1 + this.clockOffset });
    } catch {
      return null;
    }
  }

  async scrollPos() {
    try {
      return await this.page.evaluate(() => ({ x: window.scrollX, y: window.scrollY }));
    } catch {
      return null;
    }
  }

  async captureFrame() {
    const scale = Math.min(1, FRAME_WIDTH / this.vw);
    const r = await this.cdp.send('Page.captureScreenshot', {
      format: 'png',
      clip: { x: 0, y: 0, width: this.vw, height: this.vh, scale },
      captureBeyondViewport: false,
      optimizeForSpeed: true,
    });
    return frameFromImage(decodePng(Buffer.from(r.data, 'base64')));
  }

  visualThreshold(frame) {
    const n = frame.width * frame.height;
    return Math.max(3 / n, 0.0004);
  }

  /** Capture downscaled frames after `dispatch` for flash sampling and/or visual feedback. */
  async probeFrames({ dispatch, stepIndex, flashMs, visual, fb }) {
    let prev = null;
    for (;;) {
      if (!this.page || this.crashed || this.page.isClosed()) return;
      const now = epochNow();
      const wantFlash = flashMs > 0 && now < dispatch + flashMs;
      const wantVisual = !!visual && fb.visual == null && !fb.done && now < visual.deadline;
      if (!wantFlash && !wantVisual) return;
      const t0 = epochNow();
      let frame;
      try {
        frame = await this.captureFrame();
      } catch {
        await sleep(16);
        continue;
      }
      const t1 = epochNow();
      const tm = (t0 + t1) / 2;
      if (wantVisual && visual.pre) {
        // The frame reflects the page when the capture was requested (t0): the
        // change happened before t0 and after the previous capture started.
        const d = visualDiffFraction(frame, visual.pre, VISUAL_LEVEL);
        if (d !== null && d >= this.visualThreshold(frame)) fb.visual = t0;
      }
      if (wantFlash && this.flashSamples.length < MAX_FLASH_SAMPLES && this.flashBytes < MAX_FLASH_BYTES) {
        const st = frameStats(frame, prev);
        const sample = {
          t_ms: this.rel(tm),
          mean_luminance: r4(st.mean_luminance),
          changed_fraction: prev ? r4(st.changed_fraction) : 0,
          flash_fraction: prev ? r4(st.flash_fraction) : 0,
          red_fraction: r4(st.red_fraction),
          frame_index: this.frameIndex++,
          step_index: stepIndex,
          capture_ms: round1(t1 - t0),
        };
        this.addBlockStats(sample, frame);
        this.flashSamples.push(sample);
        this.flashBytes += JSON.stringify(sample).length + 160; // + pretty-print indentation in run.json
        prev = frame;
        this.flashPrev = frame;
      } else if (wantFlash && !this.flashTruncated) {
        this.flashTruncated = { t_ms: this.rel(tm), step_index: stepIndex, samples: this.flashSamples.length };
      }
      if (wantFlash) await sleep(Math.random() * FLASH_JITTER_MS);
    }
  }

  /** Block grid statistics of a flash frame (png.mjs blockStats), base64 encoded into the sample. */
  addBlockStats(sample, frame) {
    if (!this.flashGrid) this.flashGrid = makeBlockGrid(frame.width, frame.height, this.vw, this.vh);
    const bs = blockStats(frame, this.flashGrid, this.flashPrev);
    if (!bs) return; // frame size changed: no grid for this sample
    sample.block_lum = Buffer.from(bs.lum).toString('base64');
    sample.block_red = Buffer.from(bs.red).toString('base64');
    if (bs.moved) {
      sample.block_moved = Buffer.from(bs.moved).toString('base64');
      sample.motion_css = [round1((bs.shift[0] * this.vw) / frame.width), round1((bs.shift[1] * this.vh) / frame.height)];
    }
  }

  /** Sampling coverage: bursts are runs of samples of one step (one sampling window). */
  flashCoverage() {
    const s = this.flashSamples;
    const gaps = [];
    let sampled = 0;
    let bursts = s.length ? 1 : 0;
    let first = s.length ? s[0].t_ms : 0;
    for (let i = 1; i <= s.length; i++) {
      if (i === s.length || s[i].step_index !== s[i - 1].step_index) {
        sampled += s[i - 1].t_ms - first;
        if (i < s.length) {
          bursts++;
          first = s[i].t_ms;
        }
      } else {
        gaps.push(s[i].t_ms - s[i - 1].t_ms);
      }
    }
    return {
      bursts,
      sampled_ms: round1(sampled),
      mean_fps: sampled > 0 ? round1((gaps.length * 1000) / sampled) : null,
      max_gap_ms: gaps.length ? round1(Math.max(...gaps)) : null,
      mean_interval_ms: gaps.length ? round1(gaps.reduce((a, b) => a + b, 0) / gaps.length) : null,
    };
  }

  flashGridOut() {
    const g = this.flashGrid;
    if (!g) return null;
    return {
      cols: g.cols,
      rows: g.rows,
      block_css: [Math.round(g.blockCss[0] * 100) / 100, Math.round(g.blockCss[1] * 100) / 100],
      viewport_css: [g.viewportW, g.viewportH],
      frame_px: [g.frameW, g.frameH],
      min_block_css: [BLOCK_MIN_W_CSS, BLOCK_MIN_H_CSS],
      order: 'row-major: block index = row * cols + col, from the viewport top-left',
      block_lum: 'base64, one byte per block: round(255 * mean WCAG relative luminance)',
      block_red: `base64, one byte per block: round(255 * share of saturated-red pixels: linear R/(R+G+B) >= ${RED_RATIO} and (R-G-B)*320 > ${Math.round(RED_EXCESS * 320)})`,
      block_moved: `base64 bitmask, bit (b & 7) of byte (b >> 3): block b changed since the previous flash frame only because the content moved by motion_css (mean luminance and red share match the shifted previous frame within ${MOTION_MATCH}, or the content entered the viewport); absent when no content shift was detected`,
    };
  }

  // ------------------------------------------------------------------ snapshots

  async targetGroups() {
    const groups = [];
    const handlesToDispose = [];
    const hotspotRoles = {};
    for (const [role, sels] of Object.entries(this.scenario.targets)) {
      const handles = [];
      for (const sel of sels) {
        if (sel.startsWith('hotspot:')) {
          const id = sel.slice('hotspot:'.length);
          (hotspotRoles[id] ||= []).push(role);
          continue;
        }
        try {
          const hs = await this.page.locator(sel).elementHandles();
          handles.push(...hs.slice(0, 50));
          handlesToDispose.push(...hs);
        } catch (err) {
          this.warnOnce(`target:${sel}`, `target selector ${JSON.stringify(sel)} (${role}) could not be evaluated: ${firstLine(err.message)}`);
        }
      }
      groups.push({ role, handles });
    }
    return { groups, hotspotRoles, handlesToDispose };
  }

  async extract() {
    const { groups, hotspotRoles, handlesToDispose } = await this.targetGroups();
    try {
      return await this.page.evaluate(extractSnapshot, {
        key: STATE_KEY,
        cap: ELEMENT_CAP,
        groups,
        hotspots: this.scenario.hotspots,
        hotspotRoles,
        knownRoles: KNOWN_ROLES,
      });
    } finally {
      await Promise.all(handlesToDispose.map((h) => h.dispose().catch(() => {})));
    }
  }

  async snapshot(stepIndex, notes) {
    if (this.needCalibrate) {
      this.needCalibrate = false;
      await this.calibrate().catch(() => {});
    }
    const seq = this.snapSeq++;
    const id = `S-${this.runId}-${String(seq).padStart(3, '0')}`;
    let png;
    let ex;
    for (let attempt = 0; ; attempt++) {
      try {
        png = await this.page.screenshot({ type: 'png', scale: 'device', animations: 'allow', caret: 'initial', timeout: 15000 });
        ex = await this.extract();
        break;
      } catch (err) {
        if (attempt >= 2 || this.crashed || this.page.isClosed()) {
          throw new DriverFailure(`snapshot ${id} failed: ${firstLine(err.message)}`);
        }
        await this.page.waitForLoadState('load', { timeout: 10000 }).catch(() => {});
      }
    }
    const capturedAt = isoNow();
    const allNotes = [...notes];
    if (ex.truncated) allNotes.push(`elements capped at ${ELEMENT_CAP} of ${ex.candidates} candidates (roles and interactive elements first)`);
    if (ex.pageHotspotError) allNotes.push(ex.pageHotspotError);
    for (const r of ex.unknownRoles) this.warnOnce(`role:${r}`, `unknown role ${JSON.stringify(r)} (data-ergo-role or hotspot) ignored; allowed: ${KNOWN_ROLES.join(', ')}`);
    const { width, height } = pngSize(png);
    const ew = Math.round(this.vw * this.dev.base.dpr);
    const eh = Math.round(this.vh * this.dev.base.dpr);
    if (Math.abs(width - ew) > 1 || Math.abs(height - eh) > 1) allNotes.push(`screenshot is ${width}x${height}, expected about ${ew}x${eh}`);
    if (ex.viewport.w !== this.vw || ex.viewport.h !== this.vh) {
      allNotes.push(`page reports viewport ${ex.viewport.w}x${ex.viewport.h} (layout zoom or meta viewport); boxes are in page CSS px`);
    }
    this.lastActive = ex.active;
    let title = null;
    try {
      title = await this.page.title();
    } catch { /* navigating */ }
    // CSS-scale copy for fast analysis in Python (derived from the same capture).
    let cssCopy = null;
    try {
      cssCopy = cssScaleCopy(png, this.dev.base.dpr);
    } catch (err) {
      allNotes.push(`css-scale copy failed: ${firstLine(err.message)}`);
    }
    const snap = {
      schema_version: 'ergo-snapshot.v1',
      snapshot_id: id,
      run_id: this.runId,
      step_index: stepIndex,
      captured_at: capturedAt,
      surface: { kind: this.scenario.surface_kind === 'game' ? 'game' : 'web', url: this.page.url(), title, app_id: null, scroll: ex.scroll },
      device: this.dev.snapshotDevice,
      screenshot: {
        path: `${id}.png`, sha256: sha256(png), width_px: width, height_px: height,
        ...(cssCopy ? { css: { path: `${id}.css.png`, sha256: sha256(cssCopy.png), width_px: cssCopy.width, height_px: cssCopy.height, factor: cssCopy.factor } } : {}),
      },
      elements: ex.elements,
      focus_point: this.focusPoint,
      console_errors: this.consolePending.splice(0),
      notes: allNotes,
    };
    const pngPath = path.join(this.runDir, `${id}.png`);
    const jsonPath = path.join(this.runDir, `${id}.json`);
    writeFileAtomic(pngPath, png);
    if (cssCopy) writeFileAtomic(path.join(this.runDir, `${id}.css.png`), cssCopy.png);
    writeJsonAtomic(jsonPath, snap);
    this.snapshots.push({ snapshot_id: id, step_index: stepIndex, path: `${id}.json`, png: `${id}.png` });
    this.lastSnapshotId = id;
    await this.keepForReflow(id);
    // Keep recent element lists to anchor persona notes (note -> element -> selector).
    this.snapElements.set(id, { elements: ex.elements, url: snap.surface.url });
    if (this.snapElements.size > 64) this.snapElements.delete(this.snapElements.keys().next().value);
    return { id, jsonPath, pngPath, snap };
  }

  // ------------------------------------------------------------------ targets

  inViewport(p) {
    return p.x >= 0 && p.y >= 0 && p.x < this.vw && p.y < this.vh;
  }

  clampPoint(p) {
    return { x: Math.min(this.vw - 1, Math.max(0, p.x)), y: Math.min(this.vh - 1, Math.max(0, p.y)) };
  }

  async resolveTarget(target, offset, timeoutMs) {
    const rp = (p) => ({ x: Math.round(p.x * 100) / 100, y: Math.round(p.y * 100) / 100 });
    if (typeof target === 'object') {
      const hit = await this.page.evaluate(idAtPoint, { key: STATE_KEY, x: target.x, y: target.y }).catch(() => ({ id: null }));
      return { kind: 'point', point: rp(target), elementId: hit.id, handle: null, waited: false };
    }
    if (target.startsWith('hotspot:')) {
      const id = target.slice('hotspot:'.length);
      const spot = await this.page.evaluate(({ id: hid, declared }) => {
        try {
          const api = window.__ergoqa__;
          if (api && typeof api.hotspots === 'function') {
            const list = api.hotspots();
            if (Array.isArray(list)) {
              const h = list.find((x) => x && x.id === hid);
              if (h && h.box && [h.box.x, h.box.y, h.box.w, h.box.h].every((n) => typeof n === 'number' && Number.isFinite(n))) {
                return { box: { x: h.box.x, y: h.box.y, w: h.box.w, h: h.box.h }, origin: 'page' };
              }
            }
          }
        } catch (e) { /* fall back to the scenario declaration */ }
        const d = declared.find((x) => x.id === hid);
        return d ? { box: d.box, origin: 'scenario' } : null;
      }, { id, declared: this.scenario.hotspots }).catch(() => null);
      if (!spot) return { kind: 'missing', error: `hotspot ${JSON.stringify(id)} is declared neither by the scenario nor by window.__ergoqa__.hotspots()` };
      const b = spot.box;
      const point = offset ? { x: b.x + offset.x, y: b.y + offset.y } : { x: b.x + b.w / 2, y: b.y + b.h / 2 };
      return {
        kind: 'hotspot', point: rp(point), elementId: `hs-${id.replace(/[^A-Za-z0-9._-]/g, '_')}`, handle: null, box: b, origin: spot.origin, waited: false,
      };
    }
    const deadline = epochNow() + timeoutMs;
    let waited = false;
    for (;;) {
      let handle = null;
      let any = 0;
      try {
        const loc = this.page.locator(target);
        const vis = loc.filter({ visible: true });
        if ((await vis.count()) > 0) handle = await vis.first().elementHandle({ timeout: 1000 });
        else any = await loc.count();
      } catch (err) {
        const msg = firstLine(err.message);
        if (/selector|parse|Unexpected token|Unknown engine/i.test(msg)) return { kind: 'missing', error: `invalid selector ${JSON.stringify(target)}: ${msg}` };
      }
      if (handle) {
        const box = await handle.boundingBox().catch(() => null);
        if (box && box.width > 0 && box.height > 0) {
          const point = offset ? { x: box.x + offset.x, y: box.y + offset.y } : { x: box.x + box.width / 2, y: box.y + box.height / 2 };
          const info = await handle.evaluate(idForElement, STATE_KEY).catch(() => ({ id: null, exact: false, interactive: false }));
          return {
            kind: 'selector', point: rp(point), elementId: info.id, exact: info.exact, interactive: info.interactive, handle, box, waited,
          };
        }
        await handle.dispose().catch(() => {});
      }
      if (epochNow() > deadline) {
        return {
          kind: 'missing',
          error: any ? `${JSON.stringify(target)} matched ${any} element(s) but none is visible` : `no element matches ${JSON.stringify(target)}`,
        };
      }
      waited = true;
      await sleep(50);
    }
  }

  // ------------------------------------------------------------------ input

  pointerMode() {
    if (this.dev.contextOptions.hasTouch) return 'touch';
    if (this.dev.base.input === 'mouse') return 'mouse';
    this.warnOnce('pointer-fallback', `${this.dev.base.id} has no pointer (input=${this.dev.base.input}); pointer actions were sent as mouse events (fallback)`);
    return 'mouse(fallback)';
  }

  async touchPath(start, end, durationMs, holdStartMs, holdEndMs) {
    const steps = Math.max(2, Math.round(durationMs / 16));
    await this.cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: start.x, y: start.y }] });
    if (holdStartMs) await sleep(holdStartMs);
    for (let i = 1; i <= steps; i++) {
      const f = i / steps;
      await this.cdp.send('Input.dispatchTouchEvent', {
        type: 'touchMove',
        touchPoints: [{ x: start.x + (end.x - start.x) * f, y: start.y + (end.y - start.y) * f }],
      });
      await sleep(durationMs / steps);
    }
    if (holdEndMs) await sleep(holdEndMs);
    await this.cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  }

  async mousePath(start, end, durationMs, holdStartMs, holdEndMs) {
    const steps = Math.max(2, Math.round(durationMs / 16));
    await this.page.mouse.move(start.x, start.y);
    await this.page.mouse.down();
    if (holdStartMs) await sleep(holdStartMs);
    for (let i = 1; i <= steps; i++) {
      const f = i / steps;
      await this.page.mouse.move(start.x + (end.x - start.x) * f, start.y + (end.y - start.y) * f);
      await sleep(durationMs / steps);
    }
    if (holdEndMs) await sleep(holdEndMs);
    await this.page.mouse.up();
  }

  async gestureEnd(action, start) {
    if (action.to !== undefined) {
      const r = await this.resolveTarget(action.to, undefined, 2000);
      if (r.kind === 'missing') throw new Error(`gesture destination: ${r.error}`);
      if (r.handle) await r.handle.dispose().catch(() => {});
      return this.clampPoint(r.point);
    }
    let dx = action.dx ?? 0;
    let dy = action.dy ?? 0;
    if (action.direction) {
      const vertical = action.direction === 'up' || action.direction === 'down';
      const d = action.distance ?? (vertical ? this.vh : this.vw) * 0.5;
      dx = action.direction === 'right' ? d : action.direction === 'left' ? -d : 0;
      dy = action.direction === 'down' ? d : action.direction === 'up' ? -d : 0;
    }
    return this.clampPoint({ x: start.x + dx, y: start.y + dy });
  }

  async doScroll(action, anchorIn) {
    let dx = action.dx ?? 0;
    let dy = action.dy ?? 0;
    if (action.direction) {
      const vertical = action.direction === 'up' || action.direction === 'down';
      const d = action.distance ?? (vertical ? this.vh : this.vw) * 0.6;
      dx = action.direction === 'right' ? d : action.direction === 'left' ? -d : 0;
      dy = action.direction === 'down' ? d : action.direction === 'up' ? -d : 0;
    }
    const anchor = anchorIn || { x: this.vw / 2, y: this.vh / 2 };
    const mode = this.pointerMode();
    if (mode === 'touch') {
      // Finger moves opposite to the content; slow strokes with a final hold avoid
      // fling. Each stroke loses the touch slop (~10-15 CSS px in Chromium), so
      // strokes are lengthened by SLOP and, when the window is the scroller, up to
      // three corrective strokes close the remaining distance (scroll_delta
      // records what actually happened).
      const SLOP = 14;
      const maxY = Math.max(40, Math.min(this.vh * 0.6, 2 * Math.min(anchor.y, this.vh - anchor.y) - 16)) - SLOP;
      const maxX = Math.max(40, Math.min(this.vw * 0.6, 2 * Math.min(anchor.x, this.vw - anchor.x) - 16)) - SLOP;
      const stroke = async (cx, cy) => {
        const fx = cx === 0 ? 0 : cx + Math.sign(cx) * SLOP;
        const fy = cy === 0 ? 0 : cy + Math.sign(cy) * SLOP;
        const start = this.clampPoint({ x: anchor.x + fx / 2, y: anchor.y + fy / 2 });
        const end = this.clampPoint({ x: anchor.x - fx / 2, y: anchor.y - fy / 2 });
        await this.touchPath(start, end, action.duration_ms ?? 350, 0, 120);
        await sleep(60);
      };
      const origin = await this.scrollPos();
      let remX = dx;
      let remY = dy;
      for (let i = 0; i < 40 && (Math.abs(remX) > 0.5 || Math.abs(remY) > 0.5); i++) {
        const cx = Math.max(-maxX, Math.min(maxX, remX));
        const cy = Math.max(-maxY, Math.min(maxY, remY));
        await stroke(cx, cy);
        remX -= cx;
        remY -= cy;
      }
      for (let k = 0; origin && k < 3; k++) {
        const cur = await this.scrollPos();
        if (!cur || (cur.x === origin.x && cur.y === origin.y)) break; // not the window scroller
        const rx = dx - (cur.x - origin.x);
        const ry = dy - (cur.y - origin.y);
        if (Math.abs(rx) <= 2 && Math.abs(ry) <= 2) break;
        await stroke(Math.max(-maxX, Math.min(maxX, rx)), Math.max(-maxY, Math.min(maxY, ry)));
        const next = await this.scrollPos();
        if (!next || (Math.abs(next.x - cur.x) < 1 && Math.abs(next.y - cur.y) < 1)) break; // at the scroll limit
      }
      return 'touch';
    }
    await this.page.mouse.move(anchor.x, anchor.y);
    await this.page.mouse.wheel(dx, dy);
    await sleep(150);
    return mode;
  }

  async dispatchInput(action, resolved) {
    const kind = action.action;
    const p = resolved ? resolved.point : null;
    const center = { x: this.vw / 2, y: this.vh / 2 };
    const mode = POINTER.has(kind) || (kind === 'type' && p) ? this.pointerMode() : null;
    const touch = mode === 'touch';
    switch (kind) {
      case 'tap':
      case 'click':
        if (touch) await this.page.touchscreen.tap(p.x, p.y);
        else await this.page.mouse.click(p.x, p.y);
        return mode;
      case 'double_tap':
        if (touch) {
          await this.page.touchscreen.tap(p.x, p.y);
          await sleep(120);
          await this.page.touchscreen.tap(p.x, p.y);
        } else {
          await this.page.mouse.dblclick(p.x, p.y);
        }
        return mode;
      case 'long_press': {
        const ms = action.ms ?? action.duration_ms ?? 800;
        if (touch) {
          await this.cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: p.x, y: p.y }] });
          await sleep(ms);
          await this.cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
        } else {
          await this.page.mouse.move(p.x, p.y);
          await this.page.mouse.down();
          await sleep(ms);
          await this.page.mouse.up();
        }
        return mode;
      }
      case 'swipe':
      case 'drag': {
        const start = p || center;
        const end = await this.gestureEnd(action, start);
        const duration = action.duration_ms ?? (kind === 'swipe' ? 200 : 600);
        const holdStart = kind === 'drag' ? (action.hold_ms ?? 250) : 0;
        const holdEnd = kind === 'drag' ? 100 : 0;
        if (touch) await this.touchPath(start, end, duration, holdStart, holdEnd);
        else await this.mousePath(start, end, duration, holdStart, holdEnd);
        return { input: mode, start, end };
      }
      case 'type':
        if (p) {
          if (touch) await this.page.touchscreen.tap(p.x, p.y);
          else await this.page.mouse.click(p.x, p.y);
          await sleep(80);
        }
        if (action.clear) {
          await this.page.keyboard.press('ControlOrMeta+A');
          await this.page.keyboard.press('Backspace');
        }
        await this.page.keyboard.type(action.text, { delay: action.delay_ms ?? 25 });
        return p ? `${mode}+keyboard` : 'keyboard';
      case 'press':
        for (let i = 0; i < (action.repeat ?? 1); i++) {
          await this.page.keyboard.press(action.key, { delay: action.hold_ms ?? 0 });
        }
        return 'keyboard';
      case 'gamepad':
        for (const k of action.keys ?? [action.key]) {
          await this.page.keyboard.down(k);
          await sleep(action.hold_ms ?? 80);
          await this.page.keyboard.up(k);
        }
        return 'keyboard(gamepad-mapping)';
      case 'scroll':
        return this.doScroll(action, p);
      default:
        throw new Error(`unsupported action ${kind}`);
    }
  }

  /** Wait until a DOM mutation or main-frame navigation follows `dispatch`, or the deadline. */
  async waitForFeedback(dispatch, deadline) {
    while (epochNow() < deadline) {
      if (this.navEvents.some((t) => t >= dispatch)) return;
      if ((await this.firstMutation(dispatch, deadline + 1e6)) !== null) return;
      await sleep(16);
    }
  }

  async performInput(action, resolved, step) {
    const kind = action.action;
    const fbTimeout = action.feedback_timeout_ms ?? (kind === 'scroll' ? 0 : this.opts.feedbackTimeoutMs);
    const visualOn = this.opts.visualFeedback && fbTimeout > 0 && MEASURED.has(kind);
    let pre = null;
    let visualAmbient = false;
    if (visualOn) {
      try {
        const a = await this.captureFrame();
        await sleep(40);
        pre = await this.captureFrame();
        const d = visualDiffFraction(a, pre, VISUAL_LEVEL);
        visualAmbient = d !== null && d >= this.visualThreshold(pre);
      } catch {
        pre = null;
      }
    }
    const scrollBefore = ['scroll', 'swipe', 'drag'].includes(kind) ? await this.scrollPos() : null;
    const dispatch = epochNow();
    step.t_start_ms = this.rel(dispatch);
    const fb = { visual: null, done: false };
    const probe = this.probeFrames({
      dispatch,
      stepIndex: step.step_index,
      flashMs: this.opts.flashSampleMs,
      visual: visualOn && pre && !visualAmbient ? { pre, deadline: dispatch + fbTimeout } : null,
      fb,
    });
    let inputErr = null;
    try {
      const r = await this.dispatchInput(action, resolved);
      if (r && typeof r === 'object') {
        step.input = r.input;
        if (!step.point) step.point = { x: round1(r.start.x), y: round1(r.start.y) };
        step.end_point = { x: round1(r.end.x), y: round1(r.end.y) };
      } else {
        step.input = r;
      }
    } catch (err) {
      inputErr = err;
    }
    const inputEnd = epochNow();
    if (fbTimeout > 0 && !inputErr) await this.waitForFeedback(dispatch, dispatch + fbTimeout);
    fb.done = true;
    await probe;
    if (this.navEvents.some((t) => t >= dispatch)) {
      await this.page.waitForLoadState('load', { timeout: 10000 }).catch(() => {});
    }
    const early = [this.navEvents.find((t) => t >= dispatch)].filter((t) => t != null);
    const domEarly = await this.firstMutation(dispatch, epochNow());
    if (domEarly !== null) early.push(domEarly);
    if (!early.length && fb.visual != null) early.push(fb.visual);
    const anchor = Math.max(inputEnd, early.length ? Math.min(...early) : inputEnd);
    await sleep(anchor + (action.settle_ms ?? this.opts.settleMs) - epochNow());
    const end = epochNow();
    step.t_end_ms = Math.max(step.t_start_ms, this.rel(end));

    // Feedback latency (spec): first DOM mutation or main-frame navigation after
    // dispatch, within 3000 ms and before the after-snapshot. Only when neither
    // happened does a visual change of the viewport count (canvas/CSS-only
    // feedback); focus/caret or tap-highlight changes would otherwise mask
    // missing application feedback on DOM pages.
    const windowEnd = Math.min(dispatch + FEEDBACK_WINDOW_MS, end);
    const cands = [];
    const dom = await this.firstMutation(dispatch, windowEnd);
    if (dom !== null) cands.push({ t: dom, src: 'dom_mutation' });
    const nav = this.navEvents.find((t) => t >= dispatch && t <= windowEnd);
    if (nav !== undefined) cands.push({ t: nav, src: 'navigation' });
    cands.sort((a, b) => a.t - b.t);
    let first = cands[0] || null;
    if (!first && fb.visual != null && fb.visual <= windowEnd) first = { t: fb.visual, src: 'visual_change' };
    step.feedback_latency_ms = first ? round1(Math.max(0, first.t - dispatch)) : null;
    step.feedback_source = first ? first.src : null;
    step.feedback_dom_ms = dom !== null ? round1(Math.max(0, dom - dispatch)) : null;
    step.feedback_visual_ms = fb.visual != null ? round1(Math.max(0, fb.visual - dispatch)) : null;
    step.feedback_window_ms = round1(windowEnd - dispatch);
    step.feedback_ambient_mutations = await this.countMutations(dispatch - 500, dispatch);
    step.feedback_visual_ambient = visualOn ? visualAmbient : null;
    if (scrollBefore) {
      const after = await this.scrollPos();
      if (after) step.scroll_delta = { x: round1(after.x - scrollBefore.x), y: round1(after.y - scrollBefore.y) };
    }
    if (inputErr) throw inputErr;
  }

  /** Execute one validated action; always ends with an after-snapshot. */
  async act(action) {
    if (this.crashed) throw new DriverFailure('page crashed');
    const stepIndex = this.steps.length + 1;
    const step = {
      step_index: stepIndex,
      action,
      target_element_id: null,
      point: null,
      before: this.lastSnapshotId,
      after: null,
      t_start_ms: null,
      t_end_ms: null,
      feedback_latency_ms: null,
      result: 'ok',
      error: null,
      input: null,
    };
    let resolved = null;
    try {
      const kind = action.action;
      if (kind === 'wait') {
        const t0 = epochNow();
        step.t_start_ms = this.rel(t0);
        if (this.opts.flashSampleMs > 0) {
          // Flash sampling covers the whole wait: effects often play while the user waits.
          await this.probeFrames({ dispatch: t0, stepIndex, flashMs: action.ms, visual: null, fb: { done: true } });
        }
        await sleep(t0 + action.ms - epochNow());
        step.t_end_ms = Math.max(step.t_start_ms, this.rel(epochNow()));
      } else if (kind === 'snapshot') {
        const t0 = epochNow();
        step.t_start_ms = this.rel(t0);
        if (this.opts.flashSampleMs > 0) {
          await this.probeFrames({ dispatch: t0, stepIndex, flashMs: this.opts.flashSampleMs, visual: null, fb: { done: true } });
        }
        step.t_end_ms = Math.max(step.t_start_ms, this.rel(epochNow()));
      } else {
        if (action.target !== undefined) {
          const timeout = action.timeout_ms ?? DEFAULT_TARGET_TIMEOUT_MS;
          resolved = await this.resolveTarget(action.target, action.offset, timeout);
          const allowScroll = action.auto_scroll ?? this.opts.autoScroll;
          if (resolved.kind !== 'missing' && !this.inViewport(resolved.point) && allowScroll) {
            if (resolved.handle) {
              await resolved.handle.scrollIntoViewIfNeeded({ timeout: 5000 }).catch(() => {});
              await resolved.handle.dispose().catch(() => {});
              step.auto_scrolled = true;
            } else if (resolved.kind === 'hotspot' && resolved.origin === 'page') {
              // Live page hotspots follow the document; scenario boxes are fixed viewport coordinates.
              const p = resolved.point;
              await this.page.evaluate(({ dx, dy }) => window.scrollBy(dx, dy), {
                dx: p.x < 0 || p.x >= this.vw ? p.x - this.vw / 2 : 0,
                dy: p.y < 0 || p.y >= this.vh ? p.y - this.vh / 2 : 0,
              }).catch(() => {});
              step.auto_scrolled = true;
            }
            if (step.auto_scrolled) {
              await sleep(150);
              resolved = await this.resolveTarget(action.target, action.offset, timeout);
            }
          }
          const stale = resolved.kind === 'selector' && (resolved.elementId == null || (!resolved.exact && resolved.interactive));
          if (resolved.kind !== 'missing' && (resolved.waited || step.auto_scrolled || stale)) {
            // The target appeared or moved after the last snapshot: capture what the
            // user saw right before acting, and re-read ids from that snapshot.
            const why = step.auto_scrolled ? 'pre_action_auto_scroll' : 'pre_action_target_appeared';
            const pre = await this.snapshot(stepIndex, [why]);
            step.before = pre.id;
            if (resolved.handle) await resolved.handle.dispose().catch(() => {});
            resolved = await this.resolveTarget(action.target, action.offset, 1000);
          }
          if (resolved.kind === 'missing') {
            step.result = 'no_target';
            step.error = resolved.error;
          } else if (!this.inViewport(resolved.point)) {
            step.result = 'no_target';
            step.error = `target point (${resolved.point.x}, ${resolved.point.y}) is outside the ${this.vw}x${this.vh} viewport${allowScroll ? '' : ' (auto_scroll disabled)'}`;
            step.point = resolved.point;
            step.target_element_id = resolved.elementId || null;
          } else {
            step.point = resolved.point;
            step.target_element_id = resolved.elementId || null;
            const hit = await this.page.evaluate(idAtPoint, { key: STATE_KEY, x: resolved.point.x, y: resolved.point.y }).catch(() => ({ id: null }));
            step.hit_element_id = hit.id;
            if (resolved.handle) step.target_hit = await resolved.handle.evaluate(hitTest, resolved.point).catch(() => null);
            else step.target_hit = resolved.elementId ? hit.id === resolved.elementId : null;
          }
        }
        if (step.result === 'ok') await this.performInput(action, resolved, step);
      }
    } catch (err) {
      if (err instanceof DriverFailure) throw err;
      step.result = 'error';
      step.error = firstLine(err.message);
    } finally {
      if (resolved && resolved.handle) await resolved.handle.dispose().catch(() => {});
    }
    // focus_point: last pointer point; keyboard actions use the focused element.
    if (step.point && step.result === 'ok') {
      this.focusPoint = step.end_point ? { x: round1(step.end_point.x), y: round1(step.end_point.y) } : { ...step.point };
    } else if (['press', 'gamepad', 'type'].includes(action.action) && step.result === 'ok' && this.lastActive) {
      this.focusPoint = { ...this.lastActive };
    }
    let snap = null;
    try {
      snap = await this.snapshot(stepIndex, []);
      step.after = snap.id;
      if (!step.point && ['press', 'gamepad', 'type'].includes(action.action) && this.lastActive && step.result === 'ok') {
        // Keyboard focus moved during the step: update for the next snapshot.
        this.focusPoint = { ...this.lastActive };
      }
    } catch (err) {
      step.result = 'error';
      step.error = step.error || firstLine(err.message);
      this.steps.push(step);
      throw err;
    }
    step.url_after = this.page.url();
    this.steps.push(step);
    return { step, snap };
  }

  // ------------------------------------------------------------------ notes / finish

  addNote(note) {
    const entry = {
      step_index: note.step_index ?? this.steps.length,
      intent: note.intent ?? '',
      expected: note.expected ?? '',
      observed: note.observed ?? '',
      confusion: note.confusion,
      snapshot_id: this.lastSnapshotId,
      t_ms: this.rel(epochNow()),
      basis: 'judgment',
    };
    // The agent's own severity and corroboration are claims, not evidence: stored
    // under *_claimed and never used for severity or tier (corroboration is computed
    // across runs by model family and input channel).
    if (note.severity) entry.severity_claimed = note.severity;
    if (note.failure_class) entry.failure_class = note.failure_class;
    if (note.evidence) entry.evidence = note.evidence;
    if (note.corroborated !== undefined) entry.corroborated_claimed = note.corroborated;
    Object.assign(entry, this.resolveAnchor(note.anchor ?? 'acted', entry.step_index));
    this.personaNotes.push(entry);
    return this.personaNotes.length - 1;
  }

  /** Resolve a note anchor to element ids and selectors in a recorded snapshot. */
  resolveAnchor(anchor, stepIndex) {
    const out = { anchor, anchor_snapshot_id: null, anchor_element_ids: [], anchor_selectors: [], screen_key: null };
    const screenKey = (snapId) => {
      const s = this.snapElements.get(snapId);
      if (!s) return null;
      let pathname = '';
      try {
        pathname = new URL(s.url).pathname;
      } catch { /* keep empty */ }
      const heads = s.elements.filter((e) => e.role === 'heading' && e.visible && e.in_viewport).map((e) => e.text).slice(0, 4).join('|');
      const modal = s.elements.some((e) => e.inert_by_modal) ? '+modal' : '';
      return `${pathname}#${sha256(Buffer.from(heads)).slice(0, 8)}${modal}`;
    };
    if (anchor === 'acted') {
      const step = [...this.steps].reverse().find((st) => st.step_index <= stepIndex && st.target_element_id);
      if (step) {
        const s = this.snapElements.get(step.before);
        const el = s && s.elements.find((e) => e.id === step.target_element_id);
        if (el) {
          out.anchor_snapshot_id = step.before;
          out.anchor_element_ids = [el.id];
          out.anchor_selectors = el.selector ? [el.selector] : [];
        }
        out.screen_key = screenKey(step.after || step.before);
      }
      return out;
    }
    const snapId = this.lastSnapshotId;
    const s = this.snapElements.get(snapId);
    out.anchor_snapshot_id = snapId;
    out.screen_key = screenKey(snapId);
    if (!s) return out;
    const vis = s.elements.filter((e) => e.visible && e.box && e.box.w > 0 && e.box.h > 0);
    let pick = null;
    if (anchor.point) {
      const { x, y } = anchor.point;
      const inside = vis.filter((e) => x >= e.box.x && x <= e.box.x + e.box.w && y >= e.box.y && y <= e.box.y + e.box.h);
      pick = inside.sort((a, b) => a.box.w * a.box.h - b.box.w * b.box.h)[0] || null;
    } else if (anchor.box) {
      const b = anchor.box;
      const iou = (e) => {
        const ix = Math.max(0, Math.min(b.x + b.w, e.box.x + e.box.w) - Math.max(b.x, e.box.x));
        const iy = Math.max(0, Math.min(b.y + b.h, e.box.y + e.box.h) - Math.max(b.y, e.box.y));
        const inter = ix * iy;
        return inter / (b.w * b.h + e.box.w * e.box.h - inter);
      };
      const best = vis.map((e) => [iou(e), e]).sort((p, q) => q[0] - p[0])[0];
      pick = best && best[0] >= 0.3 ? best[1] : null;
    }
    if (pick) {
      out.anchor_element_ids = [pick.id];
      out.anchor_selectors = pick.selector ? [pick.selector] : [];
    }
    return out;
  }

  async evaluateSuccess() {
    const sc = this.scenario.success;
    const unevaluable = this.scenario.success_unevaluable;
    if (!sc && !unevaluable.length) return { success: null, detail: null };
    const results = [];
    const check = async (kind, value, fn) => {
      try {
        results.push({ kind, value, passed: !!(await fn()) });
      } catch (err) {
        results.push({ kind, value, passed: false, error: firstLine(err.message) });
      }
    };
    if (this.page && !this.crashed && !this.page.isClosed()) {
      for (const sel of sc?.selector_visible || []) {
        await check('selector_visible', sel, async () => (await this.page.locator(sel).filter({ visible: true }).count()) > 0);
      }
      for (const s of sc?.url_contains || []) await check('url_contains', s, async () => this.page.url().includes(s));
      if (sc?.text_present) {
        const body = await this.page.evaluate(() => (document.body ? document.body.innerText : '')).catch(() => '');
        for (const s of sc.text_present) await check('text_present', s, async () => body.includes(s));
      }
    }
    const allPassed = results.length > 0 && results.every((r) => r.passed);
    const anyFailed = results.some((r) => !r.passed) || (this.crashed && results.length === 0);
    let success;
    if (anyFailed) success = false;
    else if (unevaluable.length || !results.length) success = null;
    else success = allPassed;
    return { success, detail: { criteria: results, unevaluable } };
  }

  async finish({ personaSuccess, reason } = {}) {
    if (this.finished) return this.finished;
    const finishing = (async () => {
      if (reason) this.block(reason);
      for (const t of this.twPollers) clearInterval(t);
      const end = epochNow();
      let success = null;
      let detail = null;
      let basis = null;
      try {
        ({ success, detail } = await this.evaluateSuccess());
        if (detail) basis = 'measured';
      } catch (err) {
        this.warnings.push(`success evaluation failed: ${firstLine(err.message)}`);
      }
      // Focus walks run after the task (so they never delay step 1) and only when the
      // run ended normally: at the end state, then the initial screen in a fresh context.
      if (this.focusWalkEnabled() && !reason && !this.crashed && this.page && !this.blockReasons.length) {
        await this.boundedWalk(() => this.focusWalk(this.page, 'end', this.lastSnapshotId), 'end');
        await this.boundedWalk(() => this.focusWalkFresh(), 'load');
      }
      if (this.reflowEnabled() && !reason && !this.crashed && !this.blockReasons.length) await this.reflowPass();
      if (success === null && !detail && typeof personaSuccess === 'boolean') {
        success = personaSuccess;
        basis = 'judgment';
      }
      let finalUrl = null;
      let title = null;
      try {
        finalUrl = this.page.url();
        title = await this.page.title();
      } catch { /* page gone */ }
      let status = 'completed';
      if (this.blockReasons.length) status = 'blocked';
      else if (this.mode === 'scripted' && this.steps.some((s) => s.result !== 'ok')) status = 'failed';
      const flashCov = this.flashCoverage();
      const run = {
        schema_version: 'ergo-run.v1',
        run_id: this.runId,
        scenario_id: this.scenario.scenario_id,
        profile_id: this.profileId,
        driver: {
          name: 'playwright-web',
          version: this.pwInfo.version,
          browser: 'chromium',
          browser_version: this.browserVersion || null,
          playwright_path: this.pwInfo.path,
          emulation: this.dev ? { ...this.dev.emulation, locale: this.opts.locale, timezone: this.opts.timezoneId } : null,
          network_policy: {
            allowed_origins: [...this.allowedOrigins],
            blocked_requests: this.blockedCount,
            blocked_sample: this.blocked,
            blocked_console_messages_suppressed: this.blockedConsole,
          },
          clock: { page_offset_ms: round1(this.clockOffset), calibration_rtt_ms: round1(this.clockRtt) },
          feedback: {
            window_ms: FEEDBACK_WINDOW_MS,
            wait_ms: this.opts.feedbackTimeoutMs,
            sources: ['dom_mutation', 'navigation', ...(this.opts.visualFeedback ? ['visual_change'] : [])],
            visual_frame_width_css: FRAME_WIDTH,
            visual_pixel_level: VISUAL_LEVEL,
          },
          element_cap: ELEMENT_CAP,
        },
        device: this.dev ? this.dev.snapshotDevice : null,
        mode: this.mode,
        agent: this.opts.agentInfo ? { ...this.opts.agentInfo, ...(this.opts.agent ? { description: this.opts.agent } : {}) }
          : this.opts.agent ? { description: this.opts.agent } : (this.mode === 'interactive' ? { description: 'unrecorded' } : null),
        started_at: this.startedAt,
        ended_at: isoNow(),
        status,
        success,
        success_basis: basis,
        success_detail: detail,
        ...(this.mode === 'interactive' ? { persona_claimed_success: typeof personaSuccess === 'boolean' ? personaSuccess : null } : {}),
        surface: { kind: this.scenario.surface_kind === 'game' ? 'game' : 'web', url: this.scenario.url, final_url: finalUrl, title, http_status: this.httpStatus },
        steps: this.steps,
        timing_windows: this.timingWindowsOut(end),
        flash_samples: this.flashSamples,
        focus_walks: this.focusWalks,
        reflow: this.reflow,
        flash_sampling: this.opts.flashSampleMs > 0 ? {
          enabled: true,
          per_step_ms: this.opts.flashSampleMs,
          // After page load, after each input and during snapshot steps for per_step_ms;
          // during wait steps for the whole wait.
          during: ['load', 'input', 'snapshot', 'wait'],
          method: `CDP Page.captureScreenshot, viewport downscaled to ~${FRAME_WIDTH} CSS px wide, optimizeForSpeed, random 0-${FLASH_JITTER_MS} ms pause between captures`,
          jitter_ms: [0, FLASH_JITTER_MS],
          frames: this.flashSamples.length,
          bursts: flashCov.bursts,
          sampled_ms: flashCov.sampled_ms,
          mean_fps: flashCov.mean_fps,
          max_gap_ms: flashCov.max_gap_ms,
          run_ms: this.rel(end),
          mean_interval_ms: flashCov.mean_interval_ms,
          max_interval_ms: flashCov.max_gap_ms,
          truncated: this.flashTruncated,
          caps: { samples: MAX_FLASH_SAMPLES, bytes: MAX_FLASH_BYTES },
          block_grid: this.flashGridOut(),
          changed_fraction: 'share of pixels with |delta relative luminance| >= 0.10 vs the previous frame of the same burst (0 for the first frame)',
          flash_fraction: 'changed pixels whose darker state is < 0.80 (WCAG 2.3.1 general-flash pair condition)',
        } : { enabled: false },
        persona_notes: this.personaNotes,
        snapshots: this.snapshots,
        console_errors: this.consoleAll,
        blocked_reasons: this.blockReasons,
        warnings: this.warnings,
      };
      if (!run.device) run.device = this.deviceRequest.fallbackDevice;
      writeJsonAtomic(path.join(this.runDir, 'run.json'), run);
      try {
        if (this.browser) await this.browser.close();
      } catch { /* already gone */ }
      let exitCode = 3;
      if (status === 'blocked') exitCode = 4;
      else if (status === 'completed' && success === true) exitCode = 0;
      return { status, success, runPath: path.join(this.runDir, 'run.json'), exitCode, run };
    })();
    this.finished = finishing;
    return finishing;
  }
}

export function ensureRunDir(dir) {
  if (fs.existsSync(dir)) {
    const st = fs.lstatSync(dir);
    if (!st.isDirectory() || st.isSymbolicLink()) return `run directory ${dir} exists and is not a plain directory`;
    if (fs.readdirSync(dir).length) return `run directory ${dir} already exists and is not empty (evidence is never overwritten)`;
    return null;
  }
  fs.mkdirSync(dir, { recursive: true });
  return null;
}
