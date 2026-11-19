import test from 'node:test';
import assert from 'node:assert/strict';
import {parkingAttitude, parkingObservation, inclinedProjection, parkingWheelTicks} from '../src/features/drive/contents/vision/hud/parking_environment.js';
import {createParkingView} from '../src/features/cockpit/parking.js';
import {createParkingPerception} from '../src/features/drive/contents/vision/hud/parking_perception.js';

const points=(...columns)=>Float32Array.from(columns.flatMap(([x,y])=>[x,y,1,x,y,2]));
test('only supported raised cells describe surfaces and holes break a wall',()=>{
  const cue=environment=>parkingObservation({environment});
  assert.equal(cue([3.5,0,0,4.5,0,3]),null);
  assert.equal(cue([3.5,0,1]).shape,'surface');
  assert.equal(cue(points([3.5,.5])).shape,'column');
  assert.equal(cue(points([3.5,.5],[3.5,1.5],[3.5,2.5],[3.5,3.5])).shape,'wall');
  assert.equal(cue(points([3.5,.5],[3.5,1.5],[3.5,3.5],[3.5,4.5])).shape,'surface');
  assert.equal(parkingObservation({environment:points([2.5,.5]),environmentMotion:{x:-3,y:0,angle:0}}),null);
});

test('parking estimates compare common references and exclude predictions and image-only paint',()=>{
  const lead={origin:'native_lead_reference',kind:'unknown',x:2,y:0,state:'confirmed'};
  const cue=parkingObservation({tracks:[lead]});
  assert.equal(cue.distance,3.52);assert.equal(cue.x,2);
  const ahead=parkingObservation({tracks:[lead],environment:[3.5,.1,1]});
  assert.equal(ahead.source,'surface');assert.ok(ahead.bearing>0);
  for(const other of [{state:'predicted'},{state:'tentative'},{kind:'traffic light'},{x:Infinity},{origin:'image_only'}]){
    assert.equal(parkingObservation({tracks:[{...lead,...other}]}),null);
  }
});

test('mount correction and sign match right side down and nose up; invalid tilt disappears',()=>{
  const meas={valid:true,x:.2,y:0,xStd:.01,yStd:.01};
  const raw={livePose:{inputsOK:true,sensorsOK:true,posenetOK:true,orientationNED:meas},
    liveCalibration:{calStatus:1,rpyCalib:[-.2,0,0]}};
  const stamps={livePose:20,liveCalibration:20};
  assert.ok(Math.abs(parkingAttitude(raw,stamps,21).roll)<1e-9);
  raw.liveCalibration.rpyCalib=[0,0,0];meas.y=.15;
  const a=parkingAttitude(raw,stamps,21);
  const project=inclinedProjection((x,y,z)=>[x,y,z],a);
  assert.ok(project(0,1,0)[2]<0);assert.ok(project(1,0,0)[2]>0);
  assert.equal(parkingAttitude(raw,stamps,1020),null);
  meas.xStd=.2;assert.equal(parkingAttitude(raw,stamps,21),null);
});

test('wheel direction is measured left-positive and unknown angle draws no guides',()=>{
  assert.deepEqual(parkingWheelTicks(null),[]);assert.deepEqual(parkingWheelTicks(90),[]);
  for(const [angle,side] of [[15,-1],[-15,1],[0,0]]){
    const ticks=parkingWheelTicks(angle);
    assert.equal(ticks.length,2);
    for(const [x,y,ex,ey] of ticks){assert.ok(ex>x);assert.equal(Math.sign(ey-y),side);}
  }
});

test('fresh stationary P enters overhead, manual exit and missing telemetry clear it',()=>{
  const view=createParkingView(),sample={enabled:true,fresh:true,gear:'P',speed:0};
  assert.equal(view.update(sample).overhead,true);
  view.toggle();assert.equal(view.update(sample).overhead,false);
  assert.equal(view.update({...sample,fresh:false}).overhead,false);
  assert.equal(view.update({...sample,speed:22}).overhead,false);
});

test('an old parking worker cannot publish after calibration loss',async()=>{
  let now=0,worker,posts=0;
  const target={Worker:class{constructor(){worker=this;}terminate(){}postMessage(){posts++;}},
    OffscreenCanvas:class{},performance:{now:()=>now},setTimeout(){},clearTimeout(){},
    CarrotStateReceivedAtMonotonic:{liveCalibration:0,roadCameraState:0},
    CarrotOverlayState:{liveCalibration:{calStatus:1,rpyCalib:[0,0,0],height:[1]},roadCameraState:{sensor:'os04c10'}},
    CarrotAssetUrl:{resolve:()=>'/worker.js'},createImageBitmap:async()=>({width:480,height:271,close(){}})};
  const video={videoWidth:1344,videoHeight:760,readyState:4,currentTime:1,currentSrc:'road'};
  const perception=createParkingPerception({getElementById:()=>video},target);
  perception.update(true);await new Promise(resolve=>setImmediate(resolve));assert.equal(posts,1);
  now=1001;perception.update(true);worker.onmessage({data:{id:1,slots:[{center:[5,0]}]}});
  assert.equal(perception.scene().status,'calibration');assert.deepEqual(perception.scene().slots,[]);
  perception.destroy();
});
