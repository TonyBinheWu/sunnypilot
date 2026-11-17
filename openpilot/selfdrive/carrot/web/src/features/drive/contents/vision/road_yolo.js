// Postprocess only the pinned cone/crosswalk heads. No light-state output or
// arbitrary class-name remapping, and no shape/colour heuristics as detection.
export function resizePlan(width,height,mode,size=640){
  if(!Number.isFinite(width)||!Number.isFinite(height)||width<2||height<2||![320,640].includes(size)||!['stretch','letterbox'].includes(mode))throw Error('dimensions/resize');
  const ratio=size/Math.max(width,height),w=mode==='stretch'?size:Math.round(width*ratio),h=mode==='stretch'?size:Math.round(height*ratio);
  return {w,h,x:Math.floor((size-w)/2),y:Math.floor((size-h)/2),sx:w/width,sy:h/height};
}
export function rgbTensor(rgba,size=640){
  if(![320,640].includes(size)||rgba.length!==size*size*4)throw Error('pixels');
  const n=size*size,out=new Float32Array(n*3);
  for(let i=0;i<n;i++){out[i]=rgba[i*4]/255;out[n+i]=rgba[i*4+1]/255;out[n*2+i]=rgba[i*4+2]/255;}
  return out;
}
const iou=(a,b)=>{
  const w=Math.max(0,Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)),h=Math.max(0,Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y));
  return w*h/(a.w*a.h+b.w*b.h-w*h);
};
export function decodeRoadOutput(data,dims,model,width,height,plan){
  if(dims.length!==3||dims.some((n,i)=>n!==model.shape[i])||data.length!==dims.reduce((a,b)=>a*b,1))throw Error('model output shape');
  const v8=model.format==='yolov8',count=v8?dims[2]:dims[1],stride=v8?dims[1]:dims[2];
  if(!['yolov8','yolov5'].includes(model.format)||model.classIndex<0||model.classIndex>=stride-(v8?4:5))throw Error('class mapping');
  const read=(i,j)=>data[v8?j*count+i:i*stride+j],boxes=[];
  for(let i=0;i<count;i++){
    const confidence=read(i,model.classIndex+(v8?4:5))*(v8?1:read(i,4));
    if(!Number.isFinite(confidence)||confidence<.5||confidence>1)continue;
    const [cx,cy,w,h]=[0,1,2,3].map(j=>read(i,j));
    if(![cx,cy,w,h].every(Number.isFinite)||w<=1||h<=1)continue;
    const x=Math.max(0,Math.min(width,(cx-w/2-plan.x)/plan.sx)),y=Math.max(0,Math.min(height,(cy-h/2-plan.y)/plan.sy));
    const right=Math.max(0,Math.min(width,(cx+w/2-plan.x)/plan.sx)),bottom=Math.max(0,Math.min(height,(cy+h/2-plan.y)/plan.sy));
    if(right-x<=1||bottom-y<=1)continue;
    boxes.push({x,y,w:right-x,h:bottom-y,confidence});
  }
  const kept=[];
  for(const b of boxes.sort((a,b)=>b.confidence-a.confidence).slice(0,1000)){
    if(kept.every(k=>iou(b,k)<.45))kept.push(b);if(kept.length>=24)break;
  }
  return kept.map(b=>({categories:[{categoryName:model.label,score:b.confidence}],boundingBox:{originX:b.x,originY:b.y,width:b.w,height:b.h},detector:model.id}));
}
