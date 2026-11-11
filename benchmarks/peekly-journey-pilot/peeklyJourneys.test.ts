/** Actual copied Peekly core calls; owned adapters are not a browser or App execution. */
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { expect, test, vi } from 'vitest';
import { strFromU8, strToU8, unzipSync, zipSync } from 'fflate';
import type { AccountSnapshot, ParsedInstagramExport } from '../src/types/instagram';
import type { PersistedAppState } from '../src/storage/snapshotStore';

interface Task {
  id: string;
  success_criteria: string[];
  recovery_criteria: string[];
  expected?: Record<string, number>;
}
interface Protocol { id: string; fixed_now: string; tasks: Task[]; bounds: { case_timeout_seconds: number }; }
interface Check { kind: 'success' | 'recovery'; index: number; passed: boolean; observation: string; }
const protocol = JSON.parse(readFileSync(new URL('./protocol.json', import.meta.url), 'utf8')) as Protocol;
const task = protocol.tasks.find((row) => row.id === process.env.PEEKLY_PILOT_TASK);
const destination = process.env.PEEKLY_PILOT_OBSERVATIONS;
const root = fileURLToPath(new URL('../', import.meta.url));
if (!task || !destination || !readFileSync(root + '.remorsearch-owned-copy.json', 'utf8')) {
  throw new Error('An explicit owned copy, frozen task and observation path are required');
}
const selectedTask: Task = task;
const output: string = destination;
vi.useFakeTimers({ toFake: ['Date'] });
vi.setSystemTime(new Date(protocol.fixed_now));
const now = Date.now();
const sample = await import('../src/core/sampleData');
const parser = await import('../src/core/zipParser');
const validation = await import('../src/core/importValidation');
const diff = await import('../src/core/diffEngine');
const folder = await import('../src/core/exportFolderSync');
let storage = await import('../src/storage/snapshotStore');

class OwnedStorage {
  data = new Map<string, string>();
  quotaFailure = false;
  readFailure = false;
  writes: number[] = [];
  getItem(key: string): string | null {
    if (this.readFailure) throw new Error('Owned storage read failure');
    return this.data.get(key) ?? null;
  }
  setItem(key: string, value: string): void {
    if (key === 'peekly_state_v6') this.writes.push((JSON.parse(value) as PersistedAppState).snapshots.length);
    if (this.quotaFailure) {
      const error = new Error('Owned quota failure');
      error.name = 'QuotaExceededError';
      throw error;
    }
    this.data.set(key, value);
  }
  removeItem(key: string): void { this.data.delete(key); }
  raw(): string { return this.data.get('peekly_state_v6') ?? ''; }
}
const owned = new OwnedStorage();
vi.stubGlobal('window', { localStorage: owned });
const hash = (raw: string | Uint8Array): string => createHash('sha256').update(raw).digest('hex');
const checks: Check[] = [];
const facts: Record<string, unknown> = {};
const steps: Array<{ action: string; observation: string }> = [];
function check(kind: Check['kind'], index: number, passed: boolean, observation: string): void {
  checks.push({ kind, index, passed, observation });
}
function step(action: string, observation: string): void { steps.push({ action, observation }); }
function errorInfo(error: unknown): Record<string, string> {
  const value = error instanceof Error ? error : new Error('Non-Error failure');
  const shaped = value as Error & { fileName?: string };
  return { name: value.name, message: value.message.replaceAll(root, '<owned-product>/'),
    ...(shaped.fileName ? { file: shaped.fileName.split('/').at(-1) ?? 'unknown' } : {}) };
}
// Host construction mirrors App.tsx snapshotFromParsed's field mapping.
// The App callback, React effects and native storage are deliberately not executed.
function snapshot(parsed: ParsedInstagramExport, id: string, createdAt: number, isSample = false): AccountSnapshot {
  return {
    id, label: 'Owned synthetic record', createdAt, isSample,
    accountHandle: parsed.accountHandle ?? '', includedFiles: parsed.detectedFileTypes,
    followers: parsed.followers, following: parsed.following,
    pendingFollowRequests: parsed.pendingFollowRequests, recentlyUnfollowed: parsed.recentlyUnfollowed,
    closeFriends: parsed.closeFriends, blockedProfiles: parsed.blockedProfiles,
    restrictedProfiles: parsed.restrictedProfiles, hideStoryFrom: parsed.hideStoryFrom,
    likesGivenByAuthor: parsed.likesGivenByAuthor, commentsGivenByAuthor: parsed.commentsGivenByAuthor,
  };
}
function baseline(isSample = false): PersistedAppState {
  const previous = snapshot(parser.parseInstagramZipArchive(sample.buildSampleExportZip('previous')),
    'owned-previous', now - sample.SAMPLE_PREVIOUS_AGE_DAYS * 86400000, isSample);
  const current = snapshot(parser.parseInstagramZipArchive(sample.buildSampleExportZip('current')),
    'owned-current', now, isSample);
  return { ...storage.getDefaultAppState(), snapshots: [previous, current],
    activeSnapshotId: current.id, comparisonSnapshotId: previous.id };
}
function persist(state: PersistedAppState): void {
  const result = storage.savePersistedState(state);
  if (result.status !== 'saved') throw new Error('Owned baseline could not be prepared');
}
async function freshStorage(): Promise<typeof storage> {
  vi.resetModules();
  return import('../src/storage/snapshotStore');
}
function looseFiles(entries: Record<string, Uint8Array>): Array<{ name: string; text: string }> {
  return Object.entries(entries).map(([name, bytes]) => ({ name, text: strFromU8(bytes) }));
}
function tryParse(run: () => ParsedInstagramExport): { parsed: ParsedInstagramExport | null; error: Record<string, string> | null } {
  try { return { parsed: run(), error: null }; }
  catch (error) { return { parsed: null, error: errorInfo(error) }; }
}
async function sampleJourney(): Promise<void> {
  const state = baseline(true);
  const [previous, current] = state.snapshots;
  const expected = selectedTask.expected!;
  const counts = { previous_followers: previous.followers.length, previous_following: previous.following.length,
    current_followers: current.followers.length, current_following: current.following.length };
  facts.counts = counts;
  check('success', 0, Object.entries(counts).every(([key, value]) => expected[key] === value),
    'Both built-in ZIPs were read by the copied product parser; exact list counts were compared.');
  step('Parse the product previous and current sample ZIPs', 'Both resulting snapshots were retained for comparison.');
  const matrix = diff.classifyRelationshipMatrix(current, [previous], new Set(), {}, now);
  const departures = diff.detectDisappearances(previous, current);
  const oldNames = new Set(previous.followers.map((row) => row.username));
  const analysis = { mutual: matrix.filter((row) => row.quadrant === 'MUTUAL').length,
    nonreciprocal_following: matrix.filter((row) => ['BETRAYED_MUTUAL', 'ONE_WAY_FOLLOWING'].includes(row.quadrant)).length,
    fan_only: matrix.filter((row) => row.quadrant === 'FAN_ONLY').length,
    departures: departures.length,
    new_followers: current.followers.filter((row) => !oldNames.has(row.username)).length };
  facts.analysis = analysis;
  facts.departure_labels = [...new Set(departures.map((row) => diff.describeDeparture(row).label))];
  check('success', 1, Object.entries(analysis).every(([key, value]) => expected[key] === value),
    'The actual comparison helpers produced the frozen aggregate counts.');
  persist(state);
  const reloaded = (await freshStorage()).loadPersistedState();
  check('recovery', 0, reloaded.snapshots.length === 2 && reloaded.activeSnapshotId === current.id &&
    reloaded.comparisonSnapshotId === previous.id && reloaded.snapshots.every((row) => row.isSample),
    'A fresh storage-module load retained both owned sample records and their comparison selection.');
  step('Persist then reload through a fresh product storage module', 'Two records and the selected comparison survived.');
}
async function recoverJourney(): Promise<void> {
  const state = baseline(); persist(state);
  const progress = { step: 'waiting' as const, requestedAt: now - 3600000 };
  storage.saveOnboardingProgress(progress);
  const fresh = await freshStorage();
  check('success', 0, JSON.stringify(fresh.loadOnboardingProgress()) === JSON.stringify(progress),
    'A fresh module recovered the saved waiting stage and request time; visible resume guidance was not observed.');
  const before = owned.raw();
  const entries = unzipSync(sample.buildSampleExportZip('current'));
  const followerPath = Object.keys(entries).find((name) => name.endsWith('/followers_1.json'))!;
  const followingPath = Object.keys(entries).find((name) => name.endsWith('/following.json'))!;
  const broken = { ...entries, [followerPath]: strToU8('{ invalid owned JSON') };
  const malformed = tryParse(() => parser.parseInstagramZipArchive(zipSync(broken)));
  const missing = { ...entries }; delete missing[followingPath];
  const missingParsed = parser.parseInstagramZipArchive(zipSync(missing));
  const missingCheck = validation.checkParsedExport(missingParsed, null, sample.SAMPLE_ACCOUNT_HANDLE);
  const current = parser.parseInstagramZipArchive(sample.buildSampleExportZip('current'));
  const different = validation.checkParsedExport({ ...current, accountHandle: 'owned_other_fixture' }, null, sample.SAMPLE_ACCOUNT_HANDLE);
  facts.invalid_inputs = { malformed: malformed.error, missing_rejected: !missingCheck.ok,
    different_owner_rejected: !different.ok, stored_bytes_unchanged: owned.raw() === before };
  check('success', 1, malformed.error?.name === 'InstagramExportFormatError' && !missingCheck.ok && !different.ok,
    'Malformed JSON, a missing following list and a different owned identity were refused by actual core checks.');
  step('Try three invalid owned inputs', 'Each rejection was inspected without replacing the saved comparison.');
  const valid = validation.checkParsedExport(current, null, sample.SAMPLE_ACCOUNT_HANDLE);
  check('recovery', 0, owned.raw() === before && valid.ok && current.followers.length === 7,
    'Previously stored bytes stayed identical and the original valid current ZIP was accepted afterward.');
  facts.state_sha256_before = hash(before); facts.state_sha256_after = hash(owned.raw());
  step('Retry the unmodified current sample', 'The actual parser and admission helper accepted the valid sample.');
}
function expanded(rows: number): { archive: Uint8Array; files: Array<{ name: string; text: string }>; sizes: Record<string, number> } {
  const entries = unzipSync(sample.buildSampleExportZip('current'));
  const users = Array.from({ length: rows }, (_, index) => ({
    string_list_data: [{ value: 'owned_fixture_' + String(index).padStart(6, '0'), timestamp: 1700000000 }],
  }));
  const followerPath = Object.keys(entries).find((name) => name.endsWith('/followers_1.json'))!;
  const followingPath = Object.keys(entries).find((name) => name.endsWith('/following.json'))!;
  entries[followerPath] = strToU8(JSON.stringify(users));
  entries[followingPath] = strToU8(JSON.stringify({ relationships_following: users }));
  const sizes: Record<string, number> = {};
  for (const [name, bytes] of Object.entries(entries)) sizes[name] = bytes.length;
  return { archive: zipSync(entries, { level: 1 }), files: looseFiles(entries), sizes };
}
async function largeJourney(): Promise<void> {
  const state = baseline(); persist(state); const before = owned.raw();
  const expected = selectedTask.expected!;
  const control = expanded(expected.control_rows);
  const smallZip = tryParse(() => parser.parseInstagramZipArchive(control.archive));
  const smallJson = tryParse(() => parser.parseInstagramJsonFiles(control.files));
  const rightCounts = (p: ParsedInstagramExport | null, rows: number): boolean =>
    p?.followers.length === rows && p.following.length === rows;
  check('success', 0, rightCounts(smallZip.parsed, expected.control_rows) && rightCounts(smallJson.parsed, expected.control_rows),
    'The fixed smaller control was checked through both actual ZIP and loose-JSON product entry points.');
  const large = expanded(expected.large_rows);
  const bytes = Object.values(large.sizes);
  const total = bytes.reduce((sum, value) => sum + value, 0);
  const largest = bytes.reduce((max, value) => Math.max(max, value), 0);
  const bounded = large.archive.length <= expected.max_archive_bytes && largest <= expected.max_file_bytes && total <= expected.max_total_bytes;
  if (!bounded) throw new Error('Generated fixture exceeds frozen byte limits');
  const zipResult = tryParse(() => parser.parseInstagramZipArchive(large.archive));
  const jsonResult = tryParse(() => parser.parseInstagramJsonFiles(large.files));
  const follower = large.files.find((row) => row.name.endsWith('/followers_1.json'))!;
  const standalone = parser.parseInstagramJsonFile(follower.name, follower.text);
  facts.large = { rows_per_list: expected.large_rows, archive_bytes: large.archive.length, largest_file_bytes: largest,
    total_file_bytes: total, archive_sha256: hash(large.archive), within_documented_limits: bounded,
    zip_error: zipResult.error, json_error: jsonResult.error, standalone_followers_rows: standalone.users.length };
  check('success', 1, rightCounts(zipResult.parsed, expected.large_rows) && rightCounts(jsonResult.parsed, expected.large_rows),
    'The fixed larger input was submitted unchanged to both real parser entry points; returned counts or errors were retained.');
  const recovered = parser.parseInstagramZipArchive(sample.buildSampleExportZip('current'));
  check('recovery', 0, owned.raw() === before && recovered.followers.length === 7 && recovered.following.length === 10,
    'Stored comparison bytes remained intact and the original small sample was readable after the larger attempt.');
  facts.state_sha256_before = hash(before); facts.state_sha256_after = hash(owned.raw());
  step('Import fixed control and larger owned exports', 'Documented byte bounds and actual parser outcomes were recorded.');
  step('Recover with the original current ZIP', 'The earlier comparison and the small-input recovery were checked separately.');
}
async function storageJourney(): Promise<void> {
  const state = baseline(); persist(state); const before = owned.raw();
  const candidate = { ...state, snapshots: [...state.snapshots,
    { ...state.snapshots[1], id: 'owned-next', createdAt: now + 1000 }] };
  owned.writes = []; owned.quotaFailure = true;
  const failed = storage.saveImportedState(candidate);
  const attempted = owned.writes.slice();
  check('success', 0, failed.outcome.status === 'failed' && owned.raw() === before && JSON.stringify(attempted) === '[3,2]',
    'The real imported-state saver refused both failed writes, stopped at two records and preserved committed bytes.');
  owned.quotaFailure = false; owned.readFailure = true;
  let readFailures = 0;
  (await freshStorage()).loadPersistedState(() => { readFailures += 1; });
  check('success', 1, readFailures === 1 && owned.raw() === before,
    'A fresh read reported the injected storage error through its callback and did not replace committed bytes.');
  owned.readFailure = false;
  const retried = storage.saveImportedState(candidate);
  const reloaded = (await freshStorage()).loadPersistedState();
  check('recovery', 0, retried.outcome.status === 'saved' && reloaded.snapshots.length === 3 &&
    reloaded.activeSnapshotId === 'owned-next' && reloaded.comparisonSnapshotId === 'owned-current',
    'The same candidate saved after recovery and a fresh load retained the expected three records and selection.');
  facts.storage = { write_outcome: failed.outcome.status, attempted_history_sizes: attempted, read_failure_callbacks: readFailures,
    retry_outcome: retried.outcome.status, reloaded_records: reloaded.snapshots.length };
  step('Inject owned quota and read failures', 'Actual failure outcomes and preservation were checked.');
  step('Remove the injected failure and explicitly retry', 'Fresh loading confirmed the same candidate was committed.');
}
async function folderJourney(): Promise<void> {
  const state = baseline(); persist(state);
  const day = (value: string): number => new Date(value + 'T00:00:00+09:00').getTime();
  const oldAt = day('2026-11-10'), currentAt = day('2026-11-11'), nextAt = day('2026-11-12');
  const entries = unzipSync(sample.buildSampleExportZip('current'));
  const zip = sample.buildSampleExportZip('current');
  const listing = [{ path: 'owned-2026-11-10.zip', size: zip.length, modifiedAt: oldAt },
    { path: 'owned-2026-11-11.zip', size: zip.length, modifiedAt: currentAt }];
  const selected = folder.chooseFolderExport(listing, 'owned', oldAt, []);
  if (selected.status !== 'import') throw new Error('Cannot prepare selected folder candidate');
  const parsed = parser.parseInstagramZipArchive(zip);
  const candidate = snapshot(parsed, 'owned-folder-current', currentAt);
  candidate.exportedAt = selected.run.time;
  candidate.folderImport = { signature: selected.run.signature, fileName: selected.run.name };
  const saved = storage.saveImportedState({ ...state, snapshots: [state.snapshots[0], candidate] });
  if (saved.outcome.status !== 'saved') throw new Error('Owned folder baseline did not save');
  const restarted = (await freshStorage()).loadPersistedState();
  const persisted = restarted.snapshots.at(-1)!;
  const signatures = restarted.snapshots.flatMap((row) => row.folderImport ? [row.folderImport.signature] : []);
  const repeated = folder.chooseFolderExport(listing, 'owned', persisted.exportedAt ?? persisted.createdAt, signatures);
  const older = folder.chooseFolderExport([listing[0]], 'owned', currentAt, signatures);
  check('success', 0, selected.run.time === currentAt && repeated.status === 'current' && older.status === 'current',
    'Latest complete selection was persisted; the real selector skipped the repeated signature and older export after fresh loading.');
  const followerPath = Object.keys(entries).find((name) => name.endsWith('/followers_1.json'))!;
  const followingPath = Object.keys(entries).find((name) => name.endsWith('/following.json'))!;
  const prefix = 'owned-2026-11-12/';
  const partial = [...listing, { path: prefix + followerPath, size: entries[followerPath].length, modifiedAt: nextAt }];
  const incomplete = folder.chooseFolderExport(partial, 'owned', currentAt, signatures);
  check('success', 1, incomplete.status === 'incomplete',
    'The newest incomplete group was reported instead of silently choosing an older complete export.');
  const complete = [...partial, { path: prefix + followingPath, size: entries[followingPath].length, modifiedAt: nextAt }];
  const recovered = folder.chooseFolderExport(complete, 'owned', currentAt, signatures);
  const parsedAgain = parser.parseInstagramJsonFiles(looseFiles(entries));
  const accepted = validation.checkParsedExport(parsedAgain, null, sample.SAMPLE_ACCOUNT_HANDLE);
  let recoveredAndDeduped = false;
  if (recovered.status === 'import' && accepted.ok) {
    const next = snapshot(parsedAgain, 'owned-folder-next', nextAt);
    next.exportedAt = recovered.run.time;
    next.folderImport = { signature: recovered.run.signature, fileName: recovered.run.name };
    const stored = storage.saveImportedState({ ...restarted, snapshots: [...restarted.snapshots, next] });
    const final = (await freshStorage()).loadPersistedState();
    const finalSignatures = final.snapshots.flatMap((row) => row.folderImport ? [row.folderImport.signature] : []);
    recoveredAndDeduped = stored.outcome.status === 'saved' &&
      folder.chooseFolderExport(complete, 'owned', nextAt, finalSignatures).status === 'current';
  }
  check('recovery', 0, recoveredAndDeduped,
    'Completing the owned listing allowed real parsing/admission/storage and the persisted signature prevented a second import.');
  facts.folder = { first: selected.status, repeated: repeated.status, older: older.status,
    newest_partial: incomplete.status, repaired: recovered.status, stored_and_deduplicated: recoveredAndDeduped };
  step('Select, store, reload and recheck the owned export list', 'Repeated and stale candidates were checked against persisted metadata.');
  step('Complete a newer partial owned export', 'Recovery and subsequent deduplication were evaluated with the product helpers.');
}
const journeys: Record<string, () => Promise<void>> = {
  'T-SAMPLE': sampleJourney, 'T-RECOVER': recoverJourney, 'T-LARGE': largeJourney,
  'T-STORAGE': storageJourney, 'T-FOLDER': folderJourney,
};
test(selectedTask.id + ' frozen product goal', async () => {
  const started = performance.now();
  let harnessError: Record<string, string> | null = null;
  try { await journeys[selectedTask.id](); }
  catch (error) { harnessError = errorInfo(error); }
  const complete = checks.length === selectedTask.success_criteria.length + selectedTask.recovery_criteria.length;
  const result = {
    schema_version: 'peekly-core-observation.v1', task_id: selectedTask.id, protocol_id: protocol.id,
    scope: 'actual_product_core_owned_adapter', ui_observed: false, real_user_evidence: false,
    elapsed_seconds: (performance.now() - started) / 1000, scenario_time: protocol.fixed_now,
    process_id: process.pid, checks, steps, facts, harness_error: harnessError,
    core_goal_passed: !harnessError && complete && checks.every((row) => row.passed),
  };
  writeFileSync(output, JSON.stringify(result, null, 2) + '\n', { mode: 0o600 });
  vi.useRealTimers();
  vi.unstubAllGlobals();
  expect(harnessError, 'Harness errors are not product findings').toBeNull();
  expect(complete, 'Every frozen criterion must be evaluated').toBe(true);
  expect(result.core_goal_passed, 'Frozen product goal was not fulfilled; retain observation log').toBe(true);
}, protocol.bounds.case_timeout_seconds * 1000);
