import assert from 'node:assert/strict';
import test from 'node:test';
import {metricLayout,serviceFresh,birdScene,canEditMetrics,drawBirdScene} from '../src/features/drive/contents/vision/hud/tesla_view.js';
import {drawRainbowRibbon} from '../src/features/drive/contents/vision/rainbow_ribbon.js';
import {quotaSummary} from '../src/features/tools/recording_quota.js';

test('metric persistence clamps positions and size; malformed layouts preserve usable defaults',()=>{
  assert.deepEqual(metricLayout('{"speed":[2,-1,9]}').speed,[1,0,2.2]);
  for(const bad of ['null','[]','bad','{"speed":[null,0,1]}'])assert.equal(metricLayout(bad).speed.length,3);
});
test('stale and parked data cannot become bird-view objects and metric editing requires parking or replay',()=>{
  const model={position:{x:[0,10],y:[0,1]}},radar={leadOne:{status:true,dRel:20,yRel:0}};
  const target={CarrotOverlayState:{modelV2:model,radarState:radar},CarrotHudState:{carState:{gearShifter:'park',vEgo:0}},
    CarrotStateReceivedAtMonotonic:{modelV2:1000,radarState:900,carState:1000}};
  assert.equal(birdScene(target,1500).model,model);
  assert.equal(birdScene(target,3000).model,null);
  assert.equal(birdScene(target,3000).radar,null);
  assert.equal(canEditMetrics(target,1500),true);
  assert.equal(canEditMetrics(target,3000),false);
  target.CarrotHudState.carState.gearShifter='drive';assert.equal(canEditMetrics(target,1500),false);
  target.CarrotDeviceRuntimeState={isOffroad:true};assert.equal(birdScene(target,1500).model,null);
  target.CarrotVisionReplay={status:()=>({active:true})};assert.equal(birdScene(target,3000).model,model);
});
test('rainbow colors enter the original GPU polygon batch and invalid geometry draws nothing',()=>{
  const draws=[],bands=[];const geometry={buildBandPolygon:(l,r,a,b)=>{bands.push([a,b]);return [[0,0],[0,1],[1,1]];},drawPolygon:(...a)=>draws.push(a)};
  assert.equal(drawRainbowRibbon(geometry,{left:[[0,0],[0,1]],right:[[1,0],[1,1]]},(c,a)=>{assert.ok([c.r,c.g,c.b].every(Number.isFinite));return `rgba(${c.r},${c.g},${c.b},${a})`;}),true);
  assert.equal(draws.length,7);assert.deepEqual(bands[0],[0,1/7]);assert.equal(bands[6][1],1);
  assert.equal(drawRainbowRibbon(geometry,{left:[],right:[]},()=>''),false);assert.equal(draws.length,7);
});
test('bird-view uses supplied finite model geometry and actual detected leads only',()=>{
  const calls=[];const ctx=new Proxy({}, {get:(t,k)=>t[k]||((...a)=>calls.push([k,...a])),set:(t,k,v)=>{t[k]=v;return true;}});
  drawBirdScene(ctx,800,400,{model:{position:{x:[0,10,NaN],y:[0,1,2]},laneLines:[]},radar:{leadOne:{status:false,dRel:20,yRel:0}}});
  assert.ok(calls.flat().every(v=>typeof v!=='number'||Number.isFinite(v)));
  assert.equal(calls.filter(c=>c[0]==='strokeRect').length,1); // ego, not an invented lead
});
test('quota status distinguishes missing, disabled, expired and blocked cleanup',()=>{
  const text=(k,f)=>f;
  assert.match(quotaSummary({available:false},text),/Waiting/);
  assert.match(quotaSummary({enabled:false},text),/disabled/);
  const view=quotaSummary({enabled:true,percent:50,updatedAt:1,groups:[{usedPercent:51,overQuota:true}]},text,200000);
  assert.match(view,/outdated/);assert.match(view,/51%/);assert.match(view,/protected/);
});
