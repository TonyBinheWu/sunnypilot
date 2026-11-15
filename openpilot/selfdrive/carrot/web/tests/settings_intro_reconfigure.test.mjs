import assert from 'node:assert/strict';
import test from 'node:test';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {setupBody,setupChanges} from '../src/features/intro/draft.js';
import {openSetupGuide} from '../src/features/tools/reconfigure.js';
function mockGlobal(t,key,value){const previous=Object.getOwnPropertyDescriptor(globalThis,key);Object.defineProperty(globalThis,key,{value,writable:true,configurable:true});t.after(()=>{if(previous)Object.defineProperty(globalThis,key,previous);else delete globalThis[key];});}

function apiContext(flags={},reply={ok:true,applied:{},webLanguage:'zh-tw',requiresRestart:false}){
  const requests=[],writes=[],labels=[];
  const ctx=vm.createContext({CarrotIntro:{ctx:flags,t:key=>key},setParam:(...a)=>writes.push(a),applyCurrentCarLabel:(...a)=>labels.push(a),
    fetch:async(url,options)=>{requests.push({url,options});return {ok:true,json:async()=>reply};}});
  vm.runInContext(readFileSync(new URL('../src/features/intro/api.js',import.meta.url),'utf8'),ctx);
  return {api:ctx.CarrotIntroApi,requests,writes,labels};
}
test('repeat setup language/car/HDA/preset/completion remain a draft without writes, labels or completion resets',async()=>{
  const x=apiContext({reconfigure:true});
  await x.api.setLanguage('zh-tw');await x.api.setCar('Kia Test','Test');await x.api.setHda(0);await x.api.applyPreset('stock');await x.api.complete('test');
  await assert.rejects(x.api.restoreFile({name:'backup.json'}),/againRestore/);
  assert.deepEqual(x.requests,[]);assert.deepEqual(x.writes,[]);assert.deepEqual(x.labels,[]);
  await x.api.reconfigure({revision:'revision',lang:'zh-tw',car:'Kia Test',hda:0,preset:null});
  assert.equal(x.requests.length,1);assert.equal(x.requests[0].url,'/api/intro/reconfigure');
});
test('an incomplete apply response cannot be presented as saved',async()=>{
  const x=apiContext({reconfigure:true},{});
  await assert.rejects(x.api.reconfigure({}),/apply_unconfirmed/);
});
test('preview remains read-only, including the new apply facade; first-install writes retain their existing paths',async()=>{
  const preview=apiContext({preview:true,reconfigure:true});await preview.api.setLanguage('en');await preview.api.reconfigure({});assert.equal(preview.requests.length,0);
  const original=apiContext({});await original.api.setHda(1);await original.api.setCar('Kia Test','Test');
  assert.equal(original.requests[0].url,'/api/param_set');assert.deepEqual(original.writes,[['CarSelected3','Kia Test']]);
  await assert.rejects(original.api.reconfigure({}),/invalid_selection/);
});
test('review shows only changed selections using server-provided preset values; keep preserves custom tuning',()=>{
  const baseline={revision:'r',car:'Kia Test',lang:'zh-tw',values:{CarSelected3:'Kia Test',CanfdHDA2:1,EnableCornerRadar:2},
    presets:{camera_long:{EnableCornerRadar:0}},titles:{EnableCornerRadar:{'zh-tw':'角雷達'}}};
  const ctx={baseline,lang:'zh-tw',car:'Kia Test',hda:null,preset:null};
  assert.deepEqual(setupChanges(ctx),[]);
  ctx.preset='camera_long';ctx.hda=0;
  assert.deepEqual(setupChanges(ctx).map(r=>[r.key,r.before,r.after]),[['CanfdHDA2',1,0],['EnableCornerRadar',2,0]]);
  assert.equal(setupChanges(ctx)[1].title,'角雷達');
  assert.deepEqual(setupBody(ctx),{revision:'r',lang:'zh-tw',car:'Kia Test',hda:0,preset:'camera_long'});
  assert.equal(baseline.values.EnableCornerRadar,2);
});
test('Tools reopens the existing shell with current state and performs a GET only',async t=>{
  const calls=[],seed={ok:true,revision:'r',car:'Kia Test'};
  t.mock.method(globalThis,'fetch',async(url,options)=>{calls.push([url,options]);return {ok:true,json:async()=>seed};});
  mockGlobal(t,'CarrotIntroShell',{open:options=>calls.push(options)});
  await openSetupGuide();
  assert.equal(calls[0][0],'/api/intro/reconfigure');assert.equal(calls[0][1].cache,'no-store');assert.equal(calls[1].reconfigure,seed);
});
test('unavailable or moving state produces a localized hint without opening or resetting the wizard',async t=>{
  let opened=false;const messages=[];
  t.mock.method(globalThis,'fetch',async()=>({ok:false,json:async()=>({ok:false,error:'park_required'})}));
  mockGlobal(t,'CarrotIntroShell',{open:()=>{opened=true;}});
  mockGlobal(t,'appAlert',async message=>messages.push(message));
  await openSetupGuide();assert.equal(opened,false);assert.match(messages[0],/Park/);
});
