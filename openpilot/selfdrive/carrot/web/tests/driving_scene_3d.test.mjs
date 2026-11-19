import test from 'node:test';
import assert from 'node:assert/strict';
import * as T from 'three';
import {sceneCamera,sceneTargets,roadRibbon,createDrivingScene3D} from '../src/features/drive/contents/vision/hud/scene_3d.js';
import {createSceneModels} from '../src/features/drive/contents/vision/hud/scene_3d_models.js';
import {VEHICLE_SKINS} from '../src/features/cockpit/vehicle.js';
import {ROAD_CLASSES} from '../src/features/drive/contents/vision/hud/object_classes.js';

test('actual observations admit only finite ground classes, keeping radar unclassified and elevated observations out',()=>{
  const make=(kind,x=20,y=2)=>({kind,x,y});
  const data={radar:{leadOne:{status:true,dRel:12,yRel:3}},vision:{objects:[make('person'),make('car'),make('motorcycle'),make('traffic light'),make('stop sign'),make('car',NaN),make('car',-1),make('dog',4,99)],imageObjects:[{kind:'traffic light',box:[.1,.1,.1,.1]}]},road:{objects:[make('traffic cone')]}};
  assert.deepEqual(sceneTargets(data).map(o=>o.kind),['unknown','person','car','motorcycle','traffic cone']);
  assert.equal(sceneTargets(data)[0].y,-3);
  assert.equal(sceneTargets({vision:{objects:Array(1000).fill(make('car'))}}).length,80);
});

test('3D camera fits ego above the fixed dock on 1920x720,16:9 and4:3, and preserves orbit',()=>{
  for(const [width,height] of [[1920,720],[1920,1080],[1024,768],[800,600]])for(const progress of [0,1]){
    const spec=sceneCamera(width,height,{distance:9+7*progress,height:6+6*progress,anchorY:.78+.07*progress});
    const camera=new T.PerspectiveCamera(spec.fov,spec.aspect,.1,180);camera.up.set(0,0,1);camera.position.set(...spec.position);camera.lookAt(...spec.target);camera.updateMatrixWorld();
    const project=p=>{const v=new T.Vector3(p[0],-p[1],p[2]).project(camera);return [(v.x+1)/2*width,(1-v.y)/2*height];};
    const rear=project([-2.2,0,.3]),roof=project([0,0,1.5]);
    assert.ok(rear[1]<height*.9,`${width}x${height}: rear ${rear[1]/height}`);assert.ok(roof[1]>height*.25&&roof[1]<height*.8);
    assert.ok(project([20,3,0])[0]>width/2);
  }
  assert.notDeepEqual(sceneCamera(1280,720,{yaw:40}).position,sceneCamera(1280,720).position);
});

test('reusable road ribbons continue only an observed near segment under the viewer, never invent missing geometry',()=>{
  const path={x:[0,10,20],y:[0,1,2]};
  const out=roadRibbon(path,-.05,.05,{behind:true});assert.equal(out[0],-12);assert.equal(Math.max(...out.filter((_,i)=>i%3===0)),20);
  assert.deepEqual(roadRibbon(null,-1,1,{behind:true}),[]);
  assert.deepEqual(roadRibbon({x:[0,NaN,10],y:[0,0,0]},-1,1),[]);
  assert.equal(roadRibbon({x:[10,20],y:[0,0]},-1,1,{behind:true})[0],10);
});

test('portrait phones retain the complete default Kia mesh and a forward horizon at close and highway zoom',()=>{
  const models=createSceneModels();
  for(const [width,height] of [[320,568],[360,800],[393,852],[412,915],[480,800]])for(const progress of [0,1])for(const id of ['ev6','sorento','sportage','carnival','ev9']){
    const spec=sceneCamera(width,height,{distance:9+7*progress,height:6+6*progress,anchorY:.78+.07*progress});
    const camera=new T.PerspectiveCamera(spec.fov,spec.aspect,.1,180);camera.up.set(0,0,1);camera.position.set(...spec.position);camera.lookAt(...spec.target);camera.updateMatrixWorld();
    const mesh=models.get('ego',{skin:VEHICLE_SKINS[id]});mesh.scale.y=-1;mesh.updateMatrixWorld();
    mesh.traverse(o=>{const p=o.geometry?.getAttribute('position');if(!p)return;for(let i=0;i<p.count;i++){
      const v=new T.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld).project(camera);
      assert.ok(v.x>-.96&&v.x<.96,`${width}x${height} ${id}: horizontal ${v.x}`);
      assert.ok(v.y>-.82&&v.y<.65,`${width}x${height} ${id}: vertical ${v.y}`);
    }});
  }models.dispose();
});

test('every supported classified object has finite 3D geometry; image-only icons stay distinct from scene admission',()=>{
  const models=createSceneModels(),sizes=new Set();
  for(const kind of [...ROAD_CLASSES,'traffic cone','unknown','traffic light','stop sign','crosswalk','bird']){
    const model=models.get(kind);model.updateMatrixWorld();let vertices=0;
    model.traverse(mesh=>{const p=mesh.geometry?.getAttribute('position');if(p){vertices+=p.count;assert.ok([...p.array].every(Number.isFinite));}});
    assert.ok(vertices>8,kind);const size=new T.Box3().setFromObject(model).getSize(new T.Vector3());assert.ok(size.z>0,kind);sizes.add(vertices);
    const again=models.get(kind);assert.notEqual(again,model);assert.equal(again.children[0].geometry,model.children[0].geometry);
  }
  assert.ok(sizes.size>8);const n=models.stats();models.get('person');assert.deepEqual(models.stats(),n);models.dispose();
});

test('all Kia skins and measured lamp combinations share bounded reusable geometry with distinct silhouettes',()=>{
  const models=createSceneModels();for(const id of ['ev6','sorento','sportage','carnival','ev9'])for(const brake of [false,true]){
    const mesh=models.get('ego',{skin:VEHICLE_SKINS[id],lamps:{brake,left:true}});assert.ok(new T.Box3().setFromObject(mesh).max.z>1);
  }assert.equal(models.stats().templates,10);models.dispose();
});

test('unsupported WebGL retains the existing canvas path without GPU work or subscriptions',()=>{
  const events=new Map(),canvas={hidden:false,setAttribute(){},addEventListener:(k,v)=>events.set(k,v),removeEventListener:k=>events.delete(k),remove(){}};
  const renderer=createDrivingScene3D({createElement:()=>canvas},{ });assert.equal(renderer.render(800,600,{}),false);assert.equal(canvas.hidden,true);
  renderer.destroy();assert.equal(events.size,0);
});

test('moving classified geometry survives resize and context restoration; expired observations release nodes',()=>{
  const events=new Map(),canvas={dataset:{},hidden:false,setAttribute(){},addEventListener:(k,v)=>events.set(k,v),removeEventListener:k=>events.delete(k),remove(){}};
  const devices=[];let changes=0;
  const rendererFactory=()=>{const r={sizeChanges:0,disposed:false,info:{render:{calls:10,triangles:100}},setPixelRatio(){},setSize(){this.sizeChanges++;},render(scene){this.scene=scene;},clearDepth(){},dispose(){this.disposed=true;}};devices.push(r);return r;};
  const painter=createDrivingScene3D({createElement:()=>canvas},{WebGL2RenderingContext:class{}},{rendererFactory,onChange:()=>changes++});
  const objects=[{id:'person',kind:'person',x:10,y:-2},{id:'car',kind:'car',x:20,y:3},{id:'bike',kind:'motorcycle',x:15,y:1}];
  const scene={vision:{objects}},options={skin:VEHICLE_SKINS.ev6};
  assert.equal(painter.render(1920,720,scene,options),true);assert.equal(painter.snapshot().classified,3);assert.equal(devices[0].sizeChanges,1);
  const world=devices[0].scene.children.find(o=>o.scale.y===-1),person=world.children.find(o=>o.position.x===10);
  assert.ok(person);objects[0].x=12;painter.render(1920,720,scene,options);assert.equal(person.position.x,12);assert.equal(devices[0].sizeChanges,1);
  painter.render(1024,768,scene,options);assert.equal(devices[0].sizeChanges,2);
  const key=objects[0].id;
  objects[0].state='predicted';painter.render(1024,768,scene,options);
  assert.equal(person.userData.predicted,true);assert.equal(person.children[0].material.transparent,true);
  objects[0].state='confirmed';painter.render(1024,768,scene,options);
  assert.equal(person.userData.predicted,false);assert.equal(person.children[0].material.transparent,false);
  painter.render(1024,768,{tracks:[]},options);assert.equal(painter.snapshot().pooled,3);
  objects[0].id='new-person';painter.render(1024,768,scene,options);assert.equal(painter.snapshot().reused,3);
  assert.equal(world.children.find(o=>o.position.x===12),person);objects[0].id=key;
  const path={x:[0,10],y:[0,0]};
  assert.equal(painter.render(1024,768,{tracks:[],model:{position:path,laneLines:[path,path,path,path],laneLineProbs:[1,1,1,1]},paint:[24,24,24,24]},{...options,rainbow:true}),true);
  let prevented=false;events.get('webglcontextlost')({preventDefault(){prevented=true;}});assert.ok(prevented);assert.equal(painter.render(1024,768,scene,options),false);
  events.get('webglcontextrestored')();assert.ok(devices[0].disposed);assert.equal(changes,2);assert.equal(painter.render(1024,768,scene,options),true);assert.equal(painter.snapshot().classified,3);
  painter.render(1024,768,{vision:{objects:[]}},options);assert.equal(painter.snapshot().objects,0);
  painter.pause();assert.equal(canvas.hidden,true);painter.destroy();assert.ok(devices[1].disposed);assert.equal(events.size,0);
});
