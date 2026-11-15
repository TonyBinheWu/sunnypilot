// Model-assisted BEV review data. Never produces ground truth or control inputs.
export const BEV_SCHEMA = 'carrot-bev-annotations/v1';
const finite = value => typeof value === 'number' && Number.isFinite(value);
const probability = value => finite(value) && value >= 0 && value <= 1 ? value : null;
export function bevProjection(width,height,range=50) {
  const distance=[30,50,75].includes(Number(range))?Number(range):50;
  const scale=Math.min(width/20,height*.78/distance),cx=width/2,cy=height*.85;
  return {range:distance,scale,width,height,
    project:(x,y)=>[cx+y*scale,cy-x*scale],
    unproject:(u,v)=>[(cy-v)/scale,(u-cx)/scale]};
}
export function bevObjects(scene,range=50) {
  const objects=[];
  const vector=(path,id,kind,source,prob=null,std=null)=>{
    const parts=[];let points=[];
    const flush=()=>{if(points.length>=2)parts.push(points);points=[];};
    for(let i=0;i<Math.min(256,path?.x?.length||0,path?.y?.length||0);i++){
      const x=path.x[i],y=path.y[i];
      if(!finite(x)||!finite(y)||x<0||x>range||Math.abs(y)>100){flush();continue;}
      points.push([x,y]);
    }
    flush();
    parts.forEach((coordinates,index)=>objects.push({id:`${id}:${index}`,kind,source,
      origin:'calibrated_camera',geometry:{type:'LineString',coordinates},
      probability:probability(prob),lateralStdM:finite(std)&&std>=0?std:null,provenance:'model_assisted',reviewed:false}));
  };
  const model=scene.model;
  if(model){
    vector(model.position,'path','model_path','modelV2.position');
    (Array.isArray(model.laneLines)?model.laneLines:[]).slice(0,4).forEach((line,i)=>
      vector(line,`lane${i}`,'lane_line',`modelV2.laneLines[${i}]`,model.laneLineProbs?.[i],model.laneLineStds?.[i]));
    (Array.isArray(model.roadEdges)?model.roadEdges:[]).slice(0,2).forEach((line,i)=>
      vector(line,`edge${i}`,'road_edge',`modelV2.roadEdges[${i}]`,null,model.roadEdgeStds?.[i]));
  }
  for(const [slot,lead] of [['leadOne',scene.radar?.leadOne],['leadTwo',scene.radar?.leadTwo]]){
    if(lead?.status!==true||!finite(lead.dRel)||lead.dRel<=0||lead.dRel>range||!finite(lead.yRel)||Math.abs(lead.yRel)>100)continue;
    objects.push({id:slot,kind:'lead_target',source:`radarState.${slot}`,origin:'native_lead_reference',
      geometry:{type:'Point',coordinates:[lead.dRel,-lead.yRel]},
      relativeSpeedMps:finite(lead.vRel)?lead.vRel:null,modelProbability:probability(lead.modelProb),
      radarUsed:typeof lead.radar==='boolean'?lead.radar:null,
      nativeTrackId:lead.radar===true&&Number.isSafeInteger(lead.radarTrackId)&&lead.radarTrackId>=0?lead.radarTrackId:null,
      dimensions:null,provenance:'model_assisted',reviewed:false});
  }
  return objects;
}
export function bevSnapshot(scene,{range=50,now=Date.now(),replay=false,sourceTimes={}}={}) {
  return {schema:BEV_SCHEMA,capturedAt:new Date(now).toISOString(),mode:replay?'replay':'live',
    coordinateConvention:{units:'m',x:'forward',y:'right',z:'not_exported',
      note:'Native longitudinal origins are retained per object; no calibrated cross-sensor registration is claimed.'},
    synchronization:{frameId:Number.isSafeInteger(scene.model?.frameId)?scene.model.frameId:null,
      modelReceivedMonotonicMs:finite(sourceTimes.modelV2)?sourceTimes.modelV2:null,
      radarReceivedMonotonicMs:finite(sourceTimes.radarState)?sourceTimes.radarState:null,
      frameSynchronized:false},
    rangeM:range,groundTruth:false,reviewed:false,containsCameraImage:false,
    unavailableCapabilities:['occupancy','pedestrian_detection','traffic_sign_detection','lane_connectivity','fleet_mapping'],
    objects:bevObjects(scene,range),manual:[]};
}
export function addHumanLabel(snapshot,category,coordinates) {
  if(!snapshot||snapshot.manual.length>=64||!['unknown','vehicle','pedestrian','sign','lane_correction'].includes(category))return false;
  const line=category==='lane_correction';
  if(!Array.isArray(coordinates)||coordinates.length>(line?64:1)||coordinates.length<(line?2:1))return false;
  if(!coordinates.every(p=>Array.isArray(p)&&p.length===2&&p.every(finite)&&p[0]>=0&&p[0]<=snapshot.rangeM&&Math.abs(p[1])<=100))return false;
  snapshot.manual.push({id:`human-${snapshot.manual.length+1}`,kind:category,source:'human',origin:'display_local',
    geometry:{type:line?'LineString':'Point',coordinates:line?coordinates.map(p=>[...p]):[...coordinates[0]]},
    provenance:'human_unverified',reviewed:false,groundTruth:false});return true;
}
export function drawBevAnnotations(ctx,projection,objects,{grid=true,details=true,text=(k,f)=>f}={}) {
  const {width:w,height:h,range,scale,project}=projection;
  const font=Math.max(10,Math.min(15,w/48));ctx.font=`${font}px system-ui`;ctx.textBaseline='top';
  if(grid){
    ctx.strokeStyle='#ffffff22';ctx.lineWidth=1;
    const span=w/(2*scale),step=range<=30?5:10;
    ctx.beginPath();for(let x=0;x<=range;x+=step){const y=project(x,0)[1];ctx.moveTo(0,y);ctx.lineTo(w,y);}
    for(let y=Math.ceil(-span/step)*step;y<=span;y+=step){const u=project(0,y)[0];ctx.moveTo(u,0);ctx.lineTo(u,h);}
    ctx.stroke();ctx.fillStyle='#c5d1df';for(let x=step;x<=range;x+=step)ctx.fillText(`${x} m`,w/2+4,project(x,0)[1]+2);
    const u=w-5*scale-16,v=h-20;ctx.strokeStyle='#d9e6f7';ctx.beginPath();ctx.moveTo(u,v);ctx.lineTo(u+5*scale,v);ctx.stroke();ctx.fillText('5 m',u,v-18);
  }
  const occupied=[];
  for(const object of objects){
    const human=object.provenance==='human_unverified',point=object.geometry.type==='Point';
    const color=human?'#ffce72':object.kind==='lead_target'?'#70e3e6':object.kind==='road_edge'?'#edb88d':'#a3c5ff';
    const coords=point?[object.geometry.coordinates]:object.geometry.coordinates;
    if(!coords?.length)continue;
    const pixels=coords.map(p=>project(...p));
    ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=human?2:1;
    if(human||point||object.kind==='lane_line'){
      ctx.setLineDash?.(!human&&!point&&(object.probability===null||object.probability<.3)?[3,4]:[]);
      ctx.beginPath();if(point){ctx.arc(pixels[0][0],pixels[0][1],5,0,Math.PI*2);}
      else pixels.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.stroke();ctx.setLineDash?.([]);
    }
    if(!details&&!human)continue;
    const name=human?`${text('bev_human','Human · unverified')} ${text(`bev_kind_${object.kind}`,object.kind)}`:
      text(`bev_kind_${object.kind}`,object.kind);
    let label=`${name} ${object.id.split(':')[0]}`;
    if(point&&!human){label+=` · ${object.geometry.coordinates[0].toFixed(1)} m`;
      if(finite(object.relativeSpeedMps))label+=` · Δv ${object.relativeSpeedMps.toFixed(1)} m/s`;}
    if(object.probability!==null&&finite(object.probability))label+=` · p ${(object.probability*100).toFixed(0)}%`;
    if(finite(object.lateralStdM))label+=` · σ ${object.lateralStdM.toFixed(2)} m`;
    const anchor=pixels[Math.floor(pixels.length/2)];
    const tw=Math.min(w-8,ctx.measureText(label).width+8),x=Math.max(4,Math.min(w-tw-4,anchor[0]+8));
    let y=null;
    for(let attempt=0;attempt<18;attempt++){
      const offset=attempt===0?0:Math.ceil(attempt/2)*(attempt%2?1:-1)*(font+10);
      const candidate=Math.max(4,Math.min(h-font-28,anchor[1]+4+offset));
      if(!occupied.some(r=>x<r.x+r.w+4&&x+tw+4>r.x&&candidate<r.y+r.h+4&&candidate+font+10>r.y)){
        y=candidate;occupied.push({x,y,w:tw,h:font+6});break;
      }
    }
    if(y===null)continue;
    ctx.strokeStyle=color;ctx.lineWidth=.6;ctx.beginPath();ctx.moveTo(...anchor);ctx.lineTo(x,y+font/2);ctx.stroke();
    ctx.fillStyle='#0a131dea';ctx.fillRect(x-2,y-2,tw,font+6);ctx.fillStyle=color;ctx.fillText(label,x+2,y,w-8);
  }
}
