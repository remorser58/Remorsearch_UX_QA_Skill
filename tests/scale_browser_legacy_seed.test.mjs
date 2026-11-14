import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash,webcrypto} from 'node:crypto';
import {validateLegacySeedFixture,requireFreshOwnedProfile,requireLegacySeedReady,
  pageFreshStorage,pageApplyLegacySeed,pageReadLegacyState,isValidatedLegacyMigration,observationResult,
} from '../skills/remorsearch-ux-qa/drivers/web/scale_browser_cdp.mjs';

const FILE='peekly-legacy-unknown-state.json',ID='peekly_legacy_unknown_v6';
const PIN='51110f4c569673faa8d242d5b85c4b47afb54cbb';
const LOADER='401759c4ef2d11efcf7b710292ba6269ce66653cd3d19fd2164fa6f54883559a';
const sha=value=>createHash('sha256').update(value).digest('hex');
const canonical=value=>JSON.stringify(value,function(key,item){
  return item&&typeof item==='object'&&!Array.isArray(item)
    ?Object.fromEntries(Object.entries(item).sort(([a],[b])=>a<b?-1:a>b?1:0)):item;
});
const empty=()=>({snapshots:[],activeSnapshotId:null,comparisonSnapshotId:null,
  whitelistedUsernames:[],customTagsByUsername:{},unfollowLog:[],cleanupQueueUsernames:[],
  profileChecks:{},entitlement:{tier:'FREE',secretPassExpiresAt:null,rewardUnlockedItemIds:[],
    whitelistLimit:20,customTagLimit:2,maxAccounts:1}});
const source=()=>({...empty(),activeSnapshotId:ID,comparisonSnapshotId:ID,
  snapshots:[{id:ID,accountHandle:'peekly_fixture_owner',isSample:false,label:'synthetic legacy',
    createdAt:1765065600000,followers:[{pk:'synthetic_a',username:'synthetic_a'}],
    following:[{pk:'synthetic_b',username:'synthetic_b'}]}]});
test('an actual observation carries explicit action provenance for the pristine seed gate',()=>{
  const state={url:'http://127.0.0.1:4174/',title:'Peekly',text:'initial page',
    controls:[],storage_snapshot:{available:true,sha256:'a'.repeat(64)}};
  const capture={path:'browser-00001.png',sha256:'b'.repeat(64)};
  const result=observationResult(state,capture);
  assert.equal(result.facts.last_action,'observe');
  assert.equal([result].every(row=>row.facts.last_action==='observe'),true);
  assert.equal(result.facts.storage_snapshot,state.storage_snapshot);
  assert.deepEqual(result.captures,[capture]);
  assert.equal(Object.hasOwn(state,'last_action'),false);
});
function fixture(value=source()) {
  const bytes=Buffer.from(typeof value==='string'?value:canonical(value)+'\n'),fixtureSha=sha(bytes);
  const proof={schema_version:'peekly-legacy-product-validation.v1',product_commit:PIN,
    product_loader_sha256:LOADER,fixture_sha256:fixtureSha,
    migrated_snapshot_ids:[ID],raw_included_files_absent:true,raw_list_completeness_absent:true,
    checks:Object.fromEntries(['v6_missing_metadata_migrates_unknown','legacy_snapshot_retained',
      'legacy_excluded_from_selection','v7_roundtrip_valid','known_empty_is_known',
      'malformed_v7_rejected_without_legacy_fallback','plain_v7_under_compression_threshold'].map(key=>[key,true]))};
  const descriptor={schema_version:'peekly-legacy-seed-fixture.v1',fixture:FILE,fixture_sha256:fixtureSha,
    product_commit:PIN,product_loader_sha256:LOADER,storage_key:'peekly_state_v6',snapshot_ids:[ID],
    source_included_files_absent:true,source_list_completeness_absent:true,
    owner_sha256:sha('peekly_fixture_owner'),product_validation:proof,
    product_validation_sha256:sha(canonical(proof)+'\n')};
  return {bytes,descriptor,manifest:{files:[{name:FILE,bytes:bytes.length,sha256:fixtureSha,
    scenario:'validated-legacy-state-missing-provenance'}],coverage:{legacy_seed:descriptor}}};
}
test('seed accepts only bounded attested missing-provenance fixture bytes',()=>{
  const input=fixture();
  assert.equal(validateLegacySeedFixture(input.bytes,input.manifest),input.descriptor);
  assert.throws(()=>validateLegacySeedFixture(Buffer.concat([input.bytes,Buffer.from(' ')]),input.manifest),
    /legacy_seed_fixture_unvalidated/);
  input.descriptor.product_validation.checks.known_empty_is_known=false;
  assert.throws(()=>validateLegacySeedFixture(input.bytes,input.manifest),/unvalidated/);
});
test('known-empty current data cannot impersonate legacy UNKNOWN',()=>{
  const value=source();
  Object.assign(value.snapshots[0],{followers:[],following:[],includedFiles:['followers','following'],listCompleteness:'known'});
  const input=fixture(value);
  assert.throws(()=>validateLegacySeedFixture(input.bytes,input.manifest),/malformed/);
  const malformed=fixture('not JSON');
  assert.throws(()=>validateLegacySeedFixture(malformed.bytes,malformed.manifest),/malformed/);
});
test('a nonempty, other-directory or permissive profile is never accepted',()=>{
  const root=fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(),'peekly-owned-seed-')));
  fs.chmodSync(root,0o700);
  const profile=path.join(root,'browser-profile');fs.mkdirSync(profile,{mode:0o700});
  try {
    assert.equal(requireFreshOwnedProfile(profile,root),true);
    assert.throws(()=>requireFreshOwnedProfile(profile,path.dirname(root)),/not_fresh_owned/);
    fs.writeFileSync(path.join(profile,'Existing Profile'),'x',{mode:0o600});
    assert.throws(()=>requireFreshOwnedProfile(profile,root),/not_fresh_owned/);
    fs.unlinkSync(path.join(profile,'Existing Profile'));fs.chmodSync(profile,0o755);
    assert.throws(()=>requireFreshOwnedProfile(profile,root),/not_fresh_owned/);
  }finally{fs.rmSync(root,{recursive:true,force:true});}
});
test('authorization, first-action, initial digest and one-shot are independent gates',()=>{
  const state={fresh:true,sha256:'a'.repeat(64)};
  const ready={allowed:true,owned:true,consumed:false,mutations:0,initial:state,current:{...state}};
  assert.equal(requireLegacySeedReady(ready),undefined);
  for(const changed of [{allowed:false},{owned:false},{consumed:true},{mutations:1},
    {current:{...state,sha256:'b'.repeat(64)}},{current:{...state,fresh:false}}])
    assert.throws(()=>requireLegacySeedReady({...ready,...changed}),/legacy_seed/);
});
class Storage {
  getItem(key){return Object.hasOwn(this,key)?this[key]:null;}
  setItem(key,value){this[key]=String(value);}
  removeItem(key){delete this[key];}
}
function page(storage) {
  const values={localStorage:storage,crypto:webcrypto,location:{origin:'http://127.0.0.1:4174'}};
  const original=new Map(Object.keys(values).map(key=>[key,Object.getOwnPropertyDescriptor(globalThis,key)]));
  for(const [key,value] of Object.entries(values))Object.defineProperty(globalThis,key,{value,writable:true,configurable:true});
  return ()=>{for(const [key,descriptor] of original)descriptor?Object.defineProperty(globalThis,key,descriptor):delete globalThis[key];};
}
test('fresh check rejects any unrelated saved key or nondefault snapshot',async()=>{
  const storage=new Storage();storage.setItem('peekly_state_v7',JSON.stringify(empty()));
  const restore=page(storage);
  try {
    assert.equal((await pageFreshStorage()).fresh,true);
    storage.setItem('unrelated','private');assert.equal((await pageFreshStorage()).fresh,false);
    storage.removeItem('unrelated');storage.setItem('peekly_state_v7',JSON.stringify(source()));
    assert.equal((await pageFreshStorage()).fresh,false);
  }finally{restore();}
});
test('bounded seed writes only v6 and removes the verified empty v7 once',async()=>{
  const storage=new Storage();storage.setItem('peekly_state_v7',JSON.stringify(empty()));
  const restore=page(storage),input=fixture();
  try {
    const before=await pageFreshStorage();
    await pageApplyLegacySeed(input.bytes.toString(),input.descriptor.fixture_sha256,before.sha256,'http://127.0.0.1:4174');
    assert.deepEqual(Object.keys(storage),['peekly_state_v6']);
    assert.equal(storage.getItem('peekly_state_v6'),input.bytes.toString());
    const seeded=JSON.stringify(storage);
    await assert.rejects(pageApplyLegacySeed(input.bytes.toString(),input.descriptor.fixture_sha256,
      before.sha256,'http://127.0.0.1:4174'),/storage_changed/);
    assert.equal(JSON.stringify(storage),seeded);
  }finally{restore();}
});
test('changed profile data, fixture digest and origin cause zero storage changes',async()=>{
  const storage=new Storage();storage.setItem('peekly_state_v7',JSON.stringify(empty()));
  const restore=page(storage),input=fixture();
  try {
    const before=await pageFreshStorage();
    await assert.rejects(pageApplyLegacySeed(input.bytes.toString(),'0'.repeat(64),before.sha256,
      'http://127.0.0.1:4174'),/storage_changed/);
    await assert.rejects(pageApplyLegacySeed(input.bytes.toString(),input.descriptor.fixture_sha256,
      before.sha256,'http://127.0.0.1:1234'),/origin_changed/);
    storage.setItem('other','data');const original=JSON.stringify(storage);
    await assert.rejects(pageApplyLegacySeed(input.bytes.toString(),input.descriptor.fixture_sha256,
      before.sha256,'http://127.0.0.1:4174'),/storage_changed/);
    assert.equal(JSON.stringify(storage),original);
  }finally{restore();}
});
test('readback exposes persisted selections and hashes without raw account or list data',async()=>{
  const input=fixture(),state=source(),storage=new Storage();
  Object.assign(state.snapshots[0],{includedFiles:['followers','following'],listCompleteness:'unknown'});
  state.activeSnapshotId=null;state.comparisonSnapshotId=null;
  storage.setItem('peekly_state_v7',JSON.stringify(state));const restore=page(storage);
  try {
    const actual=await pageReadLegacyState('legacy-seed-1');
    assert.equal(isValidatedLegacyMigration(actual,input.descriptor),true);
    assert.equal(JSON.stringify(actual).includes('peekly_fixture_owner'),false);
    assert.equal(JSON.stringify(actual).includes('synthetic_a'),false);
    const changed={...actual,comparison_snapshot_id:ID};
    assert.equal(isValidatedLegacyMigration(changed,input.descriptor),false);
    assert.equal(isValidatedLegacyMigration({...actual,snapshots:[{
      ...actual.snapshots[0],list_completeness:'known'}]},input.descriptor),false);
  }finally{restore();}
});
