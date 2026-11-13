#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import vm from 'node:vm';
import {createRequire} from 'node:module';

const args=process.argv.slice(2);
const get=(name)=>{const i=args.indexOf(name);return i>=0?args[i+1]:null;};
const product=path.resolve(get('--product-root')||'');
const output=path.resolve(get('--output')||'');
if(!get('--product-root')||!get('--output')||!fs.existsSync(product+'/package.json')) throw new Error('usage: --product-root <insta-tracker-worktree> --output <new-private-directory>');
if(fs.existsSync(output) && fs.readdirSync(output).length) throw new Error('output_directory_not_empty');
fs.mkdirSync(output,{recursive:true,mode:0o700});
const require=createRequire(product+'/package.json');
const ts=require('typescript');
const fflate=require('fflate');
const fixed=Date.parse('2026-11-13T00:00:00Z');
class FixedDate extends Date { constructor(...v){super(...(v.length?v:[fixed]));} static now(){return fixed;} }
const zipSync=(entries,opts={})=>fflate.zipSync(entries,{...opts,mtime:new FixedDate(fixed)});
const sourcePath=product+'/src/core/sampleData.ts';
const source=fs.readFileSync(sourcePath,'utf8');
const compiled=ts.transpileModule(source,{fileName:sourcePath,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}});
const mod={exports:{}};
new vm.Script(compiled.outputText,{filename:'peekly-sampleData.cjs'}).runInNewContext({
  exports:mod.exports,
  require:(name)=>{if(name!=='fflate')throw new Error('dependency_not_allowlisted');return {...fflate,zipSync};},
  Date:FixedDate
});
if(typeof mod.exports.buildSampleExportZip!=='function') throw new Error('sample_zip_builder_missing');
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const files=[];
for(const kind of ['previous','current']){
  const name='peekly-sample-'+kind+'.zip';
  const bytes=Buffer.from(mod.exports.buildSampleExportZip(kind));
  fs.writeFileSync(path.join(output,name),bytes,{flag:'wx',mode:0o600});
  files.push({name,bytes:bytes.length,sha256:digest(bytes),scenario:kind});
}
const manifest={schema_version:'peekly-synthetic-fixtures.v1',version:'peekly-sample-fixtures-v2',created_at:'2026-11-13T00:00:00Z',
  product_id:'peekly',source:{path:'src/core/sampleData.ts',sha256:digest(Buffer.from(source)),typescript:ts.version,fflate:require(product+'/node_modules/fflate/package.json').version},files};
fs.writeFileSync(path.join(output,'fixture-manifest.json'),JSON.stringify(manifest,null,2)+'\n',{flag:'wx',mode:0o600});
console.log(JSON.stringify({files,manifest_sha256:digest(Buffer.from(fs.readFileSync(path.join(output,'fixture-manifest.json'))))}));
