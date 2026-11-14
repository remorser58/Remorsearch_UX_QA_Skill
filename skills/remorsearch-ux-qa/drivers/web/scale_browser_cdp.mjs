#!/usr/bin/env node
// Dedicated headless Chrome CDP transport for ScaleExecution. Never attaches to user Chrome.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';
import readline from 'node:readline';
import http from 'node:http';
import { pathToFileURL } from 'node:url';
let chrome, ws, proxy, targetOrigin, pageUrl, sequence = 0, pending = new Map(), profileDir, evidenceDir, fixturesDir, fixtureManifest, typedInputs = new Map(), proxyBlockedRequests = 0;
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const safeDir = p => {
  if (!path.isAbsolute(p) || fs.realpathSync(p) !== p || !fs.statSync(p).isDirectory() || (fs.statSync(p).mode & 0o077)) throw new Error('private_directory');
  return p;
};
function send(method, params = {}) {
  const id = ++sequence;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { pending.delete(id); reject(new Error('cdp_timeout:'+method)); }, 10000);
    pending.set(id, {resolve, reject, timer});
    ws.send(JSON.stringify({id, method, params}));
  });
}

const CLICK_REJECTED = 'click_target_not_allowed_or_visible';
let observedControls = [];
let activeImportAttemptId = null;

// Serialized into the owned page; no arbitrary caller-provided script is accepted.
export function pageClickTarget(selector, label, requireActiveImport = false) {
  const norm = s => String(s || '').replace(/\s+/g, ' ').trim();
  const structural = e => {
    const parts = [];
    while (e && e.nodeType === 1 && e !== document.body) {
      let n = 1;
      for (let p = e.previousElementSibling; p; p = p.previousElementSibling) if (p.tagName === e.tagName) n++;
      parts.unshift(e.tagName.toLowerCase() + ':nth-of-type(' + n + ')'); e = e.parentElement;
    }
    return 'body>' + parts.join('>');
  };
  const candidate = e => {
    if (!e || !e.getBoundingClientRect || e.disabled) return false;
    const r = e.getBoundingClientRect(), s = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'
      && (e.tagName === 'SUMMARY' || !e.closest('details:not([open])'))
      && e.type !== 'submit' && !(e.closest('form') && e.tagName === 'BUTTON' && e.type !== 'button');
  };
  if (requireActiveImport) {
    const status = norm(document.querySelector('[role=status][aria-live=polite]')?.textContent);
    if (!status.includes('파일을 읽고 있어요') && !status.includes('팔로우 목록을 확인하고 있어요')) return null;
  }
  let e;
  try { e = document.querySelector(selector); } catch { return null; }
  if (!candidate(e) || norm(e.getAttribute('aria-label') || e.innerText || e.textContent) !== norm(label)) return null;
  e.scrollIntoView({block:'center',inline:'nearest'});
  const r = e.getBoundingClientRect();
  const left = Math.max(0,r.left), right = Math.min(innerWidth,r.right);
  const top = Math.max(0,r.top), bottom = Math.min(innerHeight,r.bottom);
  if (right <= left || bottom <= top) return null;
  const x=(left+right)/2, y=(top+bottom)/2, hit=document.elementFromPoint(x,y);
  if (!hit || !(hit===e || e.contains(hit) || hit.closest('button,a,summary,[role=button],[role=link]')===e)) return null;
  return {x,y,tag:e.tagName,href:e.tagName==='A'?e.href:null,
    label:norm(e.getAttribute('aria-label') || e.innerText || e.textContent),selector:structural(e)};
}

export function pageVerifyClick(box, requireActiveImport = false) {
  const norm = s => String(s || '').replace(/\s+/g,' ').trim();
  let e;
  try { e=document.querySelector(box.selector); } catch { return false; }
  if (!e || e.disabled || norm(e.getAttribute('aria-label') || e.innerText || e.textContent)!==norm(box.label)) return false;
  if (requireActiveImport) {
    const text=norm(document.querySelector('[role=status][aria-live=polite]')?.textContent);
    if (!text.includes('파일을 읽고 있어요') && !text.includes('팔로우 목록을 확인하고 있어요')) return false;
  }
  const r=e.getBoundingClientRect(), s=getComputedStyle(e);
  if (s.visibility==='hidden' || s.display==='none' || r.width<=0 || r.height<=0
      || box.x<r.left || box.x>r.right || box.y<r.top || box.y>r.bottom) return false;
  const hit=document.elementFromPoint(box.x,box.y);
  return !!hit && (hit===e || e.contains(hit) || hit.closest('button,a,summary,[role=button],[role=link]')===e);
}

export async function dispatchVerifiedClick(resolveTarget, verifyTarget, emit) {
  const box=await resolveTarget();
  if (!box) throw new Error(CLICK_REJECTED);
  await emit('mouseMoved',box);
  // Recheck after scroll/mouse movement, immediately before the first button event.
  if (!await verifyTarget(box)) throw new Error(CLICK_REJECTED);
  await emit('mousePressed',box);
  await emit('mouseReleased',box);
  return box;
}

// Read-only DOM planning. A wheel is never aimed at a fixed viewport coordinate
// or a background page while an active modal owns the interaction.
export function pageScrollTarget(delta, expected = null) {
  const modalQuery='[role="dialog"][aria-modal="true"],[role="alertdialog"][aria-modal="true"],dialog[open]';
  const viewport={width:innerWidth,height:innerHeight};
  const selector=e=>{
    if(e===document.documentElement)return 'html';
    if(e===document.body)return 'body';
    const parts=[];
    while(e&&e.nodeType===1&&e!==document.body){
      let n=1;for(let p=e.previousElementSibling;p;p=p.previousElementSibling)if(p.tagName===e.tagName)n++;
      parts.unshift(e.tagName.toLowerCase()+':nth-of-type('+n+')');e=e.parentElement;
    }
    return 'body>'+parts.join('>');
  };
  const shown=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&s.visibility!=='collapse';};
  const clip=r=>({left:Math.max(0,r.left),right:Math.min(innerWidth,r.right),
    top:Math.max(0,r.top),bottom:Math.min(innerHeight,r.bottom)});
  const area=r=>Math.max(0,r.right-r.left)*Math.max(0,r.bottom-r.top);
  const points=r=>area(r)>0?[ [.5,.5],[.25,.25],[.75,.25],[.25,.75],[.75,.75] ]
    .map(([x,y])=>({x:r.left+(r.right-r.left)*x,y:r.top+(r.bottom-r.top)*y})):[];
  const modalAt=p=>document.elementFromPoint(p.x,p.y)?.closest(modalQuery)||null;
  const modals=[...document.querySelectorAll(modalQuery)].filter(shown);
  const base={viewport,document_scroll:{x:window.scrollX,y:window.scrollY},blocked_areas:[]};
  if(modals.length>8)return {...base,status:'modal_scan_limit',target:null};
  const visible=modals.filter(e=>area(clip(e.getBoundingClientRect()))>0), beneath=new Set();
  for(const a of visible)for(const b of visible){
    if(a===b)continue;
    const ar=clip(a.getBoundingClientRect()),br=clip(b.getBoundingClientRect());
    const overlap={left:Math.max(ar.left,br.left),right:Math.min(ar.right,br.right),
      top:Math.max(ar.top,br.top),bottom:Math.min(ar.bottom,br.bottom)};
    if(points(overlap).some(p=>modalAt(p)===b))beneath.add(a);
  }
  let exposed=visible.filter(e=>!beneath.has(e)&&points(clip(e.getBoundingClientRect())).some(p=>modalAt(p)===e));
  if(exposed.length>1){
    const focused=document.activeElement?.closest(modalQuery);
    exposed=focused&&exposed.includes(focused)?[focused]:[];
  }
  if(modals.length&&exposed.length!==1)
    return {...base,status:visible.length?'modal_not_uniquely_exposed':'modal_has_no_usable_area',target:null};
  const modal=exposed[0]||null,scope=modal||document.body;
  const scopeSelector=modal?selector(modal):null;
  Object.assign(base,{scope:modal?'modal':'page',modal_selector:scopeSelector,
    modal_bounds:modal?{...clip(modal.getBoundingClientRect())}:null});
  const nodes=[scope,...scope.querySelectorAll('*')];
  if(!modal&&document.scrollingElement&&!nodes.includes(document.scrollingElement))nodes.unshift(document.scrollingElement);
  if(nodes.length>1500)return {...base,status:'scroll_scan_limit',target:null};
  const metrics=e=>{
    const s=getComputedStyle(e),r=clip(e.getBoundingClientRect());
    return {selector:selector(e),scroll_top:e.scrollTop,scroll_height:e.scrollHeight,client_height:e.clientHeight,
      content_height:Math.max(0,e.clientHeight-(parseFloat(s.paddingTop)||0)-(parseFloat(s.paddingBottom)||0)),
      max_scroll_top:Math.max(0,e.scrollHeight-e.clientHeight),overflow_y:s.overflowY,
      bounds:r,visible_area:area(r)};
  };
  const styled=e=>{
    if(!e||!shown(e))return false;
    const overflow=getComputedStyle(e).overflowY;
    return ['auto','scroll','overlay'].includes(overflow)||
      (!modal&&e===document.scrollingElement&&!['hidden','clip'].includes(overflow));
  };
  const usable=e=>{
    if(!styled(e))return false;
    const m=metrics(e);
    return m.client_height>0&&m.content_height>0&&m.visible_area>0&&m.max_scroll_top>1;
  };
  const receiver=hit=>{
    for(let e=hit;e&&e.nodeType===1;e=e.parentElement){
      if(usable(e))return e;
      if(modal&&e===modal)break;
    }
    return null;
  };
  const hitTarget=(e,p)=>{
    const r=clip(e.getBoundingClientRect());
    if(p.x<r.left||p.x>=r.right||p.y<r.top||p.y>=r.bottom)return false;
    const hit=document.elementFromPoint(p.x,p.y);
    return !!hit&&(hit===e||e.contains(hit))&&(!modal||hit.closest(modalQuery)===modal)&&receiver(hit)===e;
  };
  const describe=(e,p)=>{
    const m=metrics(e),canMove=delta>0?m.scroll_top<m.max_scroll_top-1:m.scroll_top>1;
    return {...base,status:delta===0?'zero_delta':canMove?'ready':'at_boundary',target:{...m,point:p}};
  };
  base.blocked_areas=nodes.filter(styled).map(metrics)
    .filter(m=>m.client_height<=0||m.content_height<=0||m.visible_area<=0).slice(0,8);
  if(expected){
    if(expected.modal_selector!==scopeSelector)return {...base,status:'active_scope_changed',target:null};
    let e;try{e=document.querySelector(expected.selector);}catch{}
    if(!e||!nodes.includes(e)||!usable(e)||!hitTarget(e,expected.point))
      return {...base,status:'target_not_visible_or_scrollable',target:null};
    return describe(e,expected.point);
  }
  const candidates=nodes.filter(usable).sort((a,b)=>metrics(b).visible_area-metrics(a).visible_area);
  for(const e of candidates){
    const point=points(clip(e.getBoundingClientRect())).find(p=>hitTarget(e,p));
    if(point)return describe(e,point);
  }
  return {...base,status:base.blocked_areas.length?'scroll_area_has_no_usable_height':
    candidates.length?'scroll_target_occluded':'no_scrollable_area',target:null};
}

export async function runScrollAttempt(io, requestedDelta) {
  if(!Number.isInteger(requestedDelta))throw new Error('scroll_delta_invalid');
  const delta=Math.max(-900,Math.min(900,requestedDelta)),started=io.now();
  const selected=await io.inspect(delta,null);
  const result={schema_version:'owned-scroll-attempt.v1',requested_delta:requestedDelta,delta:0,
    viewport:selected.viewport,scope:selected.scope||null,modal_selector:selected.modal_selector||null,
    modal_bounds:selected.modal_bounds||null,blocked_areas:selected.blocked_areas||[],
    dispatched:false,moved:false,outcome:selected.status,before:selected.target,after:null,
    document_before:selected.document_scroll,document_after:null};
  if(selected.status!=='ready'||!selected.target)return result;
  const expected={selector:selected.target.selector,modal_selector:selected.modal_selector,
    point:selected.target.point};
  await io.move(expected.point);
  const verified=await io.inspect(delta,expected);
  if(verified.status!=='ready'||!verified.target)
    return {...result,outcome:verified.status,before:verified.target,blocked_areas:verified.blocked_areas||[]};
  result.before=verified.target;result.document_before=verified.document_scroll;
  result.viewport=verified.viewport;result.modal_bounds=verified.modal_bounds||null;
  // Keep overlap in short panes so a just-below-fold control is not skipped.
  const visibleHeight=Math.min(verified.target.client_height,
    verified.target.bounds.bottom-verified.target.bounds.top);
  result.delta=Math.sign(delta)*Math.min(Math.abs(delta),Math.max(1,Math.floor(visibleHeight*.8)));
  // Any exception after this send propagates as uncertainty. Never replay a wheel.
  await io.wheel(expected.point,result.delta);result.dispatched=true;
  const settleStarted=io.now();
  for(let sample=0;sample<12&&io.now()-settleStarted<300;sample++){
    await io.pause(25);
    const observed=await io.inspect(delta,expected);
    result.document_after=observed.document_scroll;
    if(!observed.target){result.outcome='target_changed_after_dispatch';break;}
    result.after=observed.target;
    const movement=result.after.scroll_top-result.before.scroll_top;
    result.observed_delta=movement;
    if(movement!==0){result.moved=true;result.outcome='scrolled';break;}
    result.outcome='no_movement';
  }
  result.background_moved=!!result.document_after&&(
    result.document_after.x!==result.document_before.x||result.document_after.y!==result.document_before.y);
  if(result.scope==='modal'&&result.background_moved)result.outcome='background_moved';
  result.observation_window_ms=io.now()-started;
  return result;
}

export function pageImportState() {
  const norm=s=>String(s||'').replace(/\s+/g,' ').trim();
  const phase=norm(document.querySelector('[role=status][aria-live=polite]')?.textContent);
  const active=phase.includes('파일을 읽고 있어요') || phase.includes('팔로우 목록을 확인하고 있어요');
  const analysis=phase.includes('팔로우 목록을 확인하고 있어요');
  const complete=phase.includes('결과를 불러왔어요');
  const structural=e=>{
    const parts=[];
    while(e&&e.nodeType===1&&e!==document.body){
      let n=1;for(let p=e.previousElementSibling;p;p=p.previousElementSibling)if(p.tagName===e.tagName)n++;
      parts.unshift(e.tagName.toLowerCase()+':nth-of-type('+n+')');e=e.parentElement;
    }
    return 'body>'+parts.join('>');
  };
  const candidates=[...document.querySelectorAll('button,[role=button]')]
    .filter(e=>norm(e.getAttribute('aria-label')||e.innerText||e.textContent)==='읽기 멈추기');
  const visible=candidates.filter(e=>{
    const r=e.getBoundingClientRect(),s=getComputedStyle(e);
    if(e.disabled||r.width<=0||r.height<=0||s.visibility==='hidden'||s.display==='none')return false;
    const left=Math.max(0,r.left),right=Math.min(innerWidth,r.right),top=Math.max(0,r.top),bottom=Math.min(innerHeight,r.bottom);
    if(right<=left||bottom<=top)return false;
    const hit=document.elementFromPoint((left+right)/2,(top+bottom)/2);
    return !!hit&&(hit===e||e.contains(hit)||hit.closest('button,[role=button]')===e);
  });
  return {phase,active,analysis,complete,cancel_control_present:candidates.length>0,
    cancel:visible.length===1?{selector:structural(visible[0]),label:'읽기 멈추기'}:null};
}

export async function pageStorageSnapshot() {
  const keys=['peekly_state_v7','peekly_state_v6','peekly_state'];
  try {
    const values=keys.map(key=>[key,localStorage.getItem(key)]).filter(row=>row[1]!==null);
    const bytes=new TextEncoder().encode(JSON.stringify(values));
    const digest=await globalThis.crypto.subtle.digest('SHA-256',bytes);
    return {available:true,keys:values.map(row=>row[0]),
      sha256:[...new Uint8Array(digest)].map(value=>value.toString(16).padStart(2,'0')).join('')};
  } catch { return {available:false,keys:[],sha256:null}; }
}

export function pageArmStorageFailure() {
  const name='__remorsearchOwnedStorageFailure';
  if (window[name]) throw new Error('storage_fault_already_armed');
  const original=Storage.prototype.setItem;
  const state={key:'peekly_state_v7',armed:true,consumed:false,restored:false,restore_reason:null};
  let timer;
  const cleanup=reason=>{
    if (Storage.prototype.setItem===wrapped) Storage.prototype.setItem=original;
    state.armed=false;state.restored=Storage.prototype.setItem===original;
    state.restore_reason=state.restore_reason||reason;
    if(timer)clearTimeout(timer);
  };
  function wrapped(key,value) {
    if(this===localStorage && String(key)===state.key && state.armed){
      state.consumed=true;cleanup('consumed');
      throw new DOMException('Owned synthetic one-shot storage failure','QuotaExceededError');
    }
    return original.call(this,key,value);
  }
  window[name]={state,cleanup};
  try {
    Storage.prototype.setItem=wrapped;
    timer=setTimeout(()=>cleanup('timeout'),5000);
  } catch (error) { cleanup('arm_failed');delete window[name];throw error; }
  return {...state};
}

export function pageReadStorageFailure(cleanup = false) {
  const name='__remorsearchOwnedStorageFailure',holder=window[name];
  if(!holder)return null;
  if(cleanup)holder.cleanup('finally');
  const state={...holder.state};
  if(cleanup)delete window[name];
  return state;
}

// One compound action owns the timing-sensitive UI sequence. It never retries a
// dispatched click, and reports a missed window rather than a product failure.
export async function runCancellationAttempt(io) {
  const started=io.now(), phases=[];
  let cancelActive=false, cancelDispatched=false, terminal='window_not_observed', last=null;
  while(io.now()-started<5000){
    const state=await io.readPhase();last=state;
    if(state.phase && phases.at(-1)?.text!==state.phase && phases.length<32)
      phases.push({elapsed_ms:io.now()-started,text:state.phase});
    if(state.complete){terminal='already_completed';break;}
    if(state.active && state.analysis && state.cancel){
      const current=await io.readPhase();last=current;
      if(!current.active || !current.analysis || !current.cancel){
        if(current.complete){terminal='already_completed';break;}
        await io.pause(10);continue;
      }
      cancelActive=true;
      try { await io.dispatchCancel(current.cancel);cancelDispatched=true; }
      catch(error){
        if(String(error?.message)!==CLICK_REJECTED)throw error;
        terminal='cancel_target_rejected';break;
      }
      const settled=io.now();
      while(io.now()-settled<1000){
        last=await io.readPhase();
        if(last.complete){terminal='completed_after_cancel';break;}
        await io.pause(25);
      }
      if(terminal!=='completed_after_cancel')
        terminal=last?.active?'still_active_after_cancel':'inactive_after_cancel';
      break;
    }
    await io.pause(10);
  }
  return {phase_samples:phases,cancel_active:cancelActive,cancel_dispatched:cancelDispatched,
    terminal_state:terminal,post_state:last,observation_window_ms:io.now()-started};
}

async function persistence() {
  return await evaluate('('+pageStorageSnapshot.toString()+')()');
}
async function guardedClick(selector,label,requireActiveImport=false) {
  return await dispatchVerifiedClick(
    async()=>{
      const box=await evaluate('('+pageClickTarget.toString()+')('+JSON.stringify(selector)+','+JSON.stringify(label)+','+JSON.stringify(requireActiveImport)+')');
      if(box?.href && new URL(box.href).origin!==targetOrigin)throw new Error('cross_origin_link_blocked');
      return box;
    },
    box=>evaluate('('+pageVerifyClick.toString()+')('+JSON.stringify(box)+','+JSON.stringify(requireActiveImport)+')'),
    (type,box)=>send('Input.dispatchMouseEvent',{type,x:box.x,y:box.y,...(type!=='mouseMoved'?{button:'left',clickCount:1}:{})})
  );
}

async function start(input) {
  if (chrome || process.versions.node.split('.')[0] !== '26') throw new Error('node_runtime');
  const url = new URL(input.url);
  if (url.protocol !== 'http:' || !['127.0.0.1','localhost','[::1]'].includes(url.hostname) || url.username || url.password) throw new Error('target_must_be_loopback_http');
  targetOrigin = url.origin; pageUrl = url.href; typedInputs = new Map(); proxyBlockedRequests = 0;
  profileDir = safeDir(input.profile_dir); evidenceDir = safeDir(input.evidence_path);
  fixturesDir = safeDir(input.fixtures_dir);
  const manifestPath = path.join(fixturesDir, 'fixture-manifest.json');
  const manifestStat = fs.lstatSync(manifestPath);
  if (!manifestStat.isFile() || manifestStat.isSymbolicLink() || fs.realpathSync(manifestPath)!==manifestPath) throw new Error('fixture_manifest_invalid');
  fixtureManifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  if (fixtureManifest.schema_version !== 'peekly-synthetic-fixtures.v1' || !Array.isArray(fixtureManifest.files)) throw new Error('fixture_manifest_schema');
  if (fixtureManifest.groups !== undefined) {
    if (!fixtureManifest.groups || typeof fixtureManifest.groups !== 'object' || Array.isArray(fixtureManifest.groups)) throw new Error('fixture_manifest_groups');
    for (const [group,names] of Object.entries(fixtureManifest.groups)) {
      if (!/^[a-zA-Z0-9._-]{1,80}$/.test(group) || !Array.isArray(names) || !names.length || names.length>513 || names.some(name=>typeof name!=='string'||path.basename(name)!==name)) throw new Error('fixture_manifest_group_entry');
    }
  }
  for (const row of fixtureManifest.files) {
    if (!row || typeof row.name !== 'string' || path.basename(row.name)!==row.name || !/^[a-zA-Z0-9._-]+$/.test(row.name) || !/^[a-f0-9]{64}$/.test(row.sha256) || !Number.isSafeInteger(row.bytes) || row.bytes<0 || row.bytes>134217729) throw new Error('fixture_manifest_entry');
    const filename=path.join(fixturesDir,row.name), st=fs.lstatSync(filename);
    if (!st.isFile() || st.isSymbolicLink() || fs.realpathSync(filename)!==filename || st.size!==row.bytes || hash(fs.readFileSync(filename))!==row.sha256) throw new Error('fixture_integrity');
  }
  const binary = input.chrome;
  if (!path.isAbsolute(binary) || !fs.existsSync(binary)) throw new Error('chrome_binary');
  const proxyHost = url.hostname === 'localhost' ? '127.0.0.1' : url.hostname;
  const proxyPort = Number(url.port || 80);
  proxy = http.createServer((req,res) => {
    let requested;
    try { requested = new URL(req.url); } catch { res.writeHead(400); res.end(); return; }
    if (requested.origin !== targetOrigin || requested.protocol !== 'http:') {
      proxyBlockedRequests += 1;
      res.writeHead(403, {'Cache-Control':'no-store'}); res.end('blocked'); return;
    }
    const upstream = http.request({hostname:proxyHost,port:proxyPort,
      path:requested.pathname+requested.search,method:req.method,
      headers:{...req.headers,host:url.host}}, response => {
        res.writeHead(response.statusCode || 502, response.headers);
        response.pipe(res);
      });
    upstream.on('error',()=>{ if(!res.headersSent) res.writeHead(502); res.end(); });
    req.pipe(upstream);
  });
  proxy.on('connection',socket=>socket.on('error',()=>{}));
  proxy.on('clientError',(error,socket)=>{if(socket.writable)socket.end('HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n');});
  proxy.on('connect',(req,socket)=>{proxyBlockedRequests+=1;socket.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');});
  proxy.on('upgrade',(req,socket)=>{proxyBlockedRequests+=1;socket.end('HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n');});
  await new Promise((resolve,reject)=>{proxy.once('error',reject);proxy.listen(0,'127.0.0.1',resolve);});
  const proxyPortLocal = proxy.address().port;
  chrome = spawn(binary, ['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
    '--disable-background-networking','--disable-component-update','--disable-sync','--disable-extensions',
    '--disable-features=Translate,MediaRouter','--disable-quic',
    '--proxy-server=http://127.0.0.1:'+proxyPortLocal,'--proxy-bypass-list=<-loopback>',
    '--remote-debugging-port=0','--remote-allow-origins=*','--user-data-dir='+profileDir,'about:blank'],
    {stdio:'ignore'});
  const activeFile = path.join(profileDir,'DevToolsActivePort');
  const deadline = Date.now()+15000;
  while (Date.now()<deadline && !fs.existsSync(activeFile) && chrome.exitCode===null) await new Promise(r=>setTimeout(r,100));
  if (!fs.existsSync(activeFile)) throw new Error('chrome_start_failed');
  const port = Number(fs.readFileSync(activeFile,'utf8').split('\n')[0]);
  const targets = await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  const page = targets.find(x=>x.type==='page');
  if (!page?.webSocketDebuggerUrl) throw new Error('chrome_page_missing');
  ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ ws.addEventListener('open',resolve,{once:true}); ws.addEventListener('error',reject,{once:true}); });
  ws.addEventListener('error',()=>{ for(const [id,item] of pending){clearTimeout(item.timer);item.reject(new Error('cdp_websocket_error'));pending.delete(id);} });
  ws.addEventListener('close',()=>{ for(const [id,item] of pending){clearTimeout(item.timer);item.reject(new Error('cdp_websocket_closed'));pending.delete(id);} });
  ws.addEventListener('message',event=>{
    let m; try {m=JSON.parse(event.data);} catch {return;}
    if (m.id && pending.has(m.id)) { const p=pending.get(m.id); pending.delete(m.id); clearTimeout(p.timer); m.error?p.reject(new Error(m.error.message||'cdp_error')):p.resolve(m.result||{}); }
  });
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Network.setBlockedURLs',{urls:['ws://*','wss://*','ftp://*','file://*']});
  await send('Page.navigate',{url:pageUrl});
  await new Promise(r=>setTimeout(r,700));
  const snap=await observe();
  return {started:true,url:snap.url,title:snap.title,origin:targetOrigin,available_fixtures:fixtureManifest.files.map(row=>row.name)};
}
async function evaluate(expression) {
  const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture:true});
  if (r.exceptionDetails) throw new Error('page_evaluation_failed:' + String(r.exceptionDetails.exception?.description || r.exceptionDetails.text || 'unknown').slice(0,180));
  return r.result?.value;
}
async function observe() {
  const expression = "(() => {const rendered=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&(e.tagName==='SUMMARY'||!e.closest('details:not([open])'))};const visible=e=>{if(!rendered(e))return false;const r=e.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||r.right<=0||r.left>=innerWidth)return false;const x=Math.min(innerWidth-1,Math.max(0,r.x+r.width/2)),y=Math.min(innerHeight-1,Math.max(0,r.y+r.height/2)),hit=document.elementFromPoint(x,y);return !!hit&&(hit===e||e.contains(hit)||hit.closest('button,a,summary,[role=button],[role=link]')===e)};const selector=e=>{const parts=[];while(e&&e.nodeType===1&&e!==document.body){let n=1;for(let p=e.previousElementSibling;p;p=p.previousElementSibling)if(p.tagName===e.tagName)n++;parts.unshift(e.tagName.toLowerCase()+':nth-of-type('+n+')');e=e.parentElement;}return 'body>'+parts.join('>');};const controls=[...document.querySelectorAll('button,a,summary,input,textarea,select,[role=button],[role=link]')].filter(rendered).slice(0,100).map((e,i)=>({index:i,selector:selector(e),tag:e.tagName.toLowerCase(),id:e.id||null,role:e.getAttribute('role'),type:e.type||null,label:(e.getAttribute('aria-label')||e.innerText||e.textContent||e.getAttribute('placeholder')||'').trim().slice(0,180),placeholder:e.getAttribute('placeholder')||null,title:e.getAttribute('title')||null,multiple:e.multiple===true,disabled:!!e.disabled,visible:visible(e),href:e.tagName==='A'?e.href:null}));const fileInputs=[...document.querySelectorAll('input[type=file]')].map((e,i)=>({index:i,selector:selector(e),accept:e.accept,multiple:e.multiple,disabled:!!e.disabled,hidden:!visible(e)}));const listRows=[...document.querySelectorAll('.person-list [data-row-key]')].map(e=>({key:e.getAttribute('data-row-key'),text:(e.innerText||e.textContent||'').trim().slice(0,180)}));let storageKeys=[],storageAccess='denied';try{storageKeys=Object.keys(localStorage);storageAccess='available';}catch{}return {url:location.href,title:document.title,text:(document.body?.innerText||'').slice(0,12000),controls,file_inputs:fileInputs,list_rows:listRows,storage_keys:storageKeys,storage_access:storageAccess,viewport:{width:innerWidth,height:innerHeight}};})()";
  const data=await evaluate(expression);
  if (!data || new URL(data.url).origin!==targetOrigin) throw new Error('origin_changed');
  const values = await evaluate("(() => {const out={};for(const selector of "+JSON.stringify([...typedInputs.keys()])+ "){try{const e=document.querySelector(selector);out[selector]=e&&('value' in e)?String(e.value):null;}catch{out[selector]=null;}}return out;})()");
  data.typed_input_checks = Object.entries(values||{}).map(([selector,value])=>({
    selector, retained:value!==null && hash(Buffer.from(value,'utf8'))===typedInputs.get(selector),
    expected_sha256:typedInputs.get(selector), actual_sha256:value===null?null:hash(Buffer.from(value,'utf8'))
  }));
  data.network_policy = {allowed_origin:targetOrigin,external_requests_blocked:true,blocked_request_count:proxyBlockedRequests};
  data.available_fixtures = fixtureManifest.files.map(row=>row.name);
  observedControls=data.controls.map(row=>({...row}));
  data.storage_snapshot=await persistence();
  if(activeImportAttemptId)data.import_attempt_id=activeImportAttemptId;
  return data;
}
async function screenshot() {
  const r=await send('Page.captureScreenshot',{format:'png',fromSurface:true,captureBeyondViewport:false});
  const bytes=Buffer.from(r.data,'base64');
  const name='browser-'+String(++sequence).padStart(5,'0')+'.png';
  const dest=path.join(evidenceDir,name);
  fs.writeFileSync(dest,bytes,{mode:0o600,flag:'wx'});
  return {path:name,sha256:hash(bytes)};
}
export function approvedCancelFixture(entries) {
  return Array.isArray(entries) && entries.length===1
    && entries[0]?.name==='peekly-progress-sample.zip'
    && ['large-valid-progress','recognized-relationship-json-progress'].includes(entries[0].scenario);
}
async function act(input) {
  const name=input.name, args=input.arguments||{};
  let uploadedFixture=null, uploadProgressSamples=[], importAttempt=null, clickDispatch=null, scrollAttempt=null;
  const extraCaptures=[];
  if (name==='observe') {
    const state=await observe(); const capture=await screenshot();
    return {text:'URL '+state.url+'\nTitle '+state.title+'\n'+state.text,facts:state,captures:[capture],checks:[]};
  }
  if (['upload','upload_cancel','upload_save_failure'].includes(name)) {
    const selector=args.selector, filename=args.file;
    if (typeof filename!=='string' || path.basename(filename)!==filename) throw new Error('fixture_name_invalid');
    const groupName=filename.startsWith('@group:')?filename.slice(7):null;
    const names=groupName?(fixtureManifest.groups?.[groupName]||[]):[filename];
    if (!names.length || names.some(name=>typeof name!=='string'||path.basename(name)!==name)) throw new Error('fixture_not_allowlisted');
    const entries=names.map(name=>fixtureManifest.files.find(row=>row.name===name));
    if (entries.some(entry=>!entry)) throw new Error('fixture_not_allowlisted');
    if(name==='upload_cancel' && !approvedCancelFixture(entries))
      throw new Error('cancel_fixture_not_allowlisted');
    if(name==='upload_save_failure' && (entries.length!==1 || entries[0].bytes>1048576
        || !/^peekly-(?:sample-current|sample-previous|format-json|retention-snapshot-\d{2})\.zip$/.test(filename)))
      throw new Error('storage_fault_fixture_not_allowlisted');
    const fullPaths=names.map((name,index)=>{
      const fullPath=path.join(fixturesDir,name), entry=entries[index], st=fs.lstatSync(fullPath);
      if (!st.isFile() || st.isSymbolicLink() || fs.realpathSync(fullPath)!==fullPath || st.size!==entry.bytes || hash(fs.readFileSync(fullPath))!==entry.sha256) throw new Error('fixture_integrity');
      return fullPath;
    });
    const document=await send('DOM.getDocument',{depth:-1,pierce:false});
    const found=await send('DOM.querySelector',{nodeId:document.root.nodeId,selector});
    if (!found.nodeId) throw new Error('upload_target_missing');
    const described=await send('DOM.describeNode',{nodeId:found.nodeId});
    const node=described.node;
    const attrs=Object.fromEntries((node.attributes||[]).reduce((out,value,index,array)=>{if(index%2===0)out.push([value,array[index+1]]);return out;},[]));
    if (node.nodeName!=='INPUT' || attrs.type!=='file') throw new Error('upload_target_not_single_file_input');
    const before=await persistence();
    if(name==='upload_save_failure' && (!before.available || !before.keys.includes('peekly_state_v7')))
      throw new Error('storage_fault_baseline_missing');
    importAttempt={schema_version:'peekly-import-attempt.v1',attempt_id:'upload-'+String(sequence),
      tool:name,fixture:filename,fixture_sha256:entries.length===1?entries[0].sha256:null,
      storage_before:before,phase_samples:[],cancel_active:false,cancel_dispatched:false};
    activeImportAttemptId=importAttempt.attempt_id;
    if(name!=='upload')extraCaptures.push(await screenshot());
    let faultArmed=false;
    try {
      if(name==='upload_save_failure'){
        await evaluate('('+pageArmStorageFailure.toString()+')()');faultArmed=true;
      }
      await send('DOM.setFileInputFiles',{files:fullPaths,nodeId:found.nodeId});
      uploadedFixture=filename;
      if(name==='upload_cancel'){
        const cancellation=await runCancellationAttempt({
          readPhase:()=>evaluate('('+pageImportState.toString()+')()'),
          dispatchCancel:target=>guardedClick(target.selector,target.label,true),
          pause:ms=>new Promise(resolve=>setTimeout(resolve,ms)),now:()=>Date.now()
        });
        Object.assign(importAttempt,cancellation);
        uploadProgressSamples=cancellation.phase_samples;
      } else {
        const started=Date.now();let lastPhase=null;
        while(Date.now()-started<(name==='upload_save_failure'?5000:1200)){
          const current=await evaluate('('+pageImportState.toString()+')()');
          if(current.phase && current.phase!==lastPhase && uploadProgressSamples.length<32){
            uploadProgressSamples.push({elapsed_ms:Date.now()-started,text:current.phase});lastPhase=current.phase;
          }
          if(name==='upload_save_failure'){
            const fault=await evaluate('('+pageReadStorageFailure.toString()+')()');
            if(fault?.consumed){await new Promise(resolve=>setTimeout(resolve,100));break;}
          } else if(current.complete || (!current.active && Date.now()-started>500))break;
          await new Promise(resolve=>setTimeout(resolve,25));
        }
        importAttempt.phase_samples=uploadProgressSamples;
      }
    } finally {
      if(faultArmed)importAttempt.storage_fault=await evaluate('('+pageReadStorageFailure.toString()+')(true)');
    }
  } else if (name==='click') {
    const selector=args.selector,label=args.label,norm=value=>String(value||'').replace(/\s+/g,' ').trim();
    if (typeof label!=='string' || !label.trim() || label.length>180) throw new Error('click_label_required');
    if(!observedControls.some(row=>row.selector===selector && row.visible===true && !row.disabled && norm(row.label)===norm(label)))
      throw new Error(CLICK_REJECTED);
    const box=await guardedClick(selector,label);
    clickDispatch={dispatched:true,hit_test:true,requested_selector:selector,verified_selector:box.selector,label:box.label};
  } else if (name==='type') {
    const selector=args.selector, value=args.value;
    if (typeof value!=='string'||value.length>500||/[\r\n]/.test(value)) throw new Error('typed_value_limit');
    const expression="(() => {const e=document.querySelector("+JSON.stringify(selector)+");if(!e||!['INPUT','TEXTAREA'].includes(e.tagName)||['password','email','tel','hidden'].includes(e.type)||e.disabled||e.readOnly) return false;e.focus();e.select();return true;})()";
    const focused=await evaluate(expression);
    if (!focused) throw new Error('type_target_not_allowed');
    await send('Input.insertText',{text:value});
    typedInputs.set(selector,hash(Buffer.from(value,'utf8')));
  } else if (name==='scroll') {
    scrollAttempt=await runScrollAttempt({
      inspect:(delta,expected)=>evaluate('('+pageScrollTarget.toString()+')('+JSON.stringify(delta)+','+JSON.stringify(expected)+')'),
      move:point=>send('Input.dispatchMouseEvent',{type:'mouseMoved',...point}),
      wheel:(point,delta)=>send('Input.dispatchMouseEvent',{type:'mouseWheel',...point,deltaX:0,deltaY:delta}),
      pause:ms=>new Promise(resolve=>setTimeout(resolve,ms)),now:()=>Date.now(),
    },args.delta);
  } else if (name==='wait') {
    const ms=Math.max(0,Math.min(3000,args.ms)); await new Promise(r=>setTimeout(r,ms));
  } else throw new Error('unknown_tool');
  const state=await observe(); const capture=await screenshot();
  if(importAttempt){
    importAttempt.storage_after=state.storage_snapshot;
    importAttempt.persistence_unchanged=importAttempt.storage_before.available && state.storage_snapshot.available
      ? importAttempt.storage_before.sha256===state.storage_snapshot.sha256 : null;
    if(importAttempt.terminal_state==='inactive_after_cancel' && importAttempt.persistence_unchanged===true)
      importAttempt.terminal_state='cancelled_without_new_result';
    if(name==='upload_save_failure')importAttempt.terminal_state=importAttempt.storage_fault?.consumed
      ? 'storage_fault_consumed' : 'storage_fault_not_consumed';
  }
  const actionText=scrollAttempt?'Scroll '+scrollAttempt.outcome+'; wheel dispatched='+scrollAttempt.dispatched+
    ', observed movement='+(scrollAttempt.observed_delta||0)+'.':'Action '+name+' completed.';
  return {text:actionText+'\nURL '+state.url+'\nTitle '+state.title+'\n'+state.text,
    facts:{...state,last_action:name,...(name==='click'?{last_action_label:args.label,click_dispatch:clickDispatch}:{}),
      ...(scrollAttempt?{scroll_attempt:scrollAttempt}:{}),
      ...(uploadedFixture?{uploaded_fixture:uploadedFixture,upload_progress_samples:uploadProgressSamples,import_attempt:importAttempt}:{})},
    captures:[...extraCaptures,capture],checks:[]};
}
async function close() {
  try { if(ws) ws.close(); } catch {}
  if(chrome && chrome.exitCode===null) { chrome.kill('SIGTERM'); await new Promise(resolve=>{const t=setTimeout(()=>{if(chrome.exitCode===null) chrome.kill('SIGKILL');resolve();},3000);chrome.once('exit',()=>{clearTimeout(t);resolve();});}); }
  try { if(proxy) await new Promise(resolve=>proxy.close(resolve)); } catch {}
  return {stopped:!chrome||chrome.exitCode!==null};
}
export async function main() {
process.umask(0o077);
const input = readline.createInterface({input:process.stdin});
for await (const line of input) {
  if(line.length>65536) break;
  let m; try {m=JSON.parse(line);let result;
    if(m.kind==='start') result=await start(m.payload);
    else if(m.kind==='close') result=await close();
    else result=await act(m.payload);
    process.stdout.write(JSON.stringify({id:m.id,result})+'\n');
    if(m.kind==='close') break;
  } catch (err) { process.stdout.write(JSON.stringify({id:m?.id,error:String(err?.message||'browser_tool_failed').slice(0,160)})+'\n'); if(m?.kind==='act') continue; if(chrome&&chrome.exitCode===null) chrome.kill('SIGTERM'); break; }
}
input.close();
await close().catch(()=>{});
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) await main();
