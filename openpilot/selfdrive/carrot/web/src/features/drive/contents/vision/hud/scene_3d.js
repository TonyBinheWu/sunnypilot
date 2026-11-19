import * as T from 'three';
import {createGpuSceneReceiver} from './gpu_scene_receiver.js';
import {createSceneModels} from './scene_3d_models.js';
import {surroundingTargets} from './scene_objects.js';
import {paintStripes} from './road_paint.js';
import {roadColors, pathChevrons, nearPathSurface, nearPathCar, dashedRibbon, isDashed} from './road_scene_style.js';
import {ROAD_CLASSES} from './object_classes.js';

const finite=n=>typeof n==='number'&&Number.isFinite(n);
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function sceneTargets(scene){
  return (scene?.tracks??[...surroundingTargets(scene?.radar),...(scene?.vision?.objects||[]),...(scene?.road?.objects||[])])
    .filter(o=>o&&(o.kind==='unknown'||ROAD_CLASSES.includes(o.kind)||o.kind==='traffic cone')&&finite(o.x)&&finite(o.y)&&o.x>0&&o.x<=75&&Math.abs(o.y)<=20).slice(0,80);
}
export {sceneCamera} from '../../../../cockpit/scene_camera.js';
import {sceneCamera} from '../../../../cockpit/scene_camera.js';
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
  if(target.__CARROT_BOOTSTRAP__?.visionGpuScene===true){
    const receiver=createGpuSceneReceiver(target,canvas);
    const pause=()=>{receiver.update(false);canvas.hidden=true;};
    return {canvas,pause,render(width,height,data,options={}){
      const active=options.enabled!==false&&!doc.hidden;
      canvas.hidden=!active;receiver.update(active);if(active)receiver.setView(width,height,options);return active;
    },snapshot(){const s=receiver.snapshot();return {...s,environmentCells:s.cells,raisedCells:s.raised};},
    destroy(){receiver.destroy();canvas.remove();}};
  }
  let renderer=null,failed=false,lost=false,closed=false,scene,world,camera,models,ego,egoKey='',active=false,hud,hudCamera,ground;
  const hudNodes=new Map(),parkingNodes=[];
  const objectNodes=new Map(),pool=new Map(),ribbons=[];
  let volume=null,lastPositions=null,rangeLines=null,lastRanges=null;
  function updateRanges(ranges){
    if(!ranges?.length){if(rangeLines)rangeLines.geometry.setDrawRange(0,0);lastRanges=null;return;}
    if(lastRanges===ranges)return;
    if(!rangeLines){
      const geometry=new T.BufferGeometry();
      geometry.setAttribute('position',new T.BufferAttribute(new Float32Array(16*9*6),3).setUsage(T.DynamicDrawUsage));
      rangeLines=new T.LineSegments(geometry,new T.LineBasicMaterial({color:'#aa90e1',transparent:true,opacity:.55,depthWrite:false}));
      rangeLines.userData.owned=true;rangeLines.frustumCulled=false;world.add(rangeLines);
    }
    const points=rangeLines.geometry.attributes.position;
    points.array.set(ranges);points.needsUpdate=true;rangeLines.geometry.setDrawRange(0,ranges.length/3);
    lastRanges=ranges;
  }
  const voxelTransform=new T.Matrix4();
  function updateVolume(positions) {
    if(!positions?.length){if(volume)volume.count=0;lastPositions=null;return;}
    if(lastPositions===positions)return;
    if(!volume){
      volume=new T.InstancedMesh(new T.BoxGeometry(.94,.94,.94),
        new T.MeshLambertMaterial({color:'#429fa6',transparent:true,opacity:.42,depthWrite:false}),64*36);
      volume.instanceMatrix.setUsage(T.DynamicDrawUsage);volume.frustumCulled=false;
      volume.userData.owned=true;world.add(volume);
    }
    volume.count=Math.min(64*36,Math.floor(positions.length/3));
    for(let i=0;i<volume.count;i++){
      const z=positions[3*i+2];
      // Show ground-height cells as tiles, so a flat surface never becomes a row of bollards.
      voxelTransform.makeScale(1,1,z===0?.05:1).setPosition(positions[3*i],positions[3*i+1],z);
      volume.setMatrixAt(i,voxelTransform);
    }
    volume.instanceMatrix.needsUpdate=true;lastPositions=positions;
  }
  let shadow, highlightedCar;
  const shadowMatrix=new T.Matrix4();
  function placeShadow(i,x,y,heading,length,width){
    shadowMatrix.makeRotationZ(heading);shadowMatrix.scale(shadowScale.set(length,width,1));shadowMatrix.setPosition(x,y,.035);
    shadow.setMatrixAt(i,shadowMatrix);
  }
  const shadowScale=new T.Vector3();
  let pooled=0,allocated=0,reused=0,discarded=0,predictedMesh,predictedLine,roadCache=null;
  function acquire(kind) {
    const bin=pool.get(kind);let node;
    if(bin?.length){node=bin.pop();pooled--;reused++;}
    else {node=models.get(kind);node.userData.poolKind=kind;allocated++;}
    world.add(node);return node;
  }
  function release(key,node) {
    world.remove(node);objectNodes.delete(key);
    if(pooled>=40){discarded++;return;}
    const kind=node.userData.poolKind;
    if(!pool.has(kind))pool.set(kind,[]);
    pool.get(kind).push(node);pooled++;
  }
  function appearance(node,predicted) {
    if(Boolean(node.userData.predicted)===predicted)return;
    node.userData.predicted=predicted;
    node.traverse(part=>{
      if(!part.material)return;
      if(predicted){part.userData.confirmedMaterial=part.material;part.material=part.isLine?predictedLine:predictedMesh;}
      else {part.material=part.userData.confirmedMaterial;delete part.userData.confirmedMaterial;}
    });
  }
  let renderWidth=0,renderHeight=0,lastStats={backend:'not-started',objects:0,classified:0,unknown:0};
  const dispose=()=>{for(const m of ribbons){m.geometry.dispose();m.material.dispose();}ribbons.length=0;models?.dispose();models=null;scene?.traverse(o=>{if(o.userData?.owned){o.geometry?.dispose();o.material?.dispose();}});renderer?.dispose();renderer=null;discarded+=objectNodes.size+pooled;objectNodes.clear();pool.clear();pooled=0;predictedMesh?.dispose();predictedLine?.dispose();highlightedCar?.dispose();highlightedCar=null;shadow=null;roadCache=null;hudNodes.clear();parkingNodes.length=0;ego=null;renderWidth=renderHeight=0;};
  const contextLost=e=>{e.preventDefault();lost=true;canvas.hidden=true;lastStats={...lastStats,backend:'context-lost'};onChange();};
  const contextRestored=()=>{if(closed)return;lost=false;failed=false;volume?.dispose();volume=null;lastPositions=null;rangeLines=null;lastRanges=null;dispose();onChange();};
  canvas.addEventListener('webglcontextlost',contextLost);canvas.addEventListener('webglcontextrestored',contextRestored);
  function start(){
    if(failed||lost||closed||!target.WebGL2RenderingContext)return false;if(renderer)return true;
    try{
      renderer=rendererFactory({canvas,antialias:true,alpha:false,powerPreference:'low-power'});renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;
      scene=new T.Scene();scene.background=new T.Color();scene.fog=new T.Fog(0,30,110);
      predictedMesh=new T.MeshPhongMaterial({color:'#94b0c3',opacity:.47,transparent:true,depthWrite:false});
      predictedLine=new T.LineBasicMaterial({color:'#94b0c3',opacity:.47,transparent:true,depthWrite:false});
      camera=new T.PerspectiveCamera(50,1,.1,180);camera.up.set(0,0,1);models=createSceneModels();
      // Sensor x-forward/y-right/z-up is left-handed. Reflect exactly once at
      // the render boundary; keep all observations and vehicle lamp sides intact.
      world=new T.Group();world.scale.y=-1;scene.add(world);
      scene.add(new T.HemisphereLight('#ffffff','#c9c4c1',2.2));const light=new T.DirectionalLight('#ffffff',1.9);light.position.set(-8,-12,22);scene.add(light);
      hud=new T.Scene();hud.add(new T.HemisphereLight('#eff8ff','#556c88',2));hudCamera=new T.OrthographicCamera(0,1,1,0,1,1000);hudCamera.position.z=500;
      ground=new T.Mesh(new T.PlaneGeometry(600,600),new T.MeshBasicMaterial({color:'#e8edf5'}));ground.position.set(70,0,-.04);ground.userData.owned=true;scene.add(ground);
      // Fixed reusable geometry; no per-frame GPU allocations or shadow maps.
      shadow=new T.InstancedMesh(new T.PlaneGeometry(1,1),new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,
        vertexShader:'varying vec2 p; void main(){p=uv*2.-1.;gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.);}',
        fragmentShader:'varying vec2 p;void main(){float a=1.-smoothstep(.25,1.,dot(p*p,p*p));gl_FragColor=vec4(.09,.1,.12,.19*a);}' }),81);
      shadow.userData.owned=true;shadow.frustumCulled=false;shadow.renderOrder=20;world.add(shadow);
      for(let i=0;i<20;i++){
        const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.BufferAttribute(new Float32Array((256+18)*18),3).setUsage(T.DynamicDrawUsage));geometry.setDrawRange(0,0);
        const mesh=new T.Mesh(geometry,new T.MeshBasicMaterial({color:'#ffffff',side:T.DoubleSide,depthWrite:false,transparent:true,opacity:.9}));mesh.frustumCulled=false;mesh.renderOrder=i===16||i===17?-2:(i===19?17.5:i);world.add(mesh);ribbons.push(mesh);
      }
      for(let i=0;i<12;i++){
        const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(new Float32Array(15),3));
        const node=new T.Line(g,new T.LineBasicMaterial({color:'#d69c30'}));node.userData.owned=true;node.frustumCulled=false;world.add(node);parkingNodes.push(node);
      }
      return true;
    }catch{failed=true;dispose();lastStats={...lastStats,backend:'canvas-fallback'};return false;}
  }
  function geometryAt(index,positions,color){
    const mesh=ribbons[index];const attribute=mesh.geometry.getAttribute('position');
    attribute.array.set(positions);attribute.needsUpdate=true;mesh.geometry.setDrawRange(0,positions.length/3);mesh.material.color.set(color);mesh.visible=positions.length>0;
  }
  function ribbon(index,path,left,right,color,behind){geometryAt(index,roadRibbon(path,left,right,{behind}),color);}
  return {canvas,render(width,height,data,{night=false,rainbow=false,view=null,skin=null,lamps={},enabled=true,imageSlots=[]}={}){
    active=enabled&&!doc.hidden;canvas.hidden=!active;if(!active)return false;
    if(!start()){canvas.hidden=true;return false;}
    try{
      if(renderWidth!==width||renderHeight!==height){renderer.setSize(width,height,false);renderWidth=width;renderHeight=height;}
      const spec=sceneCamera(width,height,{...view,roadOverview:true,skinScale:skin?.scale});camera.fov=spec.fov;camera.aspect=spec.aspect;camera.position.set(...spec.position);camera.lookAt(...spec.target);camera.updateProjectionMatrix();renderer.setViewport?.(0,spec.bottomInset,width,spec.viewportHeight);
      const palette=roadColors(night);scene.background.set(palette.sky);scene.fog.color.set(palette.sky);ground.material.color.set(palette.road);
      updateVolume(data.environment);
      updateRanges(data.environment&&data.environmentRanges);
      if(rangeLines){
        rangeLines.position.set(data.environmentMotion?.x||0,data.environmentMotion?.y||0,0);
        rangeLines.rotation.z=data.environmentMotion?.angle||0;
      }
      if(volume){
        volume.position.set(data.environmentMotion?.x||0,data.environmentMotion?.y||0,0);
        volume.rotation.z=data.environmentMotion?.angle||0;
      }
      const model=data.model, paintKey=JSON.stringify(data.paint??null);
      if(!roadCache||roadCache.model!==model||roadCache.paintKey!==paintKey||roadCache.night!==night||roadCache.rainbow!==rainbow){
        roadCache={model,paintKey,night,rainbow};
        for(const m of ribbons)m.visible=false;
        if(model){
        (model.roadEdges||[]).slice(0,2).forEach((p,i)=>{
          ribbon(16+i,p,i===0?-22:.08,i===0?-.08:22,palette.verge,true);
          ribbon(i,p,-.07,.07,palette.edge,true);
        });
        (model.laneLines||[]).slice(0,4).forEach((p,i)=>{
          if((model.laneLineProbs?.[i]??0)<=.3)return;
          const paint=paintStripes(data.paint?.[i],i,palette.lane);
          paint.offsets.forEach((offset,j)=>{
            const index=j?12+i:i+2;
            if(isDashed(data.paint?.[i]))geometryAt(index,dashedRibbon(p,offset-.065,offset+.065),paint.color);
            else ribbon(index,p,offset-.055,offset+.055,paint.color,true);
          });
        });
        if(rainbow)['#ff4c72','#ffad35','#f8e45d','#43dda1','#22baff','#8c74ff'].forEach((c,i)=>ribbon(i+6,model.position,-.83+i*1.66/6,-.83+(i+1)*1.66/6,c,false));
        else {ribbon(6,model.position,-.83,.83,palette.path,false);geometryAt(19,nearPathSurface(model.position),palette.near);geometryAt(18,pathChevrons(model.position),palette.chevron);}
      }
      }
      for(const [i,node] of parkingNodes.entries()){
        const slot=data.parking?.[i],corners=slot?.corners;node.visible=Array.isArray(corners)&&corners.length===4&&corners.every(p=>p.length===2&&p.every(finite));
        if(node.visible){const points=[...corners,corners[0]].flatMap(([x,y])=>[x,y,.065]);node.geometry.attributes.position.array.set(points);node.geometry.attributes.position.needsUpdate=true;}
      }
      const visible=new Set(),objects=sceneTargets(data);
      let shadowCount=0;placeShadow(shadowCount++,0,0,0,5.2*(skin?.scale?.[0]||1),2.4*(skin?.scale?.[1]||1));
      for(const [i,o] of objects.entries()){
        const key=o.trackingId!==undefined?o.id:`${o.source||'observation'}:${o.id??i}:${o.kind}`;visible.add(key);let node=objectNodes.get(key);
        if(node&&node.userData.poolKind!==o.kind){release(key,node);node=null;}
        if(!node){node=acquire(o.kind);objectNodes.set(key,node);}
        node.position.set(o.x,o.y,0);node.rotation.z=o.heading??0;appearance(node,o.state==='predicted');
        if(o.kind==='car'&&o.state!=='predicted'){
          const mesh=node.children[0];mesh.userData.neutralPaint??=mesh.material;
          if(!highlightedCar){highlightedCar=mesh.material.clone();highlightedCar.color.setRGB(.28,1.03,2.1);}
          mesh.material=nearPathCar(o,model?.position)?highlightedCar:mesh.userData.neutralPaint;
        }
        if(o.state!=='predicted'&&['car','truck','bus','motorcycle','bicycle','person'].includes(o.kind)){
          const long=o.kind==='truck'||o.kind==='bus',narrow=['bicycle','motorcycle','person'].includes(o.kind);
          placeShadow(shadowCount++,o.x,o.y,node.rotation.z,long?8:narrow?1.6:4.9,long?2.9:narrow?.85:2.2);
        }
      }
      shadow.count=shadowCount;shadow.instanceMatrix.needsUpdate=true;
      for(const [key,node] of objectNodes)if(!visible.has(key))release(key,node);
      const nextKey=`${skin?.id}:${skin?.paint}:${lamps.brake}:${lamps.left}:${lamps.right}:${lamps.lowBeam}:${lamps.highBeam}`;
      if(nextKey!==egoKey||!ego){if(ego)world.remove(ego);ego=models.get('ego',{skin,lamps});world.add(ego);egoKey=nextKey;}
      renderer.autoClear=true;renderer.render(scene,camera);const drawCalls=renderer.info.render.calls,triangles=renderer.info.render.triangles;
      const imageKeys=new Set();hudCamera.right=width;hudCamera.top=height;hudCamera.updateProjectionMatrix();
      for(const slot of imageSlots.slice(0,5)){
        if(!['traffic light','stop sign','bird','crosswalk','traffic cone'].includes(slot.kind)||![slot.x,slot.y,slot.size].every(finite))continue;
        imageKeys.add(slot.kind);let node=hudNodes.get(slot.kind);if(!node){node=models.get(slot.kind);hudNodes.set(slot.kind,node);hud.add(node);}
        node.position.set(slot.x,height-slot.y,0);node.scale.setScalar(slot.size);node.rotation.set(-.9,0,-.4);
      }
      for(const [key,node] of hudNodes)if(!imageKeys.has(key)){hud.remove(node);hudNodes.delete(key);}
      if(hudNodes.size){renderer.setViewport?.(0,0,width,height);renderer.autoClear=false;renderer.clearDepth();renderer.render(hud,hudCamera);}
      lastStats={backend:'webgl2',objects:objects.length,classified:objects.filter(o=>o.kind!=='unknown').length,unknown:objects.filter(o=>o.kind==='unknown').length,imageIcons:hudNodes.size,width,height,drawCalls,triangles,allocated,reused,discarded,pooled,geometries:renderer.info.memory?.geometries??null,textures:renderer.info.memory?.textures??null};canvas.dataset.renderer='webgl2';return true;
    }catch{failed=true;dispose();canvas.hidden=true;lastStats={...lastStats,backend:'canvas-fallback'};return false;}
  },pause(){active=false;canvas.hidden=true;},snapshot:()=>({...lastStats,environmentRanges:active&&!lost&&renderer&&lastRanges?lastRanges.length/6:0,environmentCells:active&&!lost&&renderer?volume?.count||0:0}),destroy(){closed=true;canvas.removeEventListener('webglcontextlost',contextLost);canvas.removeEventListener('webglcontextrestored',contextRestored);volume?.dispose();dispose();canvas.remove();}};
}
