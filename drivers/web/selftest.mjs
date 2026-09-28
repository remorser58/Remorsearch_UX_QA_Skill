#!/usr/bin/env node
// Self-test for drivers/web/ergo_drive.mjs.
//
// Serves fixtures/selftest.html from a local node:http server (127.0.0.1,
// ephemeral port), runs a scripted scenario on galaxy-s24 and desktop-1920,
// drives `serve` over HTTP, checks usage/blocked exits, and asserts the outputs
// against docs/ergonomic-swarm-spec.md (and ergoqa.snapshot.load_run_dir when
// Python and the ergoqa package are available). Prints PASS/FAIL/SKIP lines;
// exits 1 on any FAIL.
//
//   node drivers/web/selftest.mjs [--keep]

import { spawn, spawnSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { CATALOG } from './devices.mjs';
import { decodePng } from './png.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(HERE, '..', '..');
const DRIVER = path.join(HERE, 'ergo_drive.mjs');
const FIXTURE = path.join(HERE, 'fixtures', 'selftest.html');
const KNOWN_ROLES = new Set(['primary', 'destructive', 'critical_message', 'error_message', 'status', 'navigation', 'ad_like', 'hud', 'game_control', 'timed']);
const HEX = /^#[0-9a-f]{6}$/;
const ISO = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;

let failures = 0;
let passes = 0;
function check(name, cond, detail) {
  if (cond) {
    passes++;
    console.log(`PASS ${name}`);
  } else {
    failures++;
    console.log(`FAIL ${name}${detail !== undefined ? ` -- ${typeof detail === 'string' ? detail : JSON.stringify(detail)}` : ''}`);
  }
  return !!cond;
}
function skip(name, why) {
  console.log(`SKIP ${name} -- ${why}`);
}

function startFixtureServer() {
  const html = fs.readFileSync(FIXTURE);
  const server = http.createServer((req, res) => {
    const { pathname } = new URL(req.url, 'http://127.0.0.1');
    if (req.method === 'GET' && pathname === '/selftest.html') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(html);
      return;
    }
    if (req.method === 'GET' && pathname === '/layers.html') {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
      res.end(fs.readFileSync(path.join(path.dirname(FIXTURE), 'layers.html')));
      return;
    }
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('not found');
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

function runDriver(args, { timeoutMs = 120000, onLine } = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [DRIVER, ...args], { stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    const lines = [];
    let buf = '';
    child.stdout.on('data', (d) => {
      out += d;
      buf += d;
      let i;
      while ((i = buf.indexOf('\n')) >= 0) {
        const line = buf.slice(0, i);
        buf = buf.slice(i + 1);
        try {
          const obj = JSON.parse(line);
          lines.push(obj);
          if (onLine) onLine(obj);
        } catch { /* not JSON */ }
      }
    });
    child.stderr.on('data', (d) => { err += d; });
    const timer = setTimeout(() => child.kill('SIGKILL'), timeoutMs);
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code, out, err, lines });
    });
  });
}

function request(port, method, pathname, { body, headers = {} } = {}) {
  return new Promise((resolve, reject) => {
    const data = body === undefined ? null : (typeof body === 'string' ? body : JSON.stringify(body));
    const req = http.request({
      host: '127.0.0.1',
      port,
      method,
      path: pathname,
      headers: {
        ...(data !== null ? { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } : {}),
        ...headers,
      },
    }, (res) => {
      let text = '';
      res.on('data', (d) => { text += d; });
      res.on('end', () => {
        let json = null;
        try {
          json = JSON.parse(text);
        } catch { /* keep null */ }
        resolve({ status: res.statusCode, json, text });
      });
    });
    req.on('error', reject);
    if (data !== null) req.write(data);
    req.end();
  });
}

function scenario() {
  return {
    schema_version: 'ergo-scenario.v1',
    scenario_id: 'SC-driver-selftest-01',
    surface: { kind: 'web', url: '{BASE}/selftest.html' },
    task_goal_ko: '카드 번호를 입력하고 결제를 완료한다',
    device_ids: ['galaxy-s24', 'desktop-1920'],
    targets: {
      primary: ['#pay'],
      destructive: ['#delete-all'],
      critical_message: ['#error'],
      game_control: ['hotspot:hs-static'],
      timed: [],
    },
    steps: [
      { action: 'wait', ms: 200 },
      { action: 'tap', target: '#pay' },
      { action: 'type', target: '#card', text: '1234 5678 9012 3456' },
      { action: 'tap', target: 'hotspot:hs-jump' },
      { action: 'tap', target: '#plain-text' },
      { action: 'tap', target: '#start-qte' },
      { action: 'wait', ms: 1400 },
      { action: 'tap', target: '#below' },
      { action: 'tap', target: 'text=결제하기' },
      { action: 'tap', target: '#flash-btn' },
    ],
    timing_windows: [{ id: 'qte-1', selector: '#qte', measure: 'visible_duration', kind: 'qte' }],
    success: { selector_visible: '#done', text_present: '결제 완료', url_contains: 'selftest' },
    hotspots: [{ id: 'hs-static', name: '정적 핫스팟', box: { x: 10, y: 10, w: 40, h: 40 }, roles: ['game_control'] }],
  };
}

function profile(id, deviceId) {
  return {
    schema_version: 'ergo-profile.v1',
    profile_id: id,
    origin: 'manual',
    label_ko: '드라이버 자체 시험',
    attributes: {
      age_band: '30s', handedness: 'right', grip: deviceId.startsWith('desktop') ? 'mouse_right' : 'one_hand_right',
      thumb_length_mm: 62, hand_percentile: 50, device_id: deviceId, orientation: deviceId.startsWith('desktop') ? 'landscape' : 'portrait',
      vision: { acuity: 'normal', presbyopia: false, cvd: 'none', cvd_severity: 0, viewing_distance_mm: 300 },
      motor: { tremor: 'none', touch_sigma_mm: 1.5 },
      context: { mobility: 'seated', lighting: 'indoor', free_hands: 1, interruptions: false },
      cognition: { familiarity: 'first_use', time_pressure: 'low', reading_wpm_ko: 0 },
      reaction_time_ms: 250,
    },
    assumption_fields: ['handedness', 'grip', 'device_id'],
  };
}

function writeJson(file, obj) {
  fs.writeFileSync(file, `${JSON.stringify(obj, null, 2)}\n`);
}

function loadRun(runDir) {
  const run = JSON.parse(fs.readFileSync(path.join(runDir, 'run.json'), 'utf8'));
  const snaps = new Map();
  for (const s of run.snapshots || []) snaps.set(s.snapshot_id, JSON.parse(fs.readFileSync(path.join(runDir, s.path), 'utf8')));
  return { run, snaps };
}

const byId = (snap, id) => snap.elements.find((e) => e.id === id);
const bySel = (snap, sel) => snap.elements.find((e) => e.selector === sel);
const near = (a, b, tol) => typeof a === 'number' && Math.abs(a - b) <= tol;
function hexNear(hex, want, tol) {
  if (typeof hex !== 'string' || !HEX.test(hex)) return false;
  for (let i = 1; i < 7; i += 2) {
    if (Math.abs(parseInt(hex.slice(i, i + 2), 16) - parseInt(want.slice(i, i + 2), 16)) > tol) return false;
  }
  return true;
}
const inside = (p, b) => p && b && p.x >= b.x && p.x <= b.x + b.w && p.y >= b.y && p.y <= b.y + b.h;

function pythonAvailable() {
  const r = spawnSync('python3', ['-c', 'import ergoqa.snapshot, ergoqa.devices'], { cwd: REPO, encoding: 'utf8' });
  return r.status === 0;
}

function pythonLoadRun(label, runDir) {
  if (!pythonAvailable()) {
    skip(`${label}: ergoqa.snapshot.load_run_dir accepts the run`, 'python3 or ergoqa not importable');
    return;
  }
  const r = spawnSync('python3', ['-c', [
    'import sys',
    'from ergoqa.snapshot import load_run_dir',
    'run, snaps = load_run_dir(sys.argv[1])',
    'print(len(snaps))',
  ].join('\n'), runDir], { cwd: REPO, encoding: 'utf8' });
  check(`${label}: ergoqa.snapshot.load_run_dir accepts the run (schema, hashes, PNG sizes)`, r.status === 0, (r.stderr || '').trim().split('\n').slice(-1)[0]);
}

function checkSnapshotFiles(label, runDir, run, snaps, dev) {
  const ew = Math.round(dev.vw * dev.dpr);
  const eh = Math.round(dev.vh * dev.dpr);
  let shapeOk = true;
  let pngOk = true;
  let elemOk = true;
  let firstBad = null;
  for (const [id, s] of snaps) {
    for (const k of ['schema_version', 'snapshot_id', 'run_id', 'step_index', 'captured_at', 'surface', 'device', 'screenshot', 'elements', 'focus_point', 'console_errors', 'notes']) {
      if (!(k in s)) {
        shapeOk = false;
        firstBad = firstBad || `${id} missing ${k}`;
      }
    }
    if (s.schema_version !== 'ergo-snapshot.v1' || s.snapshot_id !== id || s.run_id !== run.run_id || !ISO.test(s.captured_at) || s.surface.kind !== 'web') {
      shapeOk = false;
      firstBad = firstBad || `${id} header`;
    }
    const pngPath = path.join(runDir, s.screenshot.path);
    const buf = fs.existsSync(pngPath) ? fs.readFileSync(pngPath) : null;
    if (!buf || crypto.createHash('sha256').update(buf).digest('hex') !== s.screenshot.sha256
      || buf.readUInt32BE(16) !== ew || buf.readUInt32BE(20) !== eh || s.screenshot.width_px !== ew || s.screenshot.height_px !== eh) {
      pngOk = false;
      firstBad = firstBad || `${id} png ${buf ? `${buf.readUInt32BE(16)}x${buf.readUInt32BE(20)}` : 'missing'} want ${ew}x${eh}`;
    }
    const ids = new Set();
    if (s.elements.length > 400) elemOk = false;
    for (const e of s.elements) {
      const good = typeof e.id === 'string' && !ids.has(e.id) && typeof e.role === 'string' && e.role.length > 0
        && e.box && ['x', 'y', 'w', 'h'].every((k) => Number.isFinite(e.box[k])) && e.box.w >= 0 && e.box.h >= 0
        && typeof e.interactive === 'boolean' && typeof e.visible === 'boolean' && typeof e.enabled === 'boolean' && typeof e.in_viewport === 'boolean'
        && Array.isArray(e.roles) && e.roles.every((r) => KNOWN_ROLES.has(r)) && ['dom', 'manual'].includes(e.source)
        && ['color_fg', 'color_bg', 'border_color'].every((k) => e[k] === null || HEX.test(e[k]))
        && (e.font_size_px === null || e.font_size_px > 0) && (e.font_weight === null || (e.font_weight >= 1 && e.font_weight <= 1000));
      if (!good) {
        elemOk = false;
        firstBad = firstBad || `${id} element ${JSON.stringify(e).slice(0, 200)}`;
      }
      ids.add(e.id);
    }
  }
  check(`${label}: every snapshot has the ergo-snapshot.v1 fields`, shapeOk, firstBad);
  check(`${label}: every PNG matches its sha256 and is viewport*dpr = ${ew}x${eh} device px`, pngOk, firstBad);
  check(`${label}: every element has typed fields, known roles, hex colours, <= 400 per snapshot`, elemOk, firstBad);
}

function checkScripted(label, runDir, dev, { flash }) {
  const { run, snaps } = loadRun(runDir);
  const sc = scenario();
  check(`${label}: run.json header (schema, ids, driver, device, mode, timestamps)`,
    run.schema_version === 'ergo-run.v1' && run.scenario_id === sc.scenario_id && typeof run.profile_id === 'string'
    && run.driver.name === 'playwright-web' && run.driver.version === '1.56.1' && run.driver.browser === 'chromium'
    && run.device.id === dev.id && run.device.viewport_css[0] === dev.vw && run.device.viewport_css[1] === dev.vh
    && run.device.dpr === dev.dpr && run.device.orientation === dev.orientation && run.mode === 'scripted'
    && ISO.test(run.started_at) && ISO.test(run.ended_at), { driver: run.driver.version, device: run.device });
  check(`${label}: status completed and success true (measured)`, run.status === 'completed' && run.success === true && run.success_basis === 'measured',
    { status: run.status, success: run.success, detail: run.success_detail, warnings: run.warnings });
  check(`${label}: one step record per scenario step`, run.steps.length === sc.steps.length, run.steps.length);
  let stepsOk = true;
  let prevEnd = -1;
  for (const s of run.steps) {
    const keys = ['step_index', 'action', 'target_element_id', 'point', 'before', 'after', 't_start_ms', 't_end_ms', 'feedback_latency_ms', 'result', 'error'];
    if (!keys.every((k) => k in s) || !snaps.has(s.before) || !snaps.has(s.after) || !(s.t_end_ms >= s.t_start_ms) || s.t_start_ms < prevEnd || s.result !== 'ok') {
      stepsOk = false;
    }
    prevEnd = s.t_end_ms;
  }
  check(`${label}: steps have spec fields, existing before/after snapshots, ordered timing, result ok`, stepsOk,
    run.steps.map((s) => [s.step_index, s.result, s.error]));
  checkSnapshotFiles(label, runDir, run, snaps, dev);

  const s0 = snaps.get(run.snapshots[0].snapshot_id);
  check(`${label}: first snapshot is step 0 with focus_point null`, s0.step_index === 0 && s0.focus_point === null);
  const pay = bySel(s0, '#pay');
  check(`${label}: #pay extracted as primary button with geometry, font and colours`,
    pay && pay.roles.join() === 'primary' && pay.interactive && pay.visible && pay.in_viewport && pay.enabled
    && pay.tag === 'button' && pay.role === 'button' && pay.name === '결제하기' && pay.box.x >= 0 && pay.box.x + pay.box.w <= dev.vw
    && near(pay.box.h, 48, 1) && pay.box.w > 100 && pay.font_size_px === 16 && pay.font_weight === 700
    && pay.color_fg === '#ffffff' && pay.color_bg === '#1a73e8', pay);
  const del = bySel(s0, '#delete-all');
  check(`${label}: #delete-all has role destructive and a border colour`, del && del.roles.join() === 'destructive' && del.border_color === '#d93025', del);
  const err0 = bySel(s0, '#error');
  check(`${label}: hidden #error is listed (visible false) with target + data-ergo-role roles`,
    err0 && err0.visible === false && err0.roles.includes('critical_message') && err0.roles.includes('error_message') && err0.role === 'alert', err0);
  check(`${label}: rgba(0,0,0,.5) over white composites to #808080`, hexNear(bySel(s0, '#overlay-label')?.color_bg, '#808080', 1), bySel(s0, '#overlay-label'));
  check(`${label}: gradient background gives color_bg null`, bySel(s0, '#grad') && bySel(s0, '#grad').color_bg === null);
  const faded = bySel(s0, '#faded');
  check(`${label}: opacity .5 disabled button composites to #8db9f4 / #ffffff, enabled false`,
    faded && hexNear(faded.color_bg, '#8db9f4', 2) && faded.color_fg === '#ffffff' && faded.enabled === false, faded);
  check(`${label}: input border colour #c4c4c4 and accessible name from <label>`,
    bySel(s0, '#card')?.border_color === '#c4c4c4' && bySel(s0, '#card')?.name === '카드 번호', bySel(s0, '#card'));
  const jump = byId(s0, 'hs-hs-jump');
  const stat = byId(s0, 'hs-hs-static');
  check(`${label}: page and scenario hotspots become source=manual elements with roles`,
    jump && jump.source === 'manual' && jump.roles.includes('game_control') && jump.selector === 'hotspot:hs-jump'
    && stat && stat.source === 'manual' && stat.roles.includes('game_control'), [jump, stat]);
  check(`${label}: canvas listed as interactive DOM element with unknown (null) background`,
    bySel(s0, '#game')?.interactive === true && bySel(s0, '#game')?.color_bg === null);

  // PNG decoder + geometry: the pixel at #pay's centre is #1a73e8.
  try {
    const img = decodePng(fs.readFileSync(path.join(runDir, s0.screenshot.path)));
    const cx = Math.round((pay.box.x + pay.box.w / 2) * dev.dpr);
    const cy = Math.round((pay.box.y + 6) * dev.dpr);
    const o = (cy * img.width + cx) * img.channels;
    const px = [img.data[o], img.data[o + 1], img.data[o + 2]];
    check(`${label}: decoded screenshot pixel inside #pay is #1a73e8 (box x dpr maps to device px)`,
      Math.abs(px[0] - 0x1a) <= 3 && Math.abs(px[1] - 0x73) <= 3 && Math.abs(px[2] - 0xe8) <= 3, px);
  } catch (err) {
    check(`${label}: decoded screenshot pixel inside #pay is #1a73e8`, false, err.message);
  }

  const [st1, st2, st3, st4, st5, , , st8, st9, st10] = run.steps;
  check(`${label}: wait step has no point and null latency`, st1.point === null && st1.feedback_latency_ms === null);
  const before2 = snaps.get(st2.before);
  const pay2 = bySel(before2, '#pay');
  check(`${label}: tap #pay point is the element centre and target_element_id matches the before snapshot`,
    pay2 && st2.target_element_id === pay2.id && near(st2.point.x, pay2.box.x + pay2.box.w / 2, 0.6) && near(st2.point.y, pay2.box.y + pay2.box.h / 2, 0.6) && st2.target_hit === true,
    { step: st2.point, id: st2.target_element_id, box: pay2 && pay2.box });
  check(`${label}: input kind is ${dev.input}`, st2.input === dev.input, st2.input);
  check(`${label}: feedback latency of the delayed (150 ms) error is measured from a DOM mutation`,
    st2.feedback_source === 'dom_mutation' && st2.feedback_latency_ms >= 120 && st2.feedback_latency_ms <= 1000, [st2.feedback_latency_ms, st2.feedback_source]);
  const after2 = snaps.get(st2.after);
  check(`${label}: #error visible after the tap, focus_point = tap point`,
    bySel(after2, '#error')?.visible === true && after2.focus_point && near(after2.focus_point.x, st2.point.x, 0.2) && near(after2.focus_point.y, st2.point.y, 0.2),
    { error: bySel(after2, '#error'), focus: after2.focus_point });
  check(`${label}: type step focuses #card by pointer and types`, st3.target_element_id === bySel(snaps.get(st3.before), '#card')?.id && /keyboard/.test(st3.input || ''), st3.input);
  const after4 = snaps.get(st4.after);
  check(`${label}: hotspot tap targets hs-hs-jump and reaches the canvas handler`,
    st4.target_element_id === 'hs-hs-jump' && bySel(after4, '#game-log')?.text === '점프 1회', { id: st4.target_element_id, log: bySel(after4, '#game-log')?.text });
  check(`${label}: console.error from the page appears in the after snapshot`,
    after4.console_errors.some((c) => String(c).includes('핫스팟')), after4.console_errors);
  check(`${label}: tap on inert text has feedback_latency_ms null after the 3000 ms window`,
    st5.feedback_latency_ms === null && st5.feedback_window_ms === 3000 && st5.feedback_source === null, [st5.feedback_latency_ms, st5.feedback_window_ms, st5.feedback_source]);
  const tw = run.timing_windows.find((w) => w.id === 'qte-1');
  check(`${label}: timing window measures both visible intervals (~400 ms, ~250 ms) with min/max`,
    tw && tw.intervals_ms.length === 2 && near(tw.intervals_ms[0], 400, 60) && near(tw.intervals_ms[1], 250, 60)
    && tw.visible_ms === Math.min(...tw.intervals_ms) && tw.max_visible_ms === Math.max(...tw.intervals_ms) && tw.text === '지금 누르세요!', tw);
  const pre8 = snaps.get(st8.before);
  check(`${label}: off-screen target is scrolled into view with a pre-action snapshot`,
    st8.auto_scrolled === true && pre8.notes.includes('pre_action_auto_scroll') && pre8.step_index === 8
    && st8.point.y >= 0 && st8.point.y < dev.vh && st8.target_hit === true && bySel(snaps.get(st8.after), '#below-status')?.text === '맨 아래 버튼을 눌렀습니다',
    { auto: st8.auto_scrolled, notes: pre8.notes, point: st8.point });
  check(`${label}: Playwright text= selector resolves to the #pay element id`,
    st9.target_element_id === bySel(snaps.get(st9.before), '#pay')?.id, st9.target_element_id);
  const last = snaps.get(run.steps[run.steps.length - 1].after);
  check(`${label}: success element #done is visible at the end`, bySel(last, '#done')?.visible === true);
  check(`${label}: off-origin image and WebSocket blocked by the network policy, no console noise`,
    run.driver.network_policy.blocked_requests >= 2
    && ['image', 'websocket'].every((t) => run.driver.network_policy.blocked_sample.some((b) => b.resource_type === t))
    && [...snaps.values()].every((s) => s.console_errors.every((c) => !/ERR_BLOCKED_BY_CLIENT|WebSocket/.test(String(c)))),
    run.driver.network_policy);
  if (flash) {
    const samples = run.flash_samples;
    const burst = samples.filter((s) => s.step_index === st10.step_index);
    const changed = burst.filter((s) => s.changed_fraction > 0.1).length;
    const monotonic = samples.every((s, i) => i === 0 || s.t_ms >= samples[i - 1].t_ms);
    check(`${label}: flash sampling records luminance frames (t_ms, mean_luminance 0..1, frame_index)`,
      run.flash_sampling.enabled && samples.length > 20 && monotonic
      && samples.every((s) => s.mean_luminance >= 0 && s.mean_luminance <= 1 && Number.isInteger(s.frame_index) && s.changed_fraction >= 0 && s.changed_fraction <= 1),
      { n: samples.length, sampling: run.flash_sampling });
    check(`${label}: 10 Hz black/white flicker shows >= 4 frames with >10% changed area`, changed >= 4, burst.map((s) => [s.t_ms, s.mean_luminance, s.changed_fraction]));
  } else {
    check(`${label}: flash sampling off by default`, run.flash_samples.length === 0 && run.flash_sampling.enabled === false);
  }
  pythonLoadRun(label, runDir);
}

function actionsScenario() {
  return {
    schema_version: 'ergo-scenario.v1',
    scenario_id: 'SC-driver-actions-01',
    surface: { kind: 'web', url: '{BASE}/selftest.html?panel=actions' },
    task_goal_ko: '제스처 입력이 페이지에 실제 이벤트로 도착하는지 확인한다',
    device_ids: ['iphone-15', 'tv-55-1080'],
    targets: {},
    steps: [
      { action: 'scroll', direction: 'down', distance: 300 },
      { action: 'scroll', dy: -300 },
      { action: 'long_press', target: '#lp-target', ms: 700 },
      { action: 'double_tap', target: '#dbl-target' },
      { action: 'drag', target: '#drag-handle', dx: 80, dy: 0 },
      { action: 'swipe', target: '#swipe-area', direction: 'left', distance: 120 },
      { action: 'press', key: 'ArrowRight' },
      { action: 'gamepad', button: 'A', key: 'Enter' },
      { action: 'tap', target: { x: 700, y: 300 } },
    ],
    success: { text_present: ['두 번 눌림', 'ArrowRight Enter'] },
  };
}

function checkActions(label, runDir, dev) {
  const { run, snaps } = loadRun(runDir);
  check(`${label}: device ${dev.id} ${dev.orientation} ${dev.vw}x${dev.vh}, completed, success`,
    run.device.id === dev.id && run.device.orientation === dev.orientation && run.device.viewport_css.join() === `${dev.vw},${dev.vh}`
    && run.status === 'completed' && run.success === true, { device: run.device, status: run.status, success: run.success, steps: run.steps.map((s) => [s.result, s.error]) });
  checkSnapshotFiles(label, runDir, run, snaps, dev);
  const [sc1, sc2, lp, dbl, drag, swipe, press, pad, pt] = run.steps;
  check(`${label}: scroll down/up 300 px measured in scroll_delta (+-6)`,
    near(sc1.scroll_delta?.y, 300, 6) && near(sc2.scroll_delta?.y, -300, 6), [sc1.scroll_delta, sc2.scroll_delta]);
  const pointer = dev.input;
  check(`${label}: pointer actions use ${pointer}, keys use keyboard / gamepad mapping`,
    [sc1, lp, dbl, drag, swipe, pt].every((s) => s.input === pointer) && press.input === 'keyboard' && pad.input === 'keyboard(gamepad-mapping)',
    run.steps.map((s) => s.input));
  if (pointer === 'mouse(fallback)') {
    check(`${label}: pointer fallback is reported in warnings`, run.warnings.some((w) => /no pointer/.test(w)), run.warnings);
  }
  check(`${label}: drag end_point = start + (80, 0)`, drag.end_point && near(drag.end_point.x - drag.point.x, 80, 0.5) && near(drag.end_point.y, drag.point.y, 0.5), [drag.point, drag.end_point]);
  const last = snaps.get(pt.after);
  const log = (sel) => bySel(last, sel)?.text || '';
  const lpMs = Number((log('#lp-log').match(/(\d+)ms/) || [])[1]);
  check(`${label}: long_press held >= 650 ms on the target`, lpMs >= 650 && lpMs <= 1500, log('#lp-log'));
  check(`${label}: double_tap produced a dblclick`, log('#dbl-log') === '두 번 눌림', log('#dbl-log'));
  const dragPx = Number((log('#drag-log').match(/-?\d+/) || [])[0]);
  check(`${label}: drag moved the handle ~80 px`, near(dragPx, 80, 10), log('#drag-log'));
  check(`${label}: swipe left reached the swipe area`, /^왼쪽/.test(log('#swipe-log')), log('#swipe-log'));
  check(`${label}: press and gamepad keys arrived`, log('#key-log') === 'ArrowRight Enter', log('#key-log'));
  check(`${label}: {x,y} target taps that point and becomes the focus_point`,
    pt.point.x === 700 && pt.point.y === 300 && last.focus_point && last.focus_point.x === 700 && last.focus_point.y === 300, [pt.point, last.focus_point]);
  pythonLoadRun(label, runDir);
}

async function serveTest(base, tmp) {
  const label = 'serve galaxy-s24';
  const outDir = path.join(tmp, 'runs');
  let ready = null;
  let resolveReady;
  const readyP = new Promise((r) => { resolveReady = r; });
  const proc = runDriver(['serve', '--scenario', path.join(tmp, 'scenario.json'), '--profile', path.join(tmp, 'p-s24.json'),
    '--out', outDir, '--run-id', 'R-serve', '--base', base, '--port', '0', '--idle-timeout-s', '120'], {
    onLine: (obj) => {
      if (obj.event === 'ready') resolveReady(obj);
    },
  });
  const guard = setTimeout(() => resolveReady(null), 60000);
  ready = await readyP;
  clearTimeout(guard);
  if (!check(`${label}: prints a ready line with a 127.0.0.1 URL and the initial snapshot`,
    ready && /^http:\/\/127\.0\.0\.1:\d+$/.test(ready.url) && fs.existsSync(ready.snapshot) && fs.existsSync(ready.png), ready)) {
    const r = await proc;
    console.log(r.err);
    return;
  }
  const port = ready.port;
  const health = await request(port, 'GET', '/health');
  check(`${label}: GET /health`, health.status === 200 && health.json.ok === true && health.json.run_id === 'R-serve', health.text);
  const snap = await request(port, 'GET', '/snapshot');
  check(`${label}: GET /snapshot writes a new snapshot without acting`,
    snap.status === 200 && snap.json.result === 'ok' && fs.existsSync(snap.json.snapshot) && fs.existsSync(snap.json.png) && snap.json.step_index === 0, snap.text);
  const tap = await request(port, 'POST', '/act', { body: { action: 'tap', target: '#pay' } });
  check(`${label}: POST /act tap returns snapshot/png paths, result ok and a feedback latency`,
    tap.status === 200 && tap.json.result === 'ok' && fs.existsSync(tap.json.snapshot) && fs.existsSync(tap.json.png)
    && typeof tap.json.feedback_latency_ms === 'number' && tap.json.target_element_id, tap.text);
  const cases = [
    ['unknown action is rejected (400)', await request(port, 'POST', '/act', { body: { action: 'evaluate', script: 'alert(1)' } }), 400],
    ['unknown key is rejected (400)', await request(port, 'POST', '/act', { body: { action: 'tap', target: '#pay', js: '1' } }), 400],
    ['non-JSON content type is rejected (415)', await request(port, 'POST', '/act', { body: '{"action":"tap","target":"#pay"}', headers: { 'Content-Type': 'text/plain' } }), 415],
    ['cross-origin Origin is rejected (403)', await request(port, 'POST', '/act', { body: { action: 'tap', target: '#pay' }, headers: { Origin: 'http://evil.example' } }), 403],
    ['foreign Host header is rejected (421)', await request(port, 'GET', '/health', { headers: { Host: `evil.example:${port}` } }), 421],
    ['wrong method is rejected (405)', await request(port, 'GET', '/act'), 405],
    ['unknown endpoint is 404', await request(port, 'GET', '/eval'), 404],
    ['oversized body is rejected (413)', await request(port, 'POST', '/act', { body: JSON.stringify({ action: 'type', text: 'x'.repeat(70000) }) }), 413],
    ['malformed JSON is rejected (400)', await request(port, 'POST', '/act', { body: '{"action":' }), 400],
    ['note without confusion flag is rejected (400)', await request(port, 'POST', '/note', { body: { intent: 'x' } }), 400],
  ];
  for (const [name, res, want] of cases) check(`${label}: ${name}`, res.status === want, `${res.status} ${res.text}`);
  const note = await request(port, 'POST', '/note', { body: { intent: '결제하기', expected: '결제 완료 화면', observed: '카드 번호 오류가 위쪽에 표시됨', confusion: true } });
  check(`${label}: POST /note records a persona note`, note.status === 200 && note.json.ok === true && note.json.step_index === 1, note.text);
  const type = await request(port, 'POST', '/act', { body: { action: 'type', target: '#card', text: '4242 4242' } });
  check(`${label}: POST /act type`, type.status === 200 && type.json.result === 'ok', type.text);
  const miss = await request(port, 'POST', '/act', { body: { action: 'tap', target: '#does-not-exist', timeout_ms: 300 } });
  check(`${label}: missing target returns result no_target (session continues)`, miss.status === 200 && miss.json.result === 'no_target', miss.text);
  const pay = await request(port, 'POST', '/act', { body: { action: 'tap', target: 'text=결제하기' } });
  check(`${label}: POST /act tap text selector`, pay.status === 200 && pay.json.result === 'ok', pay.text);
  const fin = await request(port, 'POST', '/finish', { body: { success: true } });
  check(`${label}: POST /finish writes run.json`, fin.status === 200 && fs.existsSync(fin.json.run) && fin.json.exit_code === 0, fin.text);
  const done = await proc;
  check(`${label}: process exits 0 after /finish`, done.code === 0, `${done.code} ${done.err}`);
  const runDir = path.join(outDir, 'R-serve');
  const { run, snaps } = loadRun(runDir);
  check(`${label}: run.json is interactive, completed, success measured, persona claim kept`,
    run.mode === 'interactive' && run.status === 'completed' && run.success === true && run.success_basis === 'measured' && run.persona_claimed_success === true,
    { mode: run.mode, status: run.status, success: run.success });
  const n0 = run.persona_notes[0];
  check(`${label}: persona_notes carry step_index/intent/expected/observed/confusion (basis judgment)`,
    run.persona_notes.length === 1 && n0.step_index === 1 && n0.intent === '결제하기' && n0.confusion === true && n0.basis === 'judgment', run.persona_notes);
  check(`${label}: interactive steps recorded including no_target`,
    run.steps.length === 4 && run.steps.map((s) => s.result).join() === 'ok,ok,no_target,ok', run.steps.map((s) => s.result));
  check(`${label}: on-demand snapshot is noted`, [...snaps.values()].some((s) => s.notes.includes('on_demand')));
  checkSnapshotFiles(label, runDir, run, snaps, { vw: 360, vh: 780, dpr: 3 });
  pythonLoadRun(label, runDir);
}

async function exitCodeTests(base, tmp) {
  const sc = path.join(tmp, 'scenario.json');
  const p = path.join(tmp, 'p-s24.json');
  const out = path.join(tmp, 'runs');
  let r = await runDriver(['run', '--profile', p, '--out', out]);
  check('usage: missing --scenario exits 2', r.code === 2, r.err);
  r = await runDriver(['run', '--scenario', sc, '--device', 'nokia-3310', '--out', out, '--base', base]);
  check('usage: unknown device exits 2', r.code === 2 && /unknown device/.test(r.err), r.err);
  r = await runDriver(['run', '--scenario', sc, '--profile', p, '--out', out]);
  check('usage: "{BASE}" without --base exits 2', r.code === 2 && /--base/.test(r.err), r.err);
  const bad = scenario();
  bad.steps = [{ action: 'eval', target: '#pay' }];
  writeJson(path.join(tmp, 'bad.json'), bad);
  r = await runDriver(['run', '--scenario', path.join(tmp, 'bad.json'), '--profile', p, '--out', out, '--base', base]);
  check('usage: unknown scenario action exits 2', r.code === 2 && /action must be one of/.test(r.err), r.err);
  r = await runDriver(['run', '--scenario', sc, '--profile', p, '--out', out, '--base', base, '--run-id', 'R-serve']);
  check('usage: existing non-empty run directory is never overwritten (exit 2)', r.code === 2 && /not empty/.test(r.err), r.err);
  const failing = scenario();
  failing.steps = [{ action: 'tap', target: '#missing', timeout_ms: 300 }, { action: 'tap', target: '#pay' }];
  writeJson(path.join(tmp, 'failing.json'), failing);
  r = await runDriver(['run', '--scenario', path.join(tmp, 'failing.json'), '--profile', p, '--out', out, '--base', base, '--run-id', 'R-failed']);
  const failedRun = r.code === 3 ? loadRun(path.join(out, 'R-failed')).run : null;
  check('run: failed step stops the run with status failed, success false, exit 3',
    failedRun && failedRun.status === 'failed' && failedRun.success === false && failedRun.steps.length === 1 && failedRun.steps[0].result === 'no_target',
    `${r.code} ${r.err}`);
  // A port nothing listens on: the initial navigation fails -> blocked, exit 4, run.json still written.
  const closed = await new Promise((resolve) => {
    const s = http.createServer();
    s.listen(0, '127.0.0.1', () => {
      const { port } = s.address();
      s.close(() => resolve(port));
    });
  });
  r = await runDriver(['run', '--scenario', sc, '--profile', p, '--out', out, '--base', `http://127.0.0.1:${closed}`, '--run-id', 'R-blocked']);
  const blockedRun = fs.existsSync(path.join(out, 'R-blocked', 'run.json')) ? loadRun(path.join(out, 'R-blocked')).run : null;
  check('run: unreachable surface gives status blocked, exit 4, run.json written',
    r.code === 4 && blockedRun && blockedRun.status === 'blocked' && blockedRun.blocked_reasons.length > 0, `${r.code} ${r.err}`);
}

function deviceTableTest() {
  if (!pythonAvailable()) {
    skip('device table mirrors ergoqa.devices', 'python3 or ergoqa not importable');
    return;
  }
  const r = spawnSync('python3', ['-c', [
    'import json',
    'from ergoqa.devices import list_devices',
    'print(json.dumps([{"id": d.id, "form_factor": d.form_factor, "viewport_css": list(d.viewport_css), "dpr": d.dpr, "input": d.input, "playwright_device": d.playwright_device, "has_touch": d.has_touch, "is_mobile": d.is_mobile} for d in list_devices()]))',
  ].join('\n')], { cwd: REPO, encoding: 'utf8' });
  if (r.status !== 0) {
    check('device table mirrors ergoqa.devices', false, r.stderr);
    return;
  }
  const py = JSON.parse(r.stdout);
  const diffs = [];
  for (const d of py) {
    const js = CATALOG.get(d.id);
    if (!js) {
      diffs.push(`${d.id} missing in devices.mjs`);
      continue;
    }
    const touch = js.input === 'touch' || ['phone', 'tablet', 'foldable', 'handheld_console'].includes(js.form_factor);
    const mobile = ['phone', 'tablet', 'foldable'].includes(js.form_factor);
    if (js.form_factor !== d.form_factor || js.viewport_css[0] !== d.viewport_css[0] || js.viewport_css[1] !== d.viewport_css[1]
      || js.dpr !== d.dpr || js.input !== d.input || js.playwright_device !== d.playwright_device || touch !== d.has_touch || mobile !== d.is_mobile) {
      diffs.push(`${d.id}: js ${JSON.stringify(js)} py ${JSON.stringify(d)}`);
    }
  }
  for (const id of CATALOG.keys()) if (!py.some((d) => d.id === id)) diffs.push(`${id} missing in ergoqa.devices`);
  check('device table mirrors ergoqa.devices (ids, viewport, dpr, input, touch/mobile, descriptor)', diffs.length === 0, diffs);
}

async function layersTest(base, tmp) {
  const sc = {
    schema_version: 'ergo-scenario.v1',
    scenario_id: 'SC-driver-layers-01',
    surface: { kind: 'web', url: '{BASE}/layers.html' },
    task_goal_ko: '모달을 연다',
    device_ids: ['galaxy-s24'],
    targets: {},
    steps: [{ action: 'tap', target: '#open-modal' }],
    success: { selector_visible: '#in-modal' },
  };
  writeJson(path.join(tmp, 'layers.json'), sc);
  const outDir = path.join(tmp, 'runs');
  const r = await runDriver(['run', '--scenario', path.join(tmp, 'layers.json'), '--profile', path.join(tmp, 'p-s24.json'),
    '--out', outDir, '--run-id', 'R-layers', '--base', base]);
  if (!check('layers galaxy-s24: exit 0', r.code === 0, `${r.code} ${r.err}`)) return;
  const { run, snaps } = loadRun(path.join(outDir, 'R-layers'));
  const s0 = snaps.get(run.snapshots[0].snapshot_id);
  const s1 = snaps.get(run.steps[0].after);
  const field = bySel(s0, '#wfield');
  check('layers: opaque input on a tinted card reports the card as container_bg (#fffbe6)', field && field.container_bg === '#fffbe6', field);
  const covered = bySel(s0, '#covered-btn');
  check('layers: a button under a translucent cover has occluded_fraction 1 and occluded_by #cover',
    covered && covered.occluded_fraction === 1 && covered.occluded_by === '#cover', covered);
  const free = bySel(s0, '#behind');
  check('layers: an uncovered button has occluded_fraction 0 and is not inert', free && free.occluded_fraction === 0 && free.inert_by_modal === false, free);
  check('layers: <li> without its own text node is not listed; its button is (20px)',
    !bySel(s0, '#li-owner') && bySel(s0, '#li-btn')?.font_size_px === 20, bySel(s0, '#li-owner'));
  const behind1 = bySel(s1, '#behind');
  const inModal = bySel(s1, '#in-modal');
  check('layers: after showModal() the page behind is inert_by_modal and the dialog content is not',
    behind1 && behind1.inert_by_modal === true && inModal && inModal.inert_by_modal === false, [behind1, inModal]);
}

async function main() {
  const keep = process.argv.includes('--keep');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ergo-web-selftest-'));
  const server = await startFixtureServer();
  const base = `http://127.0.0.1:${server.address().port}`;
  console.log(`# fixture ${base}/selftest.html, outputs in ${tmp}`);
  try {
    writeJson(path.join(tmp, 'scenario.json'), scenario());
    writeJson(path.join(tmp, 'p-s24.json'), profile('EP-S24', 'galaxy-s24'));
    writeJson(path.join(tmp, 'p-desk.json'), profile('EP-DESK', 'desktop-1920'));
    deviceTableTest();

    const outDir = path.join(tmp, 'runs');
    let r = await runDriver(['run', '--scenario', path.join(tmp, 'scenario.json'), '--profile', path.join(tmp, 'p-s24.json'),
      '--out', outDir, '--run-id', 'R-s24', '--base', base]);
    const fin = r.lines.find((l) => l.event === 'finished');
    if (check('run galaxy-s24: exit 0 with a finished line', r.code === 0 && fin && fin.status === 'completed' && fin.success === true, `${r.code} ${r.err}`)) {
      checkScripted('run galaxy-s24', path.join(outDir, 'R-s24'), {
        id: 'galaxy-s24', vw: 360, vh: 780, dpr: 3, orientation: 'portrait', input: 'touch',
      }, { flash: false });
    }

    r = await runDriver(['run', '--scenario', path.join(tmp, 'scenario.json'), '--profile', path.join(tmp, 'p-desk.json'),
      '--out', outDir, '--run-id', 'R-desk', '--base', base, '--flash-sample-ms', '700']);
    const fin2 = r.lines.find((l) => l.event === 'finished');
    if (check('run desktop-1920 (--flash-sample-ms 700): exit 0 with a finished line', r.code === 0 && fin2 && fin2.success === true, `${r.code} ${r.err}`)) {
      checkScripted('run desktop-1920', path.join(outDir, 'R-desk'), {
        id: 'desktop-1920', vw: 1920, vh: 1080, dpr: 1, orientation: 'landscape', input: 'mouse',
      }, { flash: true });
    }

    writeJson(path.join(tmp, 'actions.json'), actionsScenario());
    for (const [devArgs, dev] of [
      [['--device', 'iphone-15', '--orientation', 'landscape'], { id: 'iphone-15', vw: 852, vh: 393, dpr: 3, orientation: 'landscape', input: 'touch' }],
      [['--device', 'tv-55-1080'], { id: 'tv-55-1080', vw: 1920, vh: 1080, dpr: 1, orientation: 'landscape', input: 'mouse(fallback)' }],
    ]) {
      const runId = `R-actions-${dev.id}`;
      r = await runDriver(['run', '--scenario', path.join(tmp, 'actions.json'), ...devArgs, '--out', outDir, '--run-id', runId,
        '--base', base, '--feedback-timeout-ms', '1000']);
      if (check(`actions ${dev.id}: exit 0`, r.code === 0, `${r.code} ${r.err} ${r.out}`)) {
        checkActions(`actions ${dev.id}`, path.join(outDir, runId), dev);
      }
    }

    await layersTest(base, tmp);
    await serveTest(base, tmp);
    await exitCodeTests(base, tmp);
  } finally {
    server.close();
  }
  console.log(`# ${passes} passed, ${failures} failed`);
  if (!keep && failures === 0) fs.rmSync(tmp, { recursive: true, force: true });
  else console.log(`# outputs kept in ${tmp}`);
  process.exit(failures ? 1 : 0);
}

main().catch((err) => {
  console.log(`FAIL selftest crashed -- ${err && err.stack ? err.stack : err}`);
  process.exit(1);
});
