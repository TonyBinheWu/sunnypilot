import test from 'node:test';
import assert from 'node:assert/strict';
import {createSpeedZoom,sceneSpeedKph,speedZoomTarget} from '../src/features/cockpit/speed_zoom.js';
import {drivingProjection} from '../src/features/drive/contents/vision/hud/driving_scene.js';
import {drawCockpitVehicle,VEHICLE_SKINS} from '../src/features/cockpit/vehicle.js';

test('speed camera uses km/h consistently and rejects stale or malformed inputs',()=>{
  assert.equal(sceneSpeedKph({speed:50},'mph',false),80.4672);
  assert.equal(sceneSpeedKph({speed:50},'km/h',false),50);
  for(const speed of [null,NaN,Infinity,-1,'50',true,301])assert.equal(sceneSpeedKph({speed},'km/h',false),null);
  assert.equal(sceneSpeedKph({speed:100},'km/h',true),null);
  assert.equal(speedZoomTarget(0),0);assert.equal(speedZoomTarget(15),0);assert.equal(speedZoomTarget(55),.5);assert.equal(speedZoomTarget(95),1);assert.equal(speedZoomTarget(200),1);
});

test('camera movement is smooth, bounded and settles without stationary animation',()=>{
  const camera=createSpeedZoom();let previous=camera.update(0,0),next;
  assert.equal(previous.moving,false);
  for(let t=50;t<=12000;t+=50){next=camera.update(100,t);assert.ok(next.progress>=previous.progress);assert.ok(next.progress-previous.progress<=.45*.05+1e-9);previous=next;}
  assert.equal(next.progress,1);assert.equal(next.moving,false);
  for(let t=12050;t<=24000;t+=50){next=camera.update(0,t);assert.ok(next.progress<=previous.progress);assert.ok(previous.progress-next.progress<=.45*.05+1e-9);previous=next;}
  assert.equal(next.progress,0);assert.equal(next.moving,false);
});

test('stale speed, hidden views, source changes and long pauses cannot cause a zoom jump',()=>{
  const c=createSpeedZoom();let s=c.update(100,0);for(let t=50;t<=2000;t+=50)s=c.update(100,t);
  const held=s.progress;assert.equal(c.update(null,10000).progress,held);assert.equal(c.update(0,20000,{active:false}).progress,held);
  assert.equal(c.update(0,30000).progress,held);const next=c.update(0,31000);assert.ok(held-next.progress<=.045+1e-9);
  assert.equal(c.update(100,100000,{source:'replay'}).progress,next.progress);
  const before=c.update(100,100100,{source:'replay'}).progress;
  assert.equal(c.update(0,1,{source:'replay'}).progress,before);
});

test('default projection remains compatible, high-speed camera shows wider scenery',()=>{
  const w=1280,h=720,s=Math.sin(25*Math.PI/180),c=Math.cos(25*Math.PI/180),f=h*.96;
  const p=drivingProjection(w,h)(20,3,1),depth=29*c+7*s;
  assert.deepEqual(p,[w/2+f*3/depth,h*.46+f*(7*c-29*s)/depth]);
  const near=drivingProjection(w,h,{distance:9,height:6,anchorY:.78}),far=drivingProjection(w,h,{distance:16,height:12,anchorY:.85});
  assert.ok(far(15,3)[0]-w/2<near(15,3)[0]-w/2);
});

test('every supported own-vehicle skin remains fully framed around the fixed pivot across aspect ratios',()=>{
  const ctx=new Proxy({},{get:()=>()=>{}});
  for(const [w,h] of [[1920,1080],[1280,720],[800,600],[1280,364]])for(const skin of Object.values(VEHICLE_SKINS))for(const camera of [{distance:9,height:6,anchorY:.78},{distance:16,height:12,anchorY:.85}]){
    const points=[],projection=drivingProjection(w,h,camera);
    drawCockpitVehicle(ctx,(...args)=>{const p=projection(...args);if(p)points.push(p);return p;},{skin});
    assert.ok(points.length>20);assert.ok(points.every(p=>p.every(Number.isFinite)));
    const bottom=Math.max(...points.map(p=>p[1]));assert.ok(bottom>h*.55&&bottom<h*.95,`${skin.id} bottom ${bottom/h}`);
    assert.ok(points.every(([x,y])=>x>w*.04&&x<w*.96&&y>h*.04&&y<h*.96),skin.id);
  }
});
