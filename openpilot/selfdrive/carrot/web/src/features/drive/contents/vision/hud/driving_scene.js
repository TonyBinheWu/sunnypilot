import {inclinedProjection, parkingDistanceText, parkingObservation, parkingWheelTicks} from './parking_environment.js';
import {roadColors,pathChevrons,nearPathSurface,dashedRibbon,isDashed,nearPathCar,parkingOutline} from './road_scene_style.js';
import {roadModelKind} from './road_model_selection.js';
import {paintStripes} from './road_paint.js';
import {drawDetectedMesh} from './object_mesh.js';
import {ANIMALS} from './object_classes.js';
import {surroundingTargets} from './scene_objects.js';
import {sceneProjection} from '../../../../cockpit/scene_camera.js';

// Original vector artwork. Symbol dimensions are illustrative, not inferred sizes.
export function drivingProjection(width,height,camera=null) {
  if(camera)return sceneProjection(width,height,camera);
  const pitch=Number.isFinite(camera?.pitch)?Math.max(18,Math.min(60,camera.pitch)):25;
  const yaw=Number.isFinite(camera?.yaw)?camera.yaw*Math.PI/180:0;
  const s=Math.sin(pitch*Math.PI/180),c=Math.cos(pitch*Math.PI/180),f=Math.min(height*.96,width*1.35);
  const distance=Number.isFinite(camera?.distance)?Math.max(9,Math.min(16,camera.distance)):9;
  const elevation=Number.isFinite(camera?.height)?Math.max(6,Math.min(12,camera.height)):8;
  const origin=Number.isFinite(camera?.anchorY)?height*Math.max(.72,Math.min(.88,camera.anchorY))-f*(elevation*c-distance*s)/(distance*c+elevation*s):height*.46;
  const project=(x,y,z=0)=>{
    const along=x*Math.cos(yaw)+y*Math.sin(yaw),side=y*Math.cos(yaw)-x*Math.sin(yaw);
    const depth=(along+distance)*c+(elevation-z)*s;
    return depth>.1?[width/2+f*side/depth,origin+f*((elevation-z)*c-(along+distance)*s)/depth]:null;
  };
  if(camera){project.view=[-distance*Math.cos(yaw),-distance*Math.sin(yaw),elevation];project.depth=(x,y,z=0)=>(x*Math.cos(yaw)+y*Math.sin(yaw)+distance)*c+(elevation-z)*s;}
  return project;
}
export function drawSceneObject(ctx,project,object,options={}) {
  const style=roadModelKind(object);
  if(style){
    const fallback=['sedan','suv','mpv','pickup'].includes(style)?'car':style==='cone'?'traffic cone':style;
    if(fallback!==object.kind)object={...object,kind:fallback};
  }
  const heading=object.heading||0, {x,y}=object, c=Math.cos(heading),s=Math.sin(heading);
  const rotated=heading?(px,py,z)=>project(x+c*(px-x)-s*(py-y), y+s*(px-x)+c*(py-y),z):project;
  if(object.state!=='predicted')return paintSceneObject(ctx,rotated,object,options);
  ctx.save();ctx.globalAlpha*=.48;
  try {paintSceneObject(ctx,rotated,object,options);} finally {ctx.restore();}
}
function paintSceneObject(ctx,project,object,{ego=false,flat=false,night=false,text=(k,f)=>f}={}) {
  const {x,y,kind}=object;
  const polygon=(points,color)=>{
    const p=points.map(([dx,dy,z])=>project(x+dx,y+dy,z));if(p.some(v=>!v))return;
    ctx.fillStyle=color;ctx.beginPath();p.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fill();
  };
  if(kind==='unknown'){
    const p=project(x,y,.1);if(!p)return;
    ctx.strokeStyle=flat||night?'#b1beca':'#4f606d';ctx.lineWidth=1.8;ctx.beginPath();
    if(flat)ctx.ellipse(p[0],p[1],6,6,0,0,Math.PI*2);
    else{
      const corners=[[-.55,-.4,0],[-.55,.4,0],[.55,.4,0],[.55,-.4,0],[-.55,-.4,.85],[-.55,.4,.85],[.55,.4,.85],[.55,-.4,.85]].map(([dx,dy,z])=>project(x+dx,y+dy,z));
      for(const [a,b] of [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]])if(corners[a]&&corners[b]){ctx.moveTo(...corners[a]);ctx.lineTo(...corners[b]);}
    }ctx.stroke();
    if(!flat){ctx.font='12px system-ui';ctx.textAlign='center';ctx.fillStyle=ctx.strokeStyle;ctx.fillText(`${Math.round(x)} m`,p[0],p[1]-11);ctx.textAlign='left';}return;
  }
  const person=kind==='person',twoWheel=['motorcycle','bicycle'].includes(kind);
  if(kind==='barrier'||kind==='drum'){
    drawDetectedMesh(ctx,project,object);
  }else if(flat&&kind==='traffic cone'){
    polygon([[-.5,-.35,0],[.5,0,0],[-.5,.35,0]],'#ed914b');
  }else if(flat&&ANIMALS.includes(kind)){
    const p=project(x,y);if(!p)return;ctx.fillStyle='#96aebd';ctx.beginPath();ctx.ellipse(p[0],p[1],5,9,0,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(p[0],p[1]-9,3.5,0,Math.PI*2);ctx.fill();
  }else if(!flat&&['car','bus','truck','person','motorcycle','bicycle','traffic cone','barrier','drum',...ANIMALS].includes(kind)){
    drawDetectedMesh(ctx,project,object);
  }else if(person){
    const feet=project(x,y,0),head=project(x,y,1.65),hip=project(x,y,.7);if(!feet||!head||!hip)return;
    const radius=Math.max(2,Math.min(6,Math.abs(feet[1]-head[1])*.12));
    ctx.fillStyle=flat?'#c4b2e6':'#65727d';ctx.beginPath();ctx.arc(head[0],head[1],radius,0,Math.PI*2);ctx.fill();
    ctx.strokeStyle=ctx.fillStyle;ctx.lineWidth=Math.max(2,radius*.8);ctx.lineCap='round';ctx.beginPath();
    ctx.moveTo(head[0],head[1]+radius);ctx.lineTo(...hip);
    ctx.moveTo(hip[0],hip[1]);ctx.lineTo(feet[0]-radius,feet[1]);ctx.moveTo(...hip);ctx.lineTo(feet[0]+radius,feet[1]);
    ctx.moveTo(head[0]-radius*1.4,(head[1]+hip[1])/2+radius);ctx.lineTo(head[0]+radius*1.4,(head[1]+hip[1])/2+radius);ctx.stroke();
  }else if(twoWheel){
    polygon([[-.8,-.14,.15],[.8,-.14,.15],[.8,.14,.15],[-.8,.14,.15]],'#3f4c59');
    polygon([[-.55,-.3,.5],[.55,-.3,.5],[.55,.3,.5],[-.55,.3,.5]],flat?'#f5ca80':'#929ea8');
    const p=project(x,y,1.3);if(p){ctx.fillStyle='#53606d';ctx.beginPath();ctx.arc(...p,flat?3:4,0,Math.PI*2);ctx.fill();}
  }else{
    const length=kind==='bus'?8:kind==='truck'?6:4.3,halfW=kind==='bus'||kind==='truck'?1.1:.9;
    const halfL=length/2,z=kind==='bus'?2.7:kind==='truck'?2.3:1.3;
    polygon([[-halfL,-halfW,0],[halfL,-halfW,0],[halfL,halfW,0],[-halfL,halfW,0]],'#bac1c64a');
    polygon([[-halfL,-halfW,0],[-halfL,halfW,0],[-halfL,halfW,z*.65],[-halfL,-halfW,z*.65]],ego?'#b6c1cd':'#8b98a3');
    polygon([[-halfL,halfW,0],[halfL,halfW,0],[halfL,halfW,z*.65],[-halfL,halfW,z*.65]],ego?'#cfd8df':'#a4afb7');
    polygon([[-halfL,-halfW,z*.65],[halfL,-halfW,z*.65],[halfL,halfW,z*.65],[-halfL,halfW,z*.65]],ego?'#f9fafb':'#c4cbd0');
    const roofL=halfL*.56,roofW=halfW*.8;
    polygon([[-roofL,-roofW,z],[roofL,-roofW,z],[roofL,roofW,z],[-roofL,roofW,z]],ego?'#e7ecf0':'#a9b4be');
    polygon([[roofL,-roofW,z],[halfL*.85,-halfW*.88,z*.65],[halfL*.85,halfW*.88,z*.65],[roofL,roofW,z]],'#42505dd9');
    polygon([[-roofL,-roofW,z],[-halfL*.85,-halfW*.88,z*.65],[-halfL*.85,halfW*.88,z*.65],[-roofL,roofW,z]],'#4b5966d9');
    for(const sign of [-1,1])polygon([[-halfL-.02,sign*halfW*.85,z*.45],[-halfL-.02,sign*halfW*.5,z*.45],[-halfL-.02,sign*halfW*.5,z*.57],[-halfL-.02,sign*halfW*.85,z*.57]],'#d95e62');
  }
  if(!ego&&['person','motorcycle','bicycle','bus','truck','traffic cone',...ANIMALS].includes(kind)){
    const p=project(x,y,kind==='person'?2:1.8);if(!p)return;
    const label=text(`scene_kind_${kind.replaceAll(' ','_')}`,kind);ctx.font='11px system-ui';ctx.textAlign='center';
    const tw=ctx.measureText(label).width+10;ctx.fillStyle=flat?'#10202ee8':'#ffffffdd';ctx.fillRect(p[0]-tw/2,p[1]-18,tw,16);
    ctx.fillStyle=flat?'#d9e4f2':'#53616f';ctx.fillText(label,p[0],p[1]-6);ctx.textAlign='left';
  }
}

export function drawDrivingScene(ctx,width,height,scene,{rainbow=false,text,drawEgo,night=false,lift=0,camera=null,attitude=null,steer=null}={}) {
  const palette=roadColors(night);ctx.clearRect(0,0,width,height);ctx.fillStyle=palette.road;ctx.fillRect(0,0,width,height);
  const base=sceneProjection(width,height,{...camera,roadOverview:true}),shift=Number.isFinite(lift)?Math.max(0,Math.min(height*.3,lift)):0;
  const project=(x,y,z=0)=>{const p=base(x,y,z);return p?[p[0],p[1]-shift]:null;},model=scene.model;
  if(base.view){project.view=base.view;project.depth=base.depth;}
  // A distant fog band blends into the same asphalt as the hardware renderer.
  const far=project(100,0),mid=project(30,0);
  if(far&&mid&&mid[1]>0){
    const band=Math.max(1,mid[1]),gradient=ctx.createLinearGradient?.(0,0,0,band);
    if(gradient?.addColorStop){gradient.addColorStop(0,palette.sky);gradient.addColorStop(Math.max(0,Math.min(.98,far[1]/band)),palette.sky);
      gradient.addColorStop(1,palette.road);ctx.fillStyle=gradient;ctx.fillRect(0,0,width,band);}
  }
  const pathPoints=(path,offset=0)=>{
    const points=[];
    for(let i=0;i<Math.min(path?.x?.length||0,path?.y?.length||0,256);i++){
      const x=path.x[i],y=path.y[i];
      points.push(Number.isFinite(x)&&Number.isFinite(y)&&x>=0&&x<=75&&Math.abs(y)<=20?project(x,y+offset):null);
    }
    return points;
  };
  function fillTriangles(points,color) {
    ctx.fillStyle=color;ctx.beginPath();
    for(let i=0;i+8<points.length;i+=9){
      const a=project(points[i],points[i+1],points[i+2]),b=project(points[i+3],points[i+4],points[i+5]),c=project(points[i+6],points[i+7],points[i+8]);
      if(a&&b&&c){ctx.moveTo(...a);ctx.lineTo(...b);ctx.lineTo(...c);ctx.closePath();}
    }
    ctx.fill();
  }
  const stroke=(path,color,width,offset=0)=>{
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();let started=false;
    for(const p of pathPoints(path,offset)){if(!p){started=false;continue;}if(started)ctx.lineTo(...p);else{ctx.moveTo(...p);started=true;}}
    ctx.stroke();
  };
  const ribbon=(path,left,right,color)=>{
    const a=pathPoints(path,left),b=pathPoints(path,right);ctx.fillStyle=color;
    for(let i=1;i<a.length;i++){
      if(!a[i-1]||!a[i]||!b[i]||!b[i-1])continue;
      ctx.beginPath();ctx.moveTo(...a[i-1]);ctx.lineTo(...a[i]);ctx.lineTo(...b[i]);ctx.lineTo(...b[i-1]);ctx.closePath();ctx.fill();
    }
  };
  if(model){
    const edges=model.roadEdges||[],left=pathPoints(edges[0]),right=pathPoints(edges[1]);
    ribbon(edges[0],-22,-.08,palette.verge);ribbon(edges[1],.08,22,palette.verge);
    ctx.fillStyle=palette.road;
    for(let i=1;i<Math.min(left.length,right.length);i++){
      if(!left[i-1]||!left[i]||!right[i]||!right[i-1]
        ||Math.abs(edges[0].x[i]-edges[1].x[i])>.5||Math.abs(edges[0].x[i-1]-edges[1].x[i-1])>.5)continue;
      ctx.beginPath();ctx.moveTo(...left[i-1]);ctx.lineTo(...left[i]);ctx.lineTo(...right[i]);ctx.lineTo(...right[i-1]);ctx.closePath();ctx.fill();
    }
    (model.roadEdges||[]).slice(0,2).forEach(line=>stroke(line,palette.edge,2.5));
    (model.laneLines||[]).slice(0,4).forEach((line,i)=>{
      if((model.laneLineProbs?.[i]??0)<=.3)return;
      const paint=paintStripes(scene.paint?.[i],i,palette.lane);
      for(const offset of paint.offsets){if(isDashed(scene.paint?.[i]))fillTriangles(dashedRibbon(line,offset-.065,offset+.065),paint.color);else stroke(line,paint.color,1.6,offset);}
    });
    const path=camera?.parking?null:model.position;
    if(rainbow){['#f36d83','#f6b35b','#ece367','#72cba0','#6ab9e9','#a28ade','#d795cf'].forEach((color,i)=>ribbon(path,-.9+i*1.8/7,-.9+(i+1)*1.8/7,color));}
    else {ribbon(path,-.83,.83,palette.path);fillTriangles(nearPathSurface(path),palette.near);fillTriangles(pathChevrons(path),palette.chevron);}
  }
  // When WebGL is lost mid-frame, keep the same observed near-field surfaces.
  // Draw only calibrated occupied cells, in depth order, with the same ego compensation.
  if(camera?.parking && scene.environment?.length){
    const motion=scene.environmentMotion||{},c=Math.cos(motion.angle||0),s=Math.sin(motion.angle||0);
    const points=scene.environment,cells=[];
    for(let i=0;i+2<points.length;i+=3){
      const x=c*points[i]-s*points[i+1]+(motion.x||0),y=s*points[i]+c*points[i+1]+(motion.y||0),z=points[i+2];
      if(x>0&&x<20&&Math.abs(y)<10&&z>=1&&z<=6)cells.push({x,y,z,depth:project.depth(x,y,z)});
    }
    cells.sort((a,b)=>b.depth-a.depth);
    for(const {x,y,z} of cells){
      const face=(offsets,color)=>{
        const corners=offsets.map(([a,b,h])=>project(x+a*.47,y+b*.47,z+h*.47));
        if(corners.some(p=>!p))return;
        ctx.fillStyle=color;ctx.beginPath();corners.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fill();
      };
      face([[-1,-1,-1],[-1,1,-1],[-1,1,1],[-1,-1,1]],'#687e90');
      const side=y<0?1:-1;
      face([[-1,side,-1],[1,side,-1],[1,side,1],[-1,side,1]],'#8093a1');
      face([[-1,-1,1],[-1,1,1],[1,1,1],[1,-1,1]],'#a8bac6');
    }
  }
  for(const slot of (scene.parking||[]).slice(0,12)){
    const outline=parkingOutline(slot.corners);
    if(outline)fillTriangles(outline,'#e9bf72');
  }
  const objects=scene.tracks?[...scene.tracks]:[...surroundingTargets(scene.radar),...(scene.vision?.objects||[]),...(scene.road?.objects||[])];
  objects.sort((a,b)=>project.depth?project.depth(b.x,b.y)-project.depth(a.x,a.y):b.x-a.x).forEach(object=>drawSceneObject(ctx,project,{...object,pathFocus:nearPathCar(object,model?.position)},{text,night}));
  if(camera?.parking){
    const wheelProjection=inclinedProjection(project,attitude);
    ctx.strokeStyle='#3289c5';ctx.lineWidth=2;
    for(const [x,y,endX,endY] of parkingWheelTicks(steer,camera.skinScale)){
      const a=wheelProjection(x,y,.12),b=wheelProjection(endX,endY,.12);
      if(a&&b){ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();}
    }
    const cue=scene.parkingCue===undefined?parkingObservation(scene):scene.parkingCue;
    const p=cue&&project(cue.x,cue.y,.08);
    if(p){
      ctx.save();ctx.strokeStyle=cue.color;ctx.lineWidth=3;ctx.beginPath();ctx.arc(...p,8,0,2*Math.PI);ctx.stroke();
      ctx.font='bold 14px system-ui';ctx.textAlign='center';const label=parkingDistanceText(cue);
      const width=ctx.measureText(label).width+12;
      ctx.fillStyle='#17232b';ctx.fillRect(p[0]-width/2,p[1]-30,width,18);
      ctx.fillStyle='#fff';ctx.fillText(label,p[0],p[1]-16);ctx.restore();
    }
  }
  if(drawEgo)drawEgo(ctx,inclinedProjection(project,attitude));
  else drawSceneObject(ctx,project,{kind:'car',x:0,y:0},{ego:true,text});
}
