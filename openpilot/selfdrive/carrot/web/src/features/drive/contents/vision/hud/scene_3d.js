import * as T from 'three';
import {parkingObservation, parkingDistanceText, parkingWheelTicks} from './parking_environment.js';
import {createEgoVehicle3D} from '../../../../cockpit/ego_vehicle_3d.js';
import {createRoadLibrary} from './road_model_library.js';
import {metricSize,roadModelKind,roadModelLod} from './road_model_selection.js';
import {createGpuSceneReceiver} from './gpu_scene_receiver.js';
import {createSceneModels} from './scene_3d_models.js';
import {surroundingTargets} from './scene_objects.js';
import {paintStripes,stripePattern} from './road_paint.js';
import {roadColors, pathChevrons, nearPathSurface, nearPathCar, parkingOutline, dashedRibbon} from './road_scene_style.js';
import {ROAD_CLASSES} from './object_classes.js';

const finite=n=>typeof n==='number'&&Number.isFinite(n);
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function sceneTargets(scene){
  return (scene?.tracks??[...surroundingTargets(scene?.radar),...(scene?.vision?.objects||[]),...(scene?.road?.objects||[])])
    .filter(o=>o&&(!o.state||o.state==='confirmed'||o.state==='predicted')&&(o.kind==='unknown'||ROAD_CLASSES.includes(o.kind)||roadModelKind(o)!==null)&&finite(o.x)&&finite(o.y)&&o.x>0&&o.x<=75&&Math.abs(o.y)<=20).slice(0,80);
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

export function createDrivingScene3D(doc,target,{onChange=()=>{},scenery=null,rendererFactory=options=>new T.WebGLRenderer(options)}={}){
  const canvas=doc.createElement('canvas');canvas.className='tesla-scene tesla-scene-3d';canvas.hidden=true;canvas.setAttribute('aria-label','即時 3D 駕駛視覺');
  if(target.__CARROT_BOOTSTRAP__?.visionGpuScene===true){
    const receiver=createGpuSceneReceiver(target,canvas);
    const pause=()=>{receiver.update(false);canvas.hidden=true;};
    return {canvas,pause,render(width,height,data,options={}){
      const active=options.enabled!==false&&!doc.hidden;
      canvas.hidden=!active;if(active)receiver.setView(width,height,options);receiver.update(active);return active;
    },snapshot(){const s=receiver.snapshot();return {...s,environmentCells:s.cells,raisedCells:s.raised};},
    destroy(){receiver.destroy();canvas.remove();}};
  }
  let renderer=null,failed=false,lost=false,closed=false,scene,world,camera,models,ego,egoKey='',active=false,hud,hudCamera,ground;
  let egoPivot,wheelTicks, proximityMarker=null, distanceSprite=null, distanceLabel='';
  const egoModel=createEgoVehicle3D(target,doc,onChange);
  let library=createRoadLibrary(target,doc,onChange);
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
  let parkingPalette=false;
  const voxelTransform=new T.Matrix4(), voxelColor=new T.Color();
  function updateVolume(positions,parking) {
    if(!positions?.length){if(volume)volume.count=0;lastPositions=null;return;}
    if(lastPositions===positions&&parkingPalette===parking)return;
    parkingPalette=parking;
    if(!volume){
      volume=new T.InstancedMesh(new T.BoxGeometry(.94,.94,.94),
        new T.MeshLambertMaterial({color:'#ffffff',transparent:true,opacity:.42,depthWrite:false}),64*36);
      volume.instanceMatrix.setUsage(T.DynamicDrawUsage);volume.frustumCulled=false;
      volume.userData.owned=true;world.add(volume);
    }
    volume.material.opacity=parking ? .78 : .42;
    volume.count=Math.min(64*36,Math.floor(positions.length/3));
    for(let i=0;i<volume.count;i++){
      const z=positions[3*i+2];
      // Show ground-height cells as tiles, so a flat surface never becomes a row of bollards.
      voxelTransform.makeScale(1,1,z===0?.05:1).setPosition(positions[3*i],positions[3*i+1],z);
      volume.setMatrixAt(i,voxelTransform);
      volume.setColorAt(i,voxelColor.set(parking && z>0 ? '#748998' : '#429fa6'));
    }
    if(volume.instanceColor)volume.instanceColor.needsUpdate=true;
    volume.instanceMatrix.needsUpdate=true;lastPositions=positions;
  }
  let shadow, highlightedCar, mapContext, lastMapLines, followRing;
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
    else {node=models.get(kind==='barrier'||kind==='drum'?'unknown':kind);node.userData.poolKind=kind;allocated++;}
    node.scale.set(1,1,1);delete node.userData.roadLod;delete node.userData.sizeAt;
    world.add(node);return node;
  }
  function recycle(node) {
    if(pooled>=40){discarded++;return;}
    const kind=node.userData.poolKind;
    if(!pool.has(kind))pool.set(kind,[]);
    pool.get(kind).push(node);pooled++;
  }
  function release(key,node){world.remove(node);objectNodes.delete(key);recycle(node);}
  function changeKind(node,kind){
    const replacement=acquire(kind),oldParts=node.children.slice(),oldData=node.userData;
    world.remove(replacement);node.clear();node.add(...replacement.children.slice());replacement.add(...oldParts);
    node.userData=replacement.userData;replacement.userData=oldData;node.scale.set(1,1,1);recycle(replacement);
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
  const dispose=()=>{distanceSprite?.material.map.dispose();distanceSprite?.material.dispose();distanceSprite=null;distanceLabel='';proximityMarker=null;for(const m of ribbons){m.geometry.dispose();m.material.dispose();}ribbons.length=0;models?.dispose();models=null;scene?.traverse(o=>{if(o.userData?.owned){o.geometry?.dispose();o.material?.dispose();}});renderer?.dispose();renderer=null;discarded+=objectNodes.size+pooled;objectNodes.clear();pool.clear();pooled=0;predictedMesh?.dispose();predictedLine?.dispose();highlightedCar?.dispose();highlightedCar=null;shadow=null;roadCache=null;hudNodes.clear();parkingNodes.length=0;ego=null;renderWidth=renderHeight=0;};
  const contextLost=e=>{e.preventDefault();lost=true;canvas.hidden=true;lastStats={...lastStats,backend:'context-lost'};onChange();};
  const contextRestored=()=>{if(closed)return;lost=false;failed=false;volume?.dispose();volume=null;lastPositions=null;rangeLines=null;lastRanges=null;dispose();library.dispose();library=createRoadLibrary(target,doc,onChange);onChange();};
  canvas.addEventListener('webglcontextlost',contextLost);canvas.addEventListener('webglcontextrestored',contextRestored);
  function start(){
    if(failed||lost||closed||!target.WebGL2RenderingContext)return false;if(renderer)return true;
    try{
      renderer=rendererFactory({canvas,antialias:true,alpha:false,powerPreference:'low-power'});renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;
      scene=new T.Scene();scene.background=new T.Color();scene.fog=new T.Fog(0,33,108);
      predictedMesh=new T.MeshPhongMaterial({color:'#94b0c3',opacity:.47,transparent:true,depthWrite:false});
      predictedLine=new T.LineBasicMaterial({color:'#94b0c3',opacity:.47,transparent:true,depthWrite:false});
      camera=new T.PerspectiveCamera(50,1,.1,180);camera.up.set(0,0,1);models=createSceneModels();
      // Sensor x-forward/y-right/z-up is left-handed. Reflect exactly once at
      // the render boundary; keep all observations and vehicle lamp sides intact.
      world=new T.Group();world.scale.y=-1;scene.add(world);egoPivot=new T.Group();world.add(egoPivot);
      const mapGeometry=new T.BufferGeometry();
      mapGeometry.setAttribute('position',new T.BufferAttribute(new Float32Array(24*12*6),3).setUsage(T.DynamicDrawUsage));
      mapGeometry.setDrawRange(0,0);
      mapContext=new T.LineSegments(mapGeometry,new T.LineBasicMaterial({color:'#7692a6',transparent:true,opacity:.55,depthWrite:false}));
      mapContext.frustumCulled=false;mapContext.userData.owned=true;world.add(mapContext);lastMapLines=null;
      const tickGeometry=new T.BufferGeometry();
      tickGeometry.setAttribute('position',new T.BufferAttribute(new Float32Array(12),3).setUsage(T.DynamicDrawUsage));
      wheelTicks=new T.LineSegments(tickGeometry,new T.LineBasicMaterial({color:'#3289c5'}));
      wheelTicks.userData.owned=true;wheelTicks.frustumCulled=false;egoPivot.add(wheelTicks);if(scenery)world.add(scenery);
      scene.add(new T.HemisphereLight('#fffcf7','#a5a5a6',1.68));const light=new T.DirectionalLight('#fffaf4',1.68);light.position.set(-8,-12,22);scene.add(light);
      hud=new T.Scene();hud.add(new T.HemisphereLight('#eff8ff','#556c88',2));hudCamera=new T.OrthographicCamera(0,1,1,0,1,1000);hudCamera.position.z=500;
      ground=new T.Mesh(new T.PlaneGeometry(600,600),new T.MeshBasicMaterial({color:'#e8edf5'}));ground.position.set(70,0,-.04);ground.userData.owned=true;scene.add(ground);
      // Fixed reusable geometry; no per-frame GPU allocations or shadow maps.
      shadow=new T.InstancedMesh(new T.PlaneGeometry(1,1),new T.ShaderMaterial({transparent:true,depthWrite:false,side:T.DoubleSide,
        vertexShader:'varying vec2 p; void main(){p=uv*2.-1.;gl_Position=projectionMatrix*modelViewMatrix*instanceMatrix*vec4(position,1.);}',
        fragmentShader:'varying vec2 p;void main(){float a=1.-smoothstep(.25,1.,dot(p*p,p*p));gl_FragColor=vec4(.024,.025,.029,.56*a);}' }),81);
      shadow.userData.owned=true;shadow.frustumCulled=false;shadow.renderOrder=20;world.add(shadow);
      for(let i=0;i<20;i++){
        const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.BufferAttribute(new Float32Array((256+18)*18),3).setUsage(T.DynamicDrawUsage));geometry.setDrawRange(0,0);
        const mesh=new T.Mesh(geometry,new T.MeshBasicMaterial({color:'#ffffff',side:T.DoubleSide,depthWrite:false,transparent:true,opacity:.9}));mesh.frustumCulled=false;mesh.renderOrder=i===16||i===17?-2:(i===19?17.5:i);world.add(mesh);ribbons.push(mesh);
      }
      for(let i=0;i<12;i++){
        const g=new T.BufferGeometry();g.setAttribute('position',new T.BufferAttribute(new Float32Array(72),3).setUsage(T.DynamicDrawUsage));
        const node=new T.Mesh(g,new T.MeshBasicMaterial({color:'#e9bf72',side:T.DoubleSide}));node.userData.owned=true;node.frustumCulled=false;world.add(node);parkingNodes.push(node);
      }
      followRing=new T.Mesh(new T.RingGeometry(1.33,1.46,40),new T.MeshBasicMaterial({color:'#23c677',side:T.DoubleSide}));
      followRing.userData.owned=true;followRing.visible=false;world.add(followRing);
      return true;
    }catch{failed=true;dispose();lastStats={...lastStats,backend:'canvas-fallback'};return false;}
  }
  function markProximity(cue) {
    if(!cue){if(proximityMarker)proximityMarker.visible=distanceSprite.visible=false;return;}
    if(!proximityMarker){
      proximityMarker=new T.Mesh(new T.RingGeometry(.58,.75,40),new T.MeshBasicMaterial({side:T.DoubleSide,depthTest:true,depthWrite:false}));
      proximityMarker.userData.owned=true;proximityMarker.renderOrder=25;world.add(proximityMarker);
      const label=doc.createElement('canvas');label.width=192;label.height=64;
      const texture=new T.CanvasTexture(label);texture.colorSpace=T.SRGBColorSpace;
      distanceSprite=new T.Sprite(new T.SpriteMaterial({map:texture,depthTest:false,depthWrite:false}));
      distanceSprite.renderOrder=26;distanceSprite.scale.set(2.55,.85,1);distanceSprite.center.set(0,0);scene.add(distanceSprite);
    }
    proximityMarker.visible=distanceSprite.visible=true;proximityMarker.position.set(cue.x,cue.y,.08);
    distanceSprite.position.set(cue.x,-cue.y,1.65);
    proximityMarker.material.color.set(cue.color);
    const labelText=parkingDistanceText(cue);
    if(labelText!==distanceLabel){
      const texture=distanceSprite.material.map,label=texture.image,ctx=label.getContext('2d');
      ctx.fillStyle='#17232b';ctx.fillRect(0,0,label.width,label.height);
      ctx.font='bold 40px system-ui';ctx.textAlign='center';ctx.fillStyle='#ffffff';ctx.fillText(labelText,96,46);
      texture.needsUpdate=true;distanceLabel=labelText;
    }
  }
  function geometryAt(index,positions,color){
    const mesh=ribbons[index];const attribute=mesh.geometry.getAttribute('position');
    attribute.array.set(positions);attribute.needsUpdate=true;mesh.geometry.setDrawRange(0,positions.length/3);mesh.material.color.set(color);mesh.visible=positions.length>0;
  }
  function ribbon(index,path,left,right,color,behind){geometryAt(index,roadRibbon(path,left,right,{behind}),color);}
  return {canvas,render(width,height,data,{night=false,rainbow=false,view=null,skin=null,lamps={},egoMotion={},enabled=true,imageSlots=[],quality='auto'}={}){
    active=enabled&&!doc.hidden;canvas.hidden=!active;if(!active)return false;
    if(!start()){canvas.hidden=true;return false;}
    try{
      if(renderWidth!==width||renderHeight!==height){renderer.setSize(width,height,false);renderWidth=width;renderHeight=height;}
      const spec=sceneCamera(width,height,{...view,roadOverview:true,skinScale:skin?.scale});camera.fov=spec.fov;camera.aspect=spec.aspect;camera.position.set(...spec.position);camera.lookAt(...spec.target);if(spec.bottomInset>0)camera.setViewOffset(width,spec.viewportHeight,0,0,width,height);
      else camera.clearViewOffset();
      camera.updateProjectionMatrix();renderer.setViewport?.(0,0,width,height);
      const palette=roadColors(night);scene.background.set(palette.sky);scene.fog.color.set(palette.sky);ground.material.color.set(palette.road);
      const cue=view?.parking ? (data.parkingCue===undefined ? parkingObservation(data) : data.parkingCue) : null;
      const lines=data.model&&!view?.parking?data.mapLines:null;
      if(lines!==lastMapLines){
        lastMapLines=lines;
        const position=mapContext.geometry.getAttribute('position');
        let count=0;
        for(const [a,b] of (lines||[]).slice(0,24*12)){
          position.setXYZ(count++,a[0],a[1],.009);
          position.setXYZ(count++,b[0],b[1],.009);
        }
        mapContext.geometry.setDrawRange(0,count);position.needsUpdate=true;
      }
      markProximity(cue);
      updateVolume(data.environment,view?.parking===true);
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
      if(!roadCache||roadCache.model!==model||roadCache.paintKey!==paintKey||roadCache.night!==night||roadCache.rainbow!==rainbow||roadCache.parking!==Boolean(view?.parking)){
        roadCache={model,paintKey,night,rainbow,parking:Boolean(view?.parking)};
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
            const style=stripePattern(data.paint?.[i],j);
            if(style==='dashed'||style==='dots')geometryAt(index,dashedRibbon(p,offset-.065,offset+.065,style==='dots'),paint.color);
            else ribbon(index,p,offset-.055,offset+.055,style==='boundary'?palette.edge:paint.color,false);
          });
        });
        const path=view?.parking?null:model.position;
        if(rainbow)['#ff4c72','#ffad35','#f8e45d','#43dda1','#22baff','#8c74ff'].forEach((c,i)=>ribbon(i+6,path,-.83+i*1.66/6,-.83+(i+1)*1.66/6,c,false));
        else {ribbon(6,path,-.83,.83,palette.path,false);geometryAt(19,nearPathSurface(path),palette.near);geometryAt(18,pathChevrons(path),palette.chevron);}
      }
      }
      for(const [i,node] of parkingNodes.entries()){
        const positions=node.geometry.attributes.position;
        node.visible=Boolean(parkingOutline(data.parking?.[i]?.corners,positions.array));
        if(node.visible)positions.needsUpdate=true;
      }
      const visible=new Set(),objects=sceneTargets(data);
      const follow=objects.find(o=>o.following===true && o.state==='confirmed');
      followRing.visible=!!follow;
      if(follow)followRing.position.set(follow.x,follow.y,.06);
      const lodCounts=[0,0,0],frameTime=target.performance?.now?.()??Date.now();
      let shadowCount=0;placeShadow(shadowCount++,0,0,0,5.2*(skin?.scale?.[0]||1),2.4*(skin?.scale?.[1]||1));
      for(const [i,o] of objects.entries()){
        const key=o.trackingId!==undefined?o.id:`${o.source||'observation'}:${o.id??i}:${o.kind}`;visible.add(key);let node=objectNodes.get(key);
        const modelKind=roadModelKind(o);
        const fallback=['sedan','suv','mpv','pickup'].includes(modelKind)?'car':modelKind==='cone'?'traffic cone':(modelKind||o.kind);
        if(node&&node.userData.poolKind!==fallback)changeKind(node,fallback);
        if(!node){node=acquire(fallback);objectNodes.set(key,node);}
        node.position.set(o.x,o.y,0);node.rotation.z=o.heading??0;appearance(node,o.state==='predicted');
        if(modelKind)library.ensure();
        const level=roadModelLod(Math.hypot(o.x,o.y),quality==='low',node.userData.roadLod);
        const asset=modelKind&&library.get(modelKind,level);
        if(asset){
          let mesh=node.children[0];
          if(!mesh.isMesh){node.remove(mesh);mesh=new T.Mesh(asset.geometry,asset.material);node.add(mesh);}
          mesh.geometry=asset.geometry;
          const material=nearPathCar(o,model?.position)?library.focus:asset.material;
          if(o.state==='predicted'){mesh.userData.confirmedMaterial=material;mesh.material=predictedMesh;}else mesh.material=material;
          node.userData.roadLod=level;lodCounts[level]++;
          const size=['sedan','suv','mpv','pickup','bus','truck'].includes(modelKind)?metricSize(o):null;
          const gain=node.userData.sizeAt===undefined?1:1-Math.exp(-Math.max(0,frameTime-node.userData.sizeAt)/150);
          node.userData.sizeAt=frameTime;
          for(const [axis,dim] of [['x','length'],['y','width'],['z','height']]){
            const scale=size?size[dim]/asset.size[axis]:1;
            node.scale[axis]+=gain*(scale-node.scale[axis]);
          }
        }else if(fallback==='car'&&o.state!=='predicted'){
          const mesh=node.children[0];mesh.userData.neutralPaint??=mesh.material;
          if(!highlightedCar){highlightedCar=mesh.material.clone();highlightedCar.color.setRGB(1.12,1.12,1.12);}
          mesh.material=nearPathCar(o,model?.position)?highlightedCar:mesh.userData.neutralPaint;
        }
        if(o.state!=='predicted'&&['car','truck','bus','motorcycle','bicycle','person'].includes(o.kind)){
          const long=o.kind==='truck'||o.kind==='bus',narrow=['bicycle','motorcycle','person'].includes(o.kind);
          placeShadow(shadowCount++,o.x,o.y,node.rotation.z,long?8:narrow?1.6:4.9,long?2.9:narrow?.85:2.2);
        }
      }
      shadow.count=shadowCount;shadow.instanceMatrix.needsUpdate=true;
      for(const [key,node] of objectNodes)if(!visible.has(key))release(key,node);
      const cuv=egoModel.update({skin,lamps,quality,range:spec.range,at:frameTime,...egoMotion});
      if(cuv){
        if(ego!==cuv){if(ego)egoPivot.remove(ego);egoPivot.add(cuv);ego=cuv;egoKey='';}
      }else{
        const nextKey=[skin?.id,skin?.paint,lamps.brake,lamps.left,lamps.right,lamps.lowBeam,lamps.highBeam].join('/');
        if(!ego||nextKey!==egoKey){if(ego)egoPivot.remove(ego);ego=models.get('ego',{skin,lamps});egoPivot.add(ego);egoKey=nextKey;}
      }
      const ticks=view?.parking?parkingWheelTicks(egoMotion.steer,skin?.scale):[];
      wheelTicks.visible=!!ticks.length;
      if(wheelTicks.visible){
        const attr=wheelTicks.geometry.attributes.position;
        ticks.forEach(([x,y,endX,endY],i)=>{attr.setXYZ(i*2,x,y,.12);attr.setXYZ(i*2+1,endX,endY,.12);});
        attr.needsUpdate=true;
      }
      egoPivot.rotation.set(-(egoMotion.attitude?.roll||0),-(egoMotion.attitude?.pitch||0),0,'YXZ');
      renderer.autoClear=true;renderer.render(scene,camera);const drawCalls=renderer.info.render.calls,triangles=renderer.info.render.triangles;
      const imageKeys=new Set();hudCamera.right=width;hudCamera.top=height;hudCamera.updateProjectionMatrix();
      for(const slot of imageSlots.slice(0,5)){
        if(!['traffic light','stop sign','bird','crosswalk','traffic cone'].includes(slot.kind)||![slot.x,slot.y,slot.size].every(finite))continue;
        imageKeys.add(slot.kind);let node=hudNodes.get(slot.kind);if(!node){node=models.get(slot.kind);hudNodes.set(slot.kind,node);hud.add(node);}
        node.position.set(slot.x,height-slot.y,0);node.scale.setScalar(slot.size);node.rotation.set(-.9,0,-.4);
      }
      for(const [key,node] of hudNodes)if(!imageKeys.has(key)){hud.remove(node);hudNodes.delete(key);}
      if(hudNodes.size){renderer.setViewport?.(0,0,width,height);renderer.autoClear=false;renderer.clearDepth();renderer.render(hud,hudCamera);}
      lastStats={backend:'webgl2',parkingObservation:cue,followingShown:!!follow,radarContacts:objects.filter(o=>o.origin==='radar_contact').length,egoModel:cuv?'generic-cuv':skin?.id||'fallback',modelLibrary:library.status,lodCounts,objects:objects.length,classified:objects.filter(o=>o.kind!=='unknown').length,unknown:objects.filter(o=>o.kind==='unknown').length,imageIcons:hudNodes.size,width,height,drawCalls,triangles,allocated,reused,discarded,pooled,geometries:renderer.info.memory?.geometries??null,textures:renderer.info.memory?.textures??null};canvas.dataset.renderer='webgl2';return true;
    }catch{failed=true;dispose();canvas.hidden=true;lastStats={...lastStats,backend:'canvas-fallback'};return false;}
  },pause(){active=false;canvas.hidden=true;},snapshot:()=>({...lastStats,environmentRanges:active&&!lost&&renderer&&lastRanges?lastRanges.length/6:0,environmentCells:active&&!lost&&renderer?volume?.count||0:0}),destroy(){closed=true;egoModel.dispose();library.dispose();canvas.removeEventListener('webglcontextlost',contextLost);canvas.removeEventListener('webglcontextrestored',contextRestored);volume?.dispose();dispose();canvas.remove();}};
}
