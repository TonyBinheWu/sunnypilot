import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {parseRoadLibrary} from '../src/features/drive/contents/vision/hud/road_model_library.js';
import {metricSize,roadModelKind,roadModelLod} from '../src/features/drive/contents/vision/hud/road_model_selection.js';
import {createObjectTracker} from '../src/features/drive/contents/vision/hud/object_tracker.js';
import {createDrivingScene3D} from '../src/features/drive/contents/vision/hud/scene_3d.js';

const bytes=await readFile(new URL('../assets/road-models-v1.glb',import.meta.url));
const evidence={method:'stereo_3d',measuredAt:500,confidence:.95};
const dimensions={...evidence,unit:'m',length:4.8,width:1.90,height:1.72};

test('real GLB has twelve complete, strictly decreasing LOD sets in vehicle metres',async()=>{
  const lib=await parseRoadLibrary(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength));
  for(const kind of ['sedan','suv','mpv','pickup','truck','bus','bicycle','motorcycle','person','cone','barrier','drum']){
    let previous=Infinity;
    for(const level of [0,1,2]){
      const asset=lib.get(kind,level), tris=asset.geometry.index.count/3;
      assert.ok(tris>8 && tris<previous,kind+' LOD'+level);previous=tris;
      assert.ok(asset.size.toArray().every(n=>Number.isFinite(n)&&n>0&&n<12));
      assert.ok(Math.abs(asset.geometry.boundingBox.min.z)<.13);
      assert.ok(asset.material.isMeshStandardMaterial);
    }
  }
  assert.ok(lib.get('bus',0).size.x>9);
  lib.dispose();
});

test('vehicle silhouettes and scale require corroborated current metric dimensions',()=>{
  const base={measurementAt:500,kind:'car',vehicleClass:{...evidence,type:'suv'},dimensions};
  assert.equal(roadModelKind(base),'suv');
  assert.equal(roadModelKind({...base,kind:'pickup',vehicleClass:null,probability:.93}),'pickup');
  for(const d of [null,{...dimensions,measuredAt:200},{...dimensions,unit:'px'},{...dimensions,method:'image_box'},{...dimensions,width:20}]){
    assert.equal(metricSize({...base,dimensions:d}),null);assert.equal(roadModelKind({...base,dimensions:d}),'sedan');
  }
  assert.equal(roadModelKind({kind:'unknown',radarUsed:true}),null);
  assert.equal(roadModelKind({kind:'unknown',measurementAt:500,vehicleClass:{...evidence,type:'vehicle'}}),'sedan');
  assert.equal(roadModelKind({kind:'truck',probability:.97,measurementAt:500}),'sedan');
  assert.equal(roadModelKind({kind:'truck',probability:.97,measurementAt:500,dimensions}),'truck');
  assert.equal(roadModelKind({...base,vehicleClass:{...evidence,type:'pickup',confidence:.4}}),'sedan');
  assert.equal(roadModelLod(19,false,0),0);assert.equal(roadModelLod(22,false,0),1);
  assert.equal(roadModelLod(44,false,1),1);assert.equal(roadModelLod(46,false,1),2);
  assert.equal(roadModelLod(9,true,0),1);
});

test('one rendered track survives GLB loading, detail swaps, scaling and temporary prediction',async()=>{
  let world,notify;
  const loaded=new Promise(r=>notify=r);
  const canvas={dataset:{},setAttribute(){},addEventListener(){},removeEventListener(){},remove(){}};
  const renderer={setSize(){},setPixelRatio(){},dispose(){},render(s){world=s.children.find(n=>n.scale.y===-1);},info:{render:{calls:1,triangles:1}}};
  const device={WebGL2RenderingContext:class{},performance:{now:()=>500},fetch:async()=>new Response(bytes)};
  const scene=createDrivingScene3D({createElement:()=>canvas,baseURI:'https://localhost/'},device,{rendererFactory:()=>renderer,onChange:notify});
  const observed={kind:'car',x:10,y:0,id:'track-4',trackingId:4,state:'confirmed',measurementAt:500,vehicleClass:{...evidence,type:'mpv'},dimensions};
  const draw=(object)=>scene.render(800,500,{tracks:object?[object]:[]});
  draw(observed);const root=world.children.find(n=>n.position.x===10);
  await loaded;draw(observed);assert.equal(scene.snapshot().modelLibrary,'ready');
  const fine=root.children[0].geometry;
  observed.x=54;draw(observed);assert.equal(world.children.find(n=>n.position.x===54),root);
  assert.notEqual(root.children[0].geometry,fine);assert.deepEqual(scene.snapshot().lodCounts,[0,0,1]);
  assert.ok(Math.abs(root.scale.x*root.children[0].geometry.boundingBox.getSize(root.position.clone()).x-dimensions.length)<.03);
  observed.state='predicted';draw(observed);assert.ok(root.children[0].material.transparent);
  observed.state='lost';draw(observed);assert.equal(scene.snapshot().objects,0);scene.destroy();
});

test('cross traffic at a stopped intersection keeps its ID and moves between slow samples',()=>{
  const tracker=createObjectTracker(),motion={speed:0,yaw:0},ids=new Set();
  for(let i=0;i<7;i++){
    const t=i*300;
    tracker.ingest('vision',{stamp:t,objects:[{kind:'car',x:20,y:-12+i*3.6,probability:.9}]},t,motion);
    if(!i)continue;
    const a=tracker.sample(t+15,motion)[0],b=tracker.sample(t+230,motion)[0];
    assert.ok(a&&b);ids.add(a.id);ids.add(b.id);
    if(i>1){assert.ok(b.y>a.y+.8);assert.ok(Math.abs(b.heading-Math.PI/2)<.02);}
  }
  assert.equal(ids.size,1);tracker.drop('vision');assert.deepEqual(tracker.sample(1810,motion),[]);
});

test('ambiguous cross traffic cannot use the wider second-frame gate',()=>{
  const tracker=createObjectTracker(), motion={speed:0,yaw:0};
  const frame=(stamp,ys)=>tracker.ingest('vision',{stamp,objects:ys.map(y=>({kind:'car',x:20,y,probability:.91}))},stamp,motion);
  frame(0,[-6,-5.5]);frame(300,[-1.8,-1.5]);
  assert.deepEqual(tracker.sample(300,motion),[]);
});
