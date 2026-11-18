import test from 'node:test';
import assert from 'node:assert/strict';
import {assistStates,cockpitClock} from '../src/features/cockpit/status_display.js';
import {createCockpitState,telemetry} from '../src/features/cockpit/state.js';
test('axis states use independent measured flags, including lateral active while overall enabled is false',()=>{
 const s=createCockpitState(()=>0);s.accept({service:'carState',sequence:1,decoded:{vEgo:0,gearShifter:'park'}});s.accept({service:'selfdriveState',sequence:1,decoded:{enabled:false}});s.accept({service:'carControl',sequence:1,decoded:{latActive:true,longActive:false}});
 assert.deepEqual(assistStates(telemetry(s)).map(x=>[x.axis,x.state,x.text]),[['橫向','active','介入中'],['縱向','inactive','未介入']]);
 assert.deepEqual(assistStates({latActive:'true',longActive:1}).map(x=>x.state),['unknown','unknown']);
});
test('expired car state cannot leave active axis labels, even if a control packet is newer',()=>{
 let now=0;const s=createCockpitState(()=>now);s.accept({service:'carState',sequence:1,decoded:{vEgo:20}});now=1000;s.accept({service:'carControl',sequence:1,decoded:{latActive:true,longActive:true}});now=1501;
 assert.deepEqual(assistStates(telemetry(s)).map(x=>x.state),['unknown','unknown']);
});
test('Taiwan date/time crosses dates correctly and exposes running seconds',()=>{
 const first=cockpitClock(new Date('2026-11-17T16:00:00Z')),next=cockpitClock(new Date('2026-11-17T16:00:01Z'));
 assert.match(first,/2026\/11\/18/);assert.match(first,/00:00:00/);assert.match(next,/00:00:01/);assert.notEqual(first,next);assert.equal(cockpitClock(new Date(NaN)),'日期時間無法取得');
});
