import test from 'node:test';
import assert from 'node:assert/strict';
import {cockpitTraffic} from '../src/features/cockpit/traffic.js';
import {sceneTargets} from '../src/features/drive/contents/vision/hud/scene_3d.js';

const lead = (dRel, yRel) => ({status: true, dRel, yRel});
const radar = {leadOne: lead(16, 0), leadsCenter: [lead(16.8, 0.1)],
  leadsLeft: Array.from({length: 9}, (_, i) => lead(20 + i * 10, 3.5)), leadsRight: [lead(25, -3.4)]};
const model = {leadsV3: [{prob: 0.8, x: [16.4], y: [0]}, {prob: 0.6, x: [108], y: [2]}]};
const stamps = {radarState: 10, modelV2: 20};

test('cockpit shows all three lanes, distant targets and one marker per observation', () => {
  const tracks = cockpitTraffic(model, radar, stamps, 25);
  assert.equal(sceneTargets({tracks}).length, 12);
  assert.equal(tracks[0].x, 108);
  assert.equal(tracks.filter(t => t.y === -3.5).length, 9);
  assert.equal(tracks.find(t => t.x === 25).y, 3.4);
});

test('independent stream expiry, withdrawn targets and invalid radar', () => {
  assert.equal(cockpitTraffic(model, radar, stamps, 515).length, 2);
  assert.deepEqual(cockpitTraffic(model, radar, stamps, 521), []);
  assert.deepEqual(cockpitTraffic(null, {}, stamps, 25), []);
  for (const invalid of [{_sourceInvalid: true}, {radarErrors: {radarFault: true}}])
    assert.equal(cockpitTraffic(model, {...radar, ...invalid}, stamps, 25).length, 2);
});

test('positioned camera classification replaces the native marker, adjacent vehicles remain', () => {
  const car = {kind: 'car', origin: 'calibrated_camera', state: 'confirmed', x: 16.3, y: 0.1};
  const tracks = cockpitTraffic(model, radar, stamps, 25, [car]);
  assert.equal(tracks.length, 12);
  assert.ok(tracks.includes(car));
});

test('rear geometry requires fresh coordinates and merges overlapping measurements', () => {
  const car={canValid:true,displayRearLeftDistance:9,displayRearLeftLateral:3};
  const stamp={carState:1000,radarState:1000};
  const radar={leadsLeft:[{status:true,radar:true,dRel:-9.5,yRel:3}],
    leadsCenter:[{status:true,radar:true,dRel:-12,yRel:0}]};
  const traffic=cockpitTraffic(null,radar,stamp,1100,[],car);
  assert.deepEqual(traffic.map(t=>[t.x,t.y,t.rearRadar]),[[-9,-3,true],[-12,-0,true]]);
  assert.deepEqual(cockpitTraffic(null,radar,stamp,1600,[],car),[]);
  assert.deepEqual(cockpitTraffic(null,null,stamp,1100,[],{canValid:true,leftBlindspot:true}),[]);
});

test('chase camera keeps rear targets in view on landscape and portrait screens', async () => {
  const {sceneProjection}=await import('../src/features/cockpit/scene_camera.js');
  const rearPoints=[{rearRadar:true,x:-25,y:-10},{rearRadar:true,x:-7,y:6}];
  for(const [w,h] of [[536,240],[360,720]]){
    const project=sceneProjection(w,h,{roadOverview:true,rearPoints});
    for(const {x,y} of [...rearPoints,{x:0,y:0}]){
      const [u,v]=project(x,y,1);
      assert.ok(u>=0 && u<=w && v>=0 && v<=h);
    }
  }
});

test('a turn cue expires when the route ends or instructions stop updating', async () => {
  const {navigationCue}=await import('../src/features/cockpit/navigation_cue.js');
  const nav={nGoPosDist:4500,xTurnInfo:2,xDistToTurn:190};
  assert.equal(navigationCue(nav,20),'→ 190 m');
  assert.equal(navigationCue(nav,2000),'');
  assert.equal(navigationCue({...nav,nGoPosDist:0},20),'');
});
