import {test} from 'node:test';
import assert from 'node:assert/strict';
import {resolveVehicleSkin,VEHICLE_SKINS,drawCockpitVehicle,createVehicleSkinCache} from '../src/features/cockpit/vehicle.js';
import {createCockpitState,cockpitHudPayload} from '../src/features/cockpit/state.js';
test('actual fingerprint takes precedence; selection is a read-only fallback with a generic unknown silhouette',()=>{
  assert.equal(resolveVehicleSkin({CarName:'HYUNDAI_IONIQ_5',CarSelected3:'Kia EV6 (with HDA II) 2022-24'}).id,'ioniq5');
  assert.equal(resolveVehicleSkin({CarName:'unknown',CarSelected3:'Kia Sorento (without HDA II) 2024-25'}).id,'sorento');
  for(const [name,id] of [['KIA_EV6','ev6'],['TESLA_MODEL_3','model3'],['TESLA_MODEL_Y','modely'],['TOYOTA_RAV4','suv']])assert.equal(resolveVehicleSkin({CarName:name}).id,id);
  assert.equal(resolveVehicleSkin({CarName:'UNRECOGNIZED_REAL_CAR',CarSelected3:'Kia EV6'}).id,'generic');
  for(const values of [{},{CarName:0},{CarName:{toString(){throw Error();}}},{CarName:'https://example.com/skin.glb'}]){
    const skin=resolveVehicleSkin(values);assert.equal(skin.id,'generic');assert.equal(skin.illustrative,true);
  }
});
test('each supported silhouette is distinct finite original geometry; invalid preset IDs fall back',()=>{
  const signatures=[];
  for(const id of Object.keys(VEHICLE_SKINS)){
    const commands=[];const ctx=new Proxy({},{get:(t,k)=>t[k]??((...v)=>commands.push([k,...v])),set:(t,k,v)=>(t[k]=v,true)});
    drawCockpitVehicle(ctx,(x,y,z)=>{assert.ok([x,y,z].every(Number.isFinite));return [x*20+y*5,y*15-z*10];},{skin:{id}});
    assert.ok(commands.some(c=>c[0]==='fill'));signatures.push(JSON.stringify(commands));
  }
  assert.equal(new Set(signatures).size,Object.keys(VEHICLE_SKINS).length);
});
test('identity loading is GET-only, bounded, background-aware and aborts on destruction',async()=>{
  let now=0,calls=0,resolveRequest;const timers=new Map();
  const target={document:{hidden:true},AbortController,performance:{now:()=>now},setTimeout:(fn)=>{timers.set(1,fn);return 1;},clearTimeout:id=>timers.delete(id),fetch:async(url,options)=>{assert.equal(url,'/api/params_bulk?names=CarName,CarSelected3');assert.equal(options.method,undefined);calls++;return new Promise(r=>{resolveRequest=r;});}};
  const cache=createVehicleSkinCache(target);cache.refresh();assert.equal(calls,0);target.document.hidden=false;cache.refresh();await Promise.resolve();assert.equal(calls,1);
  cache.refresh();assert.equal(calls,1);resolveRequest({ok:true,json:async()=>({values:{CarName:'KIA_EV6'}})});await new Promise(setImmediate);
  assert.equal(cache.current().id,'ev6');assert.equal(timers.size,0);cache.refresh();assert.equal(calls,1);
  now=30001;cache.refresh();await Promise.resolve();assert.equal(calls,2);cache.destroy();resolveRequest({ok:true,json:async()=>({values:{CarName:'KIA_SORENTO'}})});await new Promise(setImmediate);assert.equal(cache.current().id,'ev6');assert.equal(timers.size,0);
});
test('camera-independent instruments require fresh carState and retain zero and metric normalization',()=>{
  let now=0;const state=createCockpitState(()=>now);
  assert.equal(cockpitHudPayload(state),null);
  state.accept({service:'carState',sequence:1,decoded:{gearShifter:'park',vEgoCluster:0,vCruiseCluster:90}});
  const payload=cockpitHudPayload(state,false);assert.equal(payload.vEgoKph,0);assert.equal(payload.gear,'P');assert.equal(payload.isMetric,false);
  now=1501;assert.equal(cockpitHudPayload(state),null);
});
