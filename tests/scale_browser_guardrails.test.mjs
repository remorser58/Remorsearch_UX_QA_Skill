import test from 'node:test';
import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import {
  pageClickTarget, pageVerifyClick, dispatchVerifiedClick, pageImportState,
  pageStorageSnapshot, pageArmStorageFailure, pageReadStorageFailure,
  runCancellationAttempt, approvedCancelFixture,
} from '../skills/remorsearch-ux-qa/drivers/web/scale_browser_cdp.mjs';

test('cancellation accepts recognized relationship fixture and rejects other catalogs',()=>{
  const progress={name:'peekly-progress-sample.zip',scenario:'recognized-relationship-json-progress'};
  assert.equal(approvedCancelFixture([progress]),true);
  assert.equal(approvedCancelFixture([{...progress,scenario:'large-valid-progress'}]),true);
  assert.equal(approvedCancelFixture([{...progress,name:'peekly-sample-current.zip'}]),false);
  assert.equal(approvedCancelFixture([{...progress,scenario:'oversized-rejected'}]),false);
  assert.equal(approvedCancelFixture([progress,progress]),false);
  assert.equal(approvedCancelFixture([]),false);
});

function install(values) {
  const original=new Map(Object.keys(values).map(k=>[k,Object.getOwnPropertyDescriptor(globalThis,k)]));
  for(const [key,value] of Object.entries(values))Object.defineProperty(globalThis,key,{value,writable:true,configurable:true});
  return ()=>{for(const [key,descriptor] of original)descriptor?Object.defineProperty(globalThis,key,descriptor):delete globalThis[key];};
}
function dom({covered=false,phase='팔로우 목록을 확인하고 있어요',disabled=false}={}) {
  const body={nodeType:1,tagName:'BODY'};
  const button={nodeType:1,tagName:'BUTTON',type:'button',disabled,parentElement:body,previousElementSibling:null,
    innerText:'읽기 멈추기',textContent:'읽기 멈추기',
    getBoundingClientRect:()=>({left:10,right:110,top:20,bottom:60,width:100,height:40}),
    getAttribute:()=>null,scrollIntoView:()=>{},contains:hit=>hit===button,
    closest:selector=>selector==='form'||selector==='details:not([open])'?null:button};
  const overlay={closest:()=>null};
  const status={textContent:phase};
  const document={body,querySelector:selector=>selector.includes('role=status')?status:
    (selector==='#stop'||selector==='body>button:nth-of-type(1)'?button:null),
    querySelectorAll:()=>[button],elementFromPoint:()=>covered?overlay:button};
  const restore=install({document,innerWidth:756,innerHeight:413,getComputedStyle:()=>({visibility:'visible',display:'block'})});
  return {button,status,document,restore};
}
test('covered target is rejected even though its box and label are valid',()=>{
  const state=dom({covered:true});
  try {assert.equal(pageClickTarget('#stop','읽기 멈추기'),null);}
  finally {state.restore();}
});
test('visible control is bound to the actual hit target and active import',()=>{
  const state=dom();
  try {
    const box=pageClickTarget('#stop','읽기 멈추기',true);
    assert.equal(box.label,'읽기 멈추기');assert.equal(pageVerifyClick(box,true),true);
    state.document.elementFromPoint=()=>({closest:()=>null});
    assert.equal(pageVerifyClick(box,true),false);
    state.document.elementFromPoint=()=>state.button;state.status.textContent='결과를 불러왔어요.';
    assert.equal(pageClickTarget('#stop','읽기 멈추기',true),null);
  } finally {state.restore();}
});
test('disabled and stale-label controls cannot be clicked',()=>{
  const state=dom({disabled:true});
  try {assert.equal(pageClickTarget('#stop','읽기 멈추기'),null);state.button.disabled=false;
    assert.equal(pageClickTarget('#stop','different label'),null);}
  finally {state.restore();}
});
test('occlusion appearing after mouse move emits no button event',async()=>{
  const events=[];
  await assert.rejects(dispatchVerifiedClick(async()=>({x:1,y:2}),async()=>false,
    async(type)=>events.push(type)),/click_target_not_allowed_or_visible/);
  assert.deepEqual(events,['mouseMoved']);
});
test('unknown dispatch effect is not retried or claimed successful',async()=>{
  const events=[];
  await assert.rejects(dispatchVerifiedClick(async()=>({x:1,y:2}),async()=>true,async(type)=>{
    events.push(type);if(type==='mousePressed')throw new Error('unknown_dispatch_effect');
  }),/unknown_dispatch_effect/);
  assert.deepEqual(events,['mouseMoved','mousePressed']);
});
test('successful dispatch records exactly one complete native click',async()=>{
  const events=[],box={x:1,y:2};
  assert.deepEqual(await dispatchVerifiedClick(async()=>box,async()=>true,async(type)=>events.push(type)),box);
  assert.deepEqual(events,['mouseMoved','mousePressed','mouseReleased']);
});
test('import state exposes only the actual visible stop control',()=>{
  const state=dom({covered:true,phase:'팔로우 목록을 확인하고\u00a0있어요'});
  try {const observed=pageImportState();assert.equal(observed.analysis,true);assert.equal(observed.cancel,null);
    assert.equal(observed.cancel_control_present,true);}
  finally {state.restore();}
});
function cancellationIO(states,dispatch) {
  let clock=0,index=0,captures=0;
  return {io:{now:()=>clock,pause:async ms=>{clock+=ms;},
    readPhase:async()=>states[Math.min(index++,states.length-1)],
    captureActive:async()=>{captures++;},dispatchCancel:dispatch||(async()=>{})},
    captures:()=>captures};
}
const reading={phase:'파일을 읽고 있어요',active:true,analysis:false,complete:false,cancel:null};
const analyzing={phase:'팔로우 목록을 확인하고 있어요',active:true,analysis:true,complete:false,cancel:{selector:'#stop',label:'읽기 멈추기'}};
const inactive={phase:'',active:false,analysis:false,complete:false,cancel:null};
test('compound cancellation observes both phases and dispatches only while active',async()=>{
  let clicks=0;const fixture=cancellationIO([reading,analyzing,analyzing,inactive],async()=>{clicks++;});
  const result=await runCancellationAttempt(fixture.io);
  assert.equal(clicks,1);assert.equal(result.cancel_active,true);assert.equal(result.cancel_dispatched,true);
  assert.deepEqual(result.phase_samples.map(x=>x.text),[reading.phase,analyzing.phase]);
  assert.equal(result.terminal_state,'inactive_after_cancel');assert.equal(fixture.captures(),1);
});
test('fast completion remains an untested window rather than a cancelled result',async()=>{
  let clicks=0;const fixture=cancellationIO([reading,{...inactive,phase:'결과를 불러왔어요.',complete:true}],async()=>{clicks++;});
  const result=await runCancellationAttempt(fixture.io);
  assert.equal(clicks,0);assert.equal(result.cancel_dispatched,false);assert.equal(result.terminal_state,'already_completed');
});
test('covered stop button times out without bypassing visibility',async()=>{
  let clicks=0;const fixture=cancellationIO([{...analyzing,cancel:null}],async()=>{clicks++;});
  const result=await runCancellationAttempt(fixture.io);
  assert.equal(clicks,0);assert.equal(result.terminal_state,'window_not_observed');
  assert.equal(result.observation_window_ms,5000);
});
test('pre-dispatch cancellation rejection is distinct from unknown effect',async()=>{
  const fixture=cancellationIO([analyzing],async()=>{throw new Error('click_target_not_allowed_or_visible');});
  const result=await runCancellationAttempt(fixture.io);
  assert.equal(result.cancel_dispatched,false);assert.equal(result.terminal_state,'cancel_target_rejected');
  const uncertain=cancellationIO([analyzing],async()=>{throw new Error('cdp_timeout:Input.dispatchMouseEvent');});
  await assert.rejects(runCancellationAttempt(uncertain.io),/cdp_timeout/);
});
class FakeStorage {
  constructor(){this.values=new Map();}
  setItem(key,value){this.values.set(String(key),String(value));}
  getItem(key){return this.values.has(key)?this.values.get(key):null;}
}
test('storage fault is exact-key, owned-store, one-shot and restores before retry',()=>{
  const local=new FakeStorage(),other=new FakeStorage(),window={};
  const restore=install({Storage:FakeStorage,localStorage:local,window});
  const original=FakeStorage.prototype.setItem;
  try {
    local.setItem('peekly_state_v7','baseline');
    pageArmStorageFailure();
    local.setItem('peekly_theme_preference','dark');other.setItem('peekly_state_v7','unaffected');
    assert.throws(()=>local.setItem('peekly_state_v7','new-result'),error=>error.name==='QuotaExceededError');
    const state=pageReadStorageFailure();
    assert.equal(state.consumed,true);assert.equal(state.restored,true);
    assert.equal(local.getItem('peekly_state_v7'),'baseline');
    local.setItem('peekly_state_v7','retried');assert.equal(local.getItem('peekly_state_v7'),'retried');
    assert.equal(FakeStorage.prototype.setItem,original);
  } finally {pageReadStorageFailure(true);restore();}
});
test('unconsumed fault cleanup restores setter without suppressing a later write',()=>{
  const local=new FakeStorage(),window={};const restore=install({Storage:FakeStorage,localStorage:local,window});
  const original=FakeStorage.prototype.setItem;
  try {
    pageArmStorageFailure();const state=pageReadStorageFailure(true);
    assert.equal(state.consumed,false);assert.equal(state.restored,true);
    assert.equal(FakeStorage.prototype.setItem,original);local.setItem('peekly_state_v7','safe');
    assert.equal(local.getItem('peekly_state_v7'),'safe');
  } finally {pageReadStorageFailure(true);restore();}
});
test('persistence metadata hashes only fixed result keys and exposes no values',async()=>{
  const local=new FakeStorage();local.setItem('peekly_state_v7','private synthetic baseline');
  const restore=install({localStorage:local,crypto:webcrypto});
  try {
    const before=await pageStorageSnapshot();local.setItem('peekly_theme_preference','dark');
    assert.deepEqual(await pageStorageSnapshot(),before);
    assert.equal(JSON.stringify(before).includes('private synthetic baseline'),false);
    local.setItem('peekly_state_v7','new synthetic result');
    assert.notEqual((await pageStorageSnapshot()).sha256,before.sha256);
  } finally {restore();}
});
test('storage access denial is unavailable evidence, never an empty-state pass',async()=>{
  const restore=install({localStorage:{getItem(){throw new Error('denied');}}});
  try {assert.deepEqual(await pageStorageSnapshot(),{available:false,keys:[],sha256:null});}
  finally {restore();}
});
