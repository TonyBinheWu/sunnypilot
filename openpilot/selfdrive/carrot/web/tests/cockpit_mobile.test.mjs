import test from 'node:test';
import assert from 'node:assert/strict';
import {sceneRenderSize} from '../src/features/drive/contents/vision/hud/tesla_view.js';
import {drivingProjection} from '../src/features/drive/contents/vision/hud/driving_scene.js';
import {VEHICLE_SKINS,drawCockpitVehicle} from '../src/features/cockpit/vehicle.js';

test('phone portrait rendering uses its long edge without reducing quality on rotation or changing wide display budgets',()=>{
  for(const quality of ['low','auto','high','invalid']){
    const portrait=sceneRenderSize(380,825,quality),landscape=sceneRenderSize(825,380,quality);
    assert.equal(portrait.width,landscape.height);assert.equal(portrait.height,landscape.width);
    assert.ok(Math.abs(portrait.width/portrait.height-380/825)<.003);
    assert.ok(portrait.width>0&&portrait.height>0);
  }
  assert.deepEqual(sceneRenderSize(380,825,'auto'),{width:380,height:825,factor:1});
  assert.deepEqual(sceneRenderSize(380,825,'high',3),{width:760,height:1650,factor:2});
  assert.deepEqual(sceneRenderSize(1920,720,'auto'),{width:1920,height:720,factor:1});
  assert.deepEqual(sceneRenderSize(480,300,'standard',2),{width:960,height:600,factor:2});
  assert.deepEqual(sceneRenderSize(1920,720,'low',2),{width:960,height:360,factor:.5});
  assert.deepEqual(sceneRenderSize(0,NaN,'high'),{width:1,height:1,factor:1});
});

test('2D fallback keeps the full car inside narrow phones at near and far zoom',()=>{
  for(const [w,h] of [[320,568],[360,800],[380,825],[412,915]])for(const progress of [0,1])for(const skin of [VEHICLE_SKINS.ev6,VEHICLE_SKINS.ev9]){
    const base=drivingProjection(w,h,{distance:9+7*progress,height:6+6*progress,anchorY:.78+.07*progress}),points=[];
    const project=(...p)=>{const v=base(...p);if(v)points.push(v);return v;};project.view=base.view;
    const ctx=new Proxy({},{get:(t,k)=>t[k]??(()=>{}),set:(t,k,v)=>(t[k]=v,true)});
    drawCockpitVehicle(ctx,project,{skin});assert.ok(points.length>100);
    assert.ok(points.every(p=>p.every(Number.isFinite)&&p[0]>=0&&p[0]<=w&&p[1]>=0&&p[1]<=h));
  }
});
