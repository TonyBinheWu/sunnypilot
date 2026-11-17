import test from 'node:test';
import assert from 'node:assert/strict';
import {vehicleLamps} from '../src/features/cockpit/vehicle_lamps.js';
import {drawCockpitVehicle,resolveVehicleSkin} from '../src/features/cockpit/vehicle.js';
import {createCockpitState,cockpitHudPayload} from '../src/features/cockpit/state.js';
test('brake lamps follow measured brakeLights, never inferred deceleration; stale lamps clear',()=>{
 assert.deepEqual(vehicleLamps({brakeLights:true,leftBlinker:true},false,100),{brake:true,left:true,right:false});
 assert.deepEqual(vehicleLamps({aEgo:-3,brakePressed:true},false,100),{brake:false,left:false,right:false});
 assert.deepEqual(vehicleLamps({brakeLights:true,leftBlinker:true,rightBlinker:true},true,100),{brake:false,left:false,right:false});
 assert.deepEqual(vehicleLamps({leftBlinker:true,rightBlinker:true},false,750),{brake:false,left:false,right:false});
 assert.deepEqual(vehicleLamps({leftBlinker:true,rightBlinker:true},false,1100),{brake:false,left:true,right:true});
 assert.equal(vehicleLamps({brakeLights:'true',leftBlinker:1}).brake,false);
});
test('compact cockpit HUD carries only fresh measured brake and both blinker states',()=>{
 let now=0;const s=createCockpitState(()=>now);s.accept({service:'carState',sequence:1,decoded:{brakeLights:true,leftBlinker:false,rightBlinker:true}});
 const p=cockpitHudPayload(s);assert.equal(p.brakeLights,true);assert.equal(p.leftBlinker,false);assert.equal(p.rightBlinker,true);
 now=1501;assert.equal(cockpitHudPayload(s),null);
});
test('five Kia models resolve separately, render different geometry and illuminate the correct lamp side',()=>{
 const signatures=new Set();
 for(const id of ['ev6','sorento','sportage','carnival','ev9']){
  const skin=resolveVehicleSkin({CarName:'KIA_'+id.toUpperCase()});assert.equal(skin.id,id);
  const draw=lamps=>{const faces=[];let points=[];const ctx={save(){},restore(){},beginPath(){points=[];},moveTo(...v){points.push(v);},lineTo(...v){points.push(v);},closePath(){},fill(){faces.push({color:this.fillStyle,points});}};
   drawCockpitVehicle(ctx,(x,y,z)=>[y*100,x*20-z*30],{skin,lamps});return faces;};
  const off=draw({}),on=draw({brake:true,left:true});signatures.add(JSON.stringify(off));
  assert.equal(off.some(f=>f.color==='#ff343d'),false);assert.ok(on.some(f=>f.color==='#ff343d'));
  const amber=on.filter(f=>f.color==='#ffb126');assert.equal(amber.length,3);assert.ok(amber.every(f=>f.points.every(p=>p[0]<0)));
  assert.equal(draw({right:true}).filter(f=>f.color==='#ffb126').every(f=>f.points.every(p=>p[0]>0)),true);
 }
 assert.equal(signatures.size,5);assert.equal(resolveVehicleSkin({CarName:'UNRECOGNIZED_REAL_CAR'}).id,'generic');
});
