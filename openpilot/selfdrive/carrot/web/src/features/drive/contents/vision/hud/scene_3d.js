import * as T from 'three';
import {createSceneModels} from './scene_3d_models.js';
import {surroundingTargets} from './scene_objects.js';
import {ROAD_CLASSES} from './object_classes.js';

const finite=n=>typeof n==='number'&&Number.isFinite(n);
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function sceneTargets(scene){
  return [...surroundingTargets(scene?.radar),...(scene?.vision?.objects||[]),...(scene?.road?.objects||[])]
    .filter(o=>o&&(o.kind==='unknown'||ROAD_CLASSES.includes(o.kind)||o.kind==='traffic cone')&&finite(o.x)&&finite(o.y)&&o.x>0&&o.x<=75&&Math.abs(o.y)<=20).slice(0,80);
}
// Explicit scene-camera geometry, independent of sensor calibration and control.
export function sceneCamera(width,height,camera={}){
  const yaw=finite(camera?.yaw)?camera.yaw*Math.PI/180:0,pitch=finite(camera?.pitch)?clamp(camera.pitch,18,60):25;
  const distance=finite(camera?.distance)?clamp(camera.distance,9,16):9,elevation=finite(camera?.height)?clamp(camera.height,6,12):6;
  const d=distance*.72,h=2.1+(elevation-6)*.18,aspect=width/Math.max(1,height);
  // Maintain a useful horizontal field on portrait phones instead of cropping
  // the car to the narrow viewport. Wide/4:3 camera geometry stays unchanged.
  const fov=Math.max(50,Math.min(100,2*Math.atan(Math.tan(Math.PI/8)/Math.max(.25,aspect))*180/Math.PI));
  const anchor=finite(camera?.anchorY)?clamp(camera.anchorY-.20,.56,.67):.59;
  const theta=Math.max(4*Math.PI/180,Math.atan2(h,d)-Math.atan((anchor*2-1)*Math.tan(fov*Math.PI/360)))+(pitch-25)*Math.PI/180;
  return {position:[-d*Math.cos(yaw),d*Math.sin(yaw),h],target:[(-d+20*Math.cos(theta))*Math.cos(yaw),(d-20*Math.cos(theta))*Math.sin(yaw),h-20*Math.sin(theta)],aspect,fov};
}
export function roadRibbon(path,left,right,{behind=false}={}){
  const points=[];
  for(let i=0;i<Math.min(path?.x?.length||0,path?.y?.length||0,256);i++){
    const x=path.x[i],y=path.y[i];points.push(finite(x)&&finite(y)&&x>=0&&x<=100&&Math.abs(y)<=30?[x,y]:null);
  }
  // Only continue the nearest observed segment under the camera, not beyond
  // the measured forward horizon. This removes the floating miniature stage.
  if(behind&&points[0]&&points[1]&&points[0][0]<=4&&points[1][0]>points[0][0]){
    const [a,b]=points,slope=clamp((b[1]-a[1])/(b[0]-a[0]),-.3,.3);points.unshift([-12,a[1]+(-12-a[0])*slope]);
  }
  const out=[];
  for(let i=1;i<points.length;i++){
    const a=points[i-1],b=points[i];if(!a||!b)continue;
    for(const [x,y] of [[a[0],a[1]+left],[a[0],a[1]+right],[b[0],b[1]+right],[a[0],a[1]+left],[b[0],b[1]+right],[b[0],b[1]+left]])out.push(x,y,.025);
  }return out;
}

export function createDrivingScene3D(doc,target,{onChange=()=>{},rendererFactory=options=>new T.WebGLRenderer(options)}={}){
  const canvas=doc.createElement('canvas');canvas.className='tesla-scene tesla-scene-3d';canvas.hidden=true;canvas.setAttribute('aria-label','即時 3D 駕駛視覺');
  let renderer=null,failed=false,lost=false,closed=false,scene,world,camera,models,ego,egoKey='',active=false,hud,hudCamera,ground;
  const hudNodes=new Map();
  const objectNodes=new Map(),ribbons=[];let renderWidth=0,renderHeight=0,lastStats={backend:'not-started',objects:0,classified:0,unknown:0};
  const dispose=()=>{for(const m of ribbons){m.geometry.dispose();m.material.dispose();}ribbons.length=0;models?.dispose();models=null;scene?.traverse(o=>{if(o.userData?.owned){o.geometry?.dispose();o.material?.dispose();}});renderer?.dispose();renderer=null;objectNodes.clear();hudNodes.clear();ego=null;renderWidth=renderHeight=0;};
  const contextLost=e=>{e.preventDefault();lost=true;canvas.hidden=true;lastStats={...lastStats,backend:'context-lost'};onChange();};
  const contextRestored=()=>{if(closed)return;lost=false;failed=false;dispose();onChange();};
  canvas.addEventListener('webglcontextlost',contextLost);canvas.addEventListener('webglcontextrestored',contextRestored);
  function start(){
    if(failed||lost||closed||!target.WebGL2RenderingContext)return false;if(renderer)return true;
    try{
      renderer=rendererFactory({canvas,antialias:true,alpha:false,powerPreference:'low-power'});renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;
      scene=new T.Scene();camera=new T.PerspectiveCamera(50,1,.1,180);camera.up.set(0,0,1);models=createSceneModels();
      // Sensor x-forward/y-right/z-up is left-handed. Reflect exactly once at
      // the render boundary; keep all observations and vehicle lamp sides intact.
      world=new T.Group();world.scale.y=-1;scene.add(world);
      scene.add(new T.HemisphereLight('#d6e9ff','#27313f',1.2));const light=new T.DirectionalLight('#ffffff',1.6);light.position.set(-8,-12,22);scene.add(light);
      hud=new T.Scene();hud.add(new T.HemisphereLight('#eff8ff','#556c88',2));hudCamera=new T.OrthographicCamera(0,1,1,0,1,1000);hudCamera.position.z=500;
      ground=new T.Mesh(new T.PlaneGeometry(600,600),new T.MeshBasicMaterial({color:'#e8edf5'}));ground.position.set(70,0,-.04);ground.userData.owned=true;scene.add(ground);
      // Fixed reusable geometry; no per-frame GPU allocations or shadow maps.
      for(let i=0;i<12;i++){
        const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.BufferAttribute(new Float32Array(256*18),3).setUsage(T.DynamicDrawUsage));geometry.setDrawRange(0,0);
        const mesh=new T.Mesh(geometry,new T.MeshBasicMaterial({color:'#ffffff',side:T.DoubleSide,depthWrite:false,transparent:true,opacity:.9}));mesh.frustumCulled=false;mesh.renderOrder=i;world.add(mesh);ribbons.push(mesh);
      }
      return true;
    }catch{failed=true;dispose();lastStats={...lastStats,backend:'canvas-fallback'};return false;}
  }
  function ribbon(index,path,left,right,color,behind){
    const mesh=ribbons[index],positions=roadRibbon(path,left,right,{behind});const attribute=mesh.geometry.getAttribute('position');
    attribute.array.set(positions);attribute.needsUpdate=true;mesh.geometry.setDrawRange(0,positions.length/3);mesh.material.color.set(color);mesh.visible=positions.length>0;
  }
  return {canvas,render(width,height,data,{night=false,rainbow=false,view=null,skin=null,lamps={},enabled=true,imageSlots=[]}={}){
    active=enabled&&!doc.hidden;canvas.hidden=!active;if(!active)return false;
    if(!start()){canvas.hidden=true;return false;}
    try{
      if(renderWidth!==width||renderHeight!==height){renderer.setSize(width,height,false);renderWidth=width;renderHeight=height;}
      const spec=sceneCamera(width,height,view);camera.fov=spec.fov;camera.aspect=spec.aspect;camera.position.set(...spec.position);camera.lookAt(...spec.target);camera.updateProjectionMatrix();
      const bg=night?'#0c1018':'#edf1f8';scene.background=new T.Color(bg);scene.fog=new T.Fog(bg,45,125);ground.material.color.set(night?'#191e27':'#e8edf5');
      for(const m of ribbons)m.visible=false;
      const model=data.model;
      if(model){
        (model.roadEdges||[]).slice(0,2).forEach((p,i)=>ribbon(i,p,-.07,.07,night?'#7b8a9e':'#637283',true));
        (model.laneLines||[]).slice(0,4).forEach((p,i)=>{if((model.laneLineProbs?.[i]??0)>.3)ribbon(i+2,p,-.045,.045,night?'#d4e0ef':'#ffffff',true);});
        if(rainbow)['#ff4c72','#ffad35','#f8e45d','#43dda1','#22baff','#8c74ff'].forEach((c,i)=>ribbon(i+6,model.position,-.83+i*1.66/6,-.83+(i+1)*1.66/6,c,false));
        else ribbon(6,model.position,-.83,.83,'#008dff',false);
      }
      const visible=new Set(),objects=sceneTargets(data);
      for(const [i,o] of objects.entries()){
        const key=`${o.source||'observation'}:${o.id??i}:${o.kind}`;visible.add(key);let node=objectNodes.get(key);
        if(!node){node=models.get(o.kind);world.add(node);objectNodes.set(key,node);}node.position.set(o.x,o.y,0);
      }
      for(const [key,node] of objectNodes)if(!visible.has(key)){world.remove(node);objectNodes.delete(key);}
      const nextKey=`${skin?.id}:${lamps.brake}:${lamps.left}:${lamps.right}`;
      if(nextKey!==egoKey||!ego){if(ego)world.remove(ego);ego=models.get('ego',{skin,lamps});world.add(ego);egoKey=nextKey;}
      renderer.autoClear=true;renderer.render(scene,camera);const drawCalls=renderer.info.render.calls,triangles=renderer.info.render.triangles;
      const imageKeys=new Set();hudCamera.right=width;hudCamera.top=height;hudCamera.updateProjectionMatrix();
      for(const slot of imageSlots.slice(0,5)){
        if(!['traffic light','stop sign','bird','crosswalk','traffic cone'].includes(slot.kind)||![slot.x,slot.y,slot.size].every(finite))continue;
        imageKeys.add(slot.kind);let node=hudNodes.get(slot.kind);if(!node){node=models.get(slot.kind);hudNodes.set(slot.kind,node);hud.add(node);}
        node.position.set(slot.x,height-slot.y,0);node.scale.setScalar(slot.size);node.rotation.set(-.9,0,-.4);
      }
      for(const [key,node] of hudNodes)if(!imageKeys.has(key)){hud.remove(node);hudNodes.delete(key);}
      if(hudNodes.size){renderer.autoClear=false;renderer.clearDepth();renderer.render(hud,hudCamera);}
      lastStats={backend:'webgl2',objects:objects.length,classified:objects.filter(o=>o.kind!=='unknown').length,unknown:objects.filter(o=>o.kind==='unknown').length,imageIcons:hudNodes.size,width,height,drawCalls,triangles};canvas.dataset.renderer='webgl2';return true;
    }catch{failed=true;dispose();canvas.hidden=true;lastStats={...lastStats,backend:'canvas-fallback'};return false;}
  },pause(){active=false;canvas.hidden=true;},snapshot:()=>({...lastStats}),destroy(){closed=true;canvas.removeEventListener('webglcontextlost',contextLost);canvas.removeEventListener('webglcontextrestored',contextRestored);dispose();canvas.remove();}};
}
