#!/usr/bin/env node
/**
 * Deterministic synthetic inputs, not a product or browser experiment.
 * Run with the copied build dependencies under an externally applied network-deny sandbox.
 */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { createReadStream, constants } from 'node:fs';
import * as fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const modulePath = fileURLToPath(import.meta.url);
const protocolPath = fileURLToPath(new URL('./protocol.json', import.meta.url));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const bytes = (value) => Buffer.from(JSON.stringify(value, null, 2) + '\n');
const isWithin = (child, root) => child === root || child.startsWith(root + path.sep);

async function hashFile(filename) {
  const hash = createHash('sha256');
  for await (const chunk of createReadStream(filename)) hash.update(chunk);
  return hash.digest('hex');
}

async function regular(filename) {
  const info = await fs.lstat(filename);
  assert(info.isFile() && !info.isSymbolicLink(), 'A regular, non-symlink file is required');
  assert.equal(await fs.realpath(filename), filename, 'Symlink ancestors are forbidden for fixture inputs');
  return info;
}

async function readJson(filename) {
  await regular(filename);
  return JSON.parse(await fs.readFile(filename, 'utf8'));
}

function options(argv) {
  assert.equal(argv.length, 6, 'Use --product-copy COPY --build-receipt RECEIPT --output FRESH_DIRECTORY');
  const result = {};
  for (let index = 0; index < argv.length; index += 2) {
    const key = argv[index];
    assert(['--product-copy', '--build-receipt', '--output'].includes(key) && !result[key], 'Unknown or duplicate option');
    result[key] = path.resolve(argv[index + 1]);
  }
  assert.equal(Object.keys(result).length, 3);
  return result;
}

async function main() {
  const startedAt = new Date().toISOString();
  const args = options(process.argv.slice(2));
  const product = args['--product-copy'];
  const receiptPath = args['--build-receipt'];
  const output = args['--output'];
  assert.equal(process.env.TZ, 'UTC', 'TZ=UTC is required for fixed ZIP timestamps');
  assert(!process.env.NODE_OPTIONS && !process.env.NODE_PATH, 'Injected module loader settings are forbidden');
  assert.equal(await fs.realpath(product), product);
  assert.equal(await fs.realpath(path.dirname(output)), path.dirname(output));
  assert.equal(path.dirname(output), path.dirname(product), 'Output must be a sibling of the reviewed product copy');
  assert(!isWithin(output, product));
  try {
    await fs.lstat(output);
    throw new Error('Output already exists; never overwrite or retry into a prior fixture set');
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }

  const protocol = await readJson(protocolPath);
  const receipt = await readJson(receiptPath);
  assert.equal(protocol.schema_version, 'peekly-headless-pilot-protocol.v1');
  assert.equal(receipt.schema_version, protocol.source_binding.build_receipt_schema);
  assert.equal(receipt.outcome, 'built');
  assert.equal(receipt.product_copy, product);
  assert.equal(receipt.preservation.all_required_checks_passed, true);
  assert.equal(receipt.source_manifest_sha256, protocol.peekly_source_manifest_sha256);
  assert.equal(process.version, protocol.source_binding.node_version);
  assert.equal(await hashFile(process.execPath), receipt.node.sha256, 'Use the frozen build Node binary');
  assert.equal(protocol.bounds.large_rows, 150000);
  assert.equal(protocol.bounds.control_rows, 5000);
  assert.equal(protocol.bounds.fixture_total_bytes, 33554432);

  const sourceManifestPath = receipt.source_copy_before.path;
  assert.equal(path.dirname(sourceManifestPath), path.dirname(product));
  assert.equal(await hashFile(sourceManifestPath), receipt.source_copy_before.sha256);
  const sourceManifest = await readJson(sourceManifestPath);
  assert.equal(Object.keys(sourceManifest).length, 64);
  for (const [relative, row] of Object.entries(sourceManifest)) {
    const filename = path.join(product, relative);
    assert(isWithin(filename, product));
    await regular(filename);
    assert.equal(await hashFile(filename), row.sha256, 'Copied source changed: ' + relative);
  }

  const dependenciesManifestPath = receipt.dependencies_before.path;
  assert.equal(path.dirname(dependenciesManifestPath), path.dirname(product));
  assert.equal(await hashFile(dependenciesManifestPath), receipt.dependencies_before.sha256);
  const dependencyManifest = await readJson(dependenciesManifestPath);
  const dependencyHashes = {};
  for (const relative of ['typescript/package.json', 'typescript/lib/typescript.js', 'fflate/package.json', 'fflate/lib/node.cjs']) {
    const filename = path.join(product, 'node_modules', relative);
    await regular(filename);
    const hash = await hashFile(filename);
    assert.equal(hash, dependencyManifest[relative].sha256, 'Copied dependency changed: ' + relative);
    dependencyHashes[relative] = hash;
  }
  const tsMetadata = await readJson(path.join(product, 'node_modules/typescript/package.json'));
  const zipMetadata = await readJson(path.join(product, 'node_modules/fflate/package.json'));
  assert.equal(tsMetadata.version, protocol.source_binding.typescript_version);
  assert.equal(zipMetadata.version, protocol.source_binding.fflate_version);

  // Explicit absolute paths prevent a new node_modules directory changing resolution precedence.
  const require = createRequire(import.meta.url);
  const ts = require(path.join(product, 'node_modules/typescript/lib/typescript.js'));
  const fflate = require(path.join(product, 'node_modules/fflate/lib/node.cjs'));
  const fixedTime = Date.parse(protocol.fixed_now);
  assert(Number.isFinite(fixedTime));
  class FixedDate extends Date {
    constructor(...values) { super(...(values.length ? values : [fixedTime])); }
    static now() { return fixedTime; }
  }
  const fixedZip = (entries, settings = {}) => fflate.zipSync(entries, { ...settings, mtime: new Date(fixedTime) });
  const samplePath = path.join(product, 'src/core/sampleData.ts');
  const sampleSource = await fs.readFile(samplePath, 'utf8');
  assert.equal(sha256(sampleSource), protocol.source_binding.sample_sha256);
  const transpiled = ts.transpileModule(sampleSource, {
    fileName: samplePath,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS },
    reportDiagnostics: true,
  });
  assert.equal((transpiled.diagnostics ?? []).filter(item => item.category === ts.DiagnosticCategory.Error).length, 0);
  const sample = {};
  new vm.Script(transpiled.outputText, { filename: 'reviewed-sampleData.cjs' }).runInNewContext({
    exports: sample,
    require: (name) => {
      assert.equal(name, 'fflate', 'The reviewed sample has one allowed import');
      return { zipSync: fixedZip, strToU8: fflate.strToU8 };
    },
    Date: FixedDate,
  }, { timeout: 5000 });
  assert.equal(sample.SAMPLE_ACCOUNT_HANDLE, protocol.expected_sample.account_handle);

  const previous = sample.buildSampleExportZip('previous');
  const current = sample.buildSampleExportZip('current');
  const currentEntries = fflate.unzipSync(current);
  const previousEntries = fflate.unzipSync(previous);
  const followerPath = Object.keys(currentEntries).find(name => name.endsWith('/followers_1.json'));
  const followingPath = Object.keys(currentEntries).find(name => name.endsWith('/following.json'));
  assert(followerPath && followingPath);
  const readEntry = (entries, filename) => JSON.parse(fflate.strFromU8(entries[filename]));
  assert.equal(readEntry(previousEntries, followerPath).length, 12);
  assert.equal(readEntry(previousEntries, followingPath).relationships_following.length, 12);
  assert.equal(readEntry(currentEntries, followerPath).length, 7);
  assert.equal(readEntry(currentEntries, followingPath).relationships_following.length, 10);
  const missingEntries = { ...currentEntries };
  delete missingEntries[followingPath];

  // Reuse the prior core pilot expanded(rows) construction, preserving all other built-in entries.
  function expanded(rows) {
    const entries = fflate.unzipSync(current);
    const users = Array.from({ length: rows }, (_, index) => ({
      string_list_data: [{ value: 'owned_fixture_' + String(index).padStart(6, '0'), timestamp: 1700000000 }],
    }));
    entries[followerPath] = fflate.strToU8(JSON.stringify(users));
    entries[followingPath] = fflate.strToU8(JSON.stringify({ relationships_following: users }));
    return { entries, archive: fixedZip(entries, { level: 1 }) };
  }

  const control = expanded(protocol.bounds.control_rows);
  const large = expanded(protocol.bounds.large_rows);
  const largeSizes = Object.values(large.entries).map(value => value.length);
  assert(large.archive.length <= 134217728);
  assert(Math.max(...largeSizes) <= 33554432);
  assert(largeSizes.reduce((total, value) => total + value, 0) <= 67108864);
  assert.equal(readEntry(large.entries, followerPath).length, 150000);
  assert.equal(readEntry(large.entries, followingPath).relationships_following.length, 150000);

  const generated = [];
  function add(id, relative, name, mimeType, payload, archiveEntry = null) {
    assert(/^[A-Z0-9-]+$/.test(id));
    assert.equal(path.basename(name), name);
    assert(!path.isAbsolute(relative) && !relative.split('/').includes('..'));
    const buffer = Buffer.from(payload);
    generated.push({ record: { id, path: relative, name, mime_type: mimeType, bytes: buffer.length, sha256: sha256(buffer), ...(archiveEntry ? { archive_entry: archiveEntry } : {}) }, buffer });
  }
  add('ZIP-PREVIOUS', 'previous.zip', protocol.fixture_contract.previous_name, 'application/zip', previous);
  add('ZIP-CURRENT', 'current.zip', protocol.fixture_contract.current_name, 'application/zip', current);
  add('ZIP-MISSING-FOLLOWING', 'missing-following.zip', protocol.fixture_contract.missing_name, 'application/zip', fixedZip(missingEntries));
  add('ZIP-CONTROL-5000', 'control-5000.zip', 'instagram-jimin.daily_-2026-11-12-control-5000.zip', 'application/zip', control.archive);
  add('ZIP-LARGE-150000', 'large-150000.zip', protocol.fixture_contract.large_name, 'application/zip', large.archive);
  const jsonIds = {
    'personal_information.json': 'JSON-LARGE-PROFILE',
    'followers_1.json': 'JSON-LARGE-FOLLOWERS',
    'following.json': 'JSON-LARGE-FOLLOWING',
    'pending_follow_requests.json': 'JSON-LARGE-PENDING',
    'recent_follow_requests.json': 'JSON-LARGE-RECENT-REQUESTS',
    'recently_unfollowed_profiles.json': 'JSON-LARGE-RECENT-UNFOLLOWED',
    'close_friends.json': 'JSON-LARGE-CLOSE-FRIENDS',
    'blocked_profiles.json': 'JSON-LARGE-BLOCKED',
    'restricted_profiles.json': 'JSON-LARGE-RESTRICTED',
    'hide_story_from.json': 'JSON-LARGE-HIDE-STORY',
    'liked_posts.json': 'JSON-LARGE-LIKES',
    'post_comments_1.json': 'JSON-LARGE-COMMENTS',
  };
  for (const [archiveEntry, payload] of Object.entries(large.entries)) {
    const name = path.posix.basename(archiveEntry);
    assert(jsonIds[name], 'Unexpected sample ZIP entry');
    add(jsonIds[name], 'large-json/' + name, name, 'application/json', payload, archiveEntry);
  }
  const records = generated.map(item => item.record);
  assert.equal(new Set(records.map(item => item.id)).size, 17);
  const totalBytes = records.reduce((total, item) => total + item.bytes, 0);
  assert(totalBytes <= protocol.bounds.fixture_total_bytes);
  if (protocol.fixture_hash_state === 'frozen') {
    assert.deepEqual(records, protocol.fixtures, 'Generated bytes differ from the frozen protocol');
  } else {
    assert.equal(protocol.fixture_hash_state, 'pending-initial-generation');
    assert.deepEqual(protocol.fixtures, []);
  }

  // Nothing is written before every fixture and byte-bound check passes.
  await fs.mkdir(output, { mode: 0o700 });
  await fs.mkdir(path.join(output, 'large-json'), { mode: 0o700 });
  for (const { record, buffer } of generated) {
    const filename = path.join(output, record.path);
    const handle = await fs.open(filename, constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL, 0o600);
    try { await handle.writeFile(buffer); } finally { await handle.close(); }
    assert.equal(await hashFile(filename), record.sha256);
  }
  const manifest = {
    schema_version: 'peekly-headless-fixtures.v1',
    source_manifest_sha256: protocol.peekly_source_manifest_sha256,
    sample_source_sha256: protocol.source_binding.sample_sha256,
    fixed_now: protocol.fixed_now, timezone: 'UTC',
    rows_per_large_list: 150000, control_rows: 5000, total_bytes: totalBytes,
    large_archive_bytes: large.archive.length,
    large_uncompressed_bytes: largeSizes.reduce((total, value) => total + value, 0),
    largest_json_bytes: Math.max(...largeSizes),
    files: records,
  };
  const manifestBytes = bytes(manifest);
  await fs.writeFile(path.join(output, 'fixture-manifest.json'), manifestBytes, { flag: 'wx', mode: 0o600 });
  for (const [relative, row] of Object.entries(sourceManifest)) {
    assert.equal(await hashFile(path.join(product, relative)), row.sha256, 'Copied source changed during generation');
  }
  const generationReceipt = {
    schema_version: 'peekly-headless-fixture-generation.v1',
    started_at: startedAt, finished_at: new Date().toISOString(),
    claim_scope: 'Synthetic fixture generation only; no product parser, UI, browser or user outcome executed',
    product_copy: product, build_receipt_sha256: await hashFile(receiptPath),
    node: { version: process.version, sha256: await hashFile(process.execPath) },
    generator_sha256: await hashFile(modulePath), dependency_hashes: dependencyHashes,
    fixture_manifest_sha256: sha256(manifestBytes), source_bytes_unchanged: true,
    protocol_hash_state_at_generation: protocol.fixture_hash_state,
    fixed_zip_mtime: new Date(fixedTime).toISOString(),
  };
  await fs.writeFile(path.join(output, 'generation-receipt.json'), bytes(generationReceipt), { flag: 'wx', mode: 0o600 });
  process.stdout.write(JSON.stringify({ outcome: 'generated_synthetic_inputs', output, files: records.length, total_bytes: totalBytes, large_archive_bytes: large.archive.length, largest_json_bytes: Math.max(...largeSizes), fixture_manifest_sha256: sha256(manifestBytes) }) + '\n');
}

main().catch(error => {
  process.stderr.write(String(error?.stack ?? error) + '\n');
  process.exitCode = 2;
});

