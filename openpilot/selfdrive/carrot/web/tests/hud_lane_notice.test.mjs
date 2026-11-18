import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {laneChangeNotice,createLaneChangeNotice} from '../src/features/drive/contents/vision/hud/lane_change_notice.js';
import {createDriveDataActivity} from '../src/shared/activity/drive_data.js';

const ready={ready:true,car:{gearShifter:'drive',vEgo:30,canValid:true,canTimeout:false},latActive:true,alertSize:'none'};
for(const direction of ['left','right'])for(const [source,kind] of Object.entries({forecast_desire:'forecast',forecast_path:'forecast',navigation_exit:'exit',lane_completed:'completed',lane_cancelled:'cancelled',lane_unverified:'unverified'})){
  test(`${source} ${direction} keeps forecast and completion separate`,()=>{
    assert.equal(laneChangeNotice({indicatorPrepareDirection:direction,indicatorPrepareSource:source},ready)?.kind,kind);
  });
}
test('an executing FSM has priority over a contrary forecast',()=>{
  assert.deepEqual(laneChangeNotice({laneChangeState:'laneChangeStarting',laneChangeDirection:'left',indicatorPrepareDirection:'right',indicatorPrepareSource:'forecast_desire'},ready),{kind:'changing',direction:'left',lampOn:false});
});
test('completion remains visible while the held lamp waits, and waiting alone does not announce another change',()=>{
  const meta={laneChangeState:'preLaneChange',laneChangeDirection:'left',indicatorPrepareDirection:'left',indicatorPrepareSource:'lane_completed'};
  assert.equal(laneChangeNotice(meta,ready)?.kind,'completed');
  meta.indicatorPrepareSource='lane_waiting_driver';assert.equal(laneChangeNotice(meta,ready),null);
});
test('native warnings, parked, replay, stale and inactive input hide the notice',()=>{
  const meta={indicatorPrepareDirection:'left',indicatorPrepareSource:'forecast_desire'};
  for(const changes of [{ready:false},{alertSize:'full'},{offroad:true},{replay:true},{latActive:false},{car:{gearShifter:'park',vEgo:0}},
    {car:{...ready.car,canValid:false}},{car:{...ready.car,canTimeout:true}},{car:{...ready.car,canValid:undefined}}]){
    assert.equal(laneChangeNotice(meta,{...ready,...changes}),null);
  }
});

function fixture(){
  let now=1000,id=0;
  const timers=new Map();
  class Node{constructor(){this.children=[];this.dataset={};this.textContent='';}setAttribute(){}appendChild(n){this.children.push(n);return n;}remove(){this.removed=true;}}
  const doc={createElement:()=>new Node()};
  const target={document:doc,performance:{now:()=>now},setInterval:f=>{timers.set(++id,f);return id;},clearInterval:n=>timers.delete(n),
    CarrotHudState:{carState:ready.car,selfdriveState:{alertSize:'none'}},
    CarrotOverlayState:{modelV2:{meta:{indicatorPrepareDirection:'left',indicatorPrepareSource:'forecast_desire'}},carControl:{latActive:true}},
    CarrotStateReceivedAtMonotonic:Object.fromEntries(['modelV2','carState','carControl','selfdriveState'].map(s=>[s,now]))};
  return {doc,target,timers,tick(ms){now+=ms;for(const f of [...timers.values()])f();},refresh(){for(const k in target.CarrotStateReceivedAtMonotonic)target.CarrotStateReceivedAtMonotonic[k]=now;}};
}
test('page switches cancel the timer, re-entry reads fresh state, and stale data clears without another HUD packet',()=>{
  const h=fixture(),widget=createLaneChangeNotice(h.doc,h.target);
  widget.setActive(true);assert.equal(widget.el.hidden,false);assert.equal(h.timers.size,1);
  h.tick(501);assert.equal(widget.el.hidden,true);
  widget.setActive(false);assert.equal(h.timers.size,0);
  h.refresh();widget.setActive(true);assert.equal(widget.el.hidden,false);
  h.target.CarrotHudState.selfdriveState.alertSize='mid';h.tick(1);assert.equal(widget.el.hidden,true);
  widget.destroy();assert.equal(h.timers.size,0);
  widget.setActive(true);assert.equal(h.timers.size,0);
});

test('HUD-only view obtains model data once, survives reentrant activity updates, and releases it on page exit',()=>{
  const h=fixture(),widget=createLaneChangeNotice(h.doc,h.target);
  widget.setActive(true); // The activity publisher may load after the HUD.
  const activity=createDriveDataActivity({target:{}});
  h.target.CarrotDriveDataActivity=activity;
  const stop=activity.subscribe(()=>widget.render());
  h.tick(100);widget.setActive(true);widget.render();
  assert.equal(activity.snapshot().leaseCount,1);
  assert.equal(activity.isActive('hud'),true);assert.equal(activity.isActive('overlay'),true);
  assert.equal(activity.isActive('tracks'),false);assert.equal(activity.isActive('ar'),false);
  widget.setActive(false);assert.equal(activity.snapshot().leaseCount,0);
  widget.setActive(true);assert.equal(activity.snapshot().leaseCount,1);
  widget.destroy();assert.equal(activity.snapshot().leaseCount,0);stop();
});

test('backgrounding releases the data lease and expiry timer; foregrounding cannot revive stale notices',()=>{
  const h=fixture(),handlers=new Map();
  h.doc.addEventListener=(name,f)=>handlers.set(name,f);h.doc.removeEventListener=name=>handlers.delete(name);
  const activity=createDriveDataActivity({target:{}});h.target.CarrotDriveDataActivity=activity;
  const widget=createLaneChangeNotice(h.doc,h.target);widget.setActive(true);
  h.doc.hidden=true;handlers.get('visibilitychange')();
  assert.equal(activity.snapshot().leaseCount,0);assert.equal(h.timers.size,0);assert.equal(widget.el.hidden,true);
  h.tick(800);h.doc.hidden=false;handlers.get('visibilitychange')();
  assert.equal(activity.snapshot().leaseCount,1);assert.equal(h.timers.size,1);assert.equal(widget.el.hidden,true);
  h.refresh();widget.render();assert.equal(widget.el.hidden,false);
  widget.destroy();assert.equal(handlers.size,0);assert.equal(activity.snapshot().leaseCount,0);assert.equal(h.timers.size,0);
});
test('browser decodes the actual Python compact producer fixture and accepts the older shorter frame',()=>{
  const window={};
  vm.runInNewContext(readFileSync(new URL('../js/realtime/vision_compact.js',import.meta.url),'utf8'),{window,TextDecoder,Uint8Array,ArrayBuffer,DataView});
  // Generated by encode_carrot_state_frame using SimpleNamespace model values.
  const bytes=Uint8Array.from(Buffer.from('Q1ZTMQkAEQApAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABDwBmb3JlY2FzdF9kZXNpcmU=','base64'));
  const frame=window.CarrotVisionCompact.decodeFrame(bytes);
  assert.equal(frame.decoded.frameId,41);
  assert.equal(laneChangeNotice(frame.decoded.meta,ready)?.direction,'left');
  const legacy=Uint8Array.from(Buffer.from('Q1ZTMQkAEQApAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA','base64'));
  assert.equal(laneChangeNotice(window.CarrotVisionCompact.decodeFrame(legacy).decoded.meta,ready),null);
});

test('compact health and numeric alert gates allow only fresh valid vehicle state',()=>{
  const window={};vm.runInNewContext(readFileSync(new URL('../js/realtime/vision_compact.js',import.meta.url),'utf8'),{window,TextDecoder,Uint8Array,ArrayBuffer,DataView});
  const decode=b64=>window.CarrotVisionCompact.decodeFrame(Uint8Array.from(Buffer.from(b64,'base64'))).decoded;
  const car=decode('Q1ZTMQEAEQAAAPBBAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAA=='),sd=decode('Q1ZTMQYAEQAAAAAAAAAAAAAA');
  const meta={indicatorPrepareDirection:'left',indicatorPrepareSource:'forecast_desire'};
  assert.equal(sd.alertSize,0);assert.equal(car.canValid,true);
  assert.equal(laneChangeNotice(meta,{...ready,car,alertSize:sd.alertSize})?.kind,'forecast');
  car.steeringPressed=true;assert.equal(laneChangeNotice(meta,{...ready,car,alertSize:sd.alertSize}),null);
  car.steeringPressed=false;car.canValid=false;assert.equal(laneChangeNotice(meta,{...ready,car,alertSize:sd.alertSize}),null);
});
