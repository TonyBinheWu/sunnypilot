import test from 'node:test';
import assert from 'node:assert/strict';
import {nearPathCar,pathChevrons,nearPathSurface,dashedRibbon} from '../src/features/drive/contents/vision/hud/road_scene_style.js';
import {sceneProjection} from '../src/features/cockpit/scene_camera.js';

test('display accents respect gaps, track classification, actual lateral position and prediction state',()=>{
  const path={x:[0,10,NaN,20,30],y:[0,2,0,3,4]};
  const car={kind:'car',x:8,y:1.5,state:'confirmed'};
  assert.ok(nearPathCar(car,path));
  for(const edit of [{kind:'unknown'},{x:15},{y:4},...['tentative','predicted','lost','removed'].map(state=>({state}))])assert.ok(!nearPathCar({...car,...edit},path));
  for(const values of [pathChevrons(path),nearPathSurface(path),dashedRibbon(path,-.05,.05)]){
    assert.ok(values.length>0);
    const xs=values.filter((_,i)=>i%3===0);
    assert.ok(xs.every(x=>x<=10||x>=20));
  }
  assert.deepEqual(pathChevrons(null),[]);
});

test('overview keeps ego low and complete with the observed roadway ahead across screen shapes',()=>{
  for (const [w,h] of [[740,460],[1920,720],[1280,720],[1024,768],[393,852]]) {
    const p=sceneProjection(w,h,{roadOverview:true,skinScale:[1.16,1.1,1.42]});
    const rear=p(-2.55,0,0), front=p(2.55,0,1.8), far=p(25,0,0);
    assert.ok(rear[1]<h*.94&&rear[1]>h*.65);
    assert.ok(front[1]>far[1]&&far[1]<h*.55);
  }
});
