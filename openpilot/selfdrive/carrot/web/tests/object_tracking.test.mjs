import test from 'node:test';
import assert from 'node:assert/strict';
import {createObjectTracker} from '../src/features/drive/contents/vision/hud/object_tracker.js';
import {createPerceptionScene,createRenderMeter} from '../src/features/drive/contents/vision/hud/perception_scene.js';

const car=(x,y=0,more={})=>({kind:'car',x,y,probability:.9,...more});
function rig(source='vision'){
  const tracker=createObjectTracker();
  const motion={speed:15,yaw:0};
  const frame=(stamp,objects,extra={})=>{tracker.ingest(source,{objects,stamp,...extra},stamp,motion);return tracker.sample(stamp,motion);};
  return {tracker,frame,at:t=>tracker.sample(t,motion)};
}
test('one leading car keeps its ID; repeated renders or identical capture times cannot confirm a candidate',()=>{
  const {frame,at,tracker}=rig();
  assert.deepEqual(frame(0,[car(32)]),[]);assert.deepEqual(frame(0,[car(32)]),[]);
  assert.deepEqual(at(90),[]);
  let id;
  for(let t=100;t<=6000;t+=100){
    const [o]=frame(t,[car(32-t/1000,0,{id:'slot-'+t%3})]);
    id??=o.id;assert.equal(o.id,id);assert.equal(o.state,'confirmed');
    assert.ok(Math.abs(o.x-(32-t/1000))<.6);
  }
  assert.equal(tracker.snapshot(6000).created,1);
});
test('acceleration, braking, turn and lane change are filtered continuously using actual intervals',()=>{
  const {frame,at}=rig();
  let time=0,id,prev;
  for(let i=0;i<70;i++){
    time+=[81,128,114,95][i%4];const s=time/1000;
    const x=35+2*Math.sin(s),y=1.7*(1+Math.tanh(s-3));
    const [o]=frame(time,[car(x,y)]);
    if(!o)continue;
    id??=o.id;assert.equal(o.id,id);assert.ok(Number.isFinite(o.heading));assert.ok(Math.abs(o.y-y)<.65);
    const next=at(time+35)[0];assert.ok(Math.hypot(o.x-next.x,o.y-next.y)<.65);
    if(prev)assert.ok(Math.abs(o.heading-prev.heading)<.18);prev=o;
  }
});
test('passing car and two same-class crossing targets keep their IDs across reordered detections',()=>{
  const {frame}=rig();let ids;
  for(let i=0;i<24;i++){
    const a=car(18+.8*i,-2+.15*i,{id:'slot-0'}),b=car(34-.65*i,2-.14*i,{id:'slot-1'});
    const out=frame(i*150,i%2?[b,a]:[a,b]);
    if(i===1)ids=out.map(o=>o.id);
    if(i>1){assert.deepEqual(out.map(o=>o.id),ids);assert.ok(Math.abs(out[0].x-a.x)<1.5);assert.ok(Math.abs(out[1].x-b.x)<1.5);}
  }
});
test('a short occlusion uses marked bounded prediction; lost is invisible and expired tracks are removed',()=>{
  const {frame,at,tracker}=rig();frame(0,[car(28)]);const id=frame(250,[car(27)])[0].id;
  assert.equal(frame(500,[])[0].state,'predicted');assert.equal(at(680)[0].id,id);
  assert.equal(frame(750,[car(25)])[0].id,id);
  assert.deepEqual(at(1500),[]);assert.equal(tracker.snapshot(1500).tracks[0].state,'lost');
  assert.deepEqual(at(2100),[]);assert.equal(tracker.snapshot(2100).removed,1);
});
test('exit from calibrated FOV removes the instance immediately, even while it is moving',()=>{
  const {frame,at,tracker}=rig(),geometry={width:640,height:360,fx:500,fy:500,rpy:[0,0,0],heightM:1.2};
  frame(0,[car(10,3.5)],{geometry});frame(250,[car(10,4.2)],{geometry});frame(500,[car(10,5.2)],{geometry});
  const points=at(840);assert.equal(points.length,1);
  assert.deepEqual(at(1090),[]);assert.equal(tracker.snapshot(1090).removed,1);
});
test('native IDs may change collection slot but a different sensor ID or incompatible class never steals a track',()=>{
  const {frame}=rig('radar');const ref=(x,id,slot)=>car(x,0,{kind:'unknown',trackId:id,id:slot,vRel:1});
  frame(0,[ref(24,7,'leadLeft')]);const first=frame(100,[ref(24.1,7,'leadOne')])[0].id;
  frame(200,[ref(24.2,12,'leadOne')]);const out=frame(300,[ref(24.3,12,'leadOne')]);
  assert.notEqual(out.find(o=>o.trackId===12).id,first);
  const q=rig();q.frame(0,[car(10)]);q.frame(100,[car(10)]);const objects=q.frame(200,[car(10,0,{kind:'person'})]);
  assert.ok(objects.every(o=>o.kind!=='person'));
});
test('slow variable FPS confirms on distinct measurements; no teleport or repeated creation',()=>{
  const {frame,at,tracker}=rig();let id;
  for(const t of [0,900,1700,2580,3480,4350]){
    const out=frame(t,[car(40+t*.001)]);
    if(!t) {assert.deepEqual(at(800),[]);continue;}
    id??=out[0].id;assert.equal(id,out[0].id);assert.ok(Math.abs(at(t+450)[0].x-out[0].x)<1.6);
  }
  assert.equal(tracker.snapshot(4350).created,1);
});
test('source disconnect, camera reset, seek, disabled or stale result cannot continue an old track',()=>{
  const target={CarrotVisionCompactStateActive:true},scene=createPerceptionScene(target);
  const update=(at,options={})=>scene.update({vision:{status:'ready',generation:1,capturedAt:at,objects:[car(20)],...options}},at,true,false);
  update(100);const id=update(400)[0].id;
  target.CarrotVisionCompactStateActive=false;assert.deepEqual(update(430),[]);
  target.CarrotVisionCompactStateActive=true;assert.deepEqual(update(650),[]);assert.notEqual(update(950)[0].id,id);
  assert.deepEqual(update(990,{status:'calibration'}),[]);update(1000);update(1300);
  assert.deepEqual(update(1400,{generation:2}),[]);update(1700,{generation:2});assert.deepEqual(update(1750,{status:'stale'}),[]);
});
test('out-of-order and stale frames do not refresh lifespan; image-only observations never appear in 3D',()=>{
  const {frame,tracker,at}=rig();frame(100,[car(12)]);frame(200,[car(12)]);
  tracker.ingest('vision',{stamp:150,objects:[car(30)]},250);
  tracker.ingest('vision',{stamp:500,objects:[{kind:'stop sign',box:[.2,.2,.1,.1]}]},1900);
  assert.deepEqual(at(1900),[]);
});
test('configured auto-start is idempotent, honours replay and manual stop, and never demands fullscreen',()=>{
  const calls=[],t={CarrotVisionState:{available:true},CarrotDeviceRuntimeState:{carrotVisionEnabled:0},CarrotVisionStart:o=>calls.push(o)};
  const scene=createPerceptionScene(t),s={vision_object_detection:true};scene.startConfigured(true,s);assert.equal(calls.length,0);
  t.CarrotDeviceRuntimeState.carrotVisionEnabled=1;t.CarrotVisionReplay={status:()=>({active:true})};scene.startConfigured(true,s);assert.equal(calls.length,0);
  delete t.CarrotVisionReplay;scene.startConfigured(true,s);scene.startConfigured(false,s);scene.startConfigured(true,s);
  assert.deepEqual(calls,[{automaticPerception:true}]);
});
test('two independent sources match only a unique measured radar return; no duplicate when one sensor drops out',()=>{
  const target={CarrotStateReceivedAtMonotonic:{},CarrotVisionCompactStateActive:true},scene=createPerceptionScene(target);
  const lead=(d,id)=>({status:true,dRel:d,yRel:0,vRel:0,radar:true,radarTrackId:id});
  function tick(at,others=[],extra=[]){
    target.CarrotStateReceivedAtMonotonic.radarState=at;
    return scene.update({vision:{status:'ready',capturedAt:at,objects:[car(20),...extra],generation:1},
      radar:{leadsCenter:others}},at,true,false);
  }
  tick(0,[lead(20.1,17)]);const [fused]=tick(100,[lead(20.1,17)]);
  assert.equal(fused.nativeReference,17);assert.equal(fused.kind,'car');
  assert.equal(tick(200,[lead(20.1,17)]).length,1);
  const crowded=[car(20.3,.4)];tick(300,[lead(20.1,17)],crowded);
  assert.equal(tick(400,[lead(20.1,17)],crowded).length,3);
  assert.equal(new Set(tick(500,[lead(20.1,17)],crowded).map(o=>o.id)).size,3);
});
test('invalid native data clears immediately and duplicate native sequences do not confirm a second observation',()=>{
  const target={CarrotStateReceivedAtMonotonic:{}},scene=createPerceptionScene(target);
  const tick=(at,seq,invalid=false)=>{
    target.CarrotStateReceivedAtMonotonic.radarState=at;
    return scene.update({radar:{_sourceSequence:seq,_sourceInvalid:invalid,leadOne:{status:true,dRel:20,yRel:0,vRel:0}}},at,true,false);
  };
  assert.deepEqual(tick(100,71),[]);assert.deepEqual(tick(200,71),[]);
  assert.equal(tick(300,72).length,1);assert.deepEqual(tick(310,73,true),[]);
});
test('adaptive render resolution measures draws, respects explicit quality and detects idle FPS',()=>{
  const m=createRenderMeter();for(let t=0;t<=2000;t+=50)m.frame(t,34);
  assert.equal(m.quality('auto'),'low');assert.equal(m.quality('high'),'high');assert.equal(m.snapshot(2000).fps,20);
  assert.equal(m.snapshot(4000).fps,null);
});

test('cockpit camera starts automatically with detector choices off and respects device availability',()=>{
  const starts=[],target={document:{body:{dataset:{cockpitPanel:'vision'}}},CarrotVisionState:{available:true},
    CarrotDeviceRuntimeState:{carrotVisionEnabled:0},CarrotVisionStart:o=>starts.push(o)};
  const view=createPerceptionScene(target);
  view.startConfigured(true,{});assert.equal(starts.length,0);
  target.CarrotDeviceRuntimeState.carrotVisionEnabled=1;
  view.startConfigured(true,{});view.startConfigured(true,{});assert.deepEqual(starts,[{automaticPerception:true}]);
  target.CarrotVisionState.available=false;view.startConfigured(true,{});
  target.CarrotVisionState.available=true;view.startConfigured(true,{});assert.equal(starts.length,2);
});

test('native camera lead survives an empty viewer detector and missing radar without inventing other cars',()=>{
  const target={CarrotVisionCompactStateActive:true,CarrotStateReceivedAtMonotonic:{}},scene=createPerceptionScene(target);
  function step(at,id,p=.96,radar,valid=true){
    Object.assign(target.CarrotStateReceivedAtMonotonic,{modelV2:at,radarState:at});
    return scene.update({radar,model:{frameId:id,_sourceInvalid:!valid,leadsV3:[{prob:p,x:[21.52],y:[1]}]},
      vision:{status:'ready',capturedAt:at,objects:[]}},at,true,false);
  }
  assert.deepEqual(step(100,1),[]);assert.deepEqual(step(180,1),[]);
  const [known]=step(240,2);assert.equal(known.kind,'vehicle');assert.equal(known.x,20);assert.equal(known.y,1);
  const radar={leadOne:{status:true,dRel:20,yRel:-1,radar:true,radarTrackId:7,vRel:0}};
  step(330,3,.99,radar);
  const merged=step(430,4,.99,radar);assert.equal(merged.length,1);assert.equal(merged[0].classSource,known.source);
  assert.equal(step(460,5,.99,radar,false)[0].kind,'unknown');
  assert.deepEqual(step(600,6,.4),[]);assert.deepEqual(step(700,7,.4),[]);
  step(800,8);const returned=step(900,9);assert.equal(returned.length,1);
  assert.deepEqual(scene.update({model:{frameId:9}},1300,true,false),[]);
  assert.deepEqual(step(1400,10),[]);step(1500,11);
  target.CarrotVisionCompactStateActive=false;assert.deepEqual(step(1510,12),[]);
});
test('a nearby second radar echo prevents ambiguous vehicle promotion',()=>{
  const target={CarrotStateReceivedAtMonotonic:{}},scene=createPerceptionScene(target);
  const radar={leadOne:{status:true,dRel:20,yRel:0,radar:true,radarTrackId:3},leadTwo:{status:true,dRel:20.5,yRel:0,radar:true,radarTrackId:7}};
  const tick=at=>{Object.assign(target.CarrotStateReceivedAtMonotonic,{modelV2:at,radarState:at});return scene.update({
    model:{frameId:at,leadsV3:[{prob:.99,x:[21.52],y:[0]}]},radar},at,true,false);};
  tick(100);assert.deepEqual(tick(200).map(t=>t.kind),['unknown','unknown']);
});
