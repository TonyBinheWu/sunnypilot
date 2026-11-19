import test from 'node:test';
import assert from 'node:assert/strict';
import {currentWorld,withWorldContacts,worldSource,worldNotice,vehicleInferenceOnly} from '../src/features/drive/contents/vision/hud/world_scene.js';

test('known vehicle GPU selects vehicle inference until explicitly changed',()=>{
  assert.equal(vehicleInferenceOnly({}, {vehicleGpuPreferred:true}),true);
  assert.equal(vehicleInferenceOnly({vision_compute_source:'viewer'}, {vehicleGpuPreferred:true}),false);
  assert.equal(vehicleInferenceOnly({vision_compute_source:'vehicle'},{}),true);
  assert.equal(vehicleInferenceOnly({},{}),false);
});

const p={source:'corner235',nativeId:'12',x:15,y:2,vRel:-1,ttlMs:180};
const row={contacts:[p],following:{...p,ttlMs:120},signals:{leftBlindspot:260}};
test('independent measurement, following and blindspot expiry',()=>{
  const confirmed={x:15,y:2,kind:'car',state:'confirmed',nativeReference:12};
  assert.equal(withWorldContacts([confirmed],currentWorld(row,100))[0].following,true);
  assert.equal(withWorldContacts([confirmed],currentWorld(row,120))[0].following,undefined);
  assert.equal(withWorldContacts([],currentWorld(row,180)).length,0);
  assert.equal(worldNotice(currentWorld(row,180)),'左側盲點警示');
  assert.equal(worldNotice(currentWorld(row,260)),'');
  for(const conflicts of [[confirmed,confirmed],[{...confirmed,state:'predicted'}],[{...confirmed,nativeReference:13}]]){
    assert.ok(withWorldContacts(conflicts,currentWorld(row,0)).every(o=>!o.following));
  }
  const [raw]=withWorldContacts([],currentWorld(row,0));
  assert.equal(raw.kind,'unknown');assert.equal(raw.heading,undefined);assert.equal(raw.source,'liveTracks.corner235');
});
test('late HTTP response and screen switches never revive old samples',async()=>{
  let at=0,resolve;
  const source=worldSource({performance:{now:()=>at},fetch:()=>new Promise(r=>{resolve=r}),AbortController,setTimeout,clearTimeout});
  source.update(true);
  at=220;resolve({ok:true,json:async()=>({...row,ageMs:60})});
  await new Promise(r=>setImmediate(r));
  assert.equal(source.update(true)?.contacts.length,0);
  source.clear();
  resolve({ok:true,json:async()=>({...row,ageMs:0})});
  await new Promise(r=>setImmediate(r));
  assert.equal(source.update(false),null);
});
