// Display-only observations. Never infer a class from an unclassified radar echo.
import {ROAD_CLASSES,IMAGE_ONLY_CLASSES} from './object_classes.js';
export {ROAD_CLASSES} from './object_classes.js';
const finite = n => typeof n === 'number' && Number.isFinite(n);

export function surroundingTargets(radar, range=75) {
  const out=[];
  const append=(lead,source)=>{
    if(lead?.status!==true||!finite(lead.dRel)||lead.dRel<=0||lead.dRel>range||!finite(lead.yRel)||Math.abs(lead.yRel)>20)return;
    const x=lead.dRel,y=-lead.yRel;
    const id=lead.radar===true&&Number.isSafeInteger(lead.radarTrackId)&&lead.radarTrackId>=0?lead.radarTrackId:null;
    // The same native target is repeated in primary/side/cut-in collections.
    // Without a usable track ID, only collapse nearly identical observations.
    if(out.some(p=>Math.abs(p.x-x)<(id!==null&&p.trackId===id?2:.5)&&Math.abs(p.y-y)<.35
      &&(id!==null&&p.trackId===id||(id===null||p.trackId===null)&&finite(lead.vRel)&&finite(p.vRel)&&Math.abs(p.vRel-lead.vRel)<.3)))return;
    out.push({id:source,source:`radarState.${source}`,kind:'unknown',x,y,vRel:finite(lead.vRel)?lead.vRel:null,
      trackId:id,radarUsed:typeof lead.radar==='boolean'?lead.radar:null,origin:'native_lead_reference',
      probability:finite(lead.modelProb)&&lead.modelProb>=0&&lead.modelProb<=1?lead.modelProb:null});
  };
  for(const slot of ['leadOne','leadTwo','leadLeft','leadRight'])append(radar?.[slot],slot);
  for(const slot of ['leadsLeft','leadsCenter','leadsRight','leadsLeft2','leadsRight2','leadsCutIn'])
    (Array.isArray(radar?.[slot])?radar[slot]:[]).slice(0,6).forEach((lead,i)=>append(lead,`${slot}[${i}]`));
  return out.slice(0,32);
}

export function cameraGeometry(state, width, height) {
  const cal=state?.liveCalibration,cam=state?.roadCameraState;
  const rpy=cal?.rpyCalib,h=cal?.height?.[0];
  const calibrated=cal?.calStatus===1||cal?.calStatus==='calibrated';
  if(!calibrated||!Array.isArray(rpy)||rpy.length!==3||!rpy.every(n=>finite(n)&&Math.abs(n)<1)
    ||!finite(h)||h<.5||h>3||!finite(width)||!finite(height)||width<2||height<2)return null;
  const sensor=String(cam?.sensor||'').toLowerCase();
  const config=sensor==='os04c10'?[1344,760,1141.5]:['ar0231','ox03c10'].includes(sensor)?[1928,1208,2648]:null;
  if(!config)return null;
  // Only the full, uncropped ROAD stream is supported. Reject inconsistent aspect.
  if(Math.abs((width/height)/(config[0]/config[1])-1)>.025)return null;
  return {width,height,fx:config[2]*width/config[0],fy:config[2]*height/config[1],heightM:h,rpy:[...rpy],sensor};
}

export function groundPoint(box, geometry, range=75) {
  if(!geometry||!box)return null;
  const {width:w,height:h,fx,fy,heightM,rpy}=geometry;
  const {originX:u,originY:v,width:bw,height:bh}=box;
  if(![u,v,bw,bh].every(finite)||bw<=1||bh<=1||u<0||v<0||u+bw>w+1||v+bh>=h*.985)return null;
  // Intersect the bottom-centre image ray with a locally flat ground plane.
  // This is an approximation, not depth inference or measured 3D dimensions.
  const ray=[1,(u+bw/2-w/2)/fx,(v+bh-h/2)/fy];
  const [r,p,y]=rpy,cr=Math.cos(r),sr=Math.sin(r),cp=Math.cos(p),sp=Math.sin(p),cy=Math.cos(y),sy=Math.sin(y);
  const rotation=[[cy*cp,cy*sp*sr-sy*cr,cy*sp*cr+sy*sr],
    [sy*cp,sy*sp*sr+cy*cr,sy*sp*cr-cy*sr],[-sp,cp*sr,cp*cr]];
  const calibrated=[0,1,2].map(i=>rotation[0][i]*ray[0]+rotation[1][i]*ray[1]+rotation[2][i]*ray[2]);
  if(calibrated[0]<=0||calibrated[2]<.02)return null;
  const scale=heightM/calibrated[2],x=calibrated[0]*scale,lat=calibrated[1]*scale;
  return finite(x)&&finite(lat)&&x>=1&&x<=range&&Math.abs(lat)<=20?[x,lat]:null;
}

export function cameraTargets(detections, geometry, range=75) {
  const result=[];
  for(const [i,item] of (Array.isArray(detections)?detections:[]).slice(0,24).entries()){
    const category=item?.categories?.[0],kind=category?.categoryName,score=category?.score;
    if(!ROAD_CLASSES.includes(kind)||!finite(score)||score<.5||score>1)continue;
    const point=groundPoint(item.boundingBox,geometry,range);
    if(!point)continue;
    result.push({id:`camera-${i}`,source:'browser.efficientdet_lite0',kind,x:point[0],y:point[1],probability:score,
      origin:'calibrated_camera',positionMethod:'flat_ground_projection',dimensions:null,heading:null,
      groundTruth:false,reviewed:false});
  }
  return result;
}

export function imageTargets(detections,width,height){
  if(!finite(width)||!finite(height)||width<2||height<2)return [];
  return (Array.isArray(detections)?detections:[]).slice(0,24).flatMap((item,i)=>{
    const c=item?.categories?.[0],b=item?.boundingBox;
    if(!IMAGE_ONLY_CLASSES.includes(c?.categoryName)||!finite(c.score)||c.score<.5||c.score>1
      ||!b||![b.originX,b.originY,b.width,b.height].every(finite)||b.width<=1||b.height<=1
      ||b.originX<0||b.originY<0||b.originX+b.width>width+1||b.originY+b.height>height+1)return [];
    return [{id:`image-${i}`,kind:c.categoryName,probability:c.score,
      box:[b.originX/width,b.originY/height,b.width/width,b.height/height],
      origin:'image_detection_only',position:null,distance:null,signalState:null}];
  });
}
