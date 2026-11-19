import test from 'node:test';
import assert from 'node:assert/strict';
import {GRID,opticalCrop,visibleVoxels,surfaceMotion} from '../src/features/drive/contents/vision/occupancy_grid.js';
import {createObjectPerception} from '../src/features/drive/contents/vision/hud/object_perception.js';

const geometry={width:640,height:362,fx:543,fy:543,heightM:1.5,rpy:[0,0,0]};
test('the network crop is isotropic in ray coordinates and fits both front profiles',()=>{
  for(const g of [geometry,{...geometry,width:640,height:401,fx:879,fy:879}]){
    const c=opticalCrop(g);
    assert.ok(c.x>=0&&c.y>=0);
    assert.equal(c.width/g.fx,2*GRID.halfX);
    assert.ok(Math.abs(c.height/g.fy-2*GRID.halfY)<1e-8);
  }
  assert.equal(opticalCrop({...geometry,fx:3000}),null);
});
test('only supported first surfaces generate metric cells, never empty rays or their shadow',()=>{
  const rays=GRID.width*GRID.height,n=rays*GRID.bins;
  const occupied=new Float32Array(n),free=new Float32Array(n).fill(.99),i=18*64+32;
  assert.deepEqual([...visibleVoxels(occupied,free,geometry).positions],[]);
  occupied[8*rays+i]=.28;occupied[8*rays+i+1]=.28;occupied[20*rays+i]=.23;
  const sample=visibleVoxels(occupied,free,geometry);
  assert.deepEqual([...sample.positions],[10.5,.5,1]);assert.equal(sample.supportedRays,2);
  assert.equal(sample.visibleEmpty,16);
  assert.throws(()=>visibleVoxels([],free,geometry));
});
test('bounded ambiguous elevated returns draw only a distance interval and never a solid cube',()=>{
  const rays=GRID.width*GRID.height,occupied=new Float32Array(rays*GRID.bins),free=new Float32Array(occupied.length);
  const i=14*64+34;
  for(let k=0;k<GRID.bins;k++){
    occupied[k*rays+i]=k>=6&&k<16?.1:0;
    free[k*rays+i]=1-Math.min(10,Math.max(0,k-5))/10;
  }
  const {positions,ranges,supportedRays}=visibleVoxels(occupied,free,geometry);
  assert.equal(positions.length,0);assert.equal(supportedRays,0);
  assert.equal(ranges.length,6);assert.ok(ranges[3]>ranges[0]&&ranges[3]-ranges[0]<=8);
  free.fill(.6);assert.equal(visibleVoxels(occupied,free,geometry).ranges.length,0);
});
test('a frame uses preceding calibration rather than dropping every result when telemetry leads presentation',async()=>{
  let time=100,callback,id=0;const pending=new Map(),workers=[];
  const clock={now:()=>time}, v={src:'front',readyState:2,currentTime:1,videoWidth:1344,videoHeight:760,
    requestVideoFrameCallback:fn=>{callback=fn;return 1;},cancelVideoFrameCallback(){}};
  const stamps={liveCalibration:95,roadCameraState:95};
  const w={Worker:class{constructor(){workers.push(this);}postMessage(m){this.msg=m;}terminate(){this.ended=true;}},
    performance:clock,WebAssembly:{},OffscreenCanvas:class{},CarrotVisionCompactStateActive:true,
    CarrotAssetUrl:{resolve:()=>'/worker'},CarrotWebSettingsState:{vision_environment_occupancy:true},
    CarrotOverlayState:{liveCalibration:{calStatus:1,height:[1.5],rpyCalib:[0,0,0]},roadCameraState:{sensor:'os04c10'}},
    CarrotStateReceivedAtMonotonic:stamps,createImageBitmap:async()=>({width:640,height:362,close(){}}),
    setTimeout:(f,ms)=>{pending.set(++id,{f,ms});return id;},clearTimeout:i=>pending.delete(i)};
  const doc={hidden:false,getElementById:()=>v},d=createObjectPerception(doc,w,{occupancy:true});
  d.update();const worker=workers[0];worker.onmessage({data:{type:'ready'}});d.update();
  time=200;callback(180,{mediaTime:1});stamps.roadCameraState=190;d.update();await Promise.resolve();
  assert.equal(worker.msg.type,'frame');assert.equal(worker.msg.geometry.sensor,'os04c10');
  time=300;worker.onmessage({data:{type:'result',id:worker.msg.id,positions:new Float32Array([8.5,.5,1]),ranges:new Float32Array(),supportedRays:1,visibleEmpty:4,durationMs:100}});
  assert.equal(d.scene().count,1);assert.equal(d.scene().capturedAt,180);
  time=1081;assert.equal(d.scene().positions,undefined);
  w.CarrotVisionCompactStateActive=false;d.update();assert.ok(worker.ended);assert.equal(d.scene().count,0);
  d.destroy();assert.equal(pending.size,0);
});
test('motion uses fresh speed and turn rate; uncertain travel and expired surfaces disappear',()=>{
  assert.equal(surfaceMotion({speed:12,yaw:null},400),null);
  assert.equal(surfaceMotion({speed:0,yaw:0},901),null);
  assert.equal(surfaceMotion(null,200),null);
  assert.equal(surfaceMotion({speed:10,yaw:0},350).x,-3.5);
  assert.ok(surfaceMotion({speed:10,yaw:.3},350).angle<0);
});
