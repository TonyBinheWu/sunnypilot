import assert from 'node:assert/strict';
import test from 'node:test';
import {surroundingTargets,cameraGeometry,groundPoint,cameraTargets} from '../src/features/drive/contents/vision/hud/scene_objects.js';
import {drivingProjection} from '../src/features/drive/contents/vision/hud/driving_scene.js';
import {bevSnapshot} from '../src/features/drive/contents/vision/hud/bev_annotations.js';
import {createObjectPerception,DETECTION_TTL_MS} from '../src/features/drive/contents/vision/hud/object_perception.js';
const lead=(d,y,id)=>({status:true,dRel:d,yRel:y,vRel:-1,radar:true,radarTrackId:id});
const state=()=>({liveCalibration:{calStatus:1,rpyCalib:[0,0,0],height:[1.2]},roadCameraState:{sensor:'os04c10'}});
test('all native lane collections render with right-positive coordinates, bounded counts and conservative deduplication',()=>{
  const a=lead(20,3,7),b=lead(30,-3,8),c=lead(40,-3,9);
  const out=surroundingTargets({leadOne:a,leadLeft:a,leadsLeft:[a],leadsRight:[b,c],leadsCutIn:[b]});
  assert.deepEqual(out.map(p=>[p.x,p.y]),[[20,-3],[30,3],[40,3]]);
  assert.ok(out.every(p=>p.kind==='unknown'));
  assert.equal(surroundingTargets({leadOne:a,leadsLeft:[lead(20.2,3.1,9)]}).length,2); // distinct known IDs stay distinct
  assert.equal(surroundingTargets({leadOne:lead(Infinity,0,1),leadTwo:lead(-3,0,2),leadLeft:lead(10,NaN,3)}).length,0);
});
test('camera geometry requires completed calibration, height, known sensor and uncropped aspect',()=>{
  assert.ok(cameraGeometry(state(),672,380));
  for(const mutate of [s=>s.liveCalibration.height=[],s=>s.liveCalibration.calStatus=0,
    s=>s.liveCalibration.rpyCalib=[NaN,0,0],s=>s.roadCameraState.sensor='unknown']){
    const s=state();mutate(s);assert.equal(cameraGeometry(s,672,380),null);
  }
  assert.equal(cameraGeometry(state(),640,480),null); // cropped vs 1344x760
});
test('ground-ray inverse follows metres and right-positive sign; excludes horizon, truncation and non-finite boxes',()=>{
  const g=cameraGeometry(state(),672,380),distance=12;
  const bottom=190+g.fy*1.2/distance,center=336+g.fx*2/distance;
  const box={originX:center-20,originY:bottom-60,width:40,height:60};
  const p=groundPoint(box,g);assert.ok(Math.abs(p[0]-12)<1e-8&&Math.abs(p[1]-2)<1e-8);
  for(const box of [{originX:100,originY:0,width:30,height:40},{originX:100,originY:300,width:30,height:80},
    {originX:NaN,originY:230,width:20,height:50}])assert.equal(groundPoint(box,g),null);
});
test('image classes and confidence come only from validated camera output; exports keep approximation and provenance',()=>{
  const g=cameraGeometry(state(),672,380),box={originX:330,originY:210,width:20,height:40};
  const det=(kind,score)=>({categories:[{categoryName:kind,score}],boundingBox:box});
  const objects=cameraTargets([det('person',.9),det('motorcycle',.8),det('car',.7),det('dog',.9),det('person',true),det('person',.1)],g);
  assert.deepEqual(objects.map(o=>o.kind),['person','motorcycle','car']);
  assert.equal(cameraTargets([det('person',.99)],null).length,0);
  const data=bevSnapshot({vision:{status:'ready',objects,capturedAt:400,videoTime:3}});
  assert.equal(data.objects.length,3);assert.equal(data.objects[0].classification,'person');
  assert.equal(data.objects[0].positionMethod,'flat_ground_projection');assert.equal(data.objects[0].dimensions,null);
  assert.equal(data.synchronization.frameSynchronized,false);assert.equal(data.groundTruth,false);
});
test('perspective places right targets right, far targets nearer horizon and taller geometry above ground',()=>{
  const p=drivingProjection(1280,720),a=p(0,0),b=p(20,3),c=p(20,3,1.5);
  assert.ok(b[0]>a[0]&&b[1]<a[1]&&c[1]<b[1]);assert.equal(p(-100,0),null);
});

function fixture(){
  let clock=5000,bitmapCloses=0;
  const workers=[],timers=new Map();let timerId=0;
  const video={readyState:2,videoWidth:1344,videoHeight:760,currentTime:1,src:'road.mp4',seeking:false};
  const doc={hidden:false,getElementById:()=>video};
  class Worker {constructor(url){this.url=url;this.messages=[];workers.push(this);}postMessage(m){this.messages.push(m);}terminate(){this.terminated=true;}reply(data){this.onmessage({data});}}
  const target={Worker,WebAssembly:{},OffscreenCanvas:class{},performance:{now:()=>clock},CarrotWebSettingsState:{vision_object_detection:true},
    CarrotAssetUrl:{resolve:()=>'/js/generated/bev-detector-worker.js'},CarrotOverlayState:state(),
    CarrotStateReceivedAtMonotonic:{liveCalibration:5000,roadCameraState:5000},
    createImageBitmap:async()=>({width:640,height:362,close(){bitmapCloses++;}}),
    setTimeout:(fn)=>{timers.set(++timerId,fn);return timerId;},clearTimeout:id=>timers.delete(id)};
  const perception=createObjectPerception(doc,target);
  return {target,doc,video,workers,perception,timers,setClock:n=>{clock=n;},closed:()=>bitmapCloses};
}
test('recognition owns one in-flight frame, expires paused video results and terminates on leave',async()=>{
  const f=fixture();f.perception.update();assert.equal(f.workers.length,1);
  const worker=f.workers[0];worker.reply({type:'ready'});f.perception.update();await Promise.resolve();
  const frame=worker.messages.find(m=>m.type==='frame');assert.ok(frame);
  f.video.currentTime=2;f.perception.update();assert.equal(worker.messages.filter(m=>m.type==='frame').length,1);
  worker.reply({type:'result',id:frame.id,durationMs:40,detections:[{categories:[{categoryName:'person',score:.9}],boundingBox:{originX:310,originY:190,width:20,height:40}}]});
  assert.equal(f.perception.scene().status,'ready');assert.equal(f.perception.scene().objects.length,1);
  f.setClock(5001+DETECTION_TTL_MS);assert.equal(f.perception.scene().status,'stale');assert.equal(f.perception.scene().objects.length,0);
  f.perception.update({active:false});assert.equal(worker.terminated,true);assert.equal(f.timers.size,0);
});
test('bitmap creation races are closed after a source switch or freeze; old worker callbacks cannot republish',async()=>{
  const f=fixture();let resolveBitmap;
  f.target.createImageBitmap=()=>new Promise(resolve=>{resolveBitmap=resolve;});
  f.perception.update();const w=f.workers[0];w.reply({type:'ready'});f.perception.update();
  f.perception.update({frozen:true});let closed=false;resolveBitmap({close(){closed=true;}});await Promise.resolve();
  assert.equal(closed,true);assert.equal(w.terminated,true);
  w.reply({type:'result',id:1,detections:[]});assert.equal(f.perception.scene().status,'paused');
});
test('unavailable worker support and timeouts fail closed until an explicit off/on retry',()=>{
  const f=fixture();f.target.Worker=null;f.perception.update();assert.equal(f.perception.scene().status,'unsupported');
  const g=fixture();g.perception.update();[...g.timers.values()][0]();
  assert.equal(g.perception.scene().status,'load_error');g.perception.update({active:false});
  assert.equal(g.perception.scene().status,'load_error');g.perception.update();assert.equal(g.workers.length,1);
  g.target.CarrotWebSettingsState.vision_object_detection=false;g.perception.update();
  g.target.CarrotWebSettingsState.vision_object_detection=true;g.perception.update();assert.equal(g.workers.length,2);
});
