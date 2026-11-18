import test from 'node:test';
import assert from 'node:assert/strict';
import {captureIdentity,sceneContributor} from '../src/features/drive/contents/vision/hud/scene_contribution.js';
import {lanePaint,paintStripes} from '../src/features/drive/contents/vision/hud/road_paint.js';

test('frame association requires exact live RTP and EOF, replay excluded',()=>{
  const last={source:'live',clockMappingConfidence:'exact-frame',imageMapping:'rtp',frameId:8,cameraTimestampEof:12};
  const target={DriveVisionPresentedFrames:{status:()=>({last})}};
  assert.deepEqual(captureIdentity(target,false),{frame:8,eof:12});
  assert.equal(captureIdentity(target,true),null);
  last.imageMapping='approximate';assert.equal(captureIdentity(target,false),null);
});

test('revision gating and image-only observation remain distinct',async()=>{
  let revision=null;const calls=[];
  const target={fetch:async(p,opts)=>{calls.push(opts);return {ok:true,json:async()=>({revision})};}};
  const send=sceneContributor(target,'road'), identity={eof:99,frame:1};
  const state={objects:[],imageObjects:[{kind:'crosswalk',probability:.71,box:[.2,.2,.1,.1]}]};
  await send(identity,state,0);assert.equal(calls.length,1);
  revision=1;await send(identity,state,31000);
  const body=JSON.parse(calls.at(-1).body);
  assert.equal(body.packet.objects[0].xy,null);assert.equal(body.revision,1);
});

test('paired yellow stripes are symmetric and require fresh OEM paint',()=>{
  const car={canValid:true,canTimeout:false,laneLineInfoMonoTime:1e9,leftLaneLine:24,rightLaneLine:24};
  const target={CarrotStateReceivedAtMonotonic:{carState:100,roadCameraState:100},CarrotHudState:{carState:car},
    CarrotOverlayState:{roadCameraState:{timestampEof:1e9}}};
  assert.deepEqual(lanePaint(target,210),[null,24,24,null]);
  assert.ok(paintStripes(24,1,'white').offsets[1]<0 && paintStripes(24,2,'white').offsets[1]>0);
  assert.deepEqual(lanePaint(target,900),[]);
  car.laneLineInfoMonoTime=0;assert.deepEqual(lanePaint(target,100),[]);
});
