#!/usr/bin/env node
// Read-only render of one public URL (rung R3 of the public-page reader,
// references/research/public-page-access.md section 10). Writes one
// ux-page-read.v1 document (schemas/ux-page-read.v1.schema.json).
//
//   node drivers/web/read_page.mjs URL [--out FILE] [--device ID] [--max-wait-ms 15000]
//                                  [--scrolls 8] [--timeout-s 30] [--allow-local]
//
// What it does: a fresh anonymous browser context (no stored cookies or sign-in),
// the browser's own user agent (no stealth, no disguise), images, media and fonts
// blocked, then scrolling only. It never clicks, types or presses keys. A check
// that clears by itself ("checking your browser") is waited for up to
// --max-wait-ms (at most 15 s). An interactive human check is reported and never
// solved; a password field is reported (the reader's verdict decides whether the
// page is gated).
//
// Exit codes (the reader's scheme): 0 read (document written); 3 stopped at an
// interactive human check (document written, challenge.interactive true); 2 usage
// or refused address; 4 unread (navigation failed, no document, browser missing).

import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { CATALOG, hasTouch, isMobile } from './devices.mjs';
import { loadPlaywright } from './playwright_loader.mjs';
import { isoNow, sleep, writeJsonAtomic } from './util.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const MARKERS = path.join(HERE, '..', '..', 'uxresearch', 'data', 'markers.json');
const DRIVER_VERSION = 'read_page/1';
const TEXT_MAX = 409600;
const JSON_LD_MAX_BLOCKS = 10;
const JSON_LD_MAX_CHARS = 1_000_000;
const WAIT_CAP_MS = 15000;
const SCROLL_CAP = 50;
const SCROLL_PAUSE_MS = 400;
const POLL_MS = 500;
const BLOCKED = ['image', 'media', 'font'];

const USAGE = `usage: node drivers/web/read_page.mjs URL [--out FILE] [--device ID] [--max-wait-ms N<=15000]
                                     [--scrolls N<=50] [--timeout-s N] [--allow-local]
Writes one ux-page-read.v1 document to FILE (or stdout). Exit 0 read, 3 stopped at an
interactive human check, 2 usage or refused address, 4 unread.`;

class Usage extends Error {}

function parseArgs(argv) {
  const out = { url: null, out: null, device: 'desktop-1920', maxWait: WAIT_CAP_MS, scrolls: 8, timeoutS: 30, allowLocal: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => {
      if (i + 1 >= argv.length) throw new Usage(`${a} needs a value`);
      return argv[++i];
    };
    const int = (name, lo, hi) => {
      const v = Number(val());
      if (!Number.isInteger(v) || v < lo || v > hi) throw new Usage(`${name} must be an integer within ${lo}..${hi}`);
      return v;
    };
    if (a === '--out') out.out = val();
    else if (a === '--device') out.device = val();
    else if (a === '--max-wait-ms') out.maxWait = int(a, 0, WAIT_CAP_MS);
    else if (a === '--scrolls') out.scrolls = int(a, 0, SCROLL_CAP);
    else if (a === '--timeout-s') out.timeoutS = int(a, 5, 120);
    else if (a === '--allow-local') out.allowLocal = true;
    else if (a === '--help' || a === '-h') throw new Usage('');
    else if (a.startsWith('--')) throw new Usage(`unknown option ${a}`);
    else if (!out.url) out.url = a;
    else throw new Usage(`unexpected argument ${a}`);
  }
  if (!out.url) throw new Usage('URL is required');
  if (!CATALOG.has(out.device)) throw new Usage(`unknown device ${out.device}`);
  return out;
}

/** Loopback, private, link-local and unspecified addresses are refused unless --allow-local. */
function isLocalHost(host) {
  const h = host.replace(/^\[|\]$/g, '').toLowerCase();
  if (h === 'localhost' || h.endsWith('.localhost') || h.endsWith('.local') || h.endsWith('.internal')) return true;
  if (net.isIPv4(h)) {
    const [a, b] = h.split('.').map(Number);
    return a === 10 || a === 127 || a === 0 || (a === 169 && b === 254) || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168)
      || (a === 100 && b >= 64 && b <= 127);
  }
  if (net.isIPv6(h)) return h === '::1' || h === '::' || h.startsWith('fc') || h.startsWith('fd') || h.startsWith('fe80') || h.startsWith('::ffff:');
  return false;
}

function checkUrl(raw, allowLocal) {
  let u;
  try {
    u = new URL(raw);
  } catch {
    throw new Usage(`not a URL: ${raw}`);
  }
  if (u.protocol !== 'http:' && u.protocol !== 'https:') throw new Usage(`only http and https URLs are read (${u.protocol})`);
  if (u.username || u.password) throw new Usage('URLs with credentials are refused');
  if (!allowLocal && isLocalHost(u.hostname)) throw new Usage(`refused: ${u.hostname} is a local or private address`);
  return u.href;
}

function loadMarkers() {
  try {
    const m = JSON.parse(fs.readFileSync(MARKERS, 'utf8'));
    const pick = (k) => ({
      src: (m[k] && m[k].src) || [],
      idents: (m[k] && m[k].idents) || [],
      inputs: (m[k] && m[k].inputs) || [],
      words: Object.values((m[k] && m[k].words) || {}).flat(),
    });
    return { human: pick('human_check'), js: pick('js_check') };
  } catch {
    // The skill folder ships the markers; without them nothing is recognised as a check.
    return { human: { src: [], idents: [], inputs: [], words: [] }, js: { src: [], idents: [], inputs: [], words: [] } };
  }
}

/** In-page: which challenge markers are present (scripts, frames, ids, classes, inputs, visible text). */
function findMarkers(markers) {
  const lower = (s) => String(s || '').toLowerCase();
  const text = lower(document.body ? document.body.innerText : '').slice(0, 20000);
  const srcs = [...document.querySelectorAll('script[src], iframe[src]')].map((n) => lower(n.getAttribute('src')));
  const idents = [];
  for (const n of document.querySelectorAll('[id], [class]')) {
    if (n.id) idents.push(lower(n.id));
    for (const c of n.classList || []) idents.push(lower(c));
    if (idents.length > 5000) break;
  }
  const inputs = [...document.querySelectorAll('input[name], textarea[name]')].map((n) => lower(n.getAttribute('name')));
  const hits = (set) => {
    const out = [];
    for (const s of set.src) if (srcs.some((x) => x.includes(lower(s)))) out.push(`src:${s}`);
    for (const s of set.idents) if (idents.includes(lower(s))) out.push(`ident:${s}`);
    for (const s of set.inputs) if (inputs.includes(lower(s))) out.push(`input:${s}`);
    for (const s of set.words) if (text.includes(lower(s))) out.push(`word:${s}`);
    return out;
  };
  return { human: hits(markers.human), js: hits(markers.js) };
}

/** In-page: the capture fields (no form values are read). */
function capture(limits) {
  const pick = (sel) => {
    const n = document.querySelector(sel);
    return n ? (n.getAttribute('content') || '').trim() : null;
  };
  const og = {};
  for (const n of document.querySelectorAll('meta[property^="og:"]')) {
    const k = n.getAttribute('property');
    if (Object.keys(og).length < 20 && !(k in og)) og[k] = (n.getAttribute('content') || '').slice(0, 2000);
  }
  const blocks = [];
  let total = 0;
  for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
    if (blocks.length >= limits.blocks) break;
    const raw = s.textContent || '';
    if (total + raw.length > limits.chars) break;
    total += raw.length;
    try {
      blocks.push(JSON.parse(raw));
    } catch {
      blocks.push(raw);
    }
  }
  const visible = (n) => {
    const r = n.getBoundingClientRect();
    const cs = getComputedStyle(n);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none';
  };
  return {
    title: (document.title || '').slice(0, 2000),
    lang: (document.documentElement.getAttribute('lang') || '').slice(0, 35),
    text: document.body ? document.body.innerText : '',
    json_ld: blocks,
    description: pick('meta[name="description" i]'),
    og,
    robots: pick('meta[name="robots" i]'),
    tdm: pick('meta[name="tdm-reservation" i]'),
    login_form: [...document.querySelectorAll('input[type="password" i]')].some(visible),
  };
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
    args.url = checkUrl(args.url, args.allowLocal);
  } catch (err) {
    if (!(err instanceof Usage)) throw err;
    if (err.message) process.stderr.write(`read_page: ${err.message}\n`);
    process.stderr.write(`${USAGE}\n`);
    return 2;
  }
  const report = (exit, extra) => process.stdout.write(`${JSON.stringify({ event: 'read_page', exit, url: args.url, ...extra })}\n`);
  let pw;
  try {
    ({ pw } = loadPlaywright());
  } catch (err) {
    report(4, { reason: 'no_browser', detail: String(err.message).slice(0, 300) });
    return 4;
  }
  const dev = CATALOG.get(args.device);
  const startedAt = isoNow();
  const markers = loadMarkers();
  let browser = null;
  try {
    browser = await pw.chromium.launch({ headless: true, timeout: 60000 });
    // Viewport only: the browser keeps its own user agent (no disguise).
    const context = await browser.newContext({
      viewport: { width: dev.viewport_css[0], height: dev.viewport_css[1] },
      deviceScaleFactor: dev.dpr,
      hasTouch: hasTouch(dev),
      isMobile: isMobile(dev),
      serviceWorkers: 'block',
      acceptDownloads: false,
      javaScriptEnabled: true,
    });
    await context.route('**/*', (route) => (BLOCKED.includes(route.request().resourceType()) ? route.abort() : route.continue()));
    const page = await context.newPage();
    page.on('dialog', (d) => d.dismiss().catch(() => {}));
    let response;
    try {
      response = await page.goto(args.url, { waitUntil: 'domcontentloaded', timeout: args.timeoutS * 1000 });
    } catch (err) {
      report(4, { reason: 'navigation_failed', detail: String(err.message).split('\n')[0].slice(0, 300) });
      return 4;
    }
    if (!response) {
      report(4, { reason: 'no_document' });
      return 4;
    }
    await page.waitForLoadState('load', { timeout: 5000 }).catch(() => {});
    const redirects = [];
    for (let req = response.request().redirectedFrom(); req && redirects.length < 20; req = req.redirectedFrom()) {
      const r = await req.response().catch(() => null);
      redirects.unshift({ status: r ? r.status() : 0, url: req.url().slice(0, 8192) });
    }
    // A check that clears by itself: wait while its markers stay and no human check shows.
    const t0 = Date.now();
    let found = await page.evaluate(findMarkers, markers).catch(() => ({ human: [], js: [] }));
    const checking = found.js.length > 0 && !found.human.length;
    while (!found.human.length && found.js.length && Date.now() - t0 < args.maxWait) {
      await sleep(POLL_MS);
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 }).catch(() => {});
      found = await page.evaluate(findMarkers, markers).catch(() => ({ human: [], js: [] }));
    }
    const waited = checking ? Math.min(WAIT_CAP_MS, Date.now() - t0) : 0;
    const interactive = found.human.length > 0;
    let scrolls = 0;
    if (!interactive) {
      for (; scrolls < args.scrolls; scrolls++) {
        const atEnd = await page.evaluate(() => {
          const before = window.scrollY;
          window.scrollBy(0, Math.max(200, Math.floor(window.innerHeight * 0.9)));
          return window.scrollY === before || window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
        }).catch(() => true);
        await sleep(SCROLL_PAUSE_MS);
        if (atEnd) {
          scrolls += 1;
          break;
        }
      }
    }
    const cap = await page.evaluate(capture, { blocks: JSON_LD_MAX_BLOCKS, chars: JSON_LD_MAX_CHARS });
    const headers = await response.allHeaders().catch(() => ({}));
    const tdm = cap.tdm ?? (headers['tdm-reservation'] !== undefined ? String(headers['tdm-reservation']) : null);
    const meta = { og: cap.og, tdm_reservation: tdm };
    if (cap.description) meta.description = cap.description.slice(0, 2000);
    if (cap.robots) meta.robots = cap.robots;
    const doc = {
      schema_version: 'ux-page-read.v1',
      url: args.url,
      final_url: page.url().slice(0, 8192),
      status: response.status(),
      redirects,
      title: cap.title,
      lang: cap.lang,
      text: cap.text.slice(0, TEXT_MAX),
      json_ld: cap.json_ld,
      meta,
      challenge: { interactive, markers: [...found.human, ...found.js].slice(0, 20).map((m) => m.slice(0, 100)) },
      login_form: cap.login_form,
      context: 'anonymous',
      waited_ms: waited,
      scrolls,
      blocked_types: BLOCKED,
      device_id: args.device,
      driver_version: DRIVER_VERSION,
      started_at: startedAt,
      finished_at: isoNow(),
    };
    if (args.out) writeJsonAtomic(args.out, doc);
    else process.stdout.write(`${JSON.stringify(doc)}\n`);
    const exit = interactive ? 3 : 0;
    if (args.out) report(exit, { out: args.out, status: doc.status, chars: doc.text.length, challenge: interactive, login_form: doc.login_form });
    return exit;
  } catch (err) {
    report(4, { reason: 'browser_error', detail: String(err.message).split('\n')[0].slice(0, 300) });
    return 4;
  } finally {
    if (browser) await browser.close().catch(() => {});
  }
}

main().then((code) => process.exit(code), (err) => {
  process.stderr.write(`read_page: unexpected error: ${err && err.stack ? err.stack : err}\n`);
  process.exit(4);
});
