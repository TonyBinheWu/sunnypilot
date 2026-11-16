import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createCockpitState,telemetry,MODES} from '../src/features/cockpit/state.js';
test('freshness is independent, duplicate samples never refresh stale state',()=>{
  let now=0;const s=createCockpitState(()=>now),f={service:'carState',sequence:1,decoded:{vEgoCluster:10,vCruiseCluster:90,gearShifter:'drive'}};
  assert.equal(telemetry(s).speed,null);assert.equal(s.accept(f),true);assert.equal(telemetry(s).speed,36);
  now=1400;assert.equal(s.accept(f),false);now=1501;assert.equal(telemetry(s).speed,null);
  s.accept({...f,sequence:2});assert.equal(telemetry(s).speed,36);s.clear();assert.equal(telemetry(s).speed,null);
});
test('zero is a measurement, missing/nonfinite state is never zero or enabled',()=>{
  const s=createCockpitState(()=>0);s.accept({service:'carState',sequence:0,decoded:{vEgoCluster:0}});assert.equal(telemetry(s).speed,0);
  assert.equal(telemetry(s).enabled,null);s.accept({service:'carState',sequence:1,decoded:{vEgoCluster:NaN}});assert.equal(telemetry(s).speed,null);
  assert.equal(s.accept({service:'bad',sequence:1,decoded:{}}),false);
});
test('park admission requires fresh P, stopped speed and disengaged assistance',()=>{
  let now=0;const s=createCockpitState(()=>now);const car={service:'carState',sequence:1,decoded:{gearShifter:'park',vEgo:0}};
  s.accept(car);assert.equal(telemetry(s).parked,false);s.accept({service:'selfdriveState',sequence:1,decoded:{enabled:false,alertText1:'接管',alertText2:'注意道路'}});
  assert.equal(telemetry(s).parked,false);
  s.accept({service:'carControl',sequence:1,decoded:{latActive:true,longActive:false}});
  assert.equal(telemetry(s).parked,false);assert.equal(telemetry(s).latActive,true);
  s.accept({service:'carControl',sequence:2,decoded:{latActive:false,longActive:false}});
  assert.equal(telemetry(s).parked,true);assert.equal(telemetry(s).alert,'接管\n注意道路');
  s.accept({...car,sequence:2,decoded:{gearShifter:'drive',vEgo:0}});assert.equal(telemetry(s).parked,false);
  s.accept({...car,sequence:3});now=1600;assert.equal(telemetry(s).parked,false);assert.equal(telemetry(s).alert,'');
  assert.deepEqual(Object.keys(MODES),['1','2','3','4']);
});
