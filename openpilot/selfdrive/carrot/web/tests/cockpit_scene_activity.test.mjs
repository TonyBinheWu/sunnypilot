import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createDriveDataActivity} from '../src/shared/activity/drive_data.js';
import {createCockpitSceneActivity} from '../src/features/cockpit/scene_activity.js';
import {cockpitPerceptionReport} from '../src/features/cockpit/perception_status.js';

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
