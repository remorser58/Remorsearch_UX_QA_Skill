#!/usr/bin/env node
// Dedicated headless Chrome CDP transport for ScaleExecution. Never attaches to user Chrome.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn } from 'node:child_process';
import readline from 'node:readline';
import http from 'node:http';
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
  const expression = "(() => {const rendered=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&(e.tagName==='SUMMARY'||!e.closest('details:not([open])'))};const visible=e=>{if(!rendered(e))return false;const r=e.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||r.right<=0||r.left>=innerWidth)return false;const x=Math.min(innerWidth-1,Math.max(0,r.x+r.width/2)),y=Math.min(innerHeight-1,Math.max(0,r.y+r.height/2)),hit=document.elementFromPoint(x,y);return !!hit&&(hit===e||e.contains(hit)||hit.closest('button,a,summary,[role=button],[role=link]')===e)};const selector=e=>{if(e.id)return '#'+CSS.escape(e.id);const parts=[];while(e&&e.nodeType===1&&e!==document.body){let n=1;for(let p=e.previousElementSibling;p;p=p.previousElementSibling)if(p.tagName===e.tagName)n++;parts.unshift(e.tagName.toLowerCase()+':nth-of-type('+n+')');e=e.parentElement;}return 'body>'+parts.join('>');};const controls=[...document.querySelectorAll('button,a,summary,input,textarea,select,[role=button],[role=link]')].filter(rendered).slice(0,100).map((e,i)=>({index:i,selector:selector(e),tag:e.tagName.toLowerCase(),id:e.id||null,role:e.getAttribute('role'),type:e.type||null,label:(e.getAttribute('aria-label')||e.innerText||e.textContent||e.getAttribute('placeholder')||'').trim().slice(0,180),placeholder:e.getAttribute('placeholder')||null,title:e.getAttribute('title')||null,multiple:e.multiple===true,disabled:!!e.disabled,visible:visible(e),href:e.tagName==='A'?e.href:null}));const fileInputs=[...document.querySelectorAll('input[type=file]')].map((e,i)=>({index:i,selector:selector(e),accept:e.accept,multiple:e.multiple,disabled:!!e.disabled,hidden:!visible(e)}));const listRows=[...document.querySelectorAll('.person-list [data-row-key]')].map(e=>({key:e.getAttribute('data-row-key'),text:(e.innerText||e.textContent||'').trim().slice(0,180)}));return {url:location.href,title:document.title,text:(document.body?.innerText||'').slice(0,12000),controls,file_inputs:fileInputs,list_rows:listRows,storage_keys:Object.keys(localStorage),viewport:{width:innerWidth,height:innerHeight}};})()";
  const data=await evaluate(expression);
  if (!data || new URL(data.url).origin!==targetOrigin) throw new Error('origin_changed');
  const values = await evaluate("(() => {const out={};for(const selector of "+JSON.stringify([...typedInputs.keys()])+ "){try{const e=document.querySelector(selector);out[selector]=e&&('value' in e)?String(e.value):null;}catch{out[selector]=null;}}return out;})()");
  data.typed_input_checks = Object.entries(values||{}).map(([selector,value])=>({
    selector, retained:value!==null && hash(Buffer.from(value,'utf8'))===typedInputs.get(selector),
    expected_sha256:typedInputs.get(selector), actual_sha256:value===null?null:hash(Buffer.from(value,'utf8'))
  }));
  data.network_policy = {allowed_origin:targetOrigin,external_requests_blocked:true,blocked_request_count:proxyBlockedRequests};
  data.available_fixtures = fixtureManifest.files.map(row=>row.name);
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
async function act(input) {
  const name=input.name, args=input.arguments||{};
  let uploadedFixture=null, uploadProgressSamples=[];
  if (name==='observe') {
    const state=await observe(); const capture=await screenshot();
    return {text:'URL '+state.url+'\nTitle '+state.title+'\n'+state.text,facts:state,captures:[capture],checks:[]};
  }
  if (name==='upload') {
    const selector=args.selector, filename=args.file;
    if (typeof filename!=='string' || path.basename(filename)!==filename) throw new Error('fixture_name_invalid');
    const groupName=filename.startsWith('@group:')?filename.slice(7):null;
    const names=groupName?(fixtureManifest.groups?.[groupName]||[]):[filename];
    if (!names.length || names.some(name=>typeof name!=='string'||path.basename(name)!==name)) throw new Error('fixture_not_allowlisted');
    const entries=names.map(name=>fixtureManifest.files.find(row=>row.name===name));
    if (entries.some(entry=>!entry)) throw new Error('fixture_not_allowlisted');
    const fullPaths=names.map((name,index)=>{
      const fullPath=path.join(fixturesDir,name), entry=entries[index], st=fs.lstatSync(fullPath);
      if (!st.isFile() || st.isSymbolicLink() || fs.realpathSync(fullPath)!==fullPath || st.size!==entry.bytes || hash(fs.readFileSync(fullPath))!==entry.sha256) throw new Error('fixture_integrity');
      return fullPath;
    });
    // Hidden React file inputs may be nested below several wrapper nodes.
    // Request the complete owned document tree before querying; a shallow
    // depth-1 snapshot can falsely report upload_target_missing even though
    // the input exists deeper in the page. This remains a read-only lookup.
    const document=await send('DOM.getDocument',{depth:-1,pierce:false});
    const found=await send('DOM.querySelector',{nodeId:document.root.nodeId,selector});
    if (!found.nodeId) throw new Error('upload_target_missing');
    const described=await send('DOM.describeNode',{nodeId:found.nodeId});
    const node=described.node;
    const attrs=Object.fromEntries((node.attributes||[]).reduce((out,value,index,array)=>{if(index%2===0)out.push([value,array[index+1]]);return out;},[]));
    if (node.nodeName!=='INPUT' || attrs.type!=='file') throw new Error('upload_target_not_single_file_input');
    await send('DOM.setFileInputFiles',{files:fullPaths,nodeId:found.nodeId});
    uploadedFixture=filename;
    const started=Date.now(); let sawProgress=false, lastPhase=null;
    while (Date.now()-started<1200) {
      const phase=await evaluate("(() => {const e=document.querySelector('[role=status][aria-live=polite]');return e?(e.innerText||e.textContent||'').trim():null;})()");
      if (phase) {
        sawProgress=true;
        if (phase!==lastPhase) uploadProgressSamples.push({elapsed_ms:Date.now()-started,text:phase.slice(0,240)});
        lastPhase=phase;
      } else if ((sawProgress && Date.now()-started>100) || Date.now()-started>500) break;
      await new Promise(resolve=>setTimeout(resolve,50));
    }
  } else if (name==='click') {
    const selector=args.selector, label=args.label;
    if (typeof label!=='string' || !label.trim() || label.length>180) throw new Error('click_label_required');
    const expression="(() => {const norm=s=>(s||'').replace(/\\s+/g,' ').trim();const candidate=e=>!!e&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0&&getComputedStyle(e).visibility!=='hidden'&&getComputedStyle(e).display!=='none'&&(e.tagName==='SUMMARY'||!e.closest('details:not([open])'))&&!e.disabled&&e.type!=='submit'&&!(e.closest('form')&&e.tagName==='BUTTON'&&e.type!=='button');let e=null;try{e=document.querySelector("+JSON.stringify(selector)+")}catch{};if(!candidate(e)||norm(e.getAttribute('aria-label')||e.innerText||e.textContent)!==norm("+JSON.stringify(label)+")){const matches=[...document.querySelectorAll('button,a,summary,[role=button],[role=link]')].filter(x=>candidate(x)&&norm(x.getAttribute('aria-label')||x.innerText||x.textContent)===norm("+JSON.stringify(label)+"));if(matches.length!==1)return null;e=matches[0];}e.scrollIntoView({block:'center',inline:'nearest'});const r=e.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight||r.right<=0||r.left>=innerWidth)return null;return {x:r.x+r.width/2,y:r.y+r.height/2,tag:e.tagName,href:e.tagName==='A'?e.href:null,label:norm(e.getAttribute('aria-label')||e.innerText||e.textContent),selector:e.id?'#'+CSS.escape(e.id):"+JSON.stringify(selector)+"};})()";
    const box=await evaluate(expression);
    if (!box) throw new Error('click_target_not_allowed_or_visible');
    if (box.href && new URL(box.href).origin!==targetOrigin) throw new Error('cross_origin_link_blocked');
    if (box.tag==='SUMMARY') {
      await evaluate("(() => {const e=document.querySelector("+JSON.stringify(box.selector)+");if(!e)return false;e.click();return true;})()");
    } else {
      await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:box.x,y:box.y});
      await send('Input.dispatchMouseEvent',{type:'mousePressed',x:box.x,y:box.y,button:'left',clickCount:1});
      await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:box.x,y:box.y,button:'left',clickCount:1});
    }
  } else if (name==='type') {
    const selector=args.selector, value=args.value;
    if (typeof value!=='string'||value.length>500||/[\r\n]/.test(value)) throw new Error('typed_value_limit');
    const expression="(() => {const e=document.querySelector("+JSON.stringify(selector)+");if(!e||!['INPUT','TEXTAREA'].includes(e.tagName)||['password','email','tel','hidden'].includes(e.type)||e.disabled||e.readOnly) return false;e.focus();e.select();return true;})()";
    const focused=await evaluate(expression);
    if (!focused) throw new Error('type_target_not_allowed');
    await send('Input.insertText',{text:value});
    typedInputs.set(selector,hash(Buffer.from(value,'utf8')));
  } else if (name==='scroll') {
    const delta=Math.max(-900,Math.min(900,args.delta));
    await send('Input.dispatchMouseEvent',{type:'mouseWheel',x:500,y:400,deltaX:0,deltaY:delta});
  } else if (name==='wait') {
    const ms=Math.max(0,Math.min(3000,args.ms)); await new Promise(r=>setTimeout(r,ms));
  } else throw new Error('unknown_tool');
  const state=await observe(); const capture=await screenshot();
  return {text:'Action '+name+' completed.\nURL '+state.url+'\nTitle '+state.title+'\n'+state.text,
    facts:{...state,last_action:name,...(name==='click'?{last_action_label:args.label}:{}),...(uploadedFixture?{uploaded_fixture:uploadedFixture,upload_progress_samples:uploadProgressSamples}:{})},
    captures:[capture],checks:[]};
}
async function close() {
  try { if(ws) ws.close(); } catch {}
  if(chrome && chrome.exitCode===null) { chrome.kill('SIGTERM'); await new Promise(resolve=>{const t=setTimeout(()=>{if(chrome.exitCode===null) chrome.kill('SIGKILL');resolve();},3000);chrome.once('exit',()=>{clearTimeout(t);resolve();});}); }
  try { if(proxy) await new Promise(resolve=>proxy.close(resolve)); } catch {}
  return {stopped:!chrome||chrome.exitCode!==null};
}
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
