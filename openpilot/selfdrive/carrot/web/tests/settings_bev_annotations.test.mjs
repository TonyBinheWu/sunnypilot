import assert from 'node:assert/strict';
import test from 'node:test';
import {bevProjection,bevObjects,bevSnapshot,addHumanLabel,BEV_SCHEMA} from '../src/features/drive/contents/vision/hud/bev_annotations.js';
import {birdScene} from '../src/features/drive/contents/vision/hud/tesla_view.js';
const scene=()=>({model:{frameId:123,position:{x:[0,10,20],y:[0,1,2]},laneLines:[{x:[0,10,20],y:[-1.8,-1.7,-1.6]}],laneLineProbs:[.85],laneLineStds:[.12],roadEdges:[{x:[0,10],y:[4,4.1]}],roadEdgeStds:[.3]},radar:{leadOne:{status:true,dRel:25,yRel:2,vRel:-3,radar:true,radarTrackId:7,modelProb:.8}}});
test('BEV uses equal metre scales and a reversible right-positive model frame',()=>{
  const p=bevProjection(1280,480,50),zero=p.project(0,0),forward=p.project(5,0),right=p.project(0,5);
  assert.ok(Math.abs((right[0]-zero[0])-(zero[1]-forward[1]))<1e-9);assert.ok(right[0]>zero[0]);
  const point=p.unproject(...p.project(21.3,-2.5));assert.ok(Math.abs(point[0]-21.3)<1e-9&&Math.abs(point[1]+2.5)<1e-9);
});
test('native left-positive lead y is sign converted without claiming exact sensor registration',()=>{
  const snapshot=bevSnapshot(scene());const lead=snapshot.objects.find(o=>o.id==='leadOne');
  assert.deepEqual(lead.geometry.coordinates,[25,-2]);assert.equal(lead.relativeSpeedMps,-3);
  assert.equal(lead.origin,'native_lead_reference');assert.equal(lead.dimensions,null);
  assert.equal(snapshot.synchronization.frameSynchronized,false);assert.equal(lead.nativeTrackId,7);
});
test('lane probability and native uncertainty retain their semantics, including real zero',()=>{
  const data=scene();data.model.laneLineProbs=[0];
  const lane=bevObjects(data).find(o=>o.kind==='lane_line');assert.equal(lane.probability,0);assert.equal(lane.lateralStdM,.12);
  data.model.laneLineProbs=[true];assert.equal(bevObjects(data).find(o=>o.kind==='lane_line').probability,null);
});
test('snapshots are immutable relative to inputs, provenance-bearing, image-free and unverified',()=>{
  const input=scene(),snapshot=bevSnapshot(input,{now:100000,replay:true,sourceTimes:{modelV2:12,radarState:13}});
  input.model.position.y[0]=999;assert.equal(snapshot.objects[0].geometry.coordinates[0][1],0);
  assert.equal(snapshot.schema,BEV_SCHEMA);assert.equal(snapshot.mode,'replay');assert.equal(snapshot.groundTruth,false);
  assert.equal(snapshot.synchronization.frameId,123);assert.equal(snapshot.containsCameraImage,false);
  assert.equal(snapshot.objects.some(o=>o.kind==='pedestrian'),false);
  assert.equal(snapshot.objects.every(o=>o.reviewed===false&&o.provenance==='model_assisted'),true);
});
test('invalid and out-of-range vector samples break polylines rather than bridge gaps',()=>{
  const input={model:{position:{x:[0,5,NaN,10,15,80,20],y:[0,0,0,1,1,2,2]}}};
  const objects=bevObjects(input,30);assert.equal(objects.length,2);
  assert.deepEqual(objects[0].geometry.coordinates,[[0,0],[5,0]]);assert.deepEqual(objects[1].geometry.coordinates,[[10,1],[15,1]]);
});
test('stale and parked live inputs cannot become auto annotation training labels',()=>{
  const target={CarrotOverlayState:{modelV2:scene().model,radarState:scene().radar},CarrotStateReceivedAtMonotonic:{modelV2:10,radarState:10}};
  assert.equal(bevSnapshot(birdScene(target,2000)).objects.length,0);
  target.CarrotDeviceRuntimeState={isOffroad:true};assert.equal(bevSnapshot(birdScene(target,20)).objects.length,0);
});
test('human labels are bounded, explicit and unverified; unknown detections are never promoted',()=>{
  const snapshot=bevSnapshot(scene());
  assert.equal(addHumanLabel(snapshot,'pedestrian',[[12,3]]),true);
  assert.equal(snapshot.manual[0].provenance,'human_unverified');assert.equal(snapshot.manual[0].groundTruth,false);
  for(const points of [[[Infinity,0]],[[true,0]],[[-1,0]],[[76,0]]])assert.equal(addHumanLabel(snapshot,'unknown',points),false);
  assert.equal(addHumanLabel(snapshot,'lane_correction',[[1,0]]),false);
  assert.equal(addHumanLabel(snapshot,'lane_correction',[[1,0],[2,1]]),true);
  while(snapshot.manual.length<64)assert.equal(addHumanLabel(snapshot,'unknown',[[1,0]]),true);
  assert.equal(addHumanLabel(snapshot,'unknown',[[1,0]]),false);
});
