import {installCockpitControlLayout} from '../features/cockpit/control_layout.js';
import {nightAppearance,readAppearance,setCockpitTextScale,tireLabels} from '../features/cockpit/appearance.js';
import {drawDrivingScene} from '../features/drive/contents/vision/hud/driving_scene.js';
import {createCockpitState,telemetry,cockpitHudPayload,SERVICES,MODES} from '../features/cockpit/state.js';
import {drawCockpitVehicle,createVehicleSkinCache} from '../features/cockpit/vehicle.js';
import {installCockpitHelp} from '../features/cockpit/embedded.js';
import {installDisplayPreferences} from '../shared/web/display_preferences.js';
installDisplayPreferences(window);
window.addEventListener('storage',event=>{if(event.key==='carrot_web_text_scale')window.CarrotDisplayPreferences.apply();});
const $=id=>document.getElementById(id),state=createCockpitState(),ctx=$('scene').getContext('2d');
const vehicleSkin=createVehicleSkinCache(window);
let paused=false;
let socket=null,retry=null,guard=null,failures=0,transportPhase='connecting',transportReason='',epoch=0,view='vision',primary='vision',busy=false,currentMode=null,coreReady=false,dismissed=false,hudHadData=false;
const core=$('features'),nav=$('navigation'),titles={navigation:'導航地圖',vision:'Carrot Vision',setting:'控制與設定',tools:'工具／診斷',logs:'行車紀錄'};
function status(text){$('panelStatus').textContent=text;$('panelStatus').hidden=!text;}
function coreWindow(){try{return coreReady&&core.contentWindow.location.origin===location.origin?core.contentWindow:null;}catch{return null;}}
function selectCore(next){const w=coreWindow();if(!w||typeof w.showPage!=='function')return false;w.document.body.dataset.cockpitPanel=next;w.showPage(next==='vision'?'carrot':next,false);w.CarrotVisionRaw?.syncDataActivity?.();w.CarrotVisionRaw?.markHudDirty?.();w.dispatchEvent?.(new w.Event('carrot:cockpitpanelchange'));return true;}
function panel(next){
  if(!titles[next])return;if(['navigation','vision'].includes(next))primary=next;view=next;document.body.dataset.panel=next;document.body.classList.remove('scene-full');nav.hidden=next!=='navigation';core.hidden=next==='navigation';$('searchNav').hidden=next!=='navigation';$('visionTools').hidden=next!=='vision';$('panelTitle').textContent=titles[next];$('closePanel').hidden=['navigation','vision'].includes(next);$('miniNav').hidden=next!=='vision';
  if(next!=='navigation')try{nav.contentDocument?.body.classList.remove('search-open');}catch{}
  document.querySelectorAll('[data-panel]').forEach(b=>b.classList.toggle('selected',b.dataset.panel===next));
  if(next!=='navigation')status(selectCore(next)?'':'正在載入現有功能；若持續無法開啟，請更新並重新啟動車機。');else{selectCore('setting');status('');}
}
core.addEventListener('load',()=>{
  coreReady=false;let attempts=0;
  const ready=()=>{try{const w=core.contentWindow;if(w.location.origin!==location.origin)return;
    if(typeof w.showPage!=='function'||!w.document.documentElement.hasAttribute('data-carrot-bootstrapped')){
      if(w.__CARROT_BOOTSTRAP__?.intro?.shouldShow){view='setting';nav.hidden=true;core.hidden=false;$('panelTitle').textContent='首次引導設定';setTimeout(ready,500);return;}
      if(++attempts<40)setTimeout(ready,250);return;
    }
    coreReady=true;installCockpitHelp(w.document);installCockpitControlLayout(w.document,w);selectCore(view==='navigation'?'setting':view);status('');
    if(!w.document.getElementById('cockpitEmbeddedTheme')){
      const link=w.document.createElement('link');link.id='cockpitEmbeddedTheme';link.rel='stylesheet';link.href=$('embeddedStyle').href;w.document.head.append(link);
    }
    if(!w.document.getElementById('cockpitControlsTheme')){const link=w.document.createElement('link');link.id='cockpitControlsTheme';link.rel='stylesheet';link.href=$('controlsStyle').href;w.document.head.append(link);}
    w.document.documentElement.classList.toggle('cockpit-night',document.body.classList.contains('night'));
  }catch{status('無法載入功能面板，請重新連線。');}};ready();
});
nav.addEventListener('load',()=>{try{
  const d=nav.contentDocument;if(nav.contentWindow.location.origin!==location.origin)return;
  const style=d.createElement('style');style.textContent=`:root{color-scheme:light;background:#e8e9eb;color:#252a30}body{background:#e8e9eb}main{padding:0;max-width:none}header{display:none}.layout{display:block}.layout>section:first-child{border:0;border-radius:0;padding:0;background:#e8e9eb}.map-frame{height:calc(100vh - 28px);height:calc(100dvh - 28px);aspect-ratio:auto;background:#e8e9eb}small,.note{color:#68717c}small{font-size:9px;padding:4px}.layout>section:nth-child(2){position:fixed;top:12px;left:12px;right:12px;max-height:calc(100vh - 24px);max-height:calc(100dvh - 24px);overflow:auto;box-shadow:0 6px 28px #0003;background:#fff;border:1px solid #dadde2;color:#252a30;display:none}body.search-open .layout>section:nth-child(2){display:block}input,button{background:#f4f5f6;border-color:#d5d9df;color:#252a30}#map{object-fit:contain}h2{font-size:16px}html.cockpit-night,html.cockpit-night body,html.cockpit-night .map-frame,html.cockpit-night .layout>section:first-child{background:#17191e;color:#e7ebf1}html.cockpit-night .layout>section:nth-child(2){background:#24272d;color:#e7ebf1}html.cockpit-night input,html.cockpit-night button{background:#343943;color:#e7ebf1}html,body,main,.layout{height:100%;min-height:0}.layout>section:first-child{height:100%;display:flex;flex-direction:column;min-height:0}.map-frame{flex:1;min-height:0;height:auto;aspect-ratio:auto}#mapStatus{font-size:12px;line-height:1.6;padding:12px}#mapAttribution{flex:none;font-size:9px;line-height:1.4;padding:3px 5px;overflow-wrap:anywhere;color:#62666d}#mapAttribution a{color:inherit}html.cockpit-night #mapAttribution{color:#b4b6ba}`;d.head.append(style);d.documentElement.classList.toggle('cockpit-night',document.body.classList.contains('night'));
}catch{status('導航頁面無法載入。');}});
$('visionTools').onclick=()=>{const w=coreWindow();if(w)w.document.body.classList.toggle('cockpit-vision-tools');};
$('searchNav').onclick=()=>{try{nav.contentDocument.body.classList.toggle('search-open');nav.contentDocument.getElementById('query').focus();}catch{status('請先等待導航頁載入。');}};
$('appsButton').onclick=()=>$('apps').showModal();
document.querySelectorAll('[data-panel]').forEach(b=>b.onclick=()=>{const next=b.dataset.panel;const fromApps=b.closest?.('#apps');if(fromApps)$('apps').close();panel(!fromApps&&next==='setting'&&view==='setting'?primary:next);});
function expand(){document.body.classList.toggle('scene-full');$('sceneMode').classList.toggle('selected',document.body.classList.contains('scene-full'));}
$('expand').onclick=expand;$('sceneMode').onclick=expand;
let appearance=readAppearance(localStorage),appliedAppearance=null,appliedNight=null;
function applyAppearance(){
  const night=nightAppearance(appearance);if(appearance===appliedAppearance&&night===appliedNight)return;appliedAppearance=appearance;appliedNight=night;document.body.classList.toggle('night',night);
  coreWindow()?.document.documentElement.classList.toggle('cockpit-night',night);
  try{nav.contentDocument.documentElement.classList.toggle('cockpit-night',night);}catch{}
  document.querySelectorAll('[data-appearance]').forEach(b=>{const selected=b.dataset.appearance===appearance;b.classList.toggle('current',selected);b.setAttribute('aria-pressed',String(selected));});
}
function displaySettings(){const scale=Number(coreWindow()?.getWebSettingByKey?.('web_text_scale')||100);document.querySelectorAll('button[data-text-scale]').forEach(b=>{const selected=Number(b.dataset.textScale)===scale;b.classList.toggle('current',selected);b.setAttribute('aria-pressed',String(selected));});$('displayStatus').textContent='';$('displaySettings').showModal();}
$('theme').onclick=displaySettings;$('displayShortcut').onclick=()=>{$('apps').close();displaySettings();};
document.querySelectorAll('[data-appearance]').forEach(b=>b.onclick=()=>{appearance=b.dataset.appearance;try{localStorage.setItem('carrot_cockpit_appearance',appearance);}catch{}applyAppearance();});
let savingDisplay=false;
document.querySelectorAll('button[data-text-scale]').forEach(b=>b.onclick=async()=>{
  if(savingDisplay)return;savingDisplay=true;const buttons=document.querySelectorAll('button[data-text-scale]');buttons.forEach(x=>x.disabled=true);
  try{const saved=await setCockpitTextScale(coreWindow(),window,Number(b.dataset.textScale));buttons.forEach(x=>{const selected=Number(x.dataset.textScale)===saved;x.classList.toggle('current',selected);x.setAttribute('aria-pressed',String(selected));});$('displayStatus').textContent=`已儲存字體比例 ${saved}%`;}
  catch{$('displayStatus').textContent='設定未確認，請等待車機連線後重試；不會自動重送。';}
  finally{savingDisplay=false;buttons.forEach(x=>x.disabled=false);}
});
$('closePanel').onclick=()=>panel(primary);$('miniNav').onclick=()=>panel('navigation');
$('routeOpen').onclick=()=>panel('navigation');$('routeSearch').onclick=()=>{panel('navigation');$('searchNav').onclick();};
$('routeEnd').onclick=()=>{try{const button=nav.contentDocument.getElementById('clear');if(!button||button.disabled)throw Error();button.click();$('routeFeedback').textContent='請查看導航回應；外部導航須在來源 App 結束。';}catch{$('routeFeedback').textContent='導航頁尚未就緒，請先開啟導航。';}};
applyAppearance();
$('fullscreen').onclick=()=>{dismissed=false;if(!document.fullscreenElement)document.documentElement.requestFullscreen?.().catch(()=>{});else document.exitFullscreen?.();};
window.CarrotAndroidVision={sync:()=>!dismissed,exit:()=>{dismissed=true;return true;}};
window.CarrotSelfDiagnostics={open:()=>{panel('tools');return coreWindow()?.CarrotSelfDiagnostics?.open?.();}};
window.CarrotLocalVoice=new Proxy({}, {get(_target,key){
  const api=coreWindow()?.CarrotLocalVoice,fn=api?.[key];if(typeof fn!=='function')return undefined;
  return (...args)=>{if(['findSettings','setValue','setResultValue'].includes(key))panel('setting');return fn.apply(api,args);};
}});
function disconnect(){epoch++;clearTimeout(retry);retry=null;guard?.stop();guard=null;const old=socket;socket=null;if(old){old.onclose=null;old.onerror=null;old.onmessage=null;try{old.close();}catch{}}state.clear();}
function connect(){
  if(paused||document.hidden||socket||retry)return;const token=epoch;transportPhase='connecting';
  let ws;try{ws=new WebSocket(`${location.protocol==='https:'?'wss':'ws'}://${location.host}/ws/compact_state?services=${SERVICES.join(',')}`);}catch{scheduleReconnect('connect-failed');return;}
  socket=ws;ws.binaryType='arraybuffer';const opened=performance.now();
  function lost(reason){if(socket!==ws||token!==epoch)return;disconnect();scheduleReconnect(reason);}
  guard=window.CarrotCompactConnection.watch(ws,lost,{active:()=>socket===ws&&token===epoch&&!paused&&!document.hidden});
  ws.onmessage=e=>{if(socket!==ws||token!==epoch||paused||document.hidden)return;try{
    if(typeof e.data==='string'){const hello=JSON.parse(e.data);if(hello.type==='pong')return;if(hello.mode!=='carrot-state-v1')throw Error('protocol');guard.received();transportPhase='connected';return;}
    if(e.data.byteLength>1024*1024)throw Error('size');
    for(const frame of window.CarrotVisionCompact.decodeFrames(e.data))state.accept(frame);
    guard.received();transportPhase='connected';transportReason='';if(performance.now()-opened>30000)failures=0;
  }catch{lost('format-error');}};
  ws.onerror=()=>lost('network-error');ws.onclose=()=>lost('socket-closed');
}
function scheduleReconnect(reason){
  if(paused||document.hidden||retry)return;transportPhase='retrying';transportReason=reason;failures++;
  const delay=Math.min(15000,1000*2**Math.min(failures-1,4));
  retry=setTimeout(()=>{retry=null;connect();},delay);
}
function reconnect(){disconnect();failures=0;if(!paused&&!document.hidden)connect();}
document.addEventListener('visibilitychange',()=>{disconnect();if(!document.hidden&&!paused)connect();});window.addEventListener('pagehide',disconnect);window.addEventListener('pageshow',()=>{if(!paused)connect();});window.addEventListener('online',reconnect);
$('connection').onclick=()=>{$('connectionDetails').showModal();};
$('retryConnection').onclick=()=>{reconnect();coreWindow()?.CarrotVisionRaw?.reconnect?.();};
function render(){
  if(document.hidden)return;vehicleSkin.refresh();const skin=vehicleSkin.current();$('vehicleSkinStatus').textContent=`本車外觀：${skin.identity||'車型未確認'} · ${skin.name}（示意）`;$('skinLabel').textContent=skin.name+' · 示意外觀';const t=telemetry(state),model=state.get('modelV2'),radar=state.get('radarState');
  const frameWindow=coreWindow();
  if(view==='vision'&&!frameWindow?.CarrotVisionReplay?.isActive?.()&&frameWindow?.CarrotVisionReplay?.status?.()?.active!==true){
    const metric=frameWindow?.CarrotLiveRuntimeState?.runtime?.params?.IsMetric;
    const payload=cockpitHudPayload(state,metric==null?true:Boolean(Number(metric)),frameWindow?.CarrotHudDataBridge);
    if(frameWindow)frameWindow.document.body.dataset.cockpitTelemetryFresh=String(Boolean(payload));
    if(payload){frameWindow?.DriveVisionHudContent?.update?.(payload);hudHadData=true;}
    else if(hudHadData){frameWindow?.DriveVisionHudContent?.update?.({sourceStale:true,isMetric:metric==null?true:Boolean(Number(metric))});hudHadData=false;}
  }
  $('speed').textContent=t.speed??'—';$('limit').textContent=t.limit??'—';$('setSpeed').textContent=t.setSpeed>0&&t.setSpeed<250?t.setSpeed:'—';
  $('gear').textContent=({park:'P',reverse:'R',neutral:'N',drive:'D',sport:'S'})[t.gear]||'—';
  $('assist').textContent=t.latActive===null||t.longActive===null?'控制狀態待確認':`橫向${t.latActive?'啟用':'關閉'} · 縱向${t.longActive?'啟用':'關閉'}`;
  $('visionGear').textContent=$('gear').textContent;$('visionAssist').textContent=$('assist').textContent;
  $('connection').textContent=t.gear?'車機已連線':transportPhase==='retrying'?'正在重新連線':transportPhase==='connecting'?'正在連線':'已連線 · 車況待更新';$('connection').dataset.state=t.gear?'connected':transportPhase;$('connectionSummary').textContent=transportPhase==='retrying'?'連線中斷，會保留目前裝置並自動重試。':t.gear?'車機資料持續更新。':transportPhase==='connecting'?'正在建立車機資料通道。':'通道已連接，等待車機提供新鮮車況。';$('connectionAttempts').textContent=String(failures);$('connectionReason').textContent=({'connect-timeout':'連線建立逾時','heartbeat-timeout':'通道無回應','network-error':'網路連線中斷','socket-closed':'通道已關閉','format-error':'資料格式不符，請更新車機','connect-failed':'無法建立資料通道'})[transportReason]||'—';$('clock').textContent=new Date().toLocaleTimeString('zh-TW',{hour:'2-digit',minute:'2-digit',hour12:false});$('alert').textContent=t.alert;$('alert').hidden=!t.alert;
  $('sceneStatus').textContent=t.parked?'停車車況・車輛為示意繪圖':model?'模型／雷達觀測視覺・非環景實景':'模型資料尚未更新';
  $('lead').textContent=radar?.leadOne?.status&&Number.isFinite(radar.leadOne.dRel)?`前車 ${radar.leadOne.dRel.toFixed(1)} m`:'前車 —';
  const ds=state.get('deviceState'),temps=ds?.cpuTempC?.filter(Number.isFinite)||[];$('temperatures').textContent=temps.length?`車機 ${Math.round(Math.max(...temps))}°C`:'車機 —';$('storage').textContent=Number.isFinite(ds?.freeSpacePercent)?`可用空間 ${Math.round(ds.freeSpacePercent)}%`:'空間 —';
  tireLabels(state.get('carState')).forEach((v,i)=>{$(['tireFl','tireFr','tireRl','tireRr'][i]).textContent=v;});
  try{$('routeName').textContent=nav.contentDocument.getElementById('current')?.textContent||'尚未設定目的地';$('routeEnd').disabled=nav.contentDocument.getElementById('saveCurrent')?.disabled!==false;}catch{$('routeName').textContent='等待導航連線';$('routeEnd').disabled=true;}
  applyAppearance();
  const c=$('scene'),r=c.getBoundingClientRect(),scale=Math.min(devicePixelRatio||1,1.5),w=Math.max(1,Math.round(r.width*scale)),h=Math.max(1,Math.round(r.height*scale));if(c.width!==w||c.height!==h){c.width=w;c.height=h;}ctx.setTransform(scale,0,0,scale,0,0);
  if(t.parked){
    ctx.clearRect(0,0,r.width,r.height);ctx.fillStyle=document.body.classList.contains('night')?'#101114':'#f3f4f5';ctx.fillRect(0,0,r.width,r.height);
    const unit=Math.min(r.width*.17,r.height*.17);
    drawCockpitVehicle(ctx,(x,y,z)=>[r.width*.5+(x*.48+y*.88)*unit,r.height*.66+(-x*.28-y*.16-z)*unit],{view:[-5,8,6],skin});
  }else drawDrivingScene(ctx,r.width,r.height,{model,radar},{night:document.body.classList.contains('night'),lift:view==='vision'?r.height*.24:0,drawEgo:(context,project)=>drawCockpitVehicle(context,project,{skin}),text:(k,f)=>({scene_kind_person:'行人',scene_kind_motorcycle:'機車',scene_kind_bicycle:'自行車',scene_kind_bus:'公車',scene_kind_truck:'貨車'})[k]||f});
}
async function modeRead(){try{const r=await fetch('/api/params_bulk?names=MyDrivingMode,MyDrivingModeAuto',{cache:'no-store'});if(!r.ok)throw Error();const d=await r.json();currentMode=Number(d.values?.MyDrivingMode);document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('current',Number(b.dataset.mode)===currentMode));$('profileStatus').textContent=Number(d.values?.MyDrivingModeAuto)>0?'自動駕駛模式目前開啟，實際模式可能依路況切換。':'選擇後會先確認；此處只在停車 P 檔開放修改。';}catch{$('profileStatus').textContent='無法讀取模式，請確認車機連線。';currentMode=null;}}
let pendingMode=null;
function cancelMode(){pendingMode=null;$('modeConfirm').hidden=true;}
$('modeCancel').onclick=cancelMode;$('profiles').addEventListener('close',cancelMode);
$('profile').onclick=()=>{cancelMode();$('profiles').showModal();void modeRead();};
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{
  if(busy)return;cancelMode();const mode=Number(b.dataset.mode);
  if(!telemetry(state).parked){$('profileStatus').textContent='請在 P 檔、靜止且駕駛輔助未啟用時修改。';return;}
  if(!MODES[mode])return;pendingMode=mode;$('modeQuestion').textContent=`將 Carrot 駕駛模式改為「${MODES[mode]}」？`;$('modeConfirm').hidden=false;
});
$('modeApply').onclick=async()=>{
  const mode=pendingMode;if(busy||!MODES[mode])return;cancelMode();
  if(!telemetry(state).parked){$('profileStatus').textContent='車況已變更，未送出設定。';return;}
  busy=true;document.querySelectorAll('[data-mode]').forEach(x=>x.disabled=true);
  try{const r=await fetch('/api/param_set',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:'MyDrivingMode',value:mode,source:'cockpit'})});if(!r.ok)throw Error();await modeRead();$('profileStatus').textContent=currentMode===mode?`已確認儲存：${MODES[mode]}`:'設定結果不一致，請到控制與設定確認。';}
  catch{$('profileStatus').textContent='結果未確認；不會自動重送，請到控制與設定查看。';}finally{busy=false;document.querySelectorAll('[data-mode]').forEach(x=>x.disabled=false);}
};
window.CarrotCockpit={layoutVersion:4,pause(){paused=true;disconnect();selectCore('setting');},resume(){paused=false;selectCore(view==='navigation'?'setting':view);connect();}};
panel(view);connect();setInterval(()=>{if(!paused)render();},100);render();
