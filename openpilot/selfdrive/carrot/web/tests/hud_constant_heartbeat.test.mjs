import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
test('unchanged measurements publish a bounded heartbeat only when real data arrives',()=>{
  const source=readFileSync(new URL('../js/realtime/vision_raw.js',import.meta.url),'utf8');
  const helper=source.slice(source.indexOf('let LAST_HUD_PUBLISHED_AT'),source.indexOf('function drivingHudUpdateFromCarPayload'));
  const context={};vm.runInNewContext('let LAST_HUD_PAYLOAD_SIGNATURE="";'+helper,context);
  assert.equal(context.shouldPublishHudPayload('P:0:90',0),true);
  for(const now of [50,100,500,749])assert.equal(context.shouldPublishHudPayload('P:0:90',now),false);
  assert.equal(context.shouldPublishHudPayload('P:0:90',750),true);
  assert.equal(context.shouldPublishHudPayload('D:1:90',760),true);
  assert.equal(context.shouldPublishHudPayload('D:1:90',1509),false);
  assert.equal(context.shouldPublishHudPayload('D:1:90',1510),true);
  assert.equal(context.shouldPublishHudPayload('missing',1511),true);
  assert.doesNotMatch(helper,/setInterval|setTimeout/);
});

test('cockpit requests live instruments before camera start and releases the exception outside Vision/background/replay',()=>{
  const source=readFileSync(new URL('../js/realtime/app_realtime.js',import.meta.url),'utf8');
  const helper=source.slice(source.indexOf('function shouldRunCarrotHudRealtime()'),source.indexOf('function isCarrotDriveDataRequested'));
  let replay=false;
  const context={window:{},document:{hidden:false,body:{dataset:{cockpitPanel:'vision'}}},isCarrotRecordedReplayActive:()=>replay,isCarrotPageActive:()=>true,isCarrotVisionContentRuntimeWanted:()=>false};
  vm.runInNewContext(helper,context);assert.equal(context.shouldRunCarrotHudRealtime(),true);
  context.document.hidden=true;assert.equal(context.shouldRunCarrotHudRealtime(),false);
  context.document.hidden=false;replay=true;assert.equal(context.shouldRunCarrotHudRealtime(),false);
  replay=false;context.document.body.dataset.cockpitPanel='setting';assert.equal(context.shouldRunCarrotHudRealtime(),false);
});
