import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createEgoVehicle3D} from '../src/features/cockpit/ego_vehicle_3d.js';
import {vehicleLamps} from '../src/features/cockpit/vehicle_lamps.js';
import {paintedVehicle} from '../src/features/cockpit/vehicle_paint.js';
import {deriveVehicleHudPayload} from '../src/features/drive/contents/vision/hud/data_bridge.js';

test('one generic ego instance changes paint, LOD, wheels and lamps independently of surrounding tracks',async()=>{
  let ready,loads=0;
  const loaded=new Promise(resolve=>{ready=resolve;});
  const target={fetch:async()=>{loads++;return new Response(await readFile(new URL('../assets/ego-cuv-v1.glb',import.meta.url)));}};
  const ego=createEgoVehicle3D(target,{baseURI:'http://localhost/'},ready);
  const options={skin:paintedVehicle({id:'generic'},'#AA6633'),lamps:{},quality:'auto',range:9,at:100,speed:2};
  assert.equal(ego.update(options),null);await loaded;
  const root=ego.update(options),nodes=new Map();
  root.traverse(n=>{if(n.isMesh)nodes.set(n.material.name,n.material);});
  assert.equal(root.children.filter(n=>n.visible)[0].name,'CUV_LOD0');
  assert.equal(nodes.get('Paint').color.getHexString(),'aa6633');
  const front=root.getObjectByName('FrontLeft_0');
  const updated=ego.update({...options,at:200,steer:12,lamps:vehicleLamps({brakeLights:true,rightBlinker:true},false,100)});
  assert.equal(updated,root);assert.ok(front.rotation.y>0);assert.ok(front.children[0].rotation.x>0);
  assert.ok(nodes.get('RearLens').emissiveIntensity>1);assert.ok(nodes.get('IndicatorRight').emissiveIntensity>1);
  assert.equal(nodes.get('IndicatorLeft').emissiveIntensity,0);
  for(const [quality,expected] of [['standard',0],['low',1]]){
    assert.equal(ego.update({...options,quality,lamps:vehicleLamps({},true)}),root);
    assert.deepEqual(root.children.filter(n=>n.visible).map(n=>n.name),['CUV_LOD'+expected]);
  }
  assert.equal(nodes.get('RearLens').emissiveIntensity,0);assert.equal(nodes.get('Headlamp').emissiveIntensity,0);
  assert.equal(ego.update({...options,skin:{id:'ev6'}}),null);assert.equal(loads,1);ego.dispose();
});

test('ego wheel estimate requires a measured steering angle and a usable ratio',()=>{
  const state={carControl:{actuators:{steeringAngleDeg:120}},carState:{steeringAngleDeg:35}};
  assert.equal(deriveVehicleHudPayload(state).measuredRoadWheelDeg,null);
  state.carParams={steerRatio:14};assert.equal(deriveVehicleHudPayload(state).measuredRoadWheelDeg,2.5);
  delete state.carState.steeringAngleDeg;assert.equal(deriveVehicleHudPayload(state).measuredRoadWheelDeg,null);
});
