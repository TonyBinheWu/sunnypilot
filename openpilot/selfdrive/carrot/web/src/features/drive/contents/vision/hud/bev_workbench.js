import {el,setText} from './dom.js';
import {bevProjection,bevSnapshot,addHumanLabel,drawBevAnnotations} from './bev_annotations.js';

export function createBevWorkbench(doc,target,canvas,{canEdit,refresh,getHud}) {
  const text=(k,f)=>target.getUIText?.(k,f)||f;
  const root=el(doc,'div',{class:'bev-workbench'}),panel=el(doc,'section',{class:'bev-tools'});
  panel.hidden=true;
  const toggle=el(doc,'button',{class:'bev-toggle',text:text('bev_tools','BEV annotation tools'),attrs:{type:'button','aria-expanded':'false'}});
  toggle.addEventListener('click',()=>{panel.hidden=!panel.hidden;toggle.setAttribute('aria-expanded',String(!panel.hidden));});
  let draft=null,frozen=false,enabled=false,lastScene={},pending=[],revision=0;
  const rangeSelect=el(doc,'select',{attrs:{'aria-label':text('bev_range','Forward range')}});
  for(const n of [30,50,75])rangeSelect.appendChild(el(doc,'option',{attrs:{value:n},text:`${n} m`}));
  const row=(label,control)=>{const node=el(doc,'label',{text:label});node.appendChild(control);panel.appendChild(node);};
  row(text('bev_range','Forward range'),rangeSelect);
  const changeSetting=async(key,value)=>{try{await target.setWebSettingByKey(key,value);revision++;refresh();}
    catch{target.showAppToast?.(text('vision_live_save_failed','Could not save'),{tone:'error'});}};
  rangeSelect.addEventListener('change',()=>{void changeSetting('vision_bev_range',rangeSelect.value);});
  for(const [key,label] of [['vision_bev_grid','bev_grid'],['vision_bev_details','bev_details']]){
    const input=el(doc,'input',{attrs:{type:'checkbox'}});input.dataset.bevSetting=key;
    input.addEventListener('change',()=>{void changeSetting(key,input.checked);});row(text(label,label),input);
  }
  const status=el(doc,'p',{attrs:{role:'status'}}),help=el(doc,'p',{text:text('bev_help','Freeze while parked or in replay. Click to add an unverified human point; lane correction requires at least two points. Drafts are temporary; export before closing. No model training or vehicle control is performed.')});
  const button=(key,fallback,fn)=>{const b=el(doc,'button',{attrs:{type:'button'},text:text(key,fallback)});b.addEventListener('click',e=>{e.stopPropagation();void fn();});panel.appendChild(b);return b;};
  const freeze=button('bev_freeze','Freeze snapshot',async()=>{
    if(!canEdit()||(!lastScene.model&&!lastScene.radar))return;
    if(frozen){frozen=false;pending=[];revision++;refresh();return;}
    if(draft?.snapshot.manual.length&&target.appConfirm&&!await target.appConfirm(text('bev_replace','Replace the previous annotation draft? Export it first.')))return;
    const range=Number(target.CarrotWebSettingsState?.vision_bev_range)||50;
    const scene=JSON.parse(JSON.stringify(lastScene));
    draft={scene,snapshot:bevSnapshot(scene,{range,replay:target.CarrotVisionReplay?.status?.()?.active===true,
      sourceTimes:target.CarrotStateReceivedAtMonotonic||{}})};
    draft.hud=getHud?.()||null;
    draft.snapshot.displayHud=draft.hud?{unit:draft.hud.unit,
      speed:draft.hud.stale?null:draft.hud.data.speed,
      roadLimit:draft.hud.stale?null:draft.hud.data.speedLimit,
      cruiseSetSpeed:draft.hud.stale?null:draft.hud.data.setSpeed}:null;
    frozen=true;pending=[];revision++;refresh();
  });
  const restore=button('bev_restore','View last snapshot',()=>{if(draft&&canEdit()){frozen=true;pending=[];revision++;refresh();}});
  const category=el(doc,'select',{attrs:{'aria-label':text('bev_category','Human label category')}});
  for(const key of ['unknown','vehicle','pedestrian','sign','lane_correction'])category.appendChild(el(doc,'option',{attrs:{value:key},text:text(`bev_kind_${key}`,key)}));
  row(text('bev_category','Human label category'),category);
  category.addEventListener('change',()=>{pending=[];revision++;refresh();});
  const finish=button('bev_finish_line','Finish polyline',()=>{
    if(frozen&&canEdit()&&addHumanLabel(draft.snapshot,'lane_correction',pending)){pending=[];revision++;refresh();}
  });
  const undo=button('bev_undo','Undo human label',()=>{if(!frozen||!canEdit())return;
    if(pending.length)pending.pop();else draft.snapshot.manual.pop();revision++;refresh();});
  const urls=new Set();
  const download=(blob,suffix)=>{
    const url=target.URL.createObjectURL(blob);urls.add(url);
    const a=el(doc,'a',{attrs:{href:url,download:`carrot-bev-${draft.snapshot.synchronization.frameId??'unknown'}-${Date.now()}.${suffix}`}});
    doc.body.appendChild(a);a.click();a.remove();
    target.setTimeout(()=>{target.URL.revokeObjectURL(url);urls.delete(url);},30000);
  };
  const jsonButton=button('bev_json','Download JSON (browser)',()=>{
    if(draft&&canEdit())download(new target.Blob([JSON.stringify(draft.snapshot,null,2)],{type:'application/json'}),'json');
  });
  const copyButton=button('bev_copy','View / copy annotation JSON',()=>{
    if(!draft||!canEdit())return;const json=JSON.stringify(draft.snapshot,null,2);
    return target.appAlert?.(json,{title:text('bev_export','BEV annotations · unverified'),copyText:json});
  });
  const pngButton=button('bev_png','Download PNG (browser)',()=>{
    if(!frozen||!canEdit())return;
    canvas.toBlob?.(blob=>{if(blob)download(blob,'png');},'image/png');
  });
  const inventory=el(doc,'p',{class:'bev-inventory'});
  panel.append(status,inventory,help,el(doc,'p',{text:text('bev_export_help','Downloads depend on the browser. In an APK without download support, use View / copy JSON or open the page in an external browser.')}));
  root.append(toggle,panel);
  const onPoint=event=>{
    if(!enabled||!frozen||!canEdit())return;
    event.preventDefault();event.stopPropagation();
    const r=canvas.getBoundingClientRect(),projection=bevProjection(canvas.width,canvas.height,draft.snapshot.rangeM);
    const point=projection.unproject((event.clientX-r.left)*canvas.width/r.width,(event.clientY-r.top)*canvas.height/r.height)
      .map(n=>Math.round(n*100)/100);
    if(point[0]<0||point[0]>draft.snapshot.rangeM||Math.abs(point[1])>100)return;
    if(category.value==='lane_correction'){if(pending.length<64)pending.push(point);}
    else if(!addHumanLabel(draft.snapshot,category.value,[point]))target.showAppToast?.(text('bev_limit','At most 64 human labels per snapshot.'));
    revision++;refresh();
  };
  canvas.addEventListener('pointerdown',onPoint);
  return {root,
    get revision(){return revision;},
    prepare(scene){
      lastScene=scene;enabled=target.CarrotWebSettingsState?.vision_presentation==='bev';root.hidden=!enabled;
      if(frozen&&!canEdit()){frozen=false;pending=[];revision++;}
      if(!enabled){canvas.style.pointerEvents='none';canvas.style.touchAction='auto';return scene;}
      canvas.style.pointerEvents=frozen?'auto':'none';canvas.style.touchAction=frozen?'none':'auto';
      const range=frozen?draft.snapshot.rangeM:Number(target.CarrotWebSettingsState?.vision_bev_range)||50;
      rangeSelect.value=String(range);rangeSelect.disabled=frozen;
      for(const input of panel.querySelectorAll('[data-bev-setting]'))input.checked=target.CarrotWebSettingsState?.[input.dataset.bevSetting]!==false;
      freeze.disabled=!canEdit()||(!lastScene.model&&!lastScene.radar&&!frozen);
      setText(freeze,text(frozen?'bev_resume':'bev_freeze',frozen?'Resume live / replay':'Freeze snapshot'));
      restore.disabled=!draft||frozen||!canEdit();category.disabled=!frozen||!canEdit();
      finish.disabled=!frozen||pending.length<2||!canEdit();undo.disabled=!frozen||(!pending.length&&!draft?.snapshot.manual.length)||!canEdit();
      jsonButton.disabled=copyButton.disabled=!draft||!canEdit();pngButton.disabled=!frozen||!canEdit();
      setText(status,frozen?`${text('bev_frozen','Annotation snapshot · not live')} · ${draft.snapshot.capturedAt} · ${text('bev_human','Human · unverified')}: ${draft.snapshot.manual.length}/64`:
        text(draft?'bev_last_kept':target.CarrotVisionReplay?.status?.()?.active===true?'bev_replay':'bev_live',draft?'Last snapshot retained for export; display has resumed.':target.CarrotVisionReplay?.status?.()?.active===true?'Replay model-assisted annotations · unverified':'Live model-assisted annotations · unverified'));
      const displayed=frozen?draft.scene:scene;
      const leads=['leadOne','leadTwo'].filter(slot=>displayed.radar?.[slot]?.status===true).map(slot=>({id:slot,radarUsed:displayed.radar[slot].radar}));
      setText(inventory,`${text('bev_sources','Model / native lead data; no exact cross-sensor registration')}\n${leads.map(o=>`${o.id}: ${o.radarUsed===true?'radarUsed=true':o.radarUsed===false?'radarUsed=false':'radarUsed=—'}`).join(' · ')}`);
      return displayed;
    },
    get range(){return frozen?draft.snapshot.rangeM:Number(target.CarrotWebSettingsState?.vision_bev_range)||50;},
    get frozen(){return enabled&&frozen;},
    get frozenHud(){return enabled&&frozen?draft.hud:null;},
    draw(ctx,projection,scene){
      if(!enabled)return;
      const snapshot=frozen?draft.snapshot:bevSnapshot(scene,{range:projection.range});
      drawBevAnnotations(ctx,projection,[...snapshot.objects,...(frozen?snapshot.manual:[])],{
        grid:target.CarrotWebSettingsState?.vision_bev_grid!==false,details:target.CarrotWebSettingsState?.vision_bev_details!==false,text});
      if(pending.length)drawBevAnnotations(ctx,projection,[{id:'draft',kind:'lane_correction',geometry:{type:pending.length===1?'Point':'LineString',coordinates:pending.length===1?pending[0]:pending},provenance:'human_unverified'}],{grid:false,text});
      ctx.fillStyle='#111b2bef';ctx.fillRect(0,projection.height-18,projection.width,18);ctx.fillStyle='#d5dfeb';ctx.font='11px system-ui';
      ctx.fillText(text('bev_footer','x forward / y right · model-assisted, not ground truth'),5,projection.height-16,projection.width-10);
    },
    destroy(){canvas.removeEventListener('pointerdown',onPoint);for(const url of urls)target.URL.revokeObjectURL(url);urls.clear();root.remove();}
  };
}
export const BEV_CSS=`
.bev-workbench{position:absolute;inset:0;pointer-events:none;z-index:5}.bev-workbench[hidden],.bev-workbench [hidden]{display:none!important}
.bev-toggle{position:absolute;right:8px;top:56px;pointer-events:auto;min-height:40px;background:#132337f0;border:1px solid #ffffff50;border-radius:10px;color:#bfe6ff;padding:8px;font:13px system-ui}
.bev-tools{position:absolute;right:8px;top:104px;max-height:calc(100% - 164px);overflow:auto;width:min(320px,calc(100% - 24px));box-sizing:border-box;background:#101a29f5;color:#e4efff;border:1px solid #ffffff50;border-radius:12px;padding:12px;pointer-events:auto;font:13px/1.5 system-ui;white-space:normal}
.bev-tools label{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:6px 0}.bev-tools button,.bev-tools select{color:white;background:#243951;border:1px solid #7e98b2;border-radius:8px;padding:7px;min-height:36px;font:inherit;margin:3px}.bev-tools button:disabled{opacity:.45}.bev-tools p{white-space:pre-line;overflow-wrap:anywhere;font-size:12px}.bev-inventory{color:#9dd9e9}
`;
