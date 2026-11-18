import test from 'node:test';
import assert from 'node:assert/strict';
import * as T from 'three';
import {sceneCamera,sceneProjection} from '../src/features/cockpit/scene_camera.js';
import {createSceneModels} from '../src/features/drive/contents/vision/hud/scene_3d_models.js';
import {VEHICLE_SKINS,resolveVehicleSkin} from '../src/features/cockpit/vehicle.js';
import {paintedVehicle,VEHICLE_PAINTS} from '../src/features/cockpit/vehicle_paint.js';
import {createViewOrbit} from '../src/features/cockpit/view_orbit.js';

test('every supported vehicle stays inside the viewport at orbit, pitch and zoom extremes in both renderers',()=>{
 const models=createSceneModels();
 for(const skin of Object.values(VEHICLE_SKINS)){
  const bounds=new T.Box3().setFromObject(models.get('ego',{skin}));
  for(const [w,h] of [[1920,720],[1280,720],[1024,768],[380,825],[825,380],[320,568]])for(const yaw of [-180,-90,0,90,179])for(const pitch of [18,25,60])for(const distance of [5,9,16,26]){
   const view={yaw,pitch,distance,skinScale:skin.scale,anchorY:.82},spec=sceneCamera(w,h,view),camera=new T.PerspectiveCamera(spec.fov,spec.aspect,.1,180);
   camera.up.set(0,0,1);camera.position.set(...spec.position);camera.lookAt(...spec.target);camera.updateMatrixWorld();
   const project=sceneProjection(w,h,view);
   for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
    const p=new T.Vector3(x,-y,z).project(camera),canvas=project(x,y,z);
    assert.ok(Math.abs(p.x)<.91&&Math.abs(p.y)<.85,`${skin.id} ${w}x${h} ${yaw}/${pitch}/${distance}: ${p.x},${p.y}`);
    assert.ok(Math.abs(canvas[0]-(p.x+1)/2*w)<1e-7&&Math.abs(canvas[1]-(1-p.y)/2*h)<1e-7);
   }
   const pivot=new T.Vector3(...spec.pivot).project(camera);assert.ok(Math.abs(pivot.x)<1e-10);assert.ok(Math.abs((1-pivot.y)/2-.62)<1e-10);
  }
 }models.dispose();
});
test('Kia and Hyundai skin identities remain distinct and unknown actual cars retain a generic model',()=>{
 for(const id of ['ev6','ev9','ev3','ev5','niro','seltos','k5'])assert.equal(resolveVehicleSkin({CarName:'KIA_'+id}).id,id);
 for(const [name,id] of [['IONIQ_5','ioniq5'],['IONIQ_6','ioniq6'],['TUCSON','tucson'],['SANTA_FE','santafe'],['KONA','kona'],['STARIA','staria'],['PALISADE','palisade'],['CUSTIN','custin'],['VENUE','venue'],['INSTER','inster'],['MUFASA','mufasa']])assert.equal(resolveVehicleSkin({CarName:'HYUNDAI_'+name}).id,id);
 assert.equal(resolveVehicleSkin({CarName:'UNRECOGNIZED',CarSelected3:'KIA_EV6'}).id,'generic');
});
test('paint never changes lamp geometry; active lamps emit, released lamps do not, and cache stays bounded',()=>{
 const models=createSceneModels();
 const lit=models.get('ego',{skin:paintedVehicle(VEHICLE_SKINS.ev6,'red'),lamps:{brake:true,left:true}}),dark=models.get('ego',{skin:paintedVehicle(VEHICLE_SKINS.ev6,'red'),lamps:{}});
 const a=lit.children[0].geometry.getAttribute('formosaLamp'),b=dark.children[0].geometry.getAttribute('formosaLamp');
 assert.ok([...a.array].some(v=>v===1));assert.ok([...b.array].every(v=>v===0));
 const colors=[];for(const paint of Object.keys(VEHICLE_PAINTS))colors.push([...models.get('ego',{skin:paintedVehicle(VEHICLE_SKINS.ev6,paint)}).children[0].geometry.getAttribute('color').array]);
 assert.equal(new Set(colors.map(JSON.stringify)).size,Object.keys(VEHICLE_PAINTS).length);
 for(const skin of Object.values(VEHICLE_SKINS))for(const paint of Object.keys(VEHICLE_PAINTS))models.get('ego',{skin:paintedVehicle(skin,paint)});
 assert.ok(models.stats().templates<=32);assert.ok(models.stats().geometries<40);models.dispose();
 assert.equal(paintedVehicle(VEHICLE_SKINS.ev6,'url(https://bad)').paintId,'white');
});
test('visual zoom is bounded and reset restores the vehicle pivot without control changes',()=>{
 const orbit=createViewOrbit();assert.equal(orbit.zoom,1);orbit.zoomBy(100);assert.equal(orbit.zoom,1.6);orbit.zoomBy(.0001);assert.equal(orbit.zoom,.6);assert.equal(orbit.setZoom(NaN),false);orbit.key('+');assert.ok(orbit.zoom>.6);orbit.reset();assert.equal(orbit.zoom,1);assert.deepEqual(orbit.pose,{yaw:0,pitch:25});
});
