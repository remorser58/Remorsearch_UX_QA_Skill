import assert from 'node:assert/strict';
import test from 'node:test';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import vm from 'node:vm';
import os from 'node:os';
import { validateRequest, routeReply, disableUnroutedTransports, readReviewedUploads, requireWorkerIsolation } from './journey_bridge.mjs';

function request() {
  return {
    schema_version: 'ux-journey-browser-request.v1',
    binding: { task_id: 'T-retain', attempt: 1, operation_id: 'operation-one', build_sha256: 'a'.repeat(64),
      persona_id: 'P-returning', revision: 1, profile_sha256: 'b'.repeat(64), prd_sha256: 'c'.repeat(64) },
    source: '/reviewed/product', files: { 'index.html': 'd'.repeat(64) }, output: '/owned/scratch/browser',
    scenario: { schema_version: 'ergo-scenario.v1', scenario_id: 'SC-retain',
      surface: { kind: 'web', url: 'https://remorsearch.invalid/index.html', build_id: 'a'.repeat(64) },
      task_goal_ko: 'Preserve entered data after a validation error.', device_ids: ['desktop-1920'],
      steps: [{ action: 'type', target: '#request', text: 'Synthetic request' }, { action: 'click', target: '#submit' }],
      success: { task_checks: [{ id: 'retain', selector: '#request', property: 'value', from_step: 1, after_step: 2,
        severity: 'P1', consequence: 'The entered request must survive the failed submission.' }] } },
    device_id: 'desktop-1920', timeout_seconds: 15,
  };
}

test('binds fixed measured checkpoints to the reviewed scenario', () => {
  const doc = request();
  const accepted = validateRequest(doc);
  assert.equal(accepted.scenario.success.task_checks[0].after_step, 2);
  assert.equal(accepted.scenario.build_id, doc.binding.build_sha256);
  assert.equal(accepted.runId, 'R-' + 'operation-one');
  assert.deepEqual(doc, request(), 'validation must not mutate frozen input');
});

test('rejects other URLs, credentials, ports, fragments and unreviewed files', () => {
  for (const url of ['https://example.test/index.html', 'http://127.0.0.1/index.html',
    'https://me@remorsearch.invalid/index.html', 'https://remorsearch.invalid:443/index.html',
    'https://remorsearch.invalid/index.html#entry', 'https://remorsearch.invalid/missing.html']) {
    const doc = request(); doc.scenario.surface.url = url;
    assert.throws(() => validateRequest(doc));
  }
});

test('rejects path traversal, unknown static types, oversized input maps and missing bindings', () => {
  for (const name of ['../index.html', '/index.html', 'folder/../index.html', 'a\\index.html', '.hidden.html', 'adapter.py']) {
    const doc = request(); doc.files[name] = 'd'.repeat(64);
    assert.throws(() => validateRequest(doc));
  }
  const doc = request(); delete doc.binding.operation_id;
  assert.throws(() => validateRequest(doc));
  const many = request();
  for (let i = 0; i < 64; i++) many.files['extra-' + i + '.js'] = 'd'.repeat(64);
  assert.throws(() => validateRequest(many));
});

test('rejects unmeasured success, missing checkpoints and cross-build claims', () => {
  const cases = [
    d => { d.scenario.success = { selector_visible: '#done' }; },
    d => { delete d.scenario.success.task_checks[0].after_step; },
    d => { d.scenario.success.task_checks[0].after_step = 3; },
    d => { d.scenario.surface.build_id = 'e'.repeat(64); },
    d => { d.scenario.steps[0] = { action: 'type', target: '#request', text: 'Synthetic', unexpected: true }; },
    d => { d.scenario.steps[0] = { action: 'evaluate', script: 'document.body.remove()' }; },
    d => { d.timeout_seconds = 31; },
    d => { d.output = d.source + '/browser'; },
  ];
  for (const mutate of cases) { const doc = request(); mutate(doc); assert.throws(() => validateRequest(doc)); }
});

test('serves only reviewed bytes and never offers a network fallback', () => {
  const bytes = Buffer.from('<p>Owned fixture</p>');
  const files = new Map([['index.html', { body: bytes, contentType: 'text/html; charset=utf-8' }]]);
  const reply = routeReply(files, 'https://remorsearch.invalid/index.html', 'GET');
  assert.equal(reply.status, 200); assert.equal(reply.body, bytes);
  assert.match(reply.headers['content-security-policy'], /connect-src 'none'/);
  assert.equal(routeReply(files, 'https://remorsearch.invalid/index.html', 'HEAD').body.length, 0);
  for (const [url, method] of [
    ['https://example.test/index.html', 'GET'], ['https://remorsearch.invalid/index.html', 'POST'],
    ['https://remorsearch.invalid/index.html?secret=value', 'GET'], ['file:///index.html', 'GET'],
    ['https://remorsearch.invalid/missing.js', 'GET'], ['https://remorsearch.invalid/%2e%2e/index.html', 'GET'],
  ]) assert.equal(routeReply(files, url, method), null);
});

test('worker allowance is exact and leaves network connections forbidden', () => {
  const doc = request();
  doc.files['worker.js'] = 'e'.repeat(64);
  doc.workers = { 'worker.js': 'e'.repeat(64) };
  doc.uploads = [{ id: 'owned-zip', path: 'inputs/owned.zip', name: 'owned.zip',
    mime_type: 'application/zip', size_bytes: 12, sha256: 'f'.repeat(64) }];
  doc.scenario.steps[1] = { action: 'upload', target: '#choose', input: '#files', files: ['owned-zip'], timeout_ms: 5000 };
  assert.equal(validateRequest(doc).scenario.steps[1].action, 'upload');
  const files = new Map([['worker.js', { body: Buffer.from('postMessage(1)'), contentType: 'text/javascript' }]]);
  const csp = routeReply(files, 'https://remorsearch.invalid/worker.js', 'GET', doc.workers).headers['content-security-policy'];
  assert.match(csp, /worker-src https:\/\/remorsearch.invalid\/worker.js;/);
  assert.match(csp, /connect-src 'none'/);
  doc.workers['worker.js'] = 'a'.repeat(64);
  assert.throws(() => validateRequest(doc));
});

test('upload declarations cannot smuggle paths, unknown IDs, excessive bytes or worker URLs', () => {
  const declared = () => {
    const d = request();
    d.uploads = [{ id: 'owned', path: 'inputs/owned.zip', name: 'owned.zip',
      mime_type: 'application/zip', size_bytes: 3, sha256: 'a'.repeat(64) }];
    d.scenario.steps[1] = { action: 'upload', target: '#choose', input: '#files', files: ['owned'] };
    return d;
  };
  assert.doesNotThrow(() => validateRequest(declared()));
  for (const change of [
    d => { d.uploads[0].path = '../private.zip'; },
    d => { d.uploads[0].name = '/private.zip'; },
    d => { d.uploads[0].sha256 = 'unknown'; },
    d => { d.uploads[0].size_bytes = 16 * 1024 * 1024 + 1; },
    d => { d.uploads.push({ ...d.uploads[0] }); },
    d => { d.scenario.steps[1].files = ['foreign']; },
    d => { d.workers = { 'https://remote.invalid/worker.js': 'a'.repeat(64) }; },
    d => { d.workers = { 'unreviewed.js': undefined }; },
    d => { d.workers = { 'index.html': d.files['index.html'] }; },
  ]) { const d = declared(); change(d); assert.throws(() => validateRequest(d)); }
});

test('binary fixtures require current regular owned bytes and refuse changed hashes or links', () => {
  const directory = fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), 'rq-owned-upload-')));
  try {
    const body = Buffer.from([80, 75, 0, 255, 1]);
    fs.writeFileSync(path.join(directory, 'owned.zip'), body);
    const entry = { id: 'owned', path: 'owned.zip', name: 'owned.zip', mime_type: 'application/zip',
      size_bytes: body.length, sha256: crypto.createHash('sha256').update(body).digest('hex') };
    assert.deepEqual(readReviewedUploads(directory, [entry]).get('owned').buffer, body);
    assert.throws(() => readReviewedUploads(directory, [{ ...entry, sha256: 'f'.repeat(64) }]));
    fs.symlinkSync('owned.zip', path.join(directory, 'linked.zip'));
    assert.throws(() => readReviewedUploads(directory, [{ ...entry, path: 'linked.zip' }]));
    fs.linkSync(path.join(directory, 'owned.zip'), path.join(directory, 'hard.zip'));
    assert.throws(() => readReviewedUploads(directory, [entry]));
  } finally { fs.rmSync(directory, { recursive: true }); }
});

test('a plain Node invocation cannot claim the Worker network-denial capability', async () => {
  await assert.rejects(requireWorkerIsolation(), { bridgeCode: 'worker_isolation_unavailable' });
});

test('preflight validates exact source bytes without output or a browser runtime', () => {
  const driver = path.dirname(fileURLToPath(import.meta.url));
  const doc = request();
  doc.source = path.join(driver, 'fixtures');
  doc.files = { 'inspect.html': crypto.createHash('sha256').update(fs.readFileSync(path.join(doc.source, 'inspect.html'))).digest('hex') };
  doc.scenario.surface.url = 'https://remorsearch.invalid/inspect.html';
  doc.output = path.join(driver, 'not-created-validation-' + process.pid);
  assert.equal(fs.existsSync(doc.output), false);
  const invoke = value => spawnSync(process.execPath, [path.join(driver, 'journey_bridge.mjs'), '--validate'],
    { input: JSON.stringify(value), encoding: 'utf8', timeout: 5000 });
  const accepted = invoke(doc);
  assert.equal(accepted.status, 0, accepted.stderr);
  assert.deepEqual(JSON.parse(accepted.stdout), { schema_version: 'ux-journey-browser-validation.v1', valid: true });
  doc.files['inspect.html'] = 'f'.repeat(64);
  const refused = invoke(doc);
  assert.equal(refused.status, 2);
  assert.deepEqual(JSON.parse(refused.stdout), { schema_version: 'ux-journey-browser-validation.v1', valid: false });
  assert.equal(fs.existsSync(doc.output), false);
});

test('unrouted transport guard removes constructors and prevents restoration before page code', () => {
  const calls = [];
  const context = vm.createContext({ RTCPeerConnection: function () { calls.push('rtc'); },
    WebTransport: function () { calls.push('transport'); }, RTCFutureTransport: function () { calls.push('future'); } });
  vm.runInContext('(' + disableUnroutedTransports.toString() + ')()', context);
  for (const name of ['RTCPeerConnection', 'webkitRTCPeerConnection', 'RTCIceTransport', 'WebTransport', 'RTCFutureTransport']) {
    const descriptor = Object.getOwnPropertyDescriptor(context, name);
    assert.equal(descriptor.value, undefined);
    assert.equal(descriptor.writable, false);
    assert.equal(descriptor.configurable, false);
    assert.throws(() => Object.defineProperty(context, name, { value: function () {} }));
    assert.throws(() => vm.runInContext('new ' + name + '()', context));
  }
  assert.equal(vm.runInContext('Object.isFrozen(__remorsearchOwnedNetworkGuard.disabled)', context), true);
  assert.deepEqual(calls, [], 'the guard must never call the original transport');
});
