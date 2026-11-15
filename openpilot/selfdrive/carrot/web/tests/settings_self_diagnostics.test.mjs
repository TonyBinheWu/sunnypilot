import test from 'node:test';
import assert from 'node:assert/strict';
import {classifyDiagnosticText,createDiagnosticErrors} from '../src/features/tools/diagnostics/state.js';
import {createSelfDiagnostics} from '../src/features/tools/diagnostics/index.js';
import {diagnosticText} from '../src/features/tools/diagnostics/messages.js';

test('automatic error buffer is bounded, temporary, deduplicated and excludes secrets and diagnostic recursion',()=>{
  let time=100;const store=createDiagnosticErrors({clock:()=>time});
  assert.equal(store.record({url:'/api/device/diagnostics',code:'FAILED'}),false);
  store.record({url:'http://192.168.1.2/api/params_bulk?token=secret',status:500,code:'FAIL',body:'password',message:'private'});
  store.record({url:'/api/params_bulk?other=secret',status:500,code:'FAIL'});
  assert.equal(store.list().length,1);
  assert.deepEqual(store.list()[0],{time:100,kind:'request',path:'/api/params_bulk',status:500,code:'FAIL'});
  for(let i=0;i<30;i++){time+=30001;store.record({kind:'script',code:'SCRIPT_ERROR'});}
  assert.equal(store.list().length,12);time+=900001;assert.equal(store.list().length,0);
});
test('local text interpretation offers a direction, including unknowns, without claiming a diagnosis',()=>{
  for(const [text,code] of [['CAN 錯誤請檢查連線','can_invalid'],['短暫處理逾時','processing_delay'],['NV16 retry','model_error'],['缺少麥克風權限','speech_setup'],['影像沒有畫面','camera_error']])assert.equal(classifyDiagnosticText(text),code);
  assert.equal(classifyDiagnosticText('unrecognized xyz'),null);
  assert.equal(classifyDiagnosticText("can't connect to Wi-Fi"),'network_error');
  assert.equal(classifyDiagnosticText('WebSocket retry'),'network_error');
  assert.equal(classifyDiagnosticText('retry'),null);
});
test('an error triggers only a debounced read-only check; it never retries a write or performs repairs',async()=>{
  const timers=[],calls=[],listeners={};
  const target={document:{hidden:false,getElementById:()=>null},addEventListener:(name,fn)=>{listeners[name]=fn;},
    setTimeout:(fn,ms)=>{timers.push({fn,ms});return timers.length;},clearTimeout:()=>{},
    fetch:async(url,options)=>{calls.push({url,options});return {ok:true,json:async()=>({ok:true,version:1,checks:[],actions:['reboot'],ticket:'t'})};}};
  const api=createSelfDiagnostics(target);api.install();
  listeners['carrot:diagnosticerror']({detail:{url:'/api/param_set',status:500,code:'FAILED'}});
  api.record({kind:'script',code:'SCRIPT_ERROR'});
  assert.equal(timers.filter(t=>t.ms===1000).length,1);
  timers.find(t=>t.ms===1000).fn();await api.check();
  assert.equal(calls.length,1);assert.equal(calls[0].url,'/api/device/diagnostics');assert.equal(calls[0].options.method,undefined);
  assert.equal(api.errors().length,2);
});
test('Traditional Chinese explanations distinguish observation, missing data and uncertain recovery',()=>{
  const target={CarrotWebSettingsState:{web_language:'zh-tw'}};
  assert.match(diagnosticText('repair_unconfirmed',target),/無法確認/);
  assert.match(diagnosticText('offroad_help',target),/正常現象/);
  assert.match(diagnosticText('can_invalid_help',target),/不代表所有 CAN/);
});
test('prolonged visible Vision waiting triggers a check, while ready and background states cancel it',()=>{
  const timers=new Map(),listeners={};let serial=0;
  const target={document:{hidden:false,getElementById:()=>null},addEventListener:(name,fn)=>{listeners[name]=fn;},
    setTimeout:(fn,ms)=>{timers.set(++serial,{fn,ms});return serial;},clearTimeout:id=>timers.delete(id)};
  const api=createSelfDiagnostics(target);api.install();
  const event=phase=>listeners['carrot:visionstatechange']({detail:{state:{active:true,phase}}});
  event('recovering');assert.equal([...timers.values()].filter(t=>t.ms===10000).length,1);
  event('ready');assert.equal(timers.size,0);
  event('first-frame-waiting');const wait=[...timers.values()].find(t=>t.ms===10000);wait.fn();
  assert.equal(api.errors()[0].code,'VISION_WAITING');
  event('ready');target.document.hidden=true;event('recovering');
  [...timers.values()].filter(t=>t.ms===10000).at(-1).fn();assert.equal(api.errors().length,1);
});
