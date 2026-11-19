import * as T from 'three';
import {toCreasedNormals} from 'three/addons/utils/BufferGeometryUtils.js';
import {drawVehicleMesh,VEHICLE_CONTACT_SHADOW} from './object_mesh.js';
import {ANIMALS} from './object_classes.js';

// Original illustrative geometry, not manufacturer CAD or estimated dimensions.
// Coordinates: x forward, y right, z up. Never feed this artwork to control.
export function createSceneModels(){
  const materials=new Map(),templates=new Map(),geometries=new Set(),vehicleResources=new Map();let vehicleSerial=0;
  const mat=(color)=>{if(!materials.has(color))materials.set(color,new T.MeshPhongMaterial({color,shininess:45}));return materials.get(color);};
  const geometry=g=>{geometries.add(g);return g;};
  const box=geometry(new T.BoxGeometry(1,1,1)),sphere=geometry(new T.SphereGeometry(1,16,10));
  const cylinder=geometry(new T.CylinderGeometry(1,1,1,16)),cone=geometry(new T.ConeGeometry(1,1,20));
  const part=(parent,g,color,p,s,r=null)=>{const mesh=new T.Mesh(g,mat(color));mesh.position.set(...p);mesh.scale.set(...s);if(r)mesh.rotation.set(...r);parent.add(mesh);return mesh;};
  const block=(g,p,s,c)=>part(g,box,c,p,s);
  const ball=(g,p,s,c)=>part(g,sphere,c,p,s);
  const tube=(g,p,s,c)=>part(g,cylinder,c,p,s,[Math.PI/2,0,0]);
  function vehicle(skin,lamps){
    // Reuse the canonical skin/lamps mesh so both rendering backends stay alike.
    const positions=[],colors=[],emission=[];let polygon=[],color='#fff';
    const capture={save(){},restore(){},beginPath(){polygon=[];},moveTo(...p){polygon.push(p);},lineTo(...p){polygon.push(p);},closePath(){},stroke(){},fill(){
      if(color===VEHICLE_CONTACT_SHADOW)return;const c=new T.Color(color);
      for(let i=1;i<polygon.length-1;i++)for(const p of [polygon[0],polygon[i],polygon[i+1]]){positions.push(...p.slice(0,3));colors.push(c.r,c.g,c.b);emission.push(color==='#ff343d'||color==='#ffb126'||color==='#f4f9ff'?1:0);}
    },set fillStyle(c){color=c;}};
    const project=(x,y,z)=>[x,y,z];project.view=[-8,0,6];drawVehicleMesh(capture,project,{body:skin,lamps,ego:true});
    const g=new T.Group(),buffer=geometry(new T.BufferGeometry());
    buffer.setAttribute('position',new T.Float32BufferAttribute(positions,3));buffer.setAttribute('color',new T.Float32BufferAttribute(colors,3));buffer.setAttribute('formosaLamp',new T.Float32BufferAttribute(emission,1));buffer.computeVertexNormals();toCreasedNormals(buffer,Math.PI/4);
    const paint=new T.MeshPhongMaterial({vertexColors:true,side:T.DoubleSide,shininess:30});
    paint.onBeforeCompile=shader=>{
      shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nattribute float formosaLamp; varying float vFormosaLamp;').replace('#include <begin_vertex>','#include <begin_vertex>\nvFormosaLamp = formosaLamp;');
      shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying float vFormosaLamp;').replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\ntotalEmissiveRadiance += vFormosaLamp * vColor.rgb * 0.7;');
    };
    paint.customProgramCacheKey=()=> 'formosa-vehicle-lamps-v1';
    const materialKey='vehicle-'+vehicleSerial++;materials.set(materialKey,paint);vehicleResources.set(g,{buffer,paint,materialKey});g.add(new T.Mesh(buffer,paint));
    return g;
  }
  function make(kind,skin,lamps){
    if(kind==='ego'||kind==='car')return vehicle(kind==='ego'?skin:{paint:'#c4c2be'},kind==='ego'?lamps:{});
    const g=new T.Group();
    if(kind==='unknown'){
      // Unclassified target: a neutral open volume, NEVER a car-shaped guess.
      const shape=geometry(new T.EdgesGeometry(new T.BoxGeometry(1.1,.8,.85)));
      let material=materials.get('unknown');if(!material){material=new T.LineBasicMaterial({color:'#b4c3d4',transparent:true,opacity:.7});materials.set('unknown',material);}
      const frame=new T.LineSegments(shape,material);frame.position.z=.5;g.add(frame);return g;
    }
    if(kind==='traffic cone'){
      block(g,[0,0,.04],[.65,.65,.08],'#333943');part(g,cone,'#ff7b25',[0,0,.48],[.28,.85,.28],[Math.PI/2,0,0]);
      const band=geometry(new T.CylinderGeometry(.11,.17,.18,20));part(g,band,'#f5f7fa',[0,0,.48],[1,1,1],[Math.PI/2,0,0]);return g;
    }
    // These models are UI observation icons only. Their elevated image boxes
    // do not provide the distance needed for admission to the road scene.
    if(kind==='traffic light'){
      tube(g,[0,0,.85],[.055,1.7,.055],'#899aaf');block(g,[0,0,1.7],[.28,.46,1.18],'#25364a');
      for(const z of [1.34,1.70,2.06])ball(g,[-.16,0,z],[.045,.16,.16],'#778899');return g;
    }
    if(kind==='stop sign'){
      tube(g,[0,0,.8],[.035,1.6,.035],'#b5c1d2');const disc=geometry(new T.CylinderGeometry(.47,.47,.065,8));
      part(g,disc,'#e5edf5',[0,0,1.65],[1,1,1],[0,0,Math.PI/2]);part(g,disc,'#b52d40',[-.04,0,1.65],[.88,1,.88],[0,0,Math.PI/2]);return g;
    }
    if(kind==='crosswalk'){
      block(g,[0,0,0],[2.2,1.4,.08],'#354256');for(let x=-.9;x<1;x+=.36)block(g,[x,0,.055],[.19,1.15,.04],'#dce9f6');return g;
    }
    if(kind==='bird'){
      ball(g,[0,0,.6],[.35,.18,.22],'#9db5cc');ball(g,[.29,0,.78],[.17,.14,.17],'#bfd4e6');
      for(const y of [-.43,.43])ball(g,[-.08,y,.6],[.3,.43,.055],'#6e8aa6');return g;
    }
    if(kind==='person'){
      ball(g,[0,0,1.57],[.15,.15,.18],'#c5d6e7');ball(g,[0,0,1.08],[.15,.25,.36],'#9db5cd');
      for(const s of [-1,1]){tube(g,[0,s*.14,.38],[.08,.65,.08],'#667f98');tube(g,[0,s*.31,1.02],[.07,.50,.07],'#a8bfd7');block(g,[.06,s*.14,.06],[.28,.16,.12],'#3c5064');}return g;
    }
    if(kind==='motorcycle'||kind==='bicycle'){
      for(const x of [-.7,.7]){part(g,cylinder,'#252d38',[x,0,.33],[.32,.13,.32]);part(g,cylinder,'#9fb2c7',[x,0,.33],[.22,.14,.22]);}
      block(g,[0,0,.48],[1.05,kind==='motorcycle'?.42:.08,.23],'#91adc9');block(g,[-.12,0,.76],[.55,.28,.12],'#35485c');tube(g,[.55,0,.7],[.05,.7,.05],'#b7cada');block(g,[.58,0,1.02],[.12,.62,.07],'#b7cada');return g;
    }
    if(kind==='truck'||kind==='bus'){
      block(g,[-.6,0,1.55],[5.4,2.1,2.45],'#becddb');block(g,[2.45,0,1.03],[1.5,2.05,1.7],'#91a8bf');block(g,[3.21,0,1.49],[.02,1.8,.66],'#263e58');
      if(kind==='bus')for(const s of [-1,1])block(g,[-.6,s*1.06,1.95],[5.1,.02,.78],'#304963');
      for(const x of [-2.3,2.2])for(const y of [-1,1])part(g,cylinder,'#26303a',[x,y,.46],[.43,.22,.43]);
      for(const y of [-.8,.8])block(g,[-3.31,y,.62],[.03,.24,.24],'#bf3348');return g;
    }
    if(ANIMALS.includes(kind)){
      const size=({cat:.45,dog:.65,horse:1.2,sheep:.8,cow:1.2,elephant:2.3,bear:1.1,zebra:1.2,giraffe:1.5})[kind],body=new T.Group();g.add(body);body.scale.setScalar(size);
      const coat=kind==='bear'?'#6b8198':'#9eb5cb';ball(body,[0,0,.9],[.72,.3,.36],coat);
      for(const x of [-.45,.45])for(const y of [-.21,.21])tube(body,[x,y,.37],[.07,.7,.07],'#768fa8');
      const neck=kind==='giraffe'?1.7:kind==='horse'||kind==='zebra'?.6:.2;
      ball(body,[.55,0,1.1+neck/2],[.16,.18,neck/2+.16],coat);ball(body,[.76,0,1.1+neck],[.28,.19,.22],coat);
      for(const y of [-.14,.14])ball(body,[.65,y,1.33+neck],[.09,.05,.14],coat);
      if(kind==='elephant'){tube(body,[1.01,0,.9],[.10,.9,.10],coat);for(const y of [-.35,.35])ball(body,[.55,y,1.1],[.3,.07,.4],coat);}return g;
    }
    return g;
  }
  function combine(group){
    // Bake static parts once per template; each classified object costs one
    // draw call rather than one per limb, wheel or panel on mobile hardware.
    if(group.children.some(o=>o.isLineSegments)||group.children.length<2)return group;
    group.updateMatrixWorld(true);const positions=[],normals=[],colors=[],v=new T.Vector3(),n=new T.Vector3();
    group.traverse(o=>{if(!o.isMesh)return;const g=o.geometry,p=g.getAttribute('position'),normal=g.getAttribute('normal'),index=g.index,normalMatrix=new T.Matrix3().getNormalMatrix(o.matrixWorld);
      for(let i=0;i<(index?.count??p.count);i++){const k=index?index.getX(i):i;v.fromBufferAttribute(p,k).applyMatrix4(o.matrixWorld);positions.push(v.x,v.y,v.z);n.fromBufferAttribute(normal,k).applyMatrix3(normalMatrix).normalize();normals.push(n.x,n.y,n.z);colors.push(o.material.color.r,o.material.color.g,o.material.color.b);}
    });
    const g=geometry(new T.BufferGeometry());g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setAttribute('normal',new T.Float32BufferAttribute(normals,3));g.setAttribute('color',new T.Float32BufferAttribute(colors,3));
    if(!materials.has('combined'))materials.set('combined',new T.MeshPhongMaterial({vertexColors:true,shininess:40}));
    const result=new T.Group();result.add(new T.Mesh(g,materials.get('combined')));return result;
  }
  return {get(kind,{skin,lamps={}}={}){
    const key=kind==='ego'?`ego:${skin?.id||'generic'}:${skin?.paint||'default'}:${!!lamps.brake}:${!!lamps.left}:${!!lamps.right}:${!!lamps.lowBeam}:${!!lamps.highBeam}`:kind;
    if(!templates.has(key))templates.set(key,combine(make(kind,skin,lamps)));
    else if(kind==='ego'){const value=templates.get(key);templates.delete(key);templates.set(key,value);}
    const egoKeys=[...templates.keys()].filter(key=>key.startsWith('ego:'));
    while(egoKeys.length>32){const oldest=egoKeys.shift(),template=templates.get(oldest),resource=vehicleResources.get(template);templates.delete(oldest);if(resource){resource.buffer.dispose();resource.paint.dispose();geometries.delete(resource.buffer);materials.delete(resource.materialKey);vehicleResources.delete(template);}}
    return templates.get(key).clone(true);
  },dispose(){for(const g of geometries)g.dispose();for(const m of materials.values())m.dispose();templates.clear();vehicleResources.clear();},stats:()=>({templates:templates.size,geometries:geometries.size})};
}
