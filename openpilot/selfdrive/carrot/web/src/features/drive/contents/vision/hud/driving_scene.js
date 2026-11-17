import {drawDetectedMesh} from './object_mesh.js';
import {ANIMALS} from './object_classes.js';
import {surroundingTargets} from './scene_objects.js';

// Original vector artwork. Symbol dimensions are illustrative, not inferred sizes.
export function drivingProjection(width,height) {
  const s=Math.sin(25*Math.PI/180),c=Math.cos(25*Math.PI/180),f=height*.96;
  return (x,y,z=0)=>{
    const depth=(x+9)*c+(8-z)*s;
    return depth>.1?[width/2+f*y/depth,height*.46+f*((8-z)*c-(x+9)*s)/depth]:null;
  };
}
export function drawSceneObject(ctx,project,object,{ego=false,flat=false,text=(k,f)=>f}={}) {
  const {x,y,kind}=object;
  const polygon=(points,color)=>{
    const p=points.map(([dx,dy,z])=>project(x+dx,y+dy,z));if(p.some(v=>!v))return;
    ctx.fillStyle=color;ctx.beginPath();p.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fill();
  };
  if(kind==='unknown'){
    const p=project(x,y,.1);if(!p)return;
    ctx.strokeStyle=flat?'#8cabbc':'#8796a2';ctx.lineWidth=1.4;ctx.beginPath();
    ctx.ellipse(p[0],p[1],flat?5:7,flat?5:3,0,0,Math.PI*2);ctx.stroke();return;
  }
  const person=kind==='person',twoWheel=['motorcycle','bicycle'].includes(kind);
  if(flat&&kind==='traffic cone'){
    polygon([[-.5,-.35,0],[.5,0,0],[-.5,.35,0]],'#ed914b');
  }else if(flat&&ANIMALS.includes(kind)){
    const p=project(x,y);if(!p)return;ctx.fillStyle='#96aebd';ctx.beginPath();ctx.ellipse(p[0],p[1],5,9,0,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(p[0],p[1]-9,3.5,0,Math.PI*2);ctx.fill();
  }else if(!flat&&['car','bus','truck','person','motorcycle','bicycle','traffic cone',...ANIMALS].includes(kind)){
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

export function drawDrivingScene(ctx,width,height,scene,{rainbow=false,text,drawEgo,night=false,lift=0}={}) {
  ctx.clearRect(0,0,width,height);ctx.fillStyle=night?'#101114':'#f2f3f3';ctx.fillRect(0,0,width,height);
  const base=drivingProjection(width,height),shift=Number.isFinite(lift)?Math.max(0,Math.min(height*.3,lift)):0;
  const project=(x,y,z=0)=>{const p=base(x,y,z);return p?[p[0],p[1]-shift]:null;},model=scene.model;
  const pathPoints=(path,offset=0)=>{
    const points=[];
    for(let i=0;i<Math.min(path?.x?.length||0,path?.y?.length||0,256);i++){
      const x=path.x[i],y=path.y[i];
      points.push(Number.isFinite(x)&&Number.isFinite(y)&&x>=0&&x<=75&&Math.abs(y)<=20?project(x,y+offset):null);
    }
    return points;
  };
  const stroke=(path,color,width)=>{
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();let started=false;
    for(const p of pathPoints(path)){if(!p){started=false;continue;}if(started)ctx.lineTo(...p);else{ctx.moveTo(...p);started=true;}}
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
    ctx.fillStyle=night?'#202329':'#e8eaec';
    for(let i=1;i<Math.min(left.length,right.length);i++){
      if(!left[i-1]||!left[i]||!right[i]||!right[i-1]
        ||Math.abs(edges[0].x[i]-edges[1].x[i])>.5||Math.abs(edges[0].x[i-1]-edges[1].x[i-1])>.5)continue;
      ctx.beginPath();ctx.moveTo(...left[i-1]);ctx.lineTo(...left[i]);ctx.lineTo(...right[i]);ctx.lineTo(...right[i-1]);ctx.closePath();ctx.fill();
    }
    (model.roadEdges||[]).slice(0,2).forEach(line=>stroke(line,night?'#737b86':'#c7cdd1',2.5));
    (model.laneLines||[]).slice(0,4).forEach((line,i)=>{if((model.laneLineProbs?.[i]??0)>.3)stroke(line,night?'#e0e5ee':'#b9c1c8',1.6);});
    if(rainbow){['#f36d83','#f6b35b','#ece367','#72cba0','#6ab9e9','#a28ade','#d795cf'].forEach((color,i)=>ribbon(model.position,-.9+i*1.8/7,-.9+(i+1)*1.8/7,color));}
    else ribbon(model.position,-.75,.75,night?'#168bffdc':'#69b7ecb0');
  }
  const objects=[...surroundingTargets(scene.radar),...(scene.vision?.objects||[]),...(scene.road?.objects||[])];
  objects.sort((a,b)=>b.x-a.x).forEach(object=>drawSceneObject(ctx,project,object,{text}));
  if(drawEgo)drawEgo(ctx,project);
  else drawSceneObject(ctx,project,{kind:'car',x:0,y:0},{ego:true,text});
}
