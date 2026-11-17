import test from 'node:test';
import assert from 'node:assert/strict';
import {createViewOrbit,orbitCamera} from '../src/features/cockpit/view_orbit.js';
import {drivingProjection} from '../src/features/drive/contents/vision/hud/driving_scene.js';
import {drawCockpitVehicle,VEHICLE_SKINS} from '../src/features/cockpit/vehicle.js';
test('orbit owns one pointer, ignores taps and unrelated touches, cancels and resets',()=>{
 const v=createViewOrbit();assert.equal(v.begin(1,100,100,1000,500),true);assert.equal(v.begin(2,0,0,1,1),false);
 assert.equal(v.move(2,300,300),false);assert.equal(v.move(1,102,101),false);assert.deepEqual(v.pose,{yaw:0,pitch:25});
 assert.equal(v.move(1,350,0),true);assert.deepEqual(v.pose,{yaw:90,pitch:43});assert.equal(v.end(2),false);assert.equal(v.end(1),true);
 const copy=v.pose;copy.yaw=0;assert.equal(v.pose.yaw,90);
 assert.equal(v.begin(3,0,0,1000,500),true);v.move(3,3000,1000);assert.ok(v.pose.yaw>=-180&&v.pose.yaw<180);assert.equal(v.pose.pitch,18);v.cancel();assert.equal(v.move(3,0,0),false);
 assert.equal(v.key('Escape'),false);v.key('Home');assert.deepEqual(v.pose,{yaw:0,pitch:25});v.key('ArrowRight');v.key('ArrowUp');assert.deepEqual(v.pose,{yaw:10,pitch:30});
 for(const size of [0,-1,NaN,Infinity])assert.equal(v.begin(1,0,0,size,500),false);
});
test('all skins remain finite and within the scene when orbiting near and far on wide and 4:3 displays',()=>{
 const ctx=new Proxy({},{get:()=>()=>{}});
 for(const [w,h] of [[1920,564],[960,236],[800,432],[1024,644]])for(const skin of Object.values(VEHICLE_SKINS))for(const distance of [9,16])for(const yaw of [-180,-90,0,90,179])for(const pitch of [18,25,60]){
  const camera=orbitCamera({distance,height:distance===9?6:12,anchorY:distance===9?.78:.85},{yaw,pitch}),p=drivingProjection(w,h,camera),points=[];
  drawCockpitVehicle(ctx,(...args)=>{const point=p(...args);if(point)points.push(point);return point;},{skin});
  assert.ok(points.length>20);assert.ok(points.every(v=>v.every(Number.isFinite)));assert.ok(Math.max(...points.map(v=>v[1]))<h,`${skin.id} ${yaw}/${pitch}`);
  assert.equal(p.view.length,3);assert.ok(Number.isFinite(p.depth(30,3)));
 }
});
