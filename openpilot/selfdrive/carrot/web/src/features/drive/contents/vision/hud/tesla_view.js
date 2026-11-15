import {el, setText} from './dom.js';

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
export function drawBirdScene(ctx,w,h,scene,{rainbow=false}={}) {
  ctx.clearRect(0,0,w,h);ctx.fillStyle='#171c23';ctx.fillRect(0,0,w,h);
  const model=scene.model;
  const px=(x,y)=>[w*.5-y*w/22,h*.85-x*h/90];
  const line=(path,color,width)=>{
    if(!Array.isArray(path?.x)||!Array.isArray(path?.y))return;
    ctx.beginPath();let started=false;
    for(let i=0;i<Math.min(path.x.length,path.y.length);i++){
      const x=path.x[i],y=path.y[i];if(!Number.isFinite(x)||!Number.isFinite(y)||x<0||x>75||Math.abs(y)>15)continue;
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
  for(const lead of [scene.radar?.leadOne,scene.radar?.leadTwo]){
    if(lead?.status===true&&Number.isFinite(lead.dRel)&&lead.dRel>0&&lead.dRel<=75&&Number.isFinite(lead.yRel)&&Math.abs(lead.yRel)<12)
      vehicle(lead.dRel,lead.yRel,'#b2bdca');
  }
  vehicle(0,0,'#397fdf',true);
}

export function createTeslaView(doc,target) {
  const text=(key,fallback)=>target.getUIText?.(key,fallback)||fallback;
  const root=el(doc,'div',{class:'tesla-view'});
  const canvas=el(doc,'canvas',{class:'tesla-scene',attrs:{'aria-label':text('vision_tesla_name','Bird’s-eye view')}});
  const notice=el(doc,'div',{class:'tesla-notice'});
  const metrics=el(doc,'div',{class:'tesla-metrics'});
  const editor=el(doc,'div',{class:'tesla-editor'});editor.hidden=true;
  const toggle=el(doc,'button',{class:'tesla-edit',attrs:{type:'button'}});
  let layout=metricLayout(target.CarrotWebSettingsState?.vision_metric_layout),editing=false,dirty=false,saving=false;
  let selected='speed',data={},stale=true,unit='km/h',lastMode=false,metricVisible=true,drag=null,lastSignature='',lastModel=null,lastRadar=null;
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
  root.append(notice,metrics,toggle,editor);
  function render(next={},isStale=true,units='km/h',visible=metricVisible){
    data=next||{};stale=isStale;unit=units;metricVisible=visible;
    const settings=target.CarrotWebSettingsState||{},tesla=settings.vision_presentation==='tesla';
    const custom=settings.vision_custom_metrics===true||tesla;
    root.hidden=!custom&&!tesla;canvas.hidden=!tesla;notice.hidden=!tesla;metrics.hidden=!custom||!visible;toggle.hidden=!custom||!visible;
    root.parentElement?.classList.toggle('has-custom-metrics',custom);
    root.parentElement?.classList.toggle('is-tesla-view',tesla);
    if(!editing&&!dirty)layout=metricLayout(settings.vision_metric_layout);
    if(editing&&(!visible||!canEditMetrics(target,now()))){editing=false;editor.hidden=true;drag=null;dirty=false;layout=metricLayout(settings.vision_metric_layout);}
    root.classList.toggle('is-editing',editing);toggle.disabled=!canEditMetrics(target,now())||saving;
    setText(toggle,text(editing?'vision_metric_done':'vision_metric_edit',editing?'Finish editing':'Arrange information'));
    for(const [key,card] of Object.entries(cards)){
      const v=data[{speed:'speed',set:'setSpeed',limit:'speedLimit'}[key]];
      setText(card.parts.title,text(labels[key],key));setText(card.parts.value,!stale&&Number.isFinite(v)?String(v):'—');
      setText(card.parts.units,unit);card.setAttribute('aria-label',`${text(labels[key],key)} ${!stale&&Number.isFinite(v)?v:'—'} ${unit}`);
    }
    place();
    if(tesla){
      const scene=birdScene(target,now());
      setText(notice,text(scene.model?'vision_tesla_notice':'vision_tesla_wait',scene.model?'Model bird’s-eye view · not a surround camera':'Waiting for fresh model data'));
      const vw=root.clientWidth||536,vh=root.clientHeight||300,factor=Math.min(1,960/vw,540/vh);
      const w=Math.max(1,Math.round(vw*factor)),h=Math.max(1,Math.round(vh*factor));
      const stamp=target.CarrotStateReceivedAtMonotonic?.modelV2??target.CarrotStateUpdatedAt?.modelV2;
      const rs=target.CarrotStateReceivedAtMonotonic?.radarState??target.CarrotStateUpdatedAt?.radarState;
      const signature=`${w}:${h}:${stamp}:${rs}:${!!scene.model}:${!!scene.radar}:${settings.vision_rainbow_lane}`;
      if(signature!==lastSignature||tesla!==lastMode||lastModel!==scene.model||lastRadar!==scene.radar){canvas.width=w;canvas.height=h;
        const ctx=canvas.getContext('2d');if(ctx)drawBirdScene(ctx,w,h,scene,{rainbow:settings.vision_rainbow_lane===true});lastSignature=signature;lastModel=scene.model;lastRadar=scene.radar;}
    }
    lastMode=tesla;
  }
  const observer=typeof target.ResizeObserver==='function'?new target.ResizeObserver(()=>{lastSignature='';render(data,stale,unit);}):null;
  observer?.observe(root);
  return {root,canvas,render,destroy(){observer?.disconnect();canvas.remove();root.remove();}};
}
export const TESLA_VIEW_CSS=`
.tesla-view{position:absolute;inset:0;pointer-events:none;z-index:4;color:#fff;font-family:system-ui,sans-serif}.tesla-view[hidden],.tesla-view [hidden]{display:none!important}
.tesla-scene{position:absolute;z-index:0;pointer-events:none;inset:0;width:100%;height:100%;object-fit:fill}.tesla-notice{position:absolute;top:8px;left:150px;right:110px;text-align:center;font-size:12px;background:#171c23b0;border-radius:8px;padding:6px}
.tesla-metrics{position:absolute;inset:0}.tesla-metric{position:absolute;box-sizing:border-box;min-width:96px;width:max-content;padding:8px 10px;text-align:center;background:#101924df;border:1px solid #ffffff40;border-radius:12px;transform-origin:0 0;font-variant-numeric:tabular-nums;white-space:nowrap}.tesla-metric small{display:block;font-size:12px;line-height:1.4}.tesla-metric b{display:block;font-size:34px;line-height:1.15}
.tesla-edit,.tesla-editor{position:absolute;right:8px;top:8px;pointer-events:auto;background:#101924ef;border:1px solid #ffffff50;border-radius:10px;padding:8px;color:white;font:13px system-ui}.tesla-edit{top:auto;bottom:8px;min-height:40px}.tesla-editor{top:48px;max-width:calc(100% - 24px);display:flex;flex-wrap:wrap;align-items:center;gap:8px;white-space:normal}.tesla-editor button,.tesla-editor select{min-height:36px;font:inherit;color:white;background:#24364c;border:1px solid #ffffff50;border-radius:6px;padding:6px}.tesla-editor label{display:flex;gap:8px;align-items:center;font-size:12px}.tesla-editor input{max-width:130px}.tesla-view.is-editing .tesla-metric{pointer-events:auto;touch-action:none;cursor:move;outline:2px dashed #65baff}
.chud.has-custom-metrics .chud-speed,.chud.has-custom-metrics .chud-limit,.chud.has-custom-metrics .clive-cluster{display:none!important}.chud.is-tesla-view .clive{z-index:3}.chud.is-tesla-view .tesla-view{z-index:4}.chud.is-tesla-view .clive-state{top:auto;bottom:8px;left:8px}.chud.is-tesla-view .clive-health{top:auto;bottom:54px;left:auto;right:8px}.chud.is-tesla-view .tesla-editor,.chud.is-tesla-view .tesla-edit{pointer-events:auto}.chud.is-tesla-view .clive{pointer-events:none}
`;
