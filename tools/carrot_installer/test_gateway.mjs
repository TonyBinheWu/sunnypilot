import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createGateway,retarget,patchSlot,PROFILES,TARGET,UPSTREAM,CLASSIC_UPSTREAM} from './gateway_worker.mjs';

const root=process.env.CARROT_INSTALLER_FIXTURES||'.analysis/archive/2026-11-16/install-loop/upstream-fixtures';
const raw=Object.fromEntries(await Promise.all(Object.keys(PROFILES).map(async id=>[id,new Uint8Array(await readFile(`${root}/${id}.elf`))])));
const embedded=Object.fromEntries(Object.entries(raw).map(([id,data])=>[id,Buffer.from(data).toString('base64')]));
const req=(version='19.8',path='/c4',headers={})=>new Request('https://install.test'+path,{headers:{'User-Agent':'AGNOSSetup-'+version,'X-openpilot-device-type':'mici',...headers}});

test('observed 19.8-carrot-bt1 succeeds live and with compact pinned fallback',async()=>{
  const live=createGateway({fetchImpl:async()=>new Response(raw.carrotBt1),embedded});
  const response=await live(req('19.8-carrot-bt1'));assert.equal(response.status,200);
  const expected=await retarget(raw.carrotBt1);
  assert.deepEqual(new Uint8Array(await response.arrayBuffer()),expected.bytes);
  const compact={...embedded};delete compact.carrotBt1;
  const offline=createGateway({fetchImpl:async()=>{throw Error('offline');},embedded:compact});
  const fallback=await offline(req('19.8-carrot-bt1'));assert.equal(fallback.status,200);
  assert.deepEqual(new Uint8Array(await fallback.arrayBuffer()),expected.bytes);
  assert.equal(fallback.headers.get('X-Carrot-Profile'),'carrotBt1');
});

for(const id of Object.keys(PROFILES))test(`actual ${id} ELF changes reserved slots only and retains source bytes`,async()=>{
  const before=raw[id].slice(),value=await retarget(raw[id]);
  assert.equal(value.id,id);assert.deepEqual(raw[id],before);assert.equal(value.bytes.length,before.length);
  const text=new TextDecoder('latin1').decode(value.bytes);assert.ok(text.includes(TARGET+(id==='classic'?'\0':'?')));
  if(id!=='current'){
    assert.ok(text.includes('/data/.carrot_cache_v3\0'));
    assert.ok(!text.includes('/data/.openpilot_cache\0'));
  }else assert.ok(text.includes('git remote set-url origin'));
  for(let i=0;i<before.length;i++)if(!value.slots.some(([a,b])=>a<=i&&i<b))assert.equal(value.bytes[i],before[i]);
  assert.equal(value.sha,createHash('sha256').update(value.bytes).digest('hex'));
  if(id!=='compat'){
    const a=new TextDecoder('latin1').decode(before);const start=a.indexOf('carrot-wip');
    assert.equal(text.slice(start,a.indexOf('\0',start)),a.slice(start,a.indexOf('\0',start)));
  }
});
test('reject changed, non-ELF, missing, duplicate and oversized configuration slots',async()=>{
  const altered=raw.current.slice();altered[400]^=1;await assert.rejects(retarget(altered),/unverified/);
  await assert.rejects(retarget(new Uint8Array(64)),/unverified/);
  for(const [data,marker,value] of [[new TextEncoder().encode('x?\0x?\0'),'x?','a'],[new Uint8Array(10),'absent?','x'],[new TextEncoder().encode('a?\0'),'a?','too-long']])assert.throws(()=>patchSlot(data,marker,value));
});
test('real profile negotiation preserves only version/device headers and deduplicates concurrent fetches',async()=>{
  let calls=0;
  const handler=createGateway({embedded,fetchImpl:async(url,init)=>{
    calls++;assert.equal(url,UPSTREAM);assert.deepEqual(Object.keys(init.headers).sort(),['User-Agent','X-openpilot-device-type']);
    assert.equal(JSON.stringify(init).includes('PRIVATE'),false);return new Response(raw.current);
  }});
  const requests=Array.from({length:5},()=>handler(req('19.8','/c4?repo=attacker',{Authorization:'PRIVATE','X-openpilot-serial':'PRIVATE',Cookie:'PRIVATE'})));
  for(const response of await Promise.all(requests)){
    assert.equal(response.status,200);const bytes=new Uint8Array(await response.arrayBuffer());
    assert.equal(bytes.length,PROFILES.current.size);assert.equal(response.headers.get('Content-Type'),'application/octet-stream');
    assert.equal(response.headers.get('X-Carrot-SHA256'),createHash('sha256').update(bytes).digest('hex'));
  }
  assert.equal(calls,1);
});
test('read-only diagnostic reflects version without contacting upstream or executing an installer',async()=>{
  const handler=createGateway({fetchImpl:()=>{throw Error('must not fetch');}});
  const response=await handler(req('19.6.3-carrot','/check',{'X-openpilot-serial':'PRIVATE'}));
  assert.equal(response.status,409);const text=await response.text();assert.ok(text.includes('19.6.3-carrot'));assert.ok(!text.includes('PRIVATE'));assert.ok(!text.startsWith('\x7fELF'));
});
test('known native compat profile bypasses the documented broken upstream variant',async()=>{
  const handler=createGateway({embedded,fetchImpl:()=>{throw Error('must not fetch');}});
  const response=await handler(req('19.6.3-carrot'));assert.equal(response.status,200);assert.equal(response.headers.get('X-Carrot-Profile'),'compat');
});
test('offline fallback is only for verified exact versions; changed bytes never fall back',async()=>{
  const offline=createGateway({embedded,fetchImpl:async()=>new Response('offline',{status:503})});
  assert.equal((await offline(req('19.8'))).status,200);
  assert.equal((await offline(req('unknown'))).status,409);
  const changed=createGateway({embedded,fetchImpl:async()=>new Response(new Uint8Array(100))});
  assert.equal((await changed(req('19.8'))).status,409);
});
test('browser/unknown-device/write requests cannot trigger installer delivery',async()=>{
  const handler=createGateway({embedded,fetchImpl:()=>{throw Error('must not fetch');}});
  assert.equal((await handler(new Request('https://install.test/'))).headers.get('Content-Type'),'text/html; charset=utf-8');
  assert.equal((await handler(req('19.8','/c4',{'X-openpilot-device-type':'neo'}))).status,409);
  assert.equal((await handler(new Request('https://install.test/c4',{method:'POST'}))).status,405);
  assert.equal((await handler(req('19.8','/arbitrary'))).status,404);
});

const matrix=JSON.parse(await readFile(`${root}/routing-matrix.json`,'utf8'));
for(const {device,version,profile} of matrix)test(`verified download routing ${device}/${version||'unversioned'}`,async()=>{
  let called=0;
  const handler=createGateway({embedded,fetchImpl:async(url,init)=>{
    called++;assert.equal(url,version?UPSTREAM:CLASSIC_UPSTREAM);
    assert.equal(init.headers['X-openpilot-device-type'],device);
    assert.equal(init.headers['User-Agent'],version?'AGNOSSetup-'+version:'AGNOSSetup');
    return new Response(raw[profile]);
  }});
  const request=new Request('https://install.test/',{headers:{'User-Agent':version?'AGNOSSetup-'+version:'AGNOSSetup','X-openpilot-device-type':device}});
  const response=await handler(request);
  assert.equal(response.status,200);assert.equal(response.headers.get('X-Carrot-Profile'),profile);
  assert.equal(response.headers.get('X-Carrot-Device'),device);assert.equal(called,1);
  assert.deepEqual(new Uint8Array(await response.arrayBuffer()),(await retarget(raw[profile])).bytes);
});

test('same OS cache and native C4 override remain isolated across device types',async()=>{
  const calls=[];
  const handler=createGateway({embedded,fetchImpl:async(_,init)=>{
    const device=init.headers['X-openpilot-device-type'];calls.push(device);
    return new Response(raw[device==='tici'?'current':'legacy']);
  }});
  for(const [device,profile] of [['tici','current'],['tizi','legacy'],['mici','compat'],['tici','current'],['tizi','legacy']]){
    const response=await handler(req('19.6.3-carrot','/',{'X-openpilot-device-type':device}));
    assert.equal(response.status,200);assert.equal(response.headers.get('X-Carrot-Profile'),profile);
  }
  assert.deepEqual(calls,['tici','tizi']);
});

test('all three supported device types can negotiate concurrently on a cold gateway',async()=>{
  const handler=createGateway({embedded,fetchImpl:async()=>new Response(raw.current)});
  const responses=await Promise.all(['tici','tizi','mici'].map(device=>handler(req('19.8','/',{'X-openpilot-device-type':device}))));
  for(const response of responses)assert.equal(response.status,200);
});

test('offline snapshots are keyed by both device and OS; valid wrong-device templates are rejected',async()=>{
  const handler=createGateway({embedded,fetchImpl:async()=>{throw Error('offline');}});
  for(const [device,profile] of [['tici','current'],['tizi','legacy'],['mici','legacy']]){
    const response=await handler(req('19.6.3','/',{'X-openpilot-device-type':device}));
    assert.equal(response.status,200);assert.equal(response.headers.get('X-Carrot-Profile'),profile);
  }
  const wrong=createGateway({embedded,fetchImpl:async()=>new Response(raw.compat)});
  assert.equal((await wrong(req('19.8','/',{'X-openpilot-device-type':'tizi'}))).status,409);
  const wrongClassic=createGateway({embedded,fetchImpl:async()=>new Response(raw.classic)});
  assert.equal((await wrongClassic(req('19.8'))).status,409);
});

test('unversioned requests require a known C3 device; diagnostics reflect each real device',async()=>{
  const handler=createGateway({embedded,fetchImpl:async()=>{throw Error('offline');}});
  for(const device of ['mici','unknown',''])assert.equal((await handler(new Request('https://install.test/',{headers:{'User-Agent':'AGNOSSetup','X-openpilot-device-type':device}}))).status,409);
  for(const device of ['tici','tizi','mici']){
    const response=await handler(req('19.8','/check',{'X-openpilot-device-type':device}));
    assert.equal(response.status,409);assert.ok((await response.text()).includes('Device: '+device));
  }
});
