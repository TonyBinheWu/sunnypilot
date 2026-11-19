import test from 'node:test';
import assert from 'node:assert/strict';
import {vehicleParkingSource,combineParking} from '../src/features/drive/contents/vision/hud/vehicle_parking.js';

test('GPU observations expire on capture age, duplicate, network loss and view exit',async()=>{
  let at=0,frame=41,ok=true;
  const target={performance:{now:()=>at},AbortController,setTimeout,clearTimeout,fetch:async()=>({ok,json:async()=>({backend:'drivingModelUsbGpu',frameId:frame,ageMs:150,target:[6,0],slots:[]})})};
  const source=vehicleParkingSource(target);
  const tick=async()=>{source.update(true);await new Promise(resolve=>setImmediate(resolve));};
  await tick();assert.deepEqual(source.sample().lead,[6,0]);
  at=300;await tick();at=501;assert.equal(source.sample(),null);
  frame++;await tick();assert.equal(source.sample(),null);
  at=600;await tick();assert.equal(source.sample().frame,42);
  at=850;ok=false;await tick();assert.equal(source.sample(),null);
  at=1120;ok=true;await tick();source.update(false);assert.equal(source.sample(),null);
});

test('APK receipt is sent after drawing a fresh frame in the visible cockpit',async()=>{
  let at=0;
  const headers=[];
  const target={performance:{now:()=>at},navigator:{userAgent:'Android CarrotWebAndroid/0.1'},top:{location:{pathname:'/cockpit'}},document:{hidden:false},AbortController,setTimeout,clearTimeout,
    fetch:async(url,options)=>{headers.push(options.headers);return {ok:true,json:async()=>({backend:'drivingModelUsbGpu',frameId:20,ageMs:30,target:[5,0],slots:[]})};}};
  const source=vehicleParkingSource(target);
  const poll=async()=>{source.update(true);await new Promise(resolve=>setImmediate(resolve));};
  await poll();
  assert.deepEqual(headers[0],{});
  const scene={};combineParking(scene,source.sample());
  source.drawn(source.sample(),scene);
  at=250;await poll();
  assert.equal(headers[1]['X-Carrot-Parking-Draw'],'20,1,0');
  target.document.hidden=true;source.drawn(source.sample(),scene);at=500;await poll();
  assert.deepEqual(headers[2],{});
});

test('nearer existing obstacle is preserved and coincident slots are counted once',()=>{
  const slot={center:[7,1],corners:[[5,0],[9,0],[9,2],[5,2]]};
  const scene={parking:[slot],parkingCue:{distance:2,source:'surface'}};
  combineParking(scene,{lead:[5,0],slots:[slot]});
  assert.equal(scene.parking.length,1);assert.equal(scene.parkingCue.source,'surface');
  delete scene.parkingCue;combineParking(scene,{lead:[5,0],slots:[]});
  assert.equal(scene.parkingCue.distance,5);assert.equal(scene.parkingCue.x,3.48);
});
