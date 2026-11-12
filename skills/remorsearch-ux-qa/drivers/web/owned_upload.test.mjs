// Pure contract tests. The fake page below is not browser or product evidence.
import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import { normalizeAction, normalizeScenario } from './validate.mjs';
import { chooseOwnedFiles, prepareOwnedUpload, UPLOAD_LIMITS } from './owned_upload.mjs';
import { WebSession } from './session.mjs';
import { sha256 } from './util.mjs';

const action = () => ({ action: 'upload', target: '#choose', input: '#archive', files: ['fixture-previous'], timeout_ms: 100 });

test('accepts an owned upload action with a visible target and a separate file input', () => {
  const authored = action();
  assert.deepEqual(normalizeAction(authored, { strict: true }), { action: authored, warnings: [] });
});

test('upload remains ineligible as a from_step text source', () => {
  assert.throws(() => normalizeScenario({ schema_version: 'ergo-scenario.v1', scenario_id: 'owned-upload',
    surface: { kind: 'web', url: 'https://remorsearch.invalid/index.html' }, steps: [action()],
    success: { task_checks: [{ id: 'retained', selector: '#result', property: 'text', from_step: 1,
      after_step: 1, severity: 'P1', consequence: 'Keep the previous result.' }] } }, { requireSteps: true }), /from_step must reference an authored type action/);
});

const entry = (buffer = Buffer.from('synthetic fixture bytes')) =>
  ({ name: 'synthetic-previous.zip', mimeType: 'application/zip', buffer, sha256: sha256(buffer) });
const registry = () => new Map([['fixture-previous', entry()]]);
const point = { x: 5, y: 5 };

// Execute the actual DOM predicate in a tiny VM document. No product, browser,
// screenshot or receipt is synthesized by these helper tests.
function fakePage(options = {}) {
  const calls = [];
  let pending = null;
  const document = {};
  const makeNode = (tagName, extras = {}) => ({ tagName, ownerDocument: document,
    isConnected: true, disabled: false, multiple: true, webkitdirectory: false,
    parentElement: null, hidden: false, style: { display: 'block', visibility: 'visible', opacity: '1' },
    type: tagName === 'INPUT' ? 'file' : 'button',
    matches(selector) { return selector === ':disabled' && this.disabled; },
    closest(selector) {
      if (selector === '[hidden]') for (let node = this; node; node = node.parentElement) if (node.hidden) return node;
      return null;
    },
    checkVisibility(settings) {
      assert.equal(settings.opacityProperty, true);
      assert.equal(settings.visibilityProperty, true);
      return options.visibilityCheck !== false;
    },
    getAttribute() { return null; },
    getBoundingClientRect() { return { left: 0, top: 0, width: 10, height: 10 }; },
    contains(node) { return this === node; },
    async dispose() { calls.push('dispose'); }, ...extras });
  const button = makeNode('BUTTON');
  const parent = makeNode('DIV', options.ancestorHidden ? { hidden: true } : {});
  button.parentElement = parent;
  if (options.ancestorStyle) parent.style = { ...parent.style, ...options.ancestorStyle };
  if (options.invisible) button.style.opacity = '0';
  const field = makeNode('INPUT');
  const foreign = makeNode('INPUT');
  document.querySelectorAll = selector => selector === '#choose' ? [button]
    : selector === '#archive' ? options.duplicateInput ? [field, foreign] : options.missingInput ? [] : [field] : [];
  document.elementFromPoint = () => options.occluded ? foreign : button;
  if (options.inputType) field.type = options.inputType;
  if (options.disabledInput) field.disabled = true;
  if (options.directoryInput) field.webkitdirectory = true;
  if (options.singleInput) field.multiple = false;
  if (options.disabledButton) button.disabled = true;
  const chooser = {
    page: () => options.foreignPage ? {} : page,
    element: () => options.wrongInput ? foreign : field,
    async setFiles(files, settings) {
      calls.push('setFiles');
      if (options.selectionError) throw new Error('private path /unreviewed/account.zip and raw bytes');
      page.selected = files;
      page.selectionTimeout = settings.timeout;
      field.files = []; // Product handlers may clear the input immediately.
    },
  };
  const page = {
    selected: null,
    async evaluate(fn, arg) {
      calls.push('evaluate');
      if (options.evaluateError) throw new Error('/private/unreviewed/file.zip');
      if (arg.selector && options.disableAfterClick) field.disabled = true;
      return vm.runInNewContext('(' + fn.toString() + ')', { document,
        getComputedStyle: node => node.style })(arg);
    },
    waitForEvent(name, { timeout }) {
      assert.equal(name, 'filechooser');
      assert.ok(timeout >= 1 && timeout <= UPLOAD_LIMITS.timeoutMs);
      calls.push('listen');
      return new Promise((resolve, reject) => {
        const timer = setTimeout(() => { pending = null; calls.push('listener_removed'); reject(new Error('/private/chooser-timeout')); }, timeout);
        pending = () => { clearTimeout(timer); pending = null; calls.push('listener_removed'); resolve(chooser); };
      });
    },
  };
  const click = async () => {
    calls.push('click');
    if (options.clickError) throw new Error('/private/click-error');
    if (!options.noChooser) pending();
  };
  page.mouse = { click };
  page.touchscreen = { tap: click };
  return { page, calls, click, field, button, hasListener: () => pending !== null };
}

function makeSession(ownedUploads, options = {}) {
  const scenario = normalizeScenario({ schema_version: 'ergo-scenario.v1', scenario_id: 'mock-owned-upload',
    surface: { kind: 'web', url: 'https://remorsearch.invalid/index.html' }, steps: [action()] }, { requireSteps: true }).scenario;
  const session = new WebSession({ scenario, runId: 'mock-pure-test', options: { visualFeedback: false,
    feedbackTimeoutMs: 0, flashSampleMs: 0, settleMs: 0, ...options }, ownedUploads });
  session.pointerMode = () => 'mouse';
  session.probeFrames = async () => {};
  session.firstMutation = async () => null;
  session.countMutations = async () => 0;
  return session;
}

test('rejects paths, URLs, buffers, duplicate IDs, ambiguous selectors and unbounded waits in actions', () => {
  const invalid = [
    { files: [] }, { files: Array.from({ length: 17 }, (_, i) => 'fixture-' + i) },
    { files: ['fixture-previous', 'fixture-previous'] }, { files: ['/private/export.zip'] },
    { files: ['https://example.invalid/export.zip'] }, { files: [Buffer.from('unreviewed')] },
    { input: 'input[type="file"]' }, { input: 'hotspot:archive' },
    { target: { x: 5, y: 5 } }, { target: 'hotspot:choose' },
    { timeout_ms: 0 }, { timeout_ms: 0.5 }, { timeout_ms: 5001 }, { timeout_ms: Infinity },
  ];
  for (const change of invalid) assert.throws(() => normalizeAction({ ...action(), ...change }, { strict: true }));
  for (const strict of [true, false]) {
    assert.throws(() => normalizeAction({ ...action(), path: '/private/ignored.zip' }, { strict }));
    assert.throws(() => normalizeAction({ ...action(), buffer: 'unreviewed' }, { strict }));
    assert.throws(() => normalizeAction({ ...action(), '/private/export.zip': true }, { strict }),
      error => error.message.includes('unsupported upload field') && !error.message.includes('/private'));
  }
});

test('copies bound bytes and exposes only exact file-selection metadata', () => {
  const owned = registry();
  const original = owned.get('fixture-previous');
  const prepared = prepareOwnedUpload(action(), owned);
  original.buffer.fill(0);
  assert.equal(sha256(prepared.files[0].buffer), original.sha256);
  assert.deepEqual(prepared.evidence, { method: 'playwright_filechooser', input: '#archive', files: [{
    id: 'fixture-previous', name: original.name, mime_type: 'application/zip',
    size_bytes: original.buffer.length, sha256: original.sha256 }] });
  assert.doesNotMatch(JSON.stringify(prepared.evidence), /buffer|Buffer|private\/|raw bytes/);
});

test('refuses missing, unbound, malformed or changed registry entries before any page interaction', async () => {
  const mutations = [
    e => { e.name = '/private/export.zip'; }, e => { e.name = '..'; }, e => { e.name = 'a\\b.zip'; },
    e => { e.mimeType = 'application/zip; source=private'; }, e => { e.path = '/private/export.zip'; },
    e => { e.buffer = new Uint8Array(2); }, e => { e.sha256 = 'f'.repeat(64); },
    e => { e.buffer[0] ^= 1; },
  ];
  const cases = [undefined, {}, new Map(), ...mutations.map(mutate => { const e = entry(); mutate(e); return new Map([['fixture-previous', e]]); })];
  for (const owned of cases) {
    const fake = fakePage();
    await assert.rejects(chooseOwnedFiles({ ...fake, action: action(), registry: owned, point }), error => {
      assert.match(error.message, /^upload_/); assert.doesNotMatch(error.message, /private|raw bytes/); return true;
    });
    assert.deepEqual(fake.calls, []);
  }
});

test('enforces per-file and total byte limits without invoking the browser', () => {
  assert.throws(() => prepareOwnedUpload(action(), new Map([['fixture-previous', entry(Buffer.alloc(UPLOAD_LIMITS.fileBytes + 1))]])), /upload_file_bytes_exceeded/);
  const large = entry(Buffer.alloc(UPLOAD_LIMITS.fileBytes));
  const owned = new Map([['a', large], ['b', large], ['c', entry(Buffer.from('x'))]]);
  assert.throws(() => prepareOwnedUpload({ ...action(), files: ['a', 'b', 'c'] }, owned), /upload_total_bytes_exceeded/);
  const prepared = prepareOwnedUpload({ ...action(), files: ['a', 'b'] }, owned);
  assert.equal(prepared.evidence.files.reduce((sum, item) => sum + item.size_bytes, 0), UPLOAD_LIMITS.totalBytes);
});

test('arms the chooser before a real dispatch callback and transfers only the reviewed payload', async () => {
  const fake = fakePage();
  const owned = registry();
  const evidence = await chooseOwnedFiles({ ...fake, action: action(), registry: owned, point });
  assert.ok(fake.calls.indexOf('listen') < fake.calls.indexOf('click'));
  assert.ok(fake.calls.indexOf('click') < fake.calls.indexOf('setFiles'));
  assert.equal(fake.page.selected.length, 1);
  assert.deepEqual(Object.keys(fake.page.selected[0]).sort(), ['buffer', 'mimeType', 'name']);
  assert.equal(sha256(fake.page.selected[0].buffer), owned.get('fixture-previous').sha256);
  assert.ok(fake.page.selectionTimeout >= 1 && fake.page.selectionTimeout <= 100);
  assert.equal(evidence.files[0].id, 'fixture-previous');
  assert.deepEqual(fake.field.files, [], 'input reset after selection is not mistaken for a failed transfer');
  assert.equal(fake.hasListener(), false);
  assert.equal(fake.calls.at(-1), 'dispose');
});

test('refuses hidden, covered or disabled click controls and invalid file inputs before clicking', async () => {
  for (const options of [{ invisible: true }, { occluded: true }, { disabledButton: true },
    { inputType: 'text' }, { disabledInput: true }, { directoryInput: true },
    { missingInput: true }, { duplicateInput: true }]) {
    const fake = fakePage(options);
    await assert.rejects(chooseOwnedFiles({ ...fake, action: action(), registry: registry(), point }), /upload_(target|input)_invalid/);
    assert.equal(fake.calls.includes('click'), false);
    assert.equal(fake.calls.includes('listen'), false);
  }
  const fake = fakePage({ singleInput: true });
  await assert.rejects(chooseOwnedFiles({ ...fake, action: { ...action(), files: ['a', 'b'] },
    registry: new Map([['a', entry()], ['b', entry()]]), point }), /upload_input_invalid/);
});

test('refuses a foreign chooser, another input, or an input disabled after activation', async () => {
  for (const options of [{ foreignPage: true }, { wrongInput: true }, { disableAfterClick: true }]) {
    const fake = fakePage(options);
    await assert.rejects(chooseOwnedFiles({ ...fake, action: action(), registry: registry(), point }), /upload_chooser_input_mismatch/);
    assert.equal(fake.calls.includes('click'), true);
    assert.equal(fake.calls.includes('setFiles'), false);
    assert.equal(fake.hasListener(), false);
  }
});

test('an invisible ancestor cannot activate upload even when the button receives hit tests', async () => {
  for (const options of [{ ancestorStyle: { opacity: '0' } }, { ancestorStyle: { display: 'none' } },
    { ancestorStyle: { visibility: 'hidden' } }, { ancestorHidden: true }, { visibilityCheck: false }]) {
    const fake = fakePage(options);
    await assert.rejects(chooseOwnedFiles({ ...fake, action: action(), registry: registry(), point }), /upload_target_invalid/);
    assert.equal(fake.calls.includes('listen'), false);
    assert.equal(fake.calls.includes('click'), false);
    assert.equal(fake.page.selected, null);
  }
});

test('a missing chooser times out without file transfer or a retained listener', async () => {
  const fake = fakePage({ noChooser: true });
  await assert.rejects(chooseOwnedFiles({ ...fake, action: { ...action(), timeout_ms: 10 }, registry: registry(), point }), /upload_chooser_timeout/);
  assert.equal(fake.page.selected, null);
  assert.equal(fake.hasListener(), false);
});

test('click, DOM and selection failures report fixed codes without private Playwright errors', async () => {
  for (const [options, code] of [[{ clickError: true }, 'upload_click_failed'],
    [{ evaluateError: true }, 'upload_controls_unavailable'], [{ selectionError: true }, 'upload_selection_failed']]) {
    const fake = fakePage(options);
    await assert.rejects(chooseOwnedFiles({ ...fake, action: { ...action(), timeout_ms: 10 }, registry: registry(), point }),
      error => error.message === code);
    assert.equal(fake.page.selected, null);
    assert.equal(fake.hasListener(), false);
  }
});

test('ordinary WebSession cannot use an action or options object as an upload registry', async () => {
  const session = makeSession(undefined, { ownedUploads: registry() });
  const fake = fakePage(); session.page = fake.page;
  await assert.rejects(session.dispatchInput(action(), { point }), /upload_registry_required/);
  assert.deepEqual(fake.calls, []);
});

test('native input records metadata through performInput while preserving existing redaction', async () => {
  const owned = registry();
  const session = makeSession(owned);
  const fake = fakePage(); session.page = fake.page;
  session.privateValues.add(owned.get('fixture-previous').name);
  const step = { step_index: 1, point: { ...point } };
  await session.performInput(action(), { point }, step);
  assert.equal(step.input, 'mouse+filechooser');
  assert.equal(step.file_selection.method, 'playwright_filechooser');
  assert.equal(step.end_point, undefined, 'upload metadata must not be treated as a gesture');
  const published = session.redactRecord(step);
  assert.equal(published.file_selection.files[0].name, '[redacted]');
  assert.equal(published.file_selection.files[0].id, 'fixture-previous');
  assert.equal(published.file_selection.files[0].sha256, owned.get('fixture-previous').sha256);
  assert.doesNotMatch(JSON.stringify(published), /buffer|Buffer|synthetic-previous|raw bytes/);
  assert.equal(Object.hasOwn(session.opts, 'ownedUploads'), false);
});

test('accepts explicit whitespace normalization on a text task check', () => {
  const { scenario } = normalizeScenario({ schema_version: 'ergo-scenario.v1', scenario_id: 'text-normalization',
    surface: { kind: 'web', url: 'https://remorsearch.invalid/index.html' }, steps: [{ action: 'snapshot' }],
    success: { task_checks: [{ id: 'text', selector: '#result', property: 'text', expected: '읽은 결과',
      after_step: 1, normalize_whitespace: true, severity: 'P1', consequence: 'Understand the result.' }] } }, { requireSteps: true });
  assert.equal(scenario.success.task_checks[0].normalize_whitespace, true);
});

test('accepts sixteen owned files needed by a reviewed multi-file export', () => {
  const authored = { ...action(), files: Array.from({ length: 16 }, (_, index) => 'fixture-' + index) };
  assert.deepEqual(normalizeAction(authored, { strict: true }).action.files, authored.files);
  const owned = new Map(authored.files.map(id => [id, entry()]));
  assert.equal(prepareOwnedUpload(authored, owned).evidence.files.length, 16);
});

function taskDocument(check) {
  return { schema_version: 'ergo-scenario.v1', scenario_id: 'text-unit',
    surface: { kind: 'web', url: 'https://remorsearch.invalid/index.html' },
    steps: [{ action: 'type', target: '#request', text: '  읽은\u00a0결과\n 확인  ' }],
    success: { task_checks: [{ id: 'text', selector: '#result', property: 'text', after_step: 1,
      expected: '읽은 결과 확인', severity: 'P1', consequence: 'Understand the result.', ...check }] } };
}

function fakeTextSession(actual, change = {}, afterActual = actual) {
  const doc = taskDocument(change);
  if ('from_step' in change) delete doc.success.task_checks[0].expected;
  const { scenario } = normalizeScenario(doc, { requireSteps: true });
  const session = new WebSession({ scenario, runId: 'pure-text-unit', options: {} });
  const samples = [];
  const element = { id: 'result', localName: 'p', innerText: actual, parentElement: null,
    matches: () => false, closest: () => null, querySelector: () => null, getAttribute: () => null,
    getClientRects: () => [{}], checkVisibility: () => true };
  const document = { querySelectorAll: () => [element] };
  session.page = {
    isClosed: () => false,
    async evaluateHandle(fn, arg) {
      element.innerText = samples.length ? afterActual : actual;
      const window = { [Symbol.for(arg.key)]: { ids: new Map([[element, 'E-result']]) } };
      const value = vm.runInNewContext('(' + fn.toString() + ')', { document, window,
        getComputedStyle: () => ({ display: 'block', visibility: 'visible', opacity: '1' }) })(arg);
      samples.push(value);
      return { value, async dispose() {}, async evaluate(evaluate, first) { return evaluate(value, first.value); } };
    },
  };
  session.authoredInputs.add(1);
  return { session, samples, element };
}

async function evaluateText(fake) {
  const before = await fake.session.sampleTaskChecks(1, 'ok');
  await fake.session.evaluateTaskChecks(1, { id: 'S-unit-1', snap: { step_index: 1 } }, 'ok', before);
  return fake.session.taskCheckResults.get('text');
}

test('whitespace option is a boolean restricted to text checks', () => {
  for (const property of ['value', 'checked']) for (const normalize_whitespace of [true, false]) {
    assert.throws(() => normalizeScenario(taskDocument({ property, expected: property === 'checked' ? true : 'x',
      normalize_whitespace }), { requireSteps: true }), /available only for text checks/);
  }
  for (const value of [1, 'true', null, []]) {
    assert.throws(() => normalizeScenario(taskDocument({ normalize_whitespace: value }),
      { requireSteps: true }), /normalize_whitespace/);
  }
});

test('whitespace normalization compares both strings only when explicitly enabled', async () => {
  const actual = '\n 읽은\u00a0결과\n\t확인  ';
  for (const enabled of [undefined, false, true]) {
    const options = enabled === undefined ? {} : { normalize_whitespace: enabled };
    const fake = fakeTextSession(actual, { expected: '  읽은  결과\t확인\n', ...options });
    const result = await evaluateText(fake);
    assert.equal(result.passed, enabled === true);
    assert.equal(Object.hasOwn(result, 'normalize_whitespace'), enabled !== undefined);
    if (enabled !== undefined) assert.equal(result.normalize_whitespace, enabled);
    assert.equal(fake.samples[0].private_actual, actual);
    assert.equal(fake.samples[1].private_actual, actual);
    assert.equal(fake.element.innerText, actual, 'normalization never mutates the observed text');
    assert.equal(Object.hasOwn(result, 'private_actual'), false);
  }
});

test('whitespace normalization does not hide missing words, punctuation or casing', async () => {
  for (const actual of ['읽은 결과', '읽은 결과 확인!', 'Read Result', '읽은결과 확인']) {
    const result = await evaluateText(fakeTextSession(actual, { normalize_whitespace: true }));
    assert.equal(result.result, 'fail');
  }
});

test('text checks may normalize an authored type source without changing source matching', async () => {
  const fake = fakeTextSession('읽은 결과 확인', { from_step: 1, normalize_whitespace: true });
  const result = await evaluateText(fake);
  assert.equal(result.result, 'pass');
  assert.equal(result.normalize_whitespace, true);
  const changedSource = fakeTextSession('읽은 결과 확인', { from_step: 1, normalize_whitespace: true });
  changedSource.session.mismatchedInputs.add(1);
  assert.equal((await evaluateText(changedSource)).reason, 'source_input_mismatch');
});

test('raw text changes across a capture remain unevaluable despite normalized equivalence', async () => {
  const fake = fakeTextSession('읽은\u00a0결과 확인', { normalize_whitespace: true }, '읽은 결과 확인');
  const result = await evaluateText(fake);
  assert.equal(result.result, 'unevaluable');
  assert.equal(result.reason, 'capture_state_changed');
  assert.equal(result.passed, null);
});

test('unvisited normalized checkpoints preserve the flag without inventing a pass', async () => {
  const fake = fakeTextSession('읽은 결과 확인', { normalize_whitespace: true });
  const result = await fake.session.evaluateSuccess();
  assert.equal(result.success, null);
  assert.equal(result.detail.criteria[0].reason, 'checkpoint_unvisited');
  assert.equal(result.detail.criteria[0].normalize_whitespace, true);
});
