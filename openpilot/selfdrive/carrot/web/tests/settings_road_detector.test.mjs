import assert from 'node:assert/strict';
import test from 'node:test';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resizePlan,rgbTensor,decodeRoadOutput} from '../src/features/drive/contents/vision/road_yolo.js';
import {roadCameraTargets,roadImageTargets,cameraGeometry,cameraTargets,surroundingTargets} from '../src/features/drive/contents/vision/hud/scene_objects.js';
import {createObjectPerception,DETECTION_TTL_MS} from '../src/features/drive/contents/vision/hud/object_perception.js';
import {bevSnapshot} from '../src/features/drive/contents/vision/hud/bev_annotations.js';
import {sha256} from '../vendor/road-detector/hashes/sha256.js';
const root=new URL('../vendor/road-detector/',import.meta.url);
const manifest=JSON.parse(await readFile(new URL('manifest.json',root),'utf8'));
const cone=manifest.models[0],crosswalk=manifest.models[1];
test('pinned runtime and both real ONNX models retain their exact distribution bytes',async()=>{
  assert.deepEqual(manifest.models.map(m=>[m.id,m.classIndex,m.shape,m.label]),[
    ['cone',6,[1,14,8400],'traffic cone'],['crosswalk',0,[1,6375,8],'crosswalk']]);
  assert.deepEqual(manifest.unsupported,['stop line','motorcycle waiting area']);
  for(const f of manifest.files){const b=await readFile(new URL(f.path,root));assert.ok(!f.path.includes('..'));assert.equal(b.length,f.bytes,f.path);assert.equal(createHash('sha256').update(b).digest('hex'),f.sha256,f.path);}
  // Local HTTP WebViews have no crypto.subtle. The vendored fallback still hashes.
  assert.equal(Buffer.from(sha256(new TextEncoder().encode('abc'))).toString('hex'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
});
function output(model,rows){
  const data=new Float32Array(model.shape.reduce((a,b)=>a*b));
  rows.forEach((row,i)=>row.forEach((n,j)=>{data[model.format==='yolov8'?j*model.shape[2]+i:i*model.shape[2]+j]=n;}));
  return data;
}
test('YOLOv8 class 6 means Safety Cone, without objectness; person/PPE classes are not cones',()=>{
  const a=Array(14).fill(0);a.splice(0,4,320,320,64,128);a[10]=.9;
  const person=[...a];person[10]=.1;person[9]=.99;
  const duplicate=[...a];duplicate[10]=.8;
  const out=decodeRoadOutput(output(cone,[a,person,duplicate]),cone.shape,cone,1280,720,resizePlan(1280,720,'stretch'));
  assert.equal(out.length,1);assert.equal(out[0].categories[0].categoryName,'traffic cone');
  assert.deepEqual(out[0].boundingBox,{originX:576,originY:288,width:128,height:144});
});
test('crosswalk uses objectness times class 0 and reverses 16:9 letterbox; red/green scores are ignored',()=>{
  const out=decodeRoadOutput(output(crosswalk,[[160,180,160,40,.8,.9,.99,.99],[50,150,50,20,.3,1,0,0],[25,150,20,10,1,.1,.99,.99]]),crosswalk.shape,crosswalk,1280,720,resizePlan(1280,720,'letterbox',320));
  assert.equal(out.length,1);assert.deepEqual(out[0].boundingBox,{originX:320,originY:360,width:640,height:160});
  assert.ok(Math.abs(out[0].categories[0].score-.72)<1e-6);
});
test('malformed output fails closed; NaN/negative boxes, out-of-frame and blank scores produce no observations',()=>{
  assert.throws(()=>decodeRoadOutput(new Float32Array(4),[1,4,1],cone,640,360,resizePlan(640,360,'stretch')),/shape/);
  const a=[320,320,32,32,0,0,0,0,0,0,.9,0,0,0];
  assert.equal(decodeRoadOutput(output(cone,[[...a.slice(0,2),NaN,...a.slice(3)]]),cone.shape,cone,640,360,resizePlan(640,360,'stretch')).length,0);
  assert.equal(decodeRoadOutput(output(cone,[]),cone.shape,cone,640,360,resizePlan(640,360,'stretch')).length,0);
  assert.throws(()=>resizePlan(0,4,'stretch'));assert.throws(()=>resizePlan(640,360,'guess'));
  const rgba=new Uint8ClampedArray(640*640*4);rgba.set([255,128,0,255]);const rgb=rgbTensor(rgba);
  assert.equal(rgb[0],1);assert.ok(Math.abs(rgb[640*640]-128/255)<1e-6);assert.equal(rgb[2*640*640],0);
});
const det=(kind)=>({categories:[{categoryName:kind,score:.9}],boundingBox:{originX:300,originY:200,width:40,height:50}});
const calibration={liveCalibration:{calStatus:1,rpyCalib:[0,0,0],height:[1.2]},roadCameraState:{sensor:'os04c10'}};
test('cones require calibrated ground rays; crosswalks never become fictitious BEV polygons or stop lines',()=>{
  const detections=['traffic cone','crosswalk','stop line','motorcycle waiting area','person'].map(det),g=cameraGeometry(calibration,640,362);
  assert.deepEqual(roadCameraTargets(detections,g).map(o=>o.kind),['traffic cone']);assert.equal(roadCameraTargets(detections,null).length,0);
  const images=roadImageTargets(detections,640,362);assert.deepEqual(images.map(o=>o.kind),['traffic cone','crosswalk']);
  assert.ok(images.every(o=>o.position===null&&o.distance===null));
  assert.deepEqual(cameraTargets(detections,g).map(o=>o.kind),['person']);
  assert.equal(surroundingTargets({leadOne:{status:true,dRel:20,yRel:0}})[0].kind,'unknown');
  const snapshot=bevSnapshot({road:{status:'ready',objects:roadCameraTargets(detections,g),capturedAt:300,videoTime:2},vision:{capturedAt:200,videoTime:1}});
  assert.equal(snapshot.objects[0].classification,'traffic cone');assert.equal(snapshot.perception.road.capturedMonotonicMs,300);assert.equal(snapshot.perception.capturedMonotonicMs,200);assert.equal(snapshot.perception.road.frameSynchronized,false);
});
function fixture(){
  let now=5000,id=0;const workers=[],timers=new Map(),video={readyState:2,videoWidth:1344,videoHeight:760,currentTime:1,src:'road.mp4'};
  const doc={hidden:false,getElementById:()=>video};
  class Worker{constructor(url){this.url=url;this.messages=[];workers.push(this);}postMessage(m){this.messages.push(m);}terminate(){this.terminated=true;}reply(data){this.onmessage({data});}}
  const target={Worker,WebAssembly:{},OffscreenCanvas:class{},performance:{now:()=>now},CarrotWebSettingsState:{vision_object_detection:true,vision_road_detection:true},CarrotAssetUrl:{resolve:x=>x},CarrotOverlayState:calibration,CarrotStateReceivedAtMonotonic:{liveCalibration:5000,roadCameraState:5000},createImageBitmap:async()=>({width:640,height:362,close(){}}),setTimeout:fn=>{timers.set(++id,fn);return id;},clearTimeout:i=>timers.delete(i)};
  return {doc,target,video,workers,timers,setNow:n=>{now=n;}};
}
test('road worker failure is isolated from existing people/vehicle recognition and needs off/on retry',()=>{
  const f=fixture(),normal=createObjectPerception(f.doc,f.target),road=createObjectPerception(f.doc,f.target,{road:true});
  normal.update();road.update();assert.equal(f.workers.length,2);assert.equal(f.workers[1].url,'vision.road-detector-worker');
  f.workers[0].reply({type:'ready'});f.workers[1].reply({type:'error',stage:'load'});assert.equal(road.scene().status,'load_error');assert.equal(normal.scene().status,'waiting');
  road.update();assert.equal(f.workers.length,2);f.target.CarrotWebSettingsState.vision_road_detection=false;road.update();f.target.CarrotWebSettingsState.vision_road_detection=true;road.update();assert.equal(f.workers.length,3);normal.destroy();road.destroy();assert.equal(f.timers.size,0);
});
test('road results expire after 1.2s; background/freeze kills worker and old callbacks cannot restore objects',async()=>{
  const f=fixture(),road=createObjectPerception(f.doc,f.target,{road:true});road.update();const worker=f.workers[0];worker.reply({type:'ready'});road.update();await Promise.resolve();
  const frame=worker.messages.find(m=>m.type==='frame');worker.reply({type:'result',id:frame.id,durationMs:120,detections:[det('traffic cone'),det('crosswalk')]});
  assert.equal(road.scene().objects.length,1);assert.equal(road.scene().imageObjects.length,2);
  f.setNow(5001+DETECTION_TTL_MS);assert.equal(road.scene().objects.length,0);assert.equal(road.scene().imageObjects.length,0);
  road.update({frozen:true});assert.equal(worker.terminated,true);worker.reply({type:'result',id:frame.id,detections:[det('traffic cone')]});assert.equal(road.scene().status,'paused');assert.equal(f.timers.size,0);
});
