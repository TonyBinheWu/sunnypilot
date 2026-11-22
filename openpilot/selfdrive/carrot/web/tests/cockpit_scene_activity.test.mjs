import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createDriveDataActivity} from '../src/shared/activity/drive_data.js';
import {createCockpitSceneActivity} from '../src/features/cockpit/scene_activity.js';
import {cockpitPerceptionReport,modelPerceptionSource,radarObservationSummary} from '../src/features/cockpit/perception_status.js';

test('visible cockpit leases model/radar overlays without starting a camera or duplicating leases',()=>{
  const activity=createDriveDataActivity({target:{}}),session=createCockpitSceneActivity();
  const frame={CarrotDriveDataActivity:activity,connectCamera(){throw Error('camera is independent');}};
  for(let i=0;i<1000;i++)session.sync(frame,true);
  assert.deepEqual({...activity.counts()},{hud:1,overlay:1,tracks:0,ar:0});
  assert.equal(activity.snapshot().leaseCount,1);
  session.sync(frame,false);assert.equal(activity.snapshot().leaseCount,0);
  session.sync(frame,true);frame.CarrotVisionReplay={isActive:()=>true};
  session.sync(frame,true);assert.equal(activity.snapshot().leaseCount,0);
  delete frame.CarrotVisionReplay;session.sync(frame,true);session.release();
  assert.equal(activity.snapshot().leaseCount,0);
});
test('replacing the embedded frame releases the old subscriptions before activating a new one',()=>{
  const make=()=>({CarrotDriveDataActivity:createDriveDataActivity({target:{}})}),a=make(),b=make();
  const session=createCockpitSceneActivity();session.sync(a,true);session.sync(b,true);
  assert.equal(a.CarrotDriveDataActivity.snapshot().leaseCount,0);assert.equal(b.CarrotDriveDataActivity.snapshot().leaseCount,1);
  session.sync(null,true);assert.equal(b.CarrotDriveDataActivity.snapshot().leaseCount,0);
});
test('classification status distinguishes off, missing video, loading, failure and no detections',()=>{
  const frame={CarrotWebSettingsState:{vision_object_detection:false},document:{getElementById:()=>null}};
  assert.equal(cockpitPerceptionReport(frame).objects.status,'off');
  frame.CarrotWebSettingsState.vision_object_detection=true;
  assert.equal(cockpitPerceptionReport(frame).camera,false);
  assert.match(cockpitPerceptionReport(frame).summary,/等待前鏡頭/);
  frame.document.getElementById=()=>({readyState:2,videoWidth:640,videoHeight:360});
  let status='loading';frame.CarrotVisionPerception={snapshot:()=>({objects:{status,count:0,positioned:0}})};
  assert.match(cockpitPerceptionReport(frame).objects.text,/載入/);
  for(status of ['unsupported','load_error','inference_error','stale'])assert.equal(cockpitPerceptionReport(frame).objects.status,status);
  status='ready';assert.equal(cockpitPerceptionReport(frame).objects.count,0);assert.match(cockpitPerceptionReport(frame).summary,/0/);
});

test('positioned class diagnostics name only fresh classified camera objects',()=>{
  let status='ready';const frame={CarrotWebSettingsState:{vision_object_detection:true},
    CarrotVisionPerception:{snapshot:()=>({objects:{status,count:3,positioned:3,classes:{person:1,car:1,motorcycle:1,unknown:2,truck:-1}}})}};
  assert.equal(cockpitPerceptionReport(frame).objects.classes,'行人 1、汽車 1、機車 1');
  status='stale';assert.equal(cockpitPerceptionReport(frame).objects.classes,'');
  status='ready';frame.CarrotWebSettingsState.vision_object_detection=false;
  assert.equal(cockpitPerceptionReport(frame).objects.classes,'');
});

test('calibration diagnostics retain real classifications and tell C4 stream mismatch from stale metadata',()=>{
  let reason='profile';const frame={CarrotWebSettingsState:{vision_object_detection:true},
    CarrotVisionPerception:{snapshot:()=>({objects:{status:'calibration',geometryReason:reason,count:2,positioned:0,classes:{person:1,motorcycle:1}}})}};
  assert.equal(cockpitPerceptionReport(frame).objects.classes,'行人 1、機車 1');
  assert.match(cockpitPerceptionReport(frame).objects.text,/串流比例/);
  reason='telemetry';assert.match(cockpitPerceptionReport(frame).objects.text,/資料未更新/);
});

test('compute and lens provenance must belong to a fresh valid model frame',()=>{
  const model={visionCameraInputs:'roadWide',visionCompute:'usbGpu'};
  assert.match(modelPerceptionSource(model,100,449),/遠距＋廣角（USB eGPU）/);
  for(const stamp of [null,NaN,450.1,100])assert.equal(modelPerceptionSource(model,stamp,450),'');
  assert.equal(modelPerceptionSource({...model,_sourceInvalid:true},100,200),'');
  assert.equal(modelPerceptionSource({visionCompute:'usbGpu'},100,200),'');
  assert.equal(modelPerceptionSource({visionCameraInputs:'road'},100,200),'');
});

test('report only fresh measured radar targets, deduplicating repeats', () => {
  const target = {status:true, radar:true, radarTrackId:7, dRel:15, yRel:.1, vRel:0};
  const radar = {leadOne:target, leadsCenter:[target]};
  assert.match(radarObservationSummary(radar, 100, 400), /1 個/);
  for (const sample of [null, {_sourceInvalid:true, ...radar}, {leadOne:{...target, radar:false}}]) {
    assert.equal(radarObservationSummary(sample, 100, 400), '');
  }
  assert.equal(radarObservationSummary(radar, 100, 450), '');
});
