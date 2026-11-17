import {drawCockpitVehicle,createVehicleSkinCache,VEHICLE_SKINS} from '../../../../cockpit/vehicle.js';
import {OBJECT_NAMES} from './object_classes.js';
import {visionPresentation,cockpitTelemetryStale} from '../../../../cockpit/presentation.js';
import {bevProjection} from "./bev_annotations.js";
import {createBevWorkbench,BEV_CSS} from "./bev_workbench.js";
import {el, setText} from './dom.js';
import {surroundingTargets} from './scene_objects.js';
import {drawDrivingScene,drawSceneObject} from './driving_scene.js';
import {createObjectPerception} from './object_perception.js';

export const METRIC_DEFAULTS = Object.freeze({speed:[.04,.04,1.2],limit:[.04,.43,1],set:[.04,.80,1]});
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
  return {model:!parked&&serviceFresh(target,'modelV2',now,replay)?state.modelV2:null,
    radar:!parked&&serviceFresh(target,'radarState',now,replay)?state.radarState:null};
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
  const line=(path,color,width)=>{
    if(!Array.isArray(path?.x)||!Array.isArray(path?.y))return;
    ctx.beginPath();let started=false;
    for(let i=0;i<Math.min(path.x.length,path.y.length);i++){
      const x=path.x[i],y=path.y[i];if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>maxDistance||Math.abs(y)>100){started=false;continue;}
      const p=px(x,y);if(!started){ctx.moveTo(...p);started=true;}else ctx.lineTo(...p);
    }
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();
  };
  if(model){
    (model.roadEdges||[]).slice(0,2).forEach(p=>line(p,'#5e6671',3));
    (model.laneLines||[]).slice(0,4).forEach((p,i)=>{if((model.laneLineProbs?.[i]??0)>.3)line(p,'#c2cad4',2);});
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
  for(const object of surroundingTargets(scene.radar,maxDistance))drawSceneObject(ctx,flatProject,object,{flat:true});
  for(const object of [...(scene.vision?.objects||[]),...(scene.road?.objects||[])])if(object.x<=maxDistance)drawSceneObject(ctx,flatProject,object,{flat:true,text:scene.text});
  if(drawEgo)drawEgo(ctx,(x,y)=>px(x,y));else vehicle(0,0,'#397fdf',true);
}

export function createTeslaView(doc,target) {
  const text=(key,fallback)=>target.getUIText?.(key,fallback)||fallback;
  const root=el(doc,'div',{class:'tesla-view'});
  const canvas=el(doc,'canvas',{class:'tesla-scene',attrs:{'aria-label':text('vision_tesla_name','Bird’s-eye view')}});
  const notice=el(doc,'div',{class:'tesla-notice'});
  const perceptionStatus=el(doc,'div',{class:'tesla-perception',attrs:{role:'status'}});
  const metrics=el(doc,'div',{class:'tesla-metrics'});
  const imageObservations=el(doc,'div',{class:'tesla-image-observations',attrs:{role:'status'}});
  let imageSignature=null;
  const editor=el(doc,'div',{class:'tesla-editor'});editor.hidden=true;
  const toggle=el(doc,'button',{class:'tesla-edit',attrs:{type:'button'}});
  let layout=metricLayout(target.CarrotWebSettingsState?.vision_metric_layout),editing=false,dirty=false,saving=false;
  let selected='speed',data={},stale=true,unit='km/h',lastMode=false,metricVisible=true,drag=null,lastSignature='',lastModel=null,lastRadar=null,viewActive=true;
  const labels={speed:'vision_metric_speed',limit:'vision_metric_limit',set:'vision_metric_set'};
  const cards={};
  const button=(label,fn,parent=editor)=>{const b=el(doc,'button',{attrs:{type:'button'},text:label});b.addEventListener('click',e=>{e.stopPropagation();fn();});parent.appendChild(b);return b;};
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
  const bev=createBevWorkbench(doc,target,canvas,{canEdit:()=>canEditMetrics(target,now()),refresh:()=>{lastSignature='';render(data,stale,unit);},getHud:()=>({data:{speed:data.speed,setSpeed:data.setSpeed,speedLimit:data.speedLimit},stale,unit})});
  const perception=createObjectPerception(doc,target,{onChange:()=>{lastSignature='';render(data,stale,unit);}});
  const vehicleSkin=createVehicleSkinCache(target,()=>{lastSignature='';render(data,stale,unit);});
  const roadPerception=createObjectPerception(doc,target,{road:true,onChange:()=>{lastSignature='';render(data,stale,unit);}});
  const diagnostics=Object.freeze({
    snapshot(){
      const describe=detector=>{const s=detector.scene();return {status:s.status,count:s.count,positioned:s.objects.length};};
      return {objects:describe(perception),road:describe(roadPerception)};
    },
    retry(){perception.retry();roadPerception.retry();},
  });
  target.CarrotVisionPerception=diagnostics;
  root.append(notice,perceptionStatus,imageObservations,metrics,toggle,editor,bev.root);
  function render(next={},isStale=true,units='km/h',visible=metricVisible,active=viewActive){
    data=next||{};stale=isStale;unit=units;metricVisible=visible;viewActive=active;
    const settings=target.CarrotWebSettingsState||{},isBev=visionPresentation(target)==='bev',tesla=['tesla','bev'].includes(visionPresentation(target));
    const custom=settings.vision_custom_metrics===true||tesla;
    if(tesla&&viewActive)vehicleSkin.refresh();
    const skin=(target.CarrotVisionReplay?.isActive?.()||target.CarrotVisionReplay?.status?.()?.active===true)?VEHICLE_SKINS.generic:vehicleSkin.current(),drawEgo=(context,project)=>drawCockpitVehicle(context,project,{skin});
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
    perception.update({active:tesla&&viewActive,frozen:bev.frozen});
    roadPerception.update({active:tesla&&viewActive,frozen:bev.frozen});
    const vision=perception.scene(),road=roadPerception.scene(),liveScene=tesla?{...birdScene(target,now()),vision,road}:{};
    const scene=bev.prepare(liveScene);scene.text=text;
    perceptionStatus.hidden=!tesla;
    setText(perceptionStatus,settings.vision_object_detection===true
      ? `${text(`scene_status_${vision.status}`,vision.status)}${vision.status==='ready'?` · ${vision.objects.length} ${text('scene_targets','positioned targets')}`:''}`
      :text('scene_radar_only','Model / radar targets · classes unavailable'));
    if(settings.vision_road_detection===true)perceptionStatus.textContent+=' · '+text('road_detection_short','Road detector')+': '+text('scene_status_'+road.status,road.status);
    const imageCounts=new Map();
    for(const o of [...(vision.imageObjects||[]),...(road.imageObjects||[])])imageCounts.set(o.kind,(imageCounts.get(o.kind)||0)+1);
    imageObservations.hidden=!tesla||imageCounts.size===0;
    const imageKey=[...imageCounts].map(([kind,count])=>`${kind}:${count}:${text('scene_kind_'+kind.replaceAll(' ','_'),kind)}`).join('|');
    if(imageKey!==imageSignature){
    imageSignature=imageKey;imageObservations.replaceChildren();
    for(const [kind,count] of imageCounts){
      const badge=el(doc,'span',{class:'tesla-image-object'});
      badge.dataset.kind=kind==='stop sign'?'stop':kind==='traffic light'?'signal':kind==='crosswalk'?'crosswalk':kind==='traffic cone'?'cone':'bird';
      const icon=el(doc,'b',{attrs:{'aria-hidden':'true'},text:kind==='stop sign'?'STOP':kind==='traffic light'?'● ● ●':kind==='crosswalk'?'▥':kind==='traffic cone'?'▲':'◈'});
      const label=el(doc,'span',{text:`${text('scene_kind_'+kind.replaceAll(' ','_'),OBJECT_NAMES[kind]||kind)}${count>1?' ×'+count:''}`});
      badge.append(icon,label);imageObservations.appendChild(badge);
    }
    if(imageCounts.size)imageObservations.appendChild(el(doc,'small',{text:text('scene_image_observations','Image observations · no 3D position')}));
    }
    const frozenHud=bev.frozenHud,displayData=frozenHud?.data||data,displayStale=(frozenHud?.stale??stale)||(!frozenHud&&cockpitTelemetryStale(target)),displayUnit=frozenHud?.unit||unit;
    for(const [key,card] of Object.entries(cards)){
      const v=displayData[{speed:'speed',set:'setSpeed',limit:'speedLimit'}[key]];
      setText(card.parts.title,text(labels[key],key));setText(card.parts.value,!displayStale&&Number.isFinite(v)?String(v):'—');
      setText(card.parts.units,displayUnit);card.setAttribute('aria-label',`${text(labels[key],key)} ${!displayStale&&Number.isFinite(v)?v:'—'} ${displayUnit}`);
    }
    place();
    if(tesla){
      setText(notice,bev.frozen?text('bev_frozen','Annotation snapshot · not live'):text(scene.model?'scene_live_notice':'vision_tesla_wait',scene.model?'Live observations · front camera / native targets; not 360°':'Waiting for fresh model data'));
      const vw=root.clientWidth||536,vh=root.clientHeight||300;
      const quality=settings.vision_render_quality,cap=quality==='high'?[1920,1080,2]:quality==='low'?[480,270,1]:[960,540,1];
      const factor=Math.min(cap[2],cap[0]/vw,cap[1]/vh);
      const w=Math.max(1,Math.round(vw*factor)),h=Math.max(1,Math.round(vh*factor));
      const stamp=target.CarrotStateReceivedAtMonotonic?.modelV2??target.CarrotStateUpdatedAt?.modelV2;
      const rs=target.CarrotStateReceivedAtMonotonic?.radarState??target.CarrotStateUpdatedAt?.radarState;
      const signature=`${w}:${h}:${skin.id}:${night}:${stamp}:${rs}:${!!scene.model}:${!!scene.radar}:${scene.vision?.revision}:${scene.road?.revision}:${vision.status}:${road.status}:${settings.vision_rainbow_lane}:${isBev}:${bev.range}:${settings.vision_bev_grid}:${settings.vision_bev_details}:${bev.revision}`;
      if(signature!==lastSignature||tesla!==lastMode||lastModel!==scene.model||lastRadar!==scene.radar){if(canvas.width!==w)canvas.width=w;if(canvas.height!==h)canvas.height=h;
        const ctx=canvas.getContext('2d');if(ctx){if(isBev){const projection=bevProjection(w,h,bev.range);drawBirdScene(ctx,w,h,scene,{rainbow:settings.vision_rainbow_lane===true,projection,maxDistance:bev.range,drawEgo});bev.draw(ctx,projection,scene);}else drawDrivingScene(ctx,w,h,scene,{rainbow:settings.vision_rainbow_lane===true,text,night,drawEgo,lift:doc.body.dataset.cockpitPanel==='vision'&&vw>740?h*.06:0});}lastSignature=signature;lastModel=scene.model;lastRadar=scene.radar;}
    }
    lastMode=tesla;
  }
  const observer=typeof target.ResizeObserver==='function'?new target.ResizeObserver(()=>{lastSignature='';render(data,stale,unit);}):null;
  observer?.observe(root);
  return {root,canvas,render,destroy(){viewActive=false;if(target.CarrotVisionPerception===diagnostics)delete target.CarrotVisionPerception;perception.destroy();roadPerception.destroy();vehicleSkin.destroy();bev.destroy();observer?.disconnect();canvas.remove();root.remove();}};
}
export const TESLA_VIEW_CSS=`
.tesla-view{position:absolute;inset:0;pointer-events:none;z-index:4;color:#fff;font-family:system-ui,sans-serif}.tesla-view[hidden],.tesla-view [hidden]{display:none!important}
.tesla-scene{position:absolute;z-index:0;pointer-events:none;inset:0;width:100%;height:100%;object-fit:fill}.tesla-notice{position:absolute;top:8px;left:150px;right:110px;text-align:center;font-size:12px;background:#171c23b0;border-radius:8px;padding:6px}
.tesla-metrics{position:absolute;inset:0}.tesla-metric{position:absolute;box-sizing:border-box;min-width:96px;width:max-content;padding:8px 10px;text-align:center;background:#101924df;border:1px solid #ffffff40;border-radius:12px;transform-origin:0 0;font-variant-numeric:tabular-nums;white-space:nowrap}.tesla-metric small{display:block;font-size:12px;line-height:1.4}.tesla-metric b{display:block;font-size:34px;line-height:1.15}
.tesla-edit,.tesla-editor{position:absolute;right:8px;top:8px;pointer-events:auto;background:#101924ef;border:1px solid #ffffff50;border-radius:10px;padding:8px;color:white;font:13px system-ui}.tesla-edit{top:auto;bottom:8px;min-height:40px}.tesla-editor{top:48px;max-width:calc(100% - 24px);display:flex;flex-wrap:wrap;align-items:center;gap:8px;white-space:normal}.tesla-editor button,.tesla-editor select{min-height:36px;font:inherit;color:white;background:#24364c;border:1px solid #ffffff50;border-radius:6px;padding:6px}.tesla-editor label{display:flex;gap:8px;align-items:center;font-size:12px}.tesla-editor input{max-width:130px}.tesla-view.is-editing .tesla-metric{pointer-events:auto;touch-action:none;cursor:move;outline:2px dashed #65baff}
.chud.has-custom-metrics .chud-speed,.chud.has-custom-metrics .chud-limit,.chud.has-custom-metrics .clive-cluster{display:none!important}.chud.is-tesla-view .clive{z-index:3}.chud.is-tesla-view .tesla-view{z-index:4}.chud.is-tesla-view .clive-state{top:auto;bottom:8px;left:8px}.chud.is-tesla-view .clive-health{top:auto;bottom:54px;left:auto;right:8px}.chud.is-tesla-view .tesla-editor,.chud.is-tesla-view .tesla-edit{pointer-events:auto}.chud.is-tesla-view .clive{pointer-events:none}
 .tesla-perception{position:absolute;left:150px;right:140px;bottom:12px;text-align:center;font-size:11px;color:#b7c9db;white-space:normal;overflow-wrap:anywhere}.is-light-scene .tesla-notice{color:#4e5e6c;background:#ffffffd9}.is-light-scene .tesla-perception{color:#53616f}.is-light-scene .tesla-metric{color:#263440;background:#ffffffeb;border-color:#aab6bf99;box-shadow:0 2px 12px #263b4f10}.is-light-scene .tesla-edit{color:#455564;background:#fffffff0;border-color:#aab6bf}.is-light-scene .tesla-metric b{font-weight:600}
 @media(max-width:600px){.tesla-notice{left:130px;right:8px;font-size:10px;top:56px}.tesla-perception{left:130px;right:8px;bottom:60px;font-size:10px}}
.chud.is-light-scene::before,.chud.is-light-scene::after{display:none}.chud.is-light-scene .clive-state,.chud.is-light-scene .clive-health{background:#ffffffee;color:#53616f;border:1px solid #c8d0d6}.chud.is-light-scene .clive-health[data-state=playing]{display:none}
@media(max-width:600px){.tesla-perception{top:96px;bottom:auto;background:#102030dd;border-radius:6px;padding:5px}.is-light-scene .tesla-perception{background:#ffffffe8}}
.tesla-image-observations{position:absolute;top:52px;left:160px;right:140px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap;pointer-events:none}.tesla-image-observations[hidden]{display:none}.tesla-image-object{display:flex;gap:8px;align-items:center;padding:7px 10px;border-radius:7px;background:#ffffffed;color:#354453;font-size:12px;box-shadow:0 2px 8px #0001}.tesla-image-object b{display:block;font-size:12px}.tesla-image-object[data-kind=stop] b{background:#ba343c;color:white;padding:6px 3px;clip-path:polygon(30% 0,70% 0,100% 30%,100% 70%,70% 100%,30% 100%,0 70%,0 30%)}.tesla-image-object[data-kind=signal] b{background:#28323c;color:#87919a;border-radius:5px;font-size:8px;padding:5px;max-width:16px;line-height:1.3}.tesla-image-observations small{width:100%;font-size:10px;text-align:center;color:#596a79}@media(max-width:640px){.tesla-image-observations{left:135px;right:8px;top:90px}.tesla-image-object{font-size:10px}}
` + BEV_CSS;
