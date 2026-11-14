#!/usr/bin/env node
// Offline validation against the pinned product's real load/save implementation.
// No browser, model, service, dependency install, or product write is performed.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';

const PIN='51110f4c569673faa8d242d5b85c4b47afb54cbb';
const LOADER='401759c4ef2d11efcf7b710292ba6269ce66653cd3d19fd2164fa6f54883559a';
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const [productArg,fixtureArg]=process.argv.slice(2);
if(!productArg||!fixtureArg)throw new Error('product_and_fixture_required');
const product=fs.realpathSync(productArg),fixture=fs.realpathSync(fixtureArg);
const git=(...args)=>execFileSync('git',['-C',product,...args],{encoding:'utf8',maxBuffer:2*1024*1024}).trim();
assert.equal(git('rev-parse','HEAD'),PIN,'product_commit_changed');
const raw=fs.readFileSync(fixture);
assert.ok(raw.length>0&&raw.length<65536,'seed_size');
const source=JSON.parse(raw);
assert.equal(source.snapshots.length,1);
const seed=source.snapshots[0];
assert.equal(seed.id,'peekly_legacy_unknown_v6');
assert.equal(Object.hasOwn(seed,'includedFiles'),false);
assert.equal(Object.hasOwn(seed,'listCompleteness'),false);
assert.equal(seed.isSample,false);
assert.ok(seed.followers.length&&seed.following.length);
const productRequire=createRequire(path.join(product,'package.json'));
const {build}=productRequire('esbuild');
const built=await build({absWorkingDir:product,entryPoints:['src/storage/snapshotStore.ts'],
  bundle:true,platform:'node',format:'cjs',write:false,metafile:true,logLevel:'silent'});
const sources=Object.keys(built.metafile.inputs).filter(name=>name.startsWith('src/')).sort().map(name=>{
  const bytes=fs.readFileSync(path.join(product,name));
  const committed=execFileSync('git',['-C',product,'show',PIN+':'+name],{maxBuffer:2*1024*1024});
  assert.equal(digest(bytes),digest(committed),'product_source_modified:'+name);
  return {path:name,sha256:digest(bytes)};
});
assert.equal(sources.find(row=>row.path==='src/storage/snapshotStore.ts')?.sha256,LOADER);
const values=new Map();
const storage={getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,String(value)),
  removeItem:key=>values.delete(key)};
const module={exports:{}};
new Function('module','exports','require','window',built.outputFiles[0].text)(
  module,module.exports,productRequire,{localStorage:storage});
const api=module.exports;
const failures=[];
values.set('peekly_state_v6',raw.toString('utf8'));
const migrated=api.loadPersistedState(error=>failures.push(String(error)));
assert.equal(failures.length,0);
assert.equal(migrated.snapshots.length,1);
assert.equal(migrated.snapshots[0].id,seed.id);
assert.equal(migrated.snapshots[0].listCompleteness,'unknown');
assert.deepEqual(migrated.snapshots[0].includedFiles,['followers','following']);
assert.equal(migrated.activeSnapshotId,null);
assert.equal(migrated.comparisonSnapshotId,null);
assert.equal(api.isAnalyzableSnapshot(migrated.snapshots[0]),false);
assert.equal(api.savePersistedState(migrated).status,'saved');
const saved=values.get('peekly_state_v7');
assert.ok(saved.startsWith('{')&&Buffer.byteLength(saved)<65536);
assert.deepEqual(api.loadPersistedState(error=>failures.push(String(error))),migrated);
assert.equal(failures.length,0);
// Known-empty imports are a distinct, analyzable current-format negative control.
const knownEmpty={...migrated.snapshots[0],id:'synthetic_known_empty_control',
  followers:[],following:[],includedFiles:['followers','following'],listCompleteness:'known'};
values.delete('peekly_state_v7');
values.set('peekly_state_v6',JSON.stringify({...source,snapshots:[knownEmpty],
  activeSnapshotId:knownEmpty.id,comparisonSnapshotId:knownEmpty.id}));
const known=api.loadPersistedState(error=>failures.push(String(error)));
assert.equal(known.snapshots[0].listCompleteness,'known');
assert.equal(api.isAnalyzableSnapshot(known.snapshots[0]),true);
assert.equal(known.activeSnapshotId,knownEmpty.id);
// Malformed authoritative v7 must fail closed rather than revive valid v6.
values.set('peekly_state_v6',raw.toString('utf8'));
values.set('peekly_state_v7',raw.toString('utf8'));
const invalid=api.loadPersistedState(error=>failures.push(String(error)));
assert.equal(invalid.snapshots.length,0);
assert.equal(failures.length,1);
const result={schema_version:'peekly-legacy-product-validation.v1',product_commit:PIN,
  product_loader_sha256:LOADER,fixture_sha256:digest(raw),sources,
  migrated_snapshot_ids:[seed.id],raw_included_files_absent:true,
  raw_list_completeness_absent:true,checks:{
    v6_missing_metadata_migrates_unknown:true,legacy_snapshot_retained:true,
    legacy_excluded_from_selection:true,v7_roundtrip_valid:true,known_empty_is_known:true,
    malformed_v7_rejected_without_legacy_fallback:true,plain_v7_under_compression_threshold:true}};
process.stdout.write(JSON.stringify(result)+'\n');
