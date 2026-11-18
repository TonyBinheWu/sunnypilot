import test from 'node:test';
import assert from 'node:assert/strict';
import {createParkingView,insidePolygon} from '../src/features/cockpit/parking.js';
import {slotsFromPoints,parkingMarks} from '../src/features/drive/contents/vision/parking_marks.js';
import {vehicleLamps} from '../src/features/cockpit/vehicle_lamps.js';
import {sceneCamera,sceneProjection} from '../src/features/cockpit/scene_camera.js';
import {VEHICLE_SKINS} from '../src/features/cockpit/vehicle.js';
import {deriveVehicleHudPayload,withVehicleHudFields} from '../src/features/drive/contents/vision/hud/data_bridge.js';
import {mapPayload} from '../src/features/drive/contents/vision/hud/index.js';

test('raw speed and actual lamps survive both classic compact HUD flattening boundaries',()=>{
  const source=deriveVehicleHudPayload({carState:{vEgo:0,gearShifter:'park',lightingStateValid:true,lowBeamOn:true,brakeLights:true}});
  const first=withVehicleHudFields({gear:source.gear},source),second=withVehicleHudFields({gear:first.gear},first),final=mapPayload(second);
  assert.equal(final.vehicleSpeedMps,0);assert.equal(final.vehicleGear,'P');assert.equal(final.lowBeamOn,true);assert.equal(final.lightingStateValid,true);assert.equal(final.brakeLights,true);
  const unknown=mapPayload(withVehicleHudFields({},deriveVehicleHudPayload({carState:{}})));
  assert.equal(unknown.vehicleSpeedMps,null);assert.equal(unknown.lightingStateValid,false);
});

test('P entry plays once after a confirmed stop, never on initial P or stale/reconnected data',()=>{
  const p=createParkingView(),update=(v={})=>p.update({enabled:true,fresh:true,active:true,speed:0,gear:'P',now:0,...v});
  assert.equal(update().spin,false);assert.equal(update({now:5000}).spin,false);
  update({gear:'D',speed:3,now:6000});update({gear:'P',now:7000});assert.equal(update({now:7749}).spin,false);
  assert.equal(update({now:7750}).spin,true);assert.equal(update({now:9750}).yaw,180);
  assert.equal(update({now:11750}).spin,false);assert.equal(update({now:13000}).spin,false);
  update({fresh:false});assert.equal(update({now:14000}).spin,false);
});
test('moving, gear change, manual input, hidden and reduced motion veto the parked animation',()=>{
  for(const veto of [{speed:1},{gear:'R'},{active:false},{reducedMotion:true},{fresh:false}]){
    const p=createParkingView(),u=(x)=>p.update({enabled:true,fresh:true,speed:0,gear:'P',active:true,now:0,...x});
    u({gear:'D'});u({now:100});u({now:900});assert.equal(u({now:1000,...veto}).spin,false);
  }
  const p=createParkingView();p.update({enabled:true,fresh:true,speed:0,gear:'D'});p.update({enabled:true,fresh:true,speed:0,gear:'P',now:1});p.interact();
  assert.equal(p.update({enabled:true,fresh:true,speed:0,gear:'P',now:1000}).spin,false);
});
test('map containment and reverse require fresh low speed; manual override never forces overhead at speed',()=>{
  assert.equal(insidePolygon([1,1],[[0,0],[0,2],[2,2],[2,0],[0,0]]),true);assert.equal(insidePolygon([3,1],[[0,0],[0,2],[2,2],[2,0],[0,0]]),false);
  const p=createParkingView(),u=x=>p.update({enabled:true,fresh:true,speed:5,gear:'D',...x});
  assert.equal(u({inLot:true}).overhead,true);p.interact();assert.equal(u({inLot:true}).overhead,false);
  u({inLot:false});assert.equal(u({gear:'R'}).overhead,true);assert.equal(u({gear:'R',speed:21}).overhead,false);
});
test('paint candidates require two long separators and a crossing end line; never declare occupancy',()=>{
  const points=[];for(let x=4;x<=9;x+=.1)for(const y of [-4,-1.5])points.push([x,y]);
  assert.equal(slotsFromPoints(points).length,0);
  for(let y=-4;y<=-1.5;y+=.05)points.push([9,y]);
  const slots=slotsFromPoints(points);assert.ok(slots.length>0);assert.ok(slots.every(s=>s.occupancy==='unknown'));
  assert.deepEqual(parkingMarks(new Uint8ClampedArray(320*180*4),320,180,null),[]);
  assert.deepEqual(slotsFromPoints([]),[]);
});
test('headlamps depend on known actual lighting state and go dark with stale data',()=>{
  assert.equal(vehicleLamps({lightingStateValid:true,lowBeamOn:true}).lowBeam,true);
  assert.equal(vehicleLamps({lightingStateValid:false,lowBeamOn:true}).lowBeam,undefined);
  assert.equal(vehicleLamps({lightingStateValid:true,lowBeamOn:true},true).lowBeam,undefined);
  assert.equal(vehicleLamps({lightingStateValid:true,lowBeamOn:false}).lowBeam,false);
});
test('perspective camera pixels produce a calibrated paint candidate; dark frames produce none',()=>{
  const w=480,h=301,g={width:w,height:h,fx:659,fy:659,heightM:1,rpy:[0,0,0]},image=new Uint8ClampedArray(w*h*4);
  const pixel=([x,y])=>[w/2+y*g.fx/x,h/2+g.heightM*g.fy/x];
  function line(a,b){const p=pixel(a),q=pixel(b),n=Math.ceil(Math.hypot(q[0]-p[0],q[1]-p[1]));for(let i=0;i<=n;i++)for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++){
    const x=Math.round(p[0]+(q[0]-p[0])*i/n)+dx,y=Math.round(p[1]+(q[1]-p[1])*i/n)+dy;
    if(x>=0&&x<w&&y>=0&&y<h)image.fill(240,(y*w+x)*4,(y*w+x)*4+4);
  }}
  assert.deepEqual(parkingMarks(image,w,h,g),[]);
  line([5,-1.25],[10,-1.25]);line([5,1.25],[10,1.25]);line([10,-1.25],[10,1.25]);
  assert.ok(parkingMarks(image,w,h,g).length>0);
});
test('parking camera keeps all own-vehicle bounds framed on phone and head unit',()=>{
  for(const skin of Object.values(VEHICLE_SKINS))for(const [w,h] of [[1920,720],[1024,768],[380,825],[825,380]]){
    const view={parking:true,pitch:82,distance:14,skinScale:skin.scale},spec=sceneCamera(w,h,view),p=sceneProjection(w,h,view);
    assert.ok(spec.forward[2]<-.9);
    for(const x of [-2.42*skin.scale[0],2.42*skin.scale[0]])for(const y of [-1.16*skin.scale[1],1.16*skin.scale[1]])for(const z of [0,1.66*skin.scale[2]]){
      const q=p(x,y,z);assert.ok(q&&q[0]>=0&&q[0]<=w&&q[1]>=0&&q[1]<=h);
    }
  }
  for(const [w,h] of [[1920,720],[380,825],[825,380]]){
    const corners=[[12,-2],[18,-2],[18,1],[12,1]],p=sceneProjection(w,h,{parking:true,pitch:82,distance:24,parkingPoints:corners});
    for(const [x,y] of corners){const q=p(x,y,.065);assert.ok(q&&q[0]>0&&q[0]<w&&q[1]>0&&q[1]<h);}
  }
});
