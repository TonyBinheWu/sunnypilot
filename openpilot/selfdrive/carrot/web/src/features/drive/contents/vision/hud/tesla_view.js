import {navigationCue} from '../../../../cockpit/navigation_cue.js';
import {PARKING_VIEW, parkingAttitude, parkingDistanceText, parkingObservation} from './parking_environment.js';
import {createParkingView,createParkingMap,insidePolygon} from '../../../../cockpit/parking.js';
import {combineParking,vehicleParkingSource} from './vehicle_parking.js';
import {createParkingPerception} from './parking_perception.js';
import {paintedVehicle} from '../../../../cockpit/vehicle_paint.js';
import {drawCockpitVehicle,createVehicleSkinCache,selectedSkin,VEHICLE_SKINS} from '../../../../cockpit/vehicle.js';
import {OBJECT_NAMES} from './object_classes.js';
import {describeSignal,signalBadge} from './signal_badge.js';
import {visionPresentation,cockpitTelemetryStale} from '../../../../cockpit/presentation.js';
import {createSpeedZoom,sceneSpeedKph} from '../../../../cockpit/speed_zoom.js';
import {createViewOrbit,orbitCamera} from '../../../../cockpit/view_orbit.js';
import {cockpitTraffic} from '../../../../cockpit/traffic.js';
import {vehicleLamps} from '../../../../cockpit/vehicle_lamps.js';
import {bevProjection} from "./bev_annotations.js";
import {createBevWorkbench,BEV_CSS} from "./bev_workbench.js";
import {el, setText} from './dom.js';
import {surroundingTargets} from './scene_objects.js';
import {drawDrivingScene,drawSceneObject} from './driving_scene.js';
import {createObjectPerception} from './object_perception.js';
import {surfaceMotion} from '../occupancy_grid.js';
import {researchMap} from './research_map.js';
import {forEachDash} from './road_scene_style.js';
import {lanePaint,paintStripes,stripePattern} from './road_paint.js';
import {createPerceptionScene,createRenderMeter,trackingReport} from './perception_scene.js';
import {createDrivingScene3D} from './scene_3d.js';

export const METRIC_DEFAULTS = Object.freeze({speed:[.04,.04,1.2],limit:[.04,.43,1],set:[.04,.80,1]});
export function sceneRenderSize(width,height,quality,pixelRatio=1){
  const vw=Number.isFinite(width)&&width>0?width:1,vh=Number.isFinite(height)&&height>0?height:1;
  const cap=quality==='high'?[2560,1440]:quality==='low'?[960,540]:[1920,1080];
  const density=Math.max(1,Math.min(2,Number.isFinite(pixelRatio)?pixelRatio:1));
  if(vh>vw)[cap[0],cap[1]]=[cap[1],cap[0]];
  const factor=Math.min(density,cap[0]/vw,cap[1]/vh);
  return {width:Math.max(1,Math.round(vw*factor)),height:Math.max(1,Math.round(vh*factor)),factor};
}
export function metricLayout(value) {
  let input={};try {input=typeof value==='string'?JSON.parse(value):value||{};}catch{}
  return Object.fromEntries(Object.entries(METRIC_DEFAULTS).map(([key,def])=>{
    const row=input?.[key];
    return [key,Array.isArray(row)&&row.length===3&&row.every(Number.isFinite)
      ? [Math.max(0,Math.min(1,row[0])),Math.max(0,Math.min(1,row[1])),Math.max(.6,Math.min(2.2,row[2]))] : [...def]];
  }));
}
export function serviceFresh(target, key, now, replay=false) {
  if (replay) return true;
  const mono=target.CarrotStateReceivedAtMonotonic?.[key];
  const stamp=Number.isFinite(mono)?mono:target.CarrotStateUpdatedAt?.[key];
  const age=(Number.isFinite(mono)?now:Date.now())-stamp;
  return Number.isFinite(age)&&age>=0&&age<=1500;
}
export function birdScene(target, now) {
  const replay=target.CarrotVisionReplay?.status?.()?.active===true;
  const parked=!replay&&target.CarrotDeviceRuntimeState?.isOffroad===true;
  const state=target.CarrotOverlayState||{};
  return {model:!parked&&!state.modelV2?._sourceInvalid&&serviceFresh(target,'modelV2',now,replay)?state.modelV2:null,
    radar:!parked&&!state.radarState?._sourceInvalid&&serviceFresh(target,'radarState',now,replay)?state.radarState:null};
}
export function canEditMetrics(target, now) {
  if (target.CarrotVisionReplay?.status?.()?.active===true) return true;
  const runtime=target.CarrotDeviceRuntimeState;
  if(runtime?.isOffroad===true&&runtime?.isOnroad!==true)return true;
  const car=target.CarrotHudState?.carState;
  return serviceFresh(target,'carState',now)&&car?.gearShifter==='park'&&Number.isFinite(car?.vEgo)&&Math.abs(car.vEgo)<.1;
}
export function drawBirdScene(ctx,w,h,scene,{rainbow=false,projection=null,maxDistance=75,drawEgo=null}={}) {
  ctx.clearRect(0,0,w,h);ctx.fillStyle='#171c23';ctx.fillRect(0,0,w,h);
  const model=scene.model;
  // Model y is right-positive; native lead yRel is left-positive.
  const px=projection?.project||((x,y)=>[w*.5+y*w/22,h*.85-x*h/90]);
  const line=(path,color,width,offset=0)=>{
    if(!Array.isArray(path?.x)||!Array.isArray(path?.y))return;
    ctx.beginPath();let started=false;
    for(let i=0;i<Math.min(path.x.length,path.y.length);i++){
      const x=path.x[i],y=path.y[i];if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>maxDistance||Math.abs(y)>100){started=false;continue;}
      const p=px(x,y+offset);if(!started){ctx.moveTo(...p);started=true;}else ctx.lineTo(...p);
    }
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
  };
  if(model){
    for(const [a,b] of scene.mapLines||[]){
      if(Math.min(a[0],b[0])>maxDistance)continue;
      const atHorizon=(p,q)=>p[0]<=maxDistance?p:
        [maxDistance,p[1]+(q[1]-p[1])*(maxDistance-p[0])/(q[0]-p[0])];
      const start=atHorizon(a,b),end=atHorizon(b,a);
      line({x:[start[0],end[0]],y:[start[1],end[1]]},'#41556a',1);
    }
    if(scene.mapLines?.length){ctx.fillStyle='#b2c0cb';ctx.font='12px sans-serif';ctx.fillText('© OpenStreetMap contributors',8,h-8);}
    (model.roadEdges||[]).slice(0,2).forEach(p=>line(p,'#5e6671',3));
    (model.laneLines||[]).slice(0,4).forEach((p,i)=>{
      if((model.laneLineProbs?.[i]??0)<=.3)return;
      const paint=paintStripes(scene.paint?.[i],i,'#c2cad4');
      paint.offsets.forEach((offset,j)=>{
        const pattern=stripePattern(scene.paint?.[i],j);
        if(pattern==='dashed'||pattern==='dots'){
          ctx.beginPath();
          forEachDash(p,pattern==='dots',(s,y,e,z)=>{
            if(s>=maxDistance)return;
            const end=Math.min(e,maxDistance);
            ctx.moveTo(...px(s,y+offset));
            ctx.lineTo(...px(end,y+offset+(z-y)*(end-s)/(e-s)));
          });
          ctx.strokeStyle=paint.color;ctx.lineWidth=2;ctx.stroke();
        }else line(p,pattern==='boundary'?'#91989e':paint.color,2,offset);
      });
    });
    if(rainbow){
      const colors=['#f15c66','#ffad55','#ffe773','#79e5a1','#63cafa','#a18af5','#e88cdb'];
      colors.forEach((c,i)=>line({x:model.position?.x,y:model.position?.y?.map(y=>y+(i-3)*.17)},c,Math.max(2,w/140)));
    }else line(model.position,'#4daaff',Math.max(5,w/70));
  }
  const vehicle=(x,y,color,ego=false)=>{
    const [cx,cy]=px(x,y),vw=Math.min(w*.075,h*.06),vh=vw*1.9;
    ctx.fillStyle='#0007';ctx.fillRect(cx-vw*.6,cy-vh*.4,vw*1.2,vh*.85);
    ctx.fillStyle=color;ctx.beginPath();
    if(typeof ctx.roundRect==='function')ctx.roundRect(cx-vw/2,cy-vh/2,vw,vh,vw*.23);
    else ctx.rect(cx-vw/2,cy-vh/2,vw,vh);
    ctx.fill();
    ctx.fillStyle='#111a24';ctx.fillRect(cx-vw*.36,cy-vh*.27,vw*.72,vh*.26);
    ctx.fillStyle=ego?'#82acdf':'#d1d9e3';ctx.fillRect(cx-vw*.31,cy+vh*.02,vw*.62,vh*.19);
    ctx.fillStyle='#ecf6ff';ctx.fillRect(cx-vw*.38,cy-vh*.44,vw*.2,vh*.055);ctx.fillRect(cx+vw*.18,cy-vh*.44,vw*.2,vh*.055);
    if(ego){ctx.strokeStyle='#d7e9ff';ctx.lineWidth=2;ctx.strokeRect(cx-vw/2,cy-vh/2,vw,vh);}
  };
  const flatProject=(x,y)=>px(x,y);
  for(const object of scene.tracks??[...surroundingTargets(scene.radar,maxDistance),...(scene.vision?.objects||[]),...(scene.road?.objects||[])])if(object.x<=maxDistance)drawSceneObject(ctx,flatProject,object,{flat:true,text:scene.text});
  if(drawEgo)drawEgo(ctx,(x,y)=>px(x,y));else vehicle(0,0,'#397fdf',true);
}

export function createTeslaView(doc,target) {
  const text=(key,fallback)=>target.getUIText?.(key,fallback)||fallback;
  const root=el(doc,'div',{class:'tesla-view'});
  const research=researchMap(target);
  const remoteGpu=target.__CARROT_BOOTSTRAP__?.visionGpuScene===true;
  const canvas=el(doc,'canvas',{class:'tesla-scene',attrs:{'aria-label':text('vision_tesla_name','Bird’s-eye view')}});
  const notice=el(doc,'div',{class:'tesla-notice'});
  const perceptionStatus=el(doc,'div',{class:'tesla-perception',attrs:{role:'status'}});
  const mapCredit=el(doc,'a',{class:'tesla-map-credit',text:'OSM 道路中心線 · © OpenStreetMap contributors'});
  mapCredit.href='https://www.openstreetmap.org/copyright';mapCredit.target='_blank';mapCredit.rel='noopener noreferrer';
  mapCredit.hidden=true;root.appendChild(mapCredit);
  const volumeLegend=el(doc,'small',{class:'tesla-volume-legend',text:text('occupancy_legend','青色方格為推估表面，淡紫線為估距範圍。空白含未知區域。')});
  volumeLegend.hidden=true;
  const predictionLegend=el(doc,'small',{class:'tesla-prediction-legend'});predictionLegend.hidden=true;
  const parkingStatus=el(doc,'div',{class:'tesla-parking-status',attrs:{role:'status'}});
  const metrics=el(doc,'div',{class:'tesla-metrics'});
  const imageObservations=el(doc,'div',{class:'tesla-image-observations',attrs:{role:'status'}});
  let imageSignature=null;
  const perceptionScene=createPerceptionScene(target),meter=createRenderMeter();
  const speedZoom=createSpeedZoom();
  const orbit=createViewOrbit();
  const parkingView=createParkingView();
  const vehicleParking=vehicleParkingSource(target);
  const parkingMap=createParkingMap(target,()=>{lastSignature='';render(data,stale,unit,metricVisible,viewActive);});
  const parkingPerception=createParkingPerception(doc,target,()=>{lastSignature='';render(data,stale,unit,metricVisible,viewActive);});
  let parkingAnimation=false,poseLease=null,updatingLease=false;
  function parkingPoseActive(active){
    if(updatingLease)return;
    updatingLease=true;
    try{
      if(active && !poseLease?.active && target.CarrotDriveDataActivity?.acquire)
        poseLease=target.CarrotDriveDataActivity.acquire({owner:'parking_pose',ar:true});
      if(!active && poseLease){const previous=poseLease;poseLease=null;previous.release();}
    }finally{updatingLease=false;}
  }
  const parkingPanel=el(doc,'div',{class:'tesla-parking-panel'});
  const parkingButton=el(doc,'button',{class:'tesla-parking-view',attrs:{type:'button'}});
  parkingButton.addEventListener('click',e=>{e.stopPropagation();parkingView.toggle();refreshOrbit();});
  let orbitEnabled=false;
  const orbitPointers=new Map();let pinchStart=null;
  const refreshOrbit=()=>{lastSignature='';render(data,stale,unit,metricVisible,viewActive);};
  const orbitDown=e=>{if(!orbitEnabled||e.button!==0||orbitPointers.size>=2)return;parkingView.interact();const surface=e.currentTarget||canvas,r=surface.getBoundingClientRect();orbitPointers.set(e.pointerId,[e.clientX,e.clientY]);if(orbitPointers.size===2){orbit.cancel();const [a,b]=[...orbitPointers.values()];pinchStart={distance:Math.hypot(a[0]-b[0],a[1]-b[1]),zoom:orbit.zoom};}else orbit.begin(e.pointerId,e.clientX,e.clientY,r.width,r.height);e.preventDefault();e.stopPropagation();surface.setPointerCapture?.(e.pointerId);surface.focus?.({preventScroll:true});};
  const orbitMove=e=>{if(!orbitEnabled||!orbitPointers.has(e.pointerId))return;orbitPointers.set(e.pointerId,[e.clientX,e.clientY]);let moved=false;if(orbitPointers.size===2&&pinchStart?.distance>0){const [a,b]=[...orbitPointers.values()];moved=orbit.setZoom(pinchStart.zoom*Math.hypot(a[0]-b[0],a[1]-b[1])/pinchStart.distance);}else moved=orbit.move(e.pointerId,e.clientX,e.clientY);if(moved){e.preventDefault();e.stopPropagation();refreshOrbit();}};
  const orbitEnd=e=>{orbitPointers.delete(e.pointerId);pinchStart=null;orbit.end(e.pointerId);const surface=e.currentTarget||canvas;if(surface.hasPointerCapture?.(e.pointerId))surface.releasePointerCapture?.(e.pointerId);};
  const orbitKey=e=>{if(orbitEnabled&&orbit.key(e.key)){parkingView.interact();e.preventDefault();e.stopPropagation();refreshOrbit();}};
  const orbitClick=e=>{if(orbitEnabled)e.stopPropagation();};
  const orbitWheel=e=>{if(orbitEnabled){parkingView.interact();e.preventDefault();e.stopPropagation();if(orbit.zoomBy(Math.exp(-Math.max(-120,Math.min(120,e.deltaY))*.003)))refreshOrbit();}};
  const orbitEvents={pointerdown:orbitDown,pointermove:orbitMove,pointerup:orbitEnd,pointercancel:orbitEnd,lostpointercapture:orbitEnd,keydown:orbitKey,click:orbitClick,wheel:orbitWheel};
  for(const [name,handler] of Object.entries(orbitEvents))canvas.addEventListener(name,handler,name==='wheel'?{passive:false}:undefined);
  const scene3d=createDrivingScene3D(doc,target,{onChange:refreshOrbit});
  for(const [name,handler] of Object.entries(orbitEvents))scene3d.canvas.addEventListener(name,handler,name==='wheel'?{passive:false}:undefined);
  const viewControls=Object.freeze({reset(){orbit.reset();refreshOrbit();},snapshot:()=>scene3d.snapshot()});target.CarrotVisionView=viewControls;
  let zoomFrame=null,zoomPaintedAt=-Infinity,destroyed=false;
  const stopZoomAnimation=()=>{if(zoomFrame!==null)target.cancelAnimationFrame?.(zoomFrame);zoomFrame=null;};
  const animateZoom=()=>{if(zoomFrame!==null||!target.requestAnimationFrame||destroyed)return;zoomFrame=target.requestAnimationFrame(stamp=>{
    zoomFrame=null;if(destroyed||doc.hidden||!viewActive)return;
    if(stamp-zoomPaintedAt>=40){zoomPaintedAt=stamp;render(data,stale,unit,metricVisible,viewActive);}else animateZoom();
  });};
  const visibility=()=>{if(doc.hidden){parkingPoseActive(false);stopZoomAnimation();perceptionScene.clear();environment.update({active:false});if(remoteGpu)scene3d.pause();}};doc.addEventListener?.('visibilitychange',visibility);
  const editor=el(doc,'div',{class:'tesla-editor'});editor.hidden=true;
  const toggle=el(doc,'button',{class:'tesla-edit',attrs:{type:'button'}});
  let layout=metricLayout(target.CarrotWebSettingsState?.vision_metric_layout),editing=false,dirty=false,saving=false;
  let selected='speed',data={},stale=true,unit='km/h',lastMode=false,metricVisible=true,drag=null,lastSignature='',lastModel=null,lastRadar=null,viewActive=true;
  const labels={speed:'vision_metric_speed',limit:'vision_metric_limit',set:'vision_metric_set'};
  const cards={};
  const button=(label,fn,parent=editor)=>{const b=el(doc,'button',{attrs:{type:'button'},text:label});b.addEventListener('click',e=>{e.stopPropagation();fn();});parent.appendChild(b);return b;};
  const trackDetails=el(doc,'details');const trackSummary=el(doc,'summary',{text:text('tracking_details','追蹤診斷')});
  const trackText=el(doc,'pre');trackText.style.whiteSpace='pre-wrap';trackDetails.append(trackSummary,trackText);editor.appendChild(trackDetails);
  let trackReportAt=-Infinity;
  const selector=el(doc,'select',{attrs:{'aria-label':text('vision_metric_select','Select information')}});
  for(const key of Object.keys(labels)){selector.appendChild(el(doc,'option',{attrs:{value:key},text:text(labels[key],key)}));}
  selector.addEventListener('change',()=>{selected=selector.value;size.value=String(layout[selected][2]);});
  editor.appendChild(selector);
  const sizeLabel=el(doc,'label',{text:text('vision_metric_size','Size')});
  const size=el(doc,'input',{attrs:{type:'range',min:'.6',max:'2.2',step:'.1','aria-label':text('vision_metric_size','Size')}});
  size.addEventListener('input',()=>{layout[selected][2]=Number(size.value);dirty=true;place();});sizeLabel.appendChild(size);editor.appendChild(sizeLabel);
  const save=button(text('vision_metric_save','Save'),async()=>{
    if(saving||!canEditMetrics(target,now()))return;
    saving=true;save.disabled=true;
    try{await target.setWebSettingByKey('vision_metric_layout',JSON.stringify(layout));dirty=false;editing=false;editor.hidden=true;}
    catch{target.showAppToast?.(text('vision_live_save_failed','Could not save'),{tone:'error'});}
    finally{saving=false;save.disabled=false;render(data,stale,unit);}
  });
  button(text('vision_metric_reset','Reset layout'),()=>{layout=metricLayout(null);dirty=true;size.value=String(layout[selected][2]);place();});
  button(text('cancel','Cancel'),()=>{layout=metricLayout(target.CarrotWebSettingsState?.vision_metric_layout);dirty=false;editing=false;editor.hidden=true;render(data,stale,unit);});
  const now=()=>target.performance?.now?.()??Date.now();
  function place(){
    const w=root.clientWidth||root.parentElement?.clientWidth||1,h=root.clientHeight||root.parentElement?.clientHeight||1;
    for(const [key,card] of Object.entries(cards)){
      const row=layout[key],baseW=card.offsetWidth||96,baseH=card.offsetHeight||78;
      const scale=Math.min(row[2],w/baseW,h/baseH);
      card.style.transform=`scale(${scale})`;
      card.style.left=`${row[0]*Math.max(0,w-baseW*scale)}px`;card.style.top=`${row[1]*Math.max(0,h-baseH*scale)}px`;
    }
  }
  for(const key of Object.keys(labels)){
    const title=el(doc,'small'),value=el(doc,'b'),units=el(doc,'small');
    const card=el(doc,'div',{class:'tesla-metric',attrs:{tabindex:'0','data-metric':key}},[title,value,units]);
    cards[key]=card;card.parts={title,value,units};metrics.appendChild(card);
    card.addEventListener('pointerdown',e=>{
      if(!editing||!canEditMetrics(target,now()))return;
      e.preventDefault();e.stopPropagation();selected=key;selector.value=key;size.value=String(layout[key][2]);
      drag={key,id:e.pointerId,x:e.clientX,y:e.clientY,start:[...layout[key]]};card.setPointerCapture?.(e.pointerId);
    });
    card.addEventListener('pointermove',e=>{
      if(!drag||drag.key!==key||drag.id!==e.pointerId)return;
      if(!canEditMetrics(target,now())){drag=null;return;}
      const r=card.getBoundingClientRect();
      layout[key][0]=Math.max(0,Math.min(1,drag.start[0]+(e.clientX-drag.x)/Math.max(1,root.clientWidth-r.width)));
      layout[key][1]=Math.max(0,Math.min(1,drag.start[1]+(e.clientY-drag.y)/Math.max(1,root.clientHeight-r.height)));
      dirty=true;place();
    });
    const end=()=>{drag=null;};card.addEventListener('pointerup',end);card.addEventListener('pointercancel',end);
    card.addEventListener('keydown',e=>{
      if(!editing||!canEditMetrics(target,now()))return;
      const delta={ArrowLeft:[0,-.02],ArrowRight:[0,.02],ArrowUp:[1,-.02],ArrowDown:[1,.02]}[e.key];
      if(delta){e.preventDefault();layout[key][delta[0]]=Math.max(0,Math.min(1,layout[key][delta[0]]+delta[1]));dirty=true;place();}
    });
  }
  toggle.addEventListener('click',e=>{e.stopPropagation();if(!canEditMetrics(target,now()))return;
    if(editing){layout=metricLayout(target.CarrotWebSettingsState?.vision_metric_layout);dirty=false;}
    editing=!editing;editor.hidden=!editing;size.value=String(layout[selected][2]);render(data,stale,unit);});
  const bev=createBevWorkbench(doc,target,canvas,{canEdit:()=>canEditMetrics(target,now()),refresh:()=>{lastSignature='';render(data,stale,unit);},getHud:()=>({data:{speed:data.speed,setSpeed:data.setSpeed,speedLimit:data.speedLimit,brakeLights:data.brakeLights,leftBlinker:data.leftBlinker,rightBlinker:data.rightBlinker},stale,unit,lampTime:now()})});
  const perception=createObjectPerception(doc,target,{onChange:()=>{lastSignature='';render(data,stale,unit);}});
  const vehicleSkin=createVehicleSkinCache(target,()=>{lastSignature='';render(data,stale,unit);});
  const environment=createObjectPerception(doc,target,{occupancy:true,onChange:()=>{lastSignature='';render(data,stale,unit);}});
  const roadPerception=createObjectPerception(doc,target,{road:true,onChange:()=>{lastSignature='';render(data,stale,unit);}});
  function trackingSnapshot(){
    const usage=target.CarrotHudState?.deviceState, cpu=usage?.cpuUsagePercent?.filter?.(n=>Number.isFinite(n)&&n>=0&&n<=100), mono=target.CarrotStateReceivedAtMonotonic?.deviceState;
    const fresh=Number.isFinite(mono)&&now()-mono>=0&&now()-mono<3000;
    const heap=target.performance?.memory?.usedJSHeapSize;
    return {...perceptionScene.tracker.snapshot(now()),render:{...scene3d.snapshot(),...meter.snapshot(now())},
      heapMiB:Number.isFinite(heap)?heap/1048576:null,cpu:fresh&&Array.isArray(cpu)&&cpu.length&&cpu.every(Number.isFinite)?cpu.reduce((a,b)=>a+b)/cpu.length:null,
      gpu:fresh&&usage?.gpuUsagePercent>=0&&usage.gpuUsagePercent<=100?usage.gpuUsagePercent:null,memory:fresh?usage?.memoryUsagePercent:null};
  }
  const diagnostics=Object.freeze({tracking:trackingSnapshot,
    snapshot(){
      const describe=detector=>{const s=detector.scene(),classes={};
        for(const object of [...s.objects,...s.imageObjects])classes[object.kind]=(classes[object.kind]||0)+1;
        return {status:s.status,count:s.count,positioned:s.objects.length,classes,revision:s.revision,videoTime:s.videoTime??null,
          awaitingResult:s.awaitingResult===true,geometryReason:s.geometryReason??null,frameSize:s.frameSize??null,durationMs:s.durationMs??null,delegate:s.delegate??null};};
      const occ=environment.scene();
      const external=remoteGpu?scene3d.snapshot():null;
      return {objects:describe(perception),road:describe(roadPerception),environment:external?{status:external.status,cells:external.cells,drawn:external.cells,raisedCells:external.raised,backend:external.backend}: {status:occ.status,cells:occ.count,drawn:scene3d.snapshot().environmentCells,
        raisedCells:occ.status==='ready'?occ.raisedCells??0:0,ranges:scene3d.snapshot().environmentRanges,supportedRays:occ.supportedRays??0,visibleEmptyIntervals:occ.status==='ready'?occ.visibleEmpty:0,
        latencyMs:occ.durationMs??null,cellMetres:1,coverage:'front',groundTruth:false}};
    },
    retry(){perception.retry();roadPerception.retry();environment.retry();},
  });
  target.CarrotVisionPerception=diagnostics;
  parkingPanel.append(parkingStatus,parkingButton);
  root.appendChild(volumeLegend);
  const turnCue=el(doc,'output',{class:'cockpit-turn-cue'});
  root.append(turnCue,scene3d.canvas,parkingPanel,notice,perceptionStatus,predictionLegend,imageObservations,metrics,toggle,editor,bev.root);
  function render(next={},isStale=true,units='km/h',visible=metricVisible,active=viewActive){
    data=next||{};stale=isStale;unit=units;metricVisible=visible;viewActive=active;
    const settings=target.CarrotWebSettingsState||{},isBev=visionPresentation(target)==='bev',tesla=['tesla','bev'].includes(visionPresentation(target));
    const custom=settings.vision_custom_metrics===true||tesla;
    if(tesla&&viewActive)vehicleSkin.refresh();
    const rawSkin=(target.CarrotVisionReplay?.isActive?.()||target.CarrotVisionReplay?.status?.()?.active===true)?VEHICLE_SKINS.generic:vehicleSkin.current();
    const skin=paintedVehicle(selectedSkin(rawSkin,settings.vision_vehicle_model),settings.vision_vehicle_color);
    const night=doc.documentElement?.classList.contains('cockpit-night')===true;
    canvas.setAttribute('aria-label',text(isBev?'bev_name':'vision_tesla_name',isBev?'BEV annotation view':'Bird’s-eye view'));
    root.hidden=!custom&&!tesla;canvas.hidden=!tesla;notice.hidden=!tesla;metrics.hidden=!custom||!visible;toggle.hidden=!custom||!visible;
    root.parentElement?.classList.toggle('has-custom-metrics',custom);
    root.parentElement?.classList.toggle('is-tesla-view',tesla);
    root.parentElement?.classList.toggle('is-light-scene',tesla&&!isBev);
    root.classList.toggle('is-light-scene',tesla&&!isBev);
    if(!editing&&!dirty)layout=metricLayout(settings.vision_metric_layout);
    if(editing&&(!visible||!canEditMetrics(target,now()))){editing=false;editor.hidden=true;drag=null;dirty=false;layout=metricLayout(settings.vision_metric_layout);}
    root.classList.toggle('is-editing',editing);toggle.disabled=!canEditMetrics(target,now())||saving;
    setText(toggle,text(editing?'vision_metric_done':'vision_metric_edit',editing?'Finish editing':'Arrange information'));
    perceptionScene.startConfigured(!remoteGpu&&tesla&&viewActive&&!doc.hidden&&!bev.frozen,settings);
    perception.update({active:!remoteGpu&&tesla&&viewActive,frozen:bev.frozen});
    roadPerception.update({active:!remoteGpu&&tesla&&viewActive,frozen:bev.frozen});
    const environmentActive=!remoteGpu&&tesla&&!isBev&&viewActive&&!bev.frozen&&!!target.WebGL2RenderingContext;
    environment.update({active:environmentActive,frozen:bev.frozen});
    const occ=environment.scene();
    const vision=perception.scene(),road=roadPerception.scene(),liveScene=tesla?{...birdScene(target,now()),vision,road}:{};
    const map=research.read(tesla&&!remoteGpu&&viewActive&&!doc.hidden&&!bev.frozen&&target.CarrotVisionReplay?.status?.()?.active!==true,now());
    const nav=target.CarrotHudState?.carrotMan, navAge=now()-target.CarrotStateReceivedAtMonotonic?.carrotMan;
    const cue=tesla && viewActive && !bev.frozen ? navigationCue(nav,navAge) : '';
    turnCue.hidden=!cue;
    if(cue)setText(turnCue,cue);
    if(!tesla)mapCredit.hidden=true;
    if(tesla){liveScene.paint=lanePaint(target,now());liveScene.mapLines=map.lines;}
    const scene={...bev.prepare(liveScene),text};
    scene.environment=environmentActive&&occ.status==='ready'?occ.positions:null;
    volumeLegend.hidden=!environmentActive||settings.vision_environment_occupancy!==true;
    const trackingActive=tesla&&viewActive&&!doc.hidden&&!bev.frozen;
    let tracks=perceptionScene.update(liveScene,now(),trackingActive,target.CarrotVisionReplay?.status?.()?.active===true);
    if(trackingActive && doc.body.dataset.cockpitPanel==='vision'){
      tracks=cockpitTraffic(liveScene.model,liveScene.radar,target.CarrotStateReceivedAtMonotonic||{},now(),tracks,target.CarrotHudState?.carState);
    }
    if(scene.environment){
      scene.environmentMotion=surfaceMotion(perceptionScene.motion,now()-occ.capturedAt);
      if(!scene.environmentMotion)scene.environment=null;
      else scene.environmentRanges=occ.ranges;
    }
    if(!bev.frozen)scene.tracks=tracks;
    if(trackDetails.open&&now()-trackReportAt>500){trackReportAt=now();setText(trackText,trackingReport(trackingSnapshot()));}
    perceptionStatus.hidden=!tesla;
    setText(perceptionStatus,settings.vision_object_detection===true
      ? `${text(`scene_status_${vision.status}`,vision.status)}${vision.status==='ready'?` · ${vision.objects.length} ${text('scene_targets','positioned targets')}`:''}`
      :text('scene_radar_only','Model / radar targets · classes unavailable'));
    if(settings.vision_road_detection===true)perceptionStatus.textContent+=' · '+text('road_detection_short','Road detector')+': '+text('scene_status_'+road.status,road.status);
    if(settings.vision_environment_occupancy===true&&tesla&&!isBev){
      const state=!target.WebGL2RenderingContext?'unsupported':occ.status;
      perceptionStatus.textContent+=' · '+(state==='ready'?text('occupancy_surface','前方推估表面')+' '+occ.count:
        state==='missing'?text('occupancy_missing','車機尚未安裝環境模型'):
        text('vision_environment_occupancy','3D 環境佔用')+' · '+text('scene_status_'+state,state));
    }
    predictionLegend.hidden=!trackingActive||!tracks.some(o=>o.state==='predicted');
    if(!predictionLegend.hidden)setText(predictionLegend,text('tracking_prediction','淡色模型為短暫預測'));
    const imageCounts=new Map();
    const heads=[];
    for(const o of [...(vision.imageObjects||[]),...(road.imageObjects||[])]){
      if(o.kind==='traffic light')heads.push(o);
      else imageCounts.set(o.kind,(imageCounts.get(o.kind)||0)+1);
    }
    heads.sort((a,b)=>a.box[0]-b.box[0]||a.box[1]-b.box[1]);
    imageObservations.hidden=!tesla||(!imageCounts.size&&!heads.length);
    const signals=heads.map(h=>describeSignal(h,text,vision.signalReader));
    const imageKey=JSON.stringify([signals.map(s=>s.label),[...imageCounts].map(([kind,count])=>[kind,count,text('scene_kind_'+kind.replaceAll(' ','_'),kind)])]);
    if(imageKey!==imageSignature){
    imageSignature=imageKey;imageObservations.replaceChildren();
    for(const signal of signals)imageObservations.appendChild(signalBadge(doc,signal));
    for(const [kind,count] of imageCounts){
      const badge=el(doc,'span',{class:'tesla-image-object'});
      badge.dataset.classification=kind;
      badge.dataset.kind=kind==='stop sign'?'stop':kind==='traffic light'?'signal':kind==='crosswalk'?'crosswalk':kind==='traffic cone'?'cone':'object';
      const icon=el(doc,'b',{attrs:{'aria-hidden':'true'},text:kind==='stop sign'?'STOP':kind==='traffic light'?'● ● ●':kind==='crosswalk'?'▥':kind==='traffic cone'?'▲':''});
      const label=el(doc,'span',{text:`${text('scene_kind_'+kind.replaceAll(' ','_'),OBJECT_NAMES[kind]||kind)}${count>1?' ×'+count:''}`});
      badge.append(icon,label);imageObservations.appendChild(badge);
    }
    if(imageCounts.size||heads.length)imageObservations.appendChild(el(doc,'small',{text:text('scene_image_observations','Image observations · no 3D position')}));
    }
    const frozenHud=bev.frozenHud,displayData=frozenHud?.data||data,displayStale=(frozenHud?.stale??stale)||(!frozenHud&&cockpitTelemetryStale(target)),displayUnit=frozenHud?.unit||unit;
    const zoomEnabled=doc.body.dataset.cockpitPanel==='vision'&&!isBev;
    const parkingEnabled=settings.vision_parking_assist===true&&tesla&&!isBev&&!editing&&!bev.frozen&&target.CarrotVisionReplay?.status?.()?.active!==true;
    parkingMap.update(parkingEnabled&&viewActive&&!doc.hidden);
    const lot=parkingMap.scene(),inLot=lot.status==='ready'&&lot.areas.some(a=>a.kind==='parking'&&insidePolygon(lot.position,a.points));
    const speedKph=!displayStale&&Number.isFinite(displayData.vehicleSpeedMps)?displayData.vehicleSpeedMps*3.6:null;
    const parking=parkingView.update({enabled:parkingEnabled,fresh:!displayStale,active:viewActive&&!doc.hidden,speed:speedKph,gear:displayData.vehicleGear,inLot,now:now(),reducedMotion:target.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches===true});
    parkingPoseActive(!remoteGpu&&parking.overhead&&!parking.spin);
    parkingAnimation=parking.spin;
    parkingPanel.hidden=!parkingEnabled;parkingButton.hidden=!parkingEnabled;parkingButton.disabled=displayStale||speedKph===null||speedKph>20;
    parkingButton.textContent=text(parking.overhead?'parking_view_exit':'parking_view',parking.overhead?'Return to driving view':'Parking overhead');
    parkingButton.setAttribute('aria-pressed',String(parking.overhead));
    parkingPerception.update(!remoteGpu&&parkingEnabled&&parking.overhead&&viewActive&&!displayStale&&!doc.hidden);
    const paint=parkingPerception.scene();scene.parking=paint.slots;
    vehicleParking.update(target.__CARROT_BOOTSTRAP__?.vehicleParkingScene===true&&!remoteGpu&&!displayStale&&parking.overhead&&!parking.spin&&displayData.vehicleGear==='P'&&viewActive&&!doc.hidden);
    const vehicleFrame=vehicleParking.sample();
    if(parking.overhead)perceptionStatus.textContent=text('parking_candidates','Possible paint markings · occupancy unknown')+' · '+text('scene_status_'+paint.status,paint.status);
    if(parkingEnabled&&settings.vision_parking_map===true&&lot.status!=='ready')perceptionStatus.textContent+=' · '+text('parking_map_unavailable','Parking map unconfirmed');
    if(!displayStale&&displayData.lightingStateValid!==true)perceptionStatus.textContent+=' · '+text('parking_lights_unknown','Headlamp state unavailable');
    if(!displayStale&&displayData.doorOpen===true)perceptionStatus.textContent+=' · '+text('parking_door_open','Door open');
    parkingStatus.hidden=!parking.overhead&&!parking.spin;
    parkingStatus.textContent=parking.spin?text('parking_spin','Parked · vehicle presentation, not a camera view'):text('parking_candidates','Possible paint markings · occupancy unknown')+' · '+text('scene_status_'+paint.status,paint.status);
    const attitude=!remoteGpu && parking.overhead && !parking.spin && !displayStale ? parkingAttitude(target.CarrotOverlayState,target.CarrotStateReceivedAtMonotonic,now()) : null;
    if(parking.overhead && !parking.spin){
      scene.parkingCue=remoteGpu?null:parkingObservation(scene);
      combineParking(scene,vehicleFrame);
      const cue=scene.parkingCue;
      const details=[];
      if(cue){
        const kind=cue.source==='target'?'target':(cue.shape||'surface');
        const bearing=Math.round(Math.abs(cue.bearing)/5)*5;
        const side=bearing===0?'ahead':cue.bearing<0?'left':'right';
        details.push(text('parking_shape_'+kind,kind)+' · '+text('parking_camera_distance','Camera range')+' '+parkingDistanceText(cue)+' · '+text('parking_'+side,side)+(bearing?' '+bearing+'°':''));
      }
      if(attitude)details.push(text('parking_roll','Body roll')+' '+Math.round(attitude.roll*180/Math.PI)+'°');
      if(!remoteGpu && Number.isFinite(displayData.measuredRoadWheelDeg))details.push(text('parking_wheel_angle','Front wheel angle')+' '+Math.round(displayData.measuredRoadWheelDeg)+'°');
      if(details.length)parkingStatus.textContent=text('parking_forward','Front view')+' · '+details.join(' · ');
      if(vehicleFrame)parkingStatus.textContent+=' · '+text('parking_usb_model','車機 USB eGPU 模型')+(vehicleFrame.slots.length?' · '+text('parking_paint_verified','車機影像覆核車格')+' '+vehicleFrame.slots.length:'');
    }
    if(parking.spin){predictionLegend.hidden=true;scene.tracks=[];scene.model=null;scene.radar=null;scene.vision=null;scene.road=null;scene.parking=[];scene.environment=null;}
    canvas.dataset.parkingView=String(parking.overhead);canvas.dataset.parkingSpin=String(parking.spin);canvas.dataset.parkingCandidates=String(scene.parking.length);canvas.dataset.parkingYaw=String(parking.yaw);canvas.dataset.parkingGear=String(displayData.vehicleGear);canvas.dataset.parkingSpeed=String(speedKph);
    orbitEnabled=zoomEnabled&&viewActive&&!editing&&!bev.frozen;
    if(!orbitEnabled){orbit.cancel();orbitPointers.clear();pinchStart=null;}
    if(!isBev){canvas.style.pointerEvents=orbitEnabled?'auto':'none';canvas.style.touchAction=orbitEnabled?'none':'';}
    canvas.tabIndex=orbitEnabled?0:-1;
    canvas.title=orbitEnabled?text('vision_orbit_hint','Drag to rotate; arrow keys adjust the view; Home resets'):'';
    scene3d.canvas.style.pointerEvents=orbitEnabled?'auto':'none';scene3d.canvas.style.touchAction=orbitEnabled?'none':'';scene3d.canvas.tabIndex=canvas.tabIndex;scene3d.canvas.title=canvas.title;
    if(!tesla||isBev||!viewActive)scene3d.pause();
    const lamps=vehicleLamps(displayData,displayStale,frozenHud?.lampTime??now());
    const drawEgo=(context,project)=>drawCockpitVehicle(context,project,{skin,lamps});
    const zoom=speedZoom.update(sceneSpeedKph(displayData,displayUnit,displayStale),now(),{
      active:zoomEnabled&&viewActive&&!doc.hidden&&!editing&&!bev.frozen,
      source:target.CarrotVisionReplay?.status?.()?.active===true?'replay':'live'});
    canvas.dataset.speedZoom=zoomEnabled?zoom.progress.toFixed(3):'manual';
    canvas.dataset.cameraDistance=zoomEnabled?(zoom.camera.distance/orbit.zoom).toFixed(3):'default';
    canvas.dataset.viewZoom=String(orbit.zoom);canvas.dataset.viewYaw=String(orbit.pose.yaw);canvas.dataset.viewPitch=String(orbit.pose.pitch);
    canvas.dataset.lowBeam=String(lamps.lowBeam??'unknown');canvas.dataset.highBeam=String(lamps.highBeam??'unknown');canvas.dataset.vehicleSkin=skin.id;canvas.dataset.vehiclePaint=skin.paintId;canvas.dataset.brakeLamp=String(lamps.brake);canvas.dataset.leftLamp=String(lamps.left);canvas.dataset.rightLamp=String(lamps.right);
    if(zoom.moving||parkingAnimation||(trackingActive&&perceptionScene.tracker.pending))animateZoom();else stopZoomAnimation();
    for(const [key,card] of Object.entries(cards)){
      const v=displayData[{speed:'speed',set:'setSpeed',limit:'speedLimit'}[key]];
      setText(card.parts.title,text(labels[key],key));setText(card.parts.value,!displayStale&&Number.isFinite(v)?String(v):'—');
      setText(card.parts.units,displayUnit);card.setAttribute('aria-label',`${text(labels[key],key)} ${!displayStale&&Number.isFinite(v)?v:'—'} ${displayUnit}`);
    }
    place();
    if(tesla){
      setText(notice,parking.spin?text('parking_spin','Parked · vehicle presentation; not a camera view'):parking.overhead?text('parking_front_only','Front camera paint estimates · no rear/side coverage'):bev.frozen?text('bev_frozen','Annotation snapshot · not live'):text(scene.model?'scene_live_notice':'vision_tesla_wait',scene.model?'Live observations · front camera / native targets; not 360°':'Waiting for fresh model data'));
      const vw=root.clientWidth||536,vh=root.clientHeight||300;
      const quality=meter.quality(settings.vision_render_quality);
      const {width:w,height:h,factor}=sceneRenderSize(vw,vh,quality,target.devicePixelRatio);
      const stamp=target.CarrotStateReceivedAtMonotonic?.modelV2??target.CarrotStateUpdatedAt?.modelV2;
      const rs=target.CarrotStateReceivedAtMonotonic?.radarState??target.CarrotStateUpdatedAt?.radarState;
      const bounds=root.getBoundingClientRect(),center=bounds.left+bounds.width/2;
      let inset=0;
      if(parking.overhead||parking.spin){
        for(const control of [parkingButton,parkingStatus]){
          if(control.hidden)continue;
          const rect=control.getBoundingClientRect(),guard=Math.min(vw,vh)*.12;
          if(rect.width>0&&rect.left<center+guard&&rect.right>center-guard)inset=Math.max(inset,bounds.bottom-rect.top+8);
        }
      }
      const obstruction=parseFloat(target.getComputedStyle?.(doc.documentElement)?.getPropertyValue('--cockpit-bottom-obstruction'))||0;
      const bottomFraction=Math.min(.40,Math.max(inset,obstruction)/Math.max(1,vh));
      const signature=`${occ.revision}:${occ.status}:${tracks.length?Math.floor(now()/40):0}:${w}:${h}:${skin.id}:${skin.paint}:${night}:${stamp}:${rs}:${!!scene.model}:${!!scene.radar}:${map.revision}:${scene.vision?.revision}:${scene.road?.revision}:${vision.status}:${road.status}:${settings.vision_rainbow_lane}:${isBev}:${bev.range}:${settings.vision_bev_grid}:${settings.vision_bev_details}:${bev.revision}:${zoomEnabled?zoom.progress.toFixed(3):'manual'}:${orbit.pose.yaw}:${orbit.pose.pitch}:${orbit.zoom}:${lamps.brake}:${lamps.left}:${lamps.right}:${lamps.lowBeam}:${lamps.highBeam}:${lamps.tail}:${displayData.measuredRoadWheelDeg}:${parking.overhead}:${parking.vertical}:${bottomFraction}:${parking.yaw}:${paint.revision}:${vehicleFrame?.frame}:${lot.status}:${attitude?.roll}:${attitude?.pitch}`;
      mapCredit.hidden=isBev||!scene.model||!scene.mapLines?.length||parking.overhead||parking.spin;
      const rearPoints=tracks.filter(o=>o.rearRadar);
      const drivingCamera=orbitCamera({...zoom.camera,skinScale:skin.scale},orbit.pose,orbit.zoom);
      if(rearPoints.length)Object.assign(drivingCamera,{rearPoints,roadOverview:true});
      const cameraView=parking.spin?{...drivingCamera,yaw:parking.yaw,pitch:28,distance:9,bottomFraction}:parking.overhead?{...drivingCamera,...PARKING_VIEW,pitch:parking.vertical?82:PARKING_VIEW.pitch,parkingPoints:scene.parking.flatMap(s=>s.corners),bottomFraction}:drivingCamera;
      if(signature!==lastSignature||tesla!==lastMode||lastModel!==scene.model||lastRadar!==scene.radar){const drawStart=now();if(canvas.width!==w)canvas.width=w;if(canvas.height!==h)canvas.height=h;
        const bounds=root.getBoundingClientRect?.(),imageSlots=bounds?[...imageObservations.querySelectorAll('.tesla-image-object')].filter(badge=>badge.dataset.kind!=='signal').map(badge=>{const r=badge.getBoundingClientRect();return {kind:badge.dataset.classification,x:(r.left+r.width/2-bounds.left)*factor,y:(r.top+36-bounds.top)*factor,size:20*factor};}):[];
        const rendered3d=!isBev&&scene3d.render(w,h,scene,{rainbow:settings.vision_rainbow_lane===true,night,skin,lamps,egoMotion:{attitude,speed:speedKph===null?null:speedKph/3.6,reverse:displayData.vehicleGear==='R',steer:displayStale?null:displayData.measuredRoadWheelDeg},view:zoomEnabled||rearPoints.length||parking.overhead||parking.spin?cameraView:null,enabled:viewActive,imageSlots,quality});
        root.classList.toggle('has-webgl-scene',!!rendered3d);
        canvas.hidden=!!rendered3d;
        const ctx=rendered3d?null:canvas.getContext('2d');if(ctx){if(isBev){const projection=bevProjection(w,h,bev.range);drawBirdScene(ctx,w,h,scene,{rainbow:settings.vision_rainbow_lane===true,projection,maxDistance:bev.range,drawEgo});bev.draw(ctx,projection,scene);}else drawDrivingScene(ctx,w,h,scene,{rainbow:settings.vision_rainbow_lane===true,text,night,drawEgo,attitude,steer:displayStale?null:displayData.measuredRoadWheelDeg,camera:zoomEnabled||rearPoints.length||parking.overhead||parking.spin?cameraView:null,lift:!zoomEnabled&&doc.body.dataset.cockpitPanel==='vision'&&vw>740?h*.06:0});}if(rendered3d||ctx){meter.frame(now(),now()-drawStart);vehicleParking.drawn(vehicleFrame,scene);}lastSignature=signature;lastModel=scene.model;lastRadar=scene.radar;}
      else canvas.hidden=root.classList.contains('has-webgl-scene')&&!isBev;
    }
    lastMode=tesla;
  }
  const observer=typeof target.ResizeObserver==='function'?new target.ResizeObserver(()=>{lastSignature='';render(data,stale,unit);}):null;
  observer?.observe(root);
  return {root,canvas,render,destroy(){destroyed=true;viewActive=false;parkingPoseActive(false);perceptionScene.clear();stopZoomAnimation();orbit.cancel();for(const [name,handler] of Object.entries(orbitEvents)){canvas.removeEventListener(name,handler);scene3d.canvas.removeEventListener(name,handler);}scene3d.destroy();if(target.CarrotVisionView===viewControls)delete target.CarrotVisionView;doc.removeEventListener?.('visibilitychange',visibility);if(target.CarrotVisionPerception===diagnostics)delete target.CarrotVisionPerception;perception.destroy();roadPerception.destroy();environment.destroy();vehicleSkin.destroy();bev.destroy();parkingMap.destroy();parkingPerception.destroy();vehicleParking.destroy();observer?.disconnect();canvas.remove();root.remove();}};
}
export const TESLA_VIEW_CSS=`
.tesla-volume-legend{position:absolute;z-index:2;left:50%;top:3px;transform:translateX(-50%);max-width:62%;background:#14232de8;color:#a8e5e5;border-radius:5px;padding:3px 8px;text-align:center;font:12px system-ui;pointer-events:none}
.tesla-view{position:absolute;inset:0;pointer-events:none;z-index:4;color:#fff;font-family:system-ui,sans-serif}.tesla-view[hidden],.tesla-view [hidden]{display:none!important}
.tesla-map-credit{position:absolute;z-index:1;bottom:3px;left:8px;font:11px/1.25 system-ui;color:#b1c5da;background:#24272bd9;border-radius:3px;padding:2px 4px}.tesla-map-credit[hidden]{display:none}
.cockpit-turn-cue:not([hidden]){position:absolute;z-index:3;left:50%;top:4%;transform:translateX(-50%);max-width:44%;padding:.3em .65em;border-radius:.55em;background:#16232de8;color:white;font:600 1rem system-ui;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;pointer-events:none}
.tesla-scene{position:absolute;z-index:0;pointer-events:none;inset:0;width:100%;height:100%;object-fit:fill}.tesla-notice{position:absolute;top:8px;left:150px;right:110px;text-align:center;font-size:12px;background:#171c23b0;border-radius:8px;padding:6px}
.has-webgl-scene .tesla-image-object{display:flex;flex-direction:column;background:#182432e8;color:#e2edf8;min-width:74px;padding:5px 8px;gap:3px;text-align:center}
.has-webgl-scene .tesla-image-object b{visibility:hidden;display:block;width:48px;height:48px;padding:0}
.has-webgl-scene .tesla-image-observations{left:auto;right:16px;top:116px;width:min(320px,34%);gap:6px;justify-content:flex-end}
.tesla-prediction-legend{position:absolute;right:12px;bottom:60px;padding:4px 8px;border-radius:6px;color:white;background:#243241e8;font:12px system-ui;pointer-events:none}
.has-webgl-scene .tesla-image-object[data-kind=object] b{display:none}
.tesla-image-observations .signal-observation,.has-webgl-scene .tesla-image-object.signal-observation{flex-direction:row;align-self:flex-start;min-width:0;gap:.45em;background:#182432ef;color:#e2edf8}
.signal-lamp{font-size:clamp(12px,1.3vw,18px);font-weight:650;white-space:nowrap}
.signal-lamp[data-color=red]{color:#ff989c}.signal-lamp[data-color=yellow]{color:#ffdb73}.signal-lamp[data-color=green]{color:#72e9ab}
.has-webgl-scene .tesla-image-observations small{color:#a7b9ce;text-shadow:0 1px 4px #000}
.tesla-metrics{position:absolute;inset:0}.tesla-metric{position:absolute;box-sizing:border-box;min-width:96px;width:max-content;padding:8px 10px;text-align:center;background:#101924df;border:1px solid #ffffff40;border-radius:12px;transform-origin:0 0;font-variant-numeric:tabular-nums;white-space:nowrap}.tesla-metric small{display:block;font-size:12px;line-height:1.4}.tesla-metric b{display:block;font-size:34px;line-height:1.15}
.tesla-edit,.tesla-editor{position:absolute;right:8px;top:8px;pointer-events:auto;background:#101924ef;border:1px solid #ffffff50;border-radius:10px;padding:8px;color:white;font:13px system-ui}.tesla-edit{top:auto;bottom:8px;min-height:40px}.tesla-editor{top:48px;max-width:calc(100% - 24px);display:flex;flex-wrap:wrap;align-items:center;gap:8px;white-space:normal}.tesla-editor button,.tesla-editor select{min-height:36px;font:inherit;color:white;background:#24364c;border:1px solid #ffffff50;border-radius:6px;padding:6px}.tesla-editor label{display:flex;gap:8px;align-items:center;font-size:12px}.tesla-editor input{max-width:130px}.tesla-view.is-editing .tesla-metric{pointer-events:auto;touch-action:none;cursor:move;outline:2px dashed #65baff}
.chud.has-custom-metrics .chud-speed,.chud.has-custom-metrics .chud-limit,.chud.has-custom-metrics .clive-cluster{display:none!important}.chud.is-tesla-view .clive{z-index:3}.chud.is-tesla-view .tesla-view{z-index:4}.chud.is-tesla-view .clive-state{top:auto;bottom:8px;left:8px}.chud.is-tesla-view .clive-health{top:auto;bottom:54px;left:auto;right:8px}.chud.is-tesla-view .tesla-editor,.chud.is-tesla-view .tesla-edit{pointer-events:auto}.chud.is-tesla-view .clive{pointer-events:none}
 .tesla-perception{position:absolute;left:150px;right:140px;bottom:12px;text-align:center;font-size:11px;color:#b7c9db;white-space:normal;overflow-wrap:anywhere}.is-light-scene .tesla-notice{color:#4e5e6c;background:#ffffffd9}.is-light-scene .tesla-perception{color:#53616f}.is-light-scene .tesla-metric{color:#263440;background:#ffffffeb;border-color:#aab6bf99;box-shadow:0 2px 12px #263b4f10}.is-light-scene .tesla-edit{color:#455564;background:#fffffff0;border-color:#aab6bf}.is-light-scene .tesla-metric b{font-weight:600}
 @media(max-width:600px){.tesla-notice{left:130px;right:8px;font-size:10px;top:56px}.tesla-perception{left:130px;right:8px;bottom:60px;font-size:10px}}
.chud.is-light-scene::before,.chud.is-light-scene::after{display:none}.chud.is-light-scene .clive-state,.chud.is-light-scene .clive-health{background:#ffffffee;color:#53616f;border:1px solid #c8d0d6}.chud.is-light-scene .clive-health[data-state=playing]{display:none}
@media(max-width:600px){.tesla-perception{top:96px;bottom:auto;background:#102030dd;border-radius:6px;padding:5px}.is-light-scene .tesla-perception{background:#ffffffe8}}
.tesla-image-observations{position:absolute;top:52px;left:160px;right:140px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;pointer-events:none}.tesla-image-observations[hidden]{display:none}.tesla-image-object{display:flex;gap:8px;align-items:center;padding:7px 10px;border-radius:7px;background:#ffffffed;color:#354453;font-size:12px;box-shadow:0 2px 8px #0001}.tesla-image-object b{display:block;font-size:12px}.tesla-image-object[data-kind=stop] b{background:#ba343c;color:white;padding:6px 3px;clip-path:polygon(30% 0,70% 0,100% 30%,100% 70%,70% 100%,30% 100%,0 70%,0 30%)}.tesla-image-object[data-kind=signal] b{background:#28323c;color:#87919a;border-radius:5px;font-size:8px;padding:5px;max-width:16px;line-height:1.3}.tesla-image-observations small{width:100%;font-size:10px;text-align:center;color:#596a79}@media(max-width:640px){.tesla-image-observations{left:135px;right:8px;top:90px}.tesla-image-object{font-size:10px}}
 .tesla-parking-panel{position:absolute;left:12px;right:12px;bottom:calc(var(--cockpit-bottom-obstruction,52px) + 12px);z-index:4;display:flex;flex-direction:column;align-items:flex-end;gap:8px;pointer-events:none}
.tesla-parking-view{pointer-events:auto;max-width:100%;padding:10px 14px;border-radius:10px;border:1px solid #8293a6;background:#192b42e8;color:white;font:600 calc(14px * min(var(--carrot-text-scale,1),1.25)) system-ui;min-height:44px}.tesla-parking-view:disabled{opacity:.5}.is-light-scene .tesla-parking-view{background:#ffffffed;color:#263a50}
.tesla-parking-status{max-width:100%;max-height:6em;overflow:auto;pointer-events:auto;padding:7px 9px;border-radius:7px;background:#142238e8;color:#fff;font:calc(13px * min(var(--carrot-text-scale,1),1.25)) system-ui;line-height:1.4;overflow-wrap:anywhere}.is-light-scene .tesla-parking-status{background:#ffffffed;color:#35475a}
@media(max-height:450px) and (min-width:600px){.tesla-parking-panel{flex-direction:row;align-items:center;justify-content:flex-end}.tesla-parking-status{max-width:calc(100% - 170px);margin-right:auto}}
` + BEV_CSS;
