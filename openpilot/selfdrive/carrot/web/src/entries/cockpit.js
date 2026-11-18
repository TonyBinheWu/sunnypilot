import {paintedVehicle,vehiclePaint} from '../features/cockpit/vehicle_paint.js';
import {createCockpitSceneActivity} from '../features/cockpit/scene_activity.js';
import {cockpitPerceptionReport} from '../features/cockpit/perception_status.js';
import {installCockpitControlLayout} from '../features/cockpit/control_layout.js';
import {installCockpitDialogHeaders,closeEmbeddedDialog} from '../features/cockpit/interactions.js';
import {nightAppearance,readAppearance,setCockpitTextScale,tireLabels} from '../features/cockpit/appearance.js';
import {drawDrivingScene} from '../features/drive/contents/vision/hud/driving_scene.js';
import {createCockpitState,telemetry,cockpitHudPayload,SERVICES,MODES} from '../features/cockpit/state.js';
import {drawCockpitVehicle,createVehicleSkinCache} from '../features/cockpit/vehicle.js';
import {cockpitClock,assistStates} from '../features/cockpit/status_display.js';
import {vehicleLamps} from '../features/cockpit/vehicle_lamps.js';
import {installCockpitHelp} from '../features/cockpit/embedded.js';
import {installDisplayPreferences} from '../shared/web/display_preferences.js';
installDisplayPreferences(window);
window.addEventListener('storage',event=>{if(event.key==='carrot_web_text_scale'){window.CarrotDisplayPreferences.apply();syncNavigationTextScale();}});
const $=id=>document.getElementById(id),state=createCockpitState(),ctx=$('scene').getContext('2d');
installCockpitDialogHeaders(document);
const vehicleSkin=createVehicleSkinCache(window);
let paused=false;
const sceneActivity=createCockpitSceneActivity();
let socket=null,retry=null,guard=null,failures=0,transportPhase='connecting',transportReason='',epoch=0,view='vision',primary='vision',busy=false,currentMode=null,coreReady=false,coreFaulted=false,dismissed=false,hudHadData=false;
const core=$('features'),nav=$('navigation'),titles={navigation:'導航地圖',vision:'Carrot Vision',setting:'控制與設定',tools:'工具／診斷',logs:'行車紀錄'};
function syncNavigationTextScale(){try{if(nav.contentWindow.location.origin===location.origin)nav.contentWindow.CarrotDisplayPreferences?.apply({web_text_scale:Number(document.documentElement.dataset.textScale)||100});}catch{}}
function closeNavigationSearch(){try{nav.contentDocument?.body.classList.remove('search-open');nav.contentDocument?.getElementById('query')?.blur?.();}catch{}$('searchNav').textContent='搜尋目的地／最愛';$('searchNav').setAttribute('aria-expanded','false');}
function status(text,retry=false){$('panelStatusText').textContent=text;$('panelStatus').hidden=!text;$('retryPanel').hidden=!retry;}
$('retryPanel').onclick=()=>{const frame=view==='navigation'?nav:core;if(frame===core){coreLoadEpoch++;coreReady=false;coreFaulted=false;}status('正在重新載入功能頁…');frame.src=frame.src;};
function coreFailure(text){coreReady=false;coreFaulted=true;if(view!=='navigation')status(text,true);}
function coreWindow(){try{return coreReady&&core.contentWindow.location.origin===location.origin?core.contentWindow:null;}catch{return null;}}
function selectCore(next){const w=coreWindow();if(!w||typeof w.showPage!=='function')return false;w.document.body.dataset.cockpitPanel=next;w.showPage(next==='vision'?'carrot':next,false);w.CarrotVisionRaw?.syncDataActivity?.();w.CarrotVisionRaw?.markHudDirty?.();w.dispatchEvent?.(new w.Event('carrot:cockpitpanelchange'));return true;}
let appReturn = null;
let soundRequested = false;

function bindAppDialog(shortcut, dialog, open) {
  $(shortcut).onclick = () => {
    appReturn = {shortcut: $(shortcut), dialog: $(dialog), scroll: $('apps').scrollTop};
    $('apps').close();
    open();
  };
}

document.addEventListener('close', event => {
  if (!appReturn || event.target !== appReturn.dialog || event.target.open) return;
  const {shortcut, scroll} = appReturn;
  appReturn = null;
  $('apps').showModal();
  shortcut.focus({preventScroll: true});
  $('apps').scrollTop = scroll;
}, true);

function syncDock() {
  const logs = document.querySelector('.dock [data-panel="logs"]');
  const appsCurrent = view === 'tools' || (view === 'logs' && !logs?.offsetWidth);
  $('appsButton').classList.toggle('selected', appsCurrent);
  $('appsButton').setAttribute('aria-current', appsCurrent ? 'page' : 'false');
  document.querySelectorAll('.dock [data-panel]').forEach(button => {
    button.setAttribute('aria-current', button.dataset.panel === view && button.offsetWidth !== 0 ? 'page' : 'false');
  });
}
window.addEventListener('resize', syncDock);

function panel(next){
  appReturn = null;
  soundRequested = false;
  $('resetView').hidden=next!=='vision';
  if(!titles[next])return;if(['navigation','vision'].includes(next))primary=next;view=next;document.body.dataset.panel=next;document.body.classList.remove('scene-full');nav.hidden=next!=='navigation';core.hidden=next==='navigation';$('searchNav').hidden=next!=='navigation';$('visionTools').hidden=next!=='vision';$('vehicleButton').hidden=next!=='vision';$('panelTitle').textContent=titles[next];$('closePanel').hidden=['navigation','vision'].includes(next);$('miniNav').hidden=next!=='vision';
  if(next!=='navigation')closeNavigationSearch();
  document.querySelectorAll('button[data-panel]').forEach(b=>b.classList.toggle('selected',b.dataset.panel===next));
  $('shellPageName').textContent=next==='vision'?'駕駛視覺':titles[next];
  $('closePanel').textContent=primary==='navigation'?'返回導航':'返回駕駛';
  if(next==='vision'&&document.body.classList.contains('advanced-vision')){$('closePanel').hidden=false;$('closePanel').textContent='收起工具';}
  syncDock();
  if(next!=='navigation')status(selectCore(next)?'':coreFaulted?'功能頁尚未就緒，請確認車機連線後重新載入。':'正在載入現有功能；若持續無法開啟，請更新並重新啟動車機。',coreFaulted);else{selectCore('setting');status('');void navigationView()?.refresh();}
}
let coreLoadEpoch=0;
core.addEventListener('load',()=>{
  sceneActivity.release();coreReady=false;coreFaulted=false;let attempts=0;const token=++coreLoadEpoch;
  const ready=()=>{if(token!==coreLoadEpoch)return;try{const w=core.contentWindow;if(w.location.origin!==location.origin)throw Error('origin');
    if(typeof w.showPage!=='function'||!w.document.documentElement.hasAttribute('data-carrot-bootstrapped')){
      if(w.__CARROT_BOOTSTRAP__?.intro?.shouldShow){if(view!=='setting')panel('setting');$('panelTitle').textContent='首次引導設定';status('');setTimeout(ready,500);return;}
      if(++attempts<40)setTimeout(ready,250);else coreFailure('功能頁尚未就緒。請確認車機連線後重新載入。');return;
    }
    coreReady=true;coreFaulted=false;installCockpitHelp(w.document);installCockpitControlLayout(w.document,w,{onAction:cockpitAction});selectCore(view==='navigation'?'setting':view);status('');
    if (soundRequested && view === 'setting') {
      w.CarrotCockpitControls?.selectSection('sound');
      soundRequested = false;
    }
    const navLink=w.document.querySelector('#toolsPrimaryActions a[href="/navigation"]');
    if(navLink)navLink.onclick=event=>{if(event.button||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();panel('navigation');};
    if(!w.document.getElementById('cockpitEmbeddedTheme')){
      const link=w.document.createElement('link');link.id='cockpitEmbeddedTheme';link.rel='stylesheet';link.href=$('embeddedStyle').href;w.document.head.append(link);
    }
    if(!w.document.getElementById('cockpitControlsTheme')){const link=w.document.createElement('link');link.id='cockpitControlsTheme';link.rel='stylesheet';link.href=$('controlsStyle').href;w.document.head.append(link);}
    w.document.documentElement.classList.toggle('cockpit-night',document.body.classList.contains('night'));
  }catch{coreFailure('無法載入功能面板，請確認車機連線後重試。');}};ready();
});
core.addEventListener('error',()=>coreFailure('功能頁載入失敗，請重新載入。'));
nav.addEventListener('error',()=>status('導航頁載入失敗，請重新載入。',true));
nav.addEventListener('load',()=>{try{
  const d=nav.contentDocument;if(nav.contentWindow.location.origin!==location.origin)return;
  const navStyle=d.createElement('link');navStyle.rel='stylesheet';navStyle.href=$('navigationStyle').href;
  const style=d.createElement('style');style.textContent=`:root{color-scheme:light;background:#e8e9eb;color:#252a30}body{background:#e8e9eb}main{padding:0;max-width:none}header{display:none}.layout{display:block}.layout>section:first-child{border:0;border-radius:0;padding:0;background:#e8e9eb}.map-frame{height:calc(100vh - 28px);height:calc(100dvh - 28px);aspect-ratio:auto;background:#e8e9eb}small,.note{color:#68717c}small{font-size:9px;padding:4px}.layout>section:nth-child(2){position:fixed;top:12px;left:12px;right:12px;max-height:calc(100vh - 24px);max-height:calc(100dvh - 24px);overflow:auto;box-shadow:0 6px 28px #0003;background:#fff;border:1px solid #dadde2;color:#252a30;display:none}body.search-open .layout>section:nth-child(2){display:block}input,button{background:#f4f5f6;border-color:#d5d9df;color:#252a30}#map{object-fit:contain}h2{font-size:16px}html.cockpit-night,html.cockpit-night body,html.cockpit-night .map-frame,html.cockpit-night .layout>section:first-child{background:#17191e;color:#e7ebf1}html.cockpit-night .layout>section:nth-child(2){background:#24272d;color:#e7ebf1}html.cockpit-night input,html.cockpit-night button{background:#343943;color:#e7ebf1}html,body,main,.layout{height:100%;min-height:0}.layout>section:first-child{height:100%;display:flex;flex-direction:column;min-height:0}.map-frame{flex:1;min-height:0;height:auto;aspect-ratio:auto}#mapStatus{font-size:12px;line-height:1.6;padding:12px}#mapAttribution{flex:none;font-size:9px;line-height:1.4;padding:3px 5px;overflow-wrap:anywhere;color:#62666d}#mapAttribution a{color:inherit}html.cockpit-night #mapAttribution{color:#b4b6ba}`;d.head.append(style);d.documentElement.classList.toggle('cockpit-night',document.body.classList.contains('night'));
  d.head.append(navStyle);nav.contentWindow.addEventListener("carrot-navigation-started",()=>{closeNavigationSearch();});
  syncNavigationTextScale();
}catch{status('導航頁面無法載入。',true);}});
function showVehicle(){$('vehicleDetails').showModal();void navigationView()?.refresh();}
if($('vehicleDock'))$('vehicleDock').onclick=showVehicle;
function cockpitAction(action){const handlers={profile:()=>{$('profile').click();},vision:()=>{$('visionTools').click();},vehicle:showVehicle,display:()=>{$('theme').click();},connection:()=>{$('connectionDetails').showModal();},diagnostics:()=>window.CarrotSelfDiagnostics.open()};handlers[action]?.();}
function openSound(){
  panel('setting');
  const controls=coreWindow()?.CarrotCockpitControls;
  if(controls)controls.selectSection('sound');
  else soundRequested=true;
}
$('soundDock').onclick=openSound;$('soundShortcut').onclick=()=>{$('apps').close();openSound();};
$('visionTools').onclick=()=>{$('visionSettingFeedback').textContent='';$('visionSettings').showModal();};
bindAppDialog('visionShortcut','visionSettings',()=>$('visionTools').onclick());
$('vehicleButton').onclick=showVehicle;
$('resetView').onclick=()=>coreWindow()?.CarrotVisionView?.reset();
$('resetViewSetting').onclick=()=>{const api=coreWindow()?.CarrotVisionView;if(!api)return;api.reset();$('visionSettingFeedback').textContent='已將駕駛視覺回到前方。';};
bindAppDialog('vehicleShortcut','vehicleDetails',showVehicle);
bindAppDialog('profileShortcut','profiles',()=>$('profile').onclick());
function advancedVision(open){
  coreWindow()?.document.body.classList.toggle('cockpit-vision-tools',open);document.body.classList.toggle('advanced-vision',open);
  $('closePanel').hidden=!open;$('closePanel').textContent='收起工具';
}
$('advancedVisionTools').onclick=()=>{
  $('visionSettings').close();panel('vision');const w=coreWindow();
  if(w)advancedVision(!document.body.classList.contains('advanced-vision'));
};
$('openBev').onclick=async()=>{
  const w=coreWindow();if(!w)return;const next=w.CarrotWebSettingsState?.vision_presentation==='bev'?'tesla':'bev';
  try{await w.setWebSettingByKey('vision_presentation',next);$('visionSettingFeedback').textContent=next==='bev'?'已切換為俯視視角。':'已切換為道路視角。';}
  catch{$('visionSettingFeedback').textContent='視角設定未確認，請重新查看。';}
};
$('connectVision').onclick=()=>{
  panel('vision');const w=coreWindow(),button=w?.document.getElementById('btnStartVision');
  if(!button||button.disabled){$('visionSettingFeedback').textContent=button?.title||'車機尚未開放鏡頭，請查看工具／診斷。';return;}
  button.click();$('visionSettingFeedback').textContent='已提出鏡頭連線要求，請等待影像狀態更新。';
};
$('visionDiagnosis').onclick=()=>{$('visionSettings').close();window.CarrotSelfDiagnostics.open?.();};
$('retryDetection').onclick=()=>{
  const api=coreWindow()?.CarrotVisionPerception;
  if(!api){$('visionSettingFeedback').textContent='請先等待座艙視覺載入。';return;}
  api.retry();$('visionSettingFeedback').textContent='已重新初始化已啟用的辨識模型；未啟用項目保持關閉。';
};
let savingVision=false;
for(const [id,key] of [['detectionObjects','vision_object_detection'],['detectionRoad','vision_road_detection']])$(id).onchange=async()=>{
  if(savingVision)return;const w=coreWindow(),value=$(id).checked;
  savingVision=true;$('detectionObjects').disabled=true;$('detectionRoad').disabled=true;
  try{if(typeof w?.setWebSettingByKey!=='function')throw Error();await w.setWebSettingByKey(key,value);
    if(w.CarrotWebSettingsState?.[key]!==value)throw Error();
    $('visionSettingFeedback').textContent='辨識開關已儲存；模型狀態請見上方。';
  }catch{$('visionSettingFeedback').textContent='設定未確認，請確認連線後重試；不會自動重送。';}
  finally{savingVision=false;$('detectionObjects').disabled=false;$('detectionRoad').disabled=false;}
};
$('searchNav').onclick=()=>{try{const doc=nav.contentDocument,open=!doc.body.classList.contains('search-open');if(!open){closeNavigationSearch();return;}doc.body.classList.add('search-open');$('searchNav').setAttribute('aria-expanded','true');$('searchNav').textContent='關閉搜尋／最愛';doc.getElementById('query').focus();}catch{status('請先等待導航頁載入。');}};
$('appsButton').onclick=()=>{
  const apps = $('apps');
  apps.showModal();
  apps.scrollTop = 0;
};
document.querySelectorAll('button[data-panel]').forEach(b=>b.onclick=()=>{const next=b.dataset.panel;const fromApps=b.closest?.('#apps');if(fromApps)$('apps').close();panel(!fromApps&&next==='setting'&&view==='setting'?primary:next);});
// Every road-view entry uses the same camera/classification renderer. The old
// parent-only expansion had model/radar data but no classified camera objects.
function expand(){$('apps').close();panel('vision');}
$('expand').onclick=expand;$('sceneMode').onclick=expand;
let appearance=readAppearance(localStorage),appliedAppearance=null,appliedNight=null;
function applyAppearance(){
  const night=nightAppearance(appearance);if(appearance===appliedAppearance&&night===appliedNight)return;appliedAppearance=appearance;appliedNight=night;document.body.classList.toggle('night',night);
  coreWindow()?.document.documentElement.classList.toggle('cockpit-night',night);
  try{nav.contentDocument.documentElement.classList.toggle('cockpit-night',night);}catch{}
  document.querySelectorAll('[data-appearance]').forEach(b=>{const selected=b.dataset.appearance===appearance;b.classList.toggle('current',selected);b.setAttribute('aria-pressed',String(selected));});
}
function displaySettings(){const scale=Number(coreWindow()?.getWebSettingByKey?.('web_text_scale'));document.querySelectorAll('button[data-text-scale]').forEach(b=>{const selected=Number(b.dataset.textScale)===scale;b.classList.toggle('current',selected);b.setAttribute('aria-pressed',String(selected));});$('displayStatus').textContent=Number.isFinite(scale)&&scale>0?`目前字體比例 ${scale}%`:'正在等待車機提供字體設定。';$('displaySettings').showModal();}
$('theme').onclick=displaySettings;bindAppDialog('displayShortcut','displaySettings',displaySettings);
document.querySelectorAll('[data-appearance]').forEach(b=>b.onclick=()=>{appearance=b.dataset.appearance;try{localStorage.setItem('carrot_cockpit_appearance',appearance);}catch{}applyAppearance();});
let savingPaint=false;
$('vehiclePaint').onchange=async()=>{
  const value=vehiclePaint($('vehiclePaint').value),core=coreWindow();if(savingPaint)return;
  if(!core?.setWebSettingByKey){$('vehiclePaintStatus').textContent='正在等待車機連線，請稍後重試';$('vehiclePaint').value=vehiclePaint(core?.getWebSettingByKey?.('vision_vehicle_color'));return;}
  savingPaint=true;$('vehiclePaint').disabled=true;
  try{await core.setWebSettingByKey('vision_vehicle_color',value);if(core.getWebSettingByKey('vision_vehicle_color')!==value)throw Error();$('vehiclePaintStatus').textContent='已儲存車身顏色';}
  catch{$('vehiclePaintStatus').textContent='顏色未確認，請檢查連線後重試';}
  finally{savingPaint=false;$('vehiclePaint').disabled=false;$('vehiclePaint').value=vehiclePaint(core.getWebSettingByKey('vision_vehicle_color'));}
};
let savingDisplay=false;
document.querySelectorAll('button[data-text-scale]').forEach(b=>b.onclick=async()=>{
  if(savingDisplay)return;savingDisplay=true;const buttons=document.querySelectorAll('button[data-text-scale]');buttons.forEach(x=>x.disabled=true);
  try{const saved=await setCockpitTextScale(coreWindow(),window,Number(b.dataset.textScale));syncNavigationTextScale();buttons.forEach(x=>{const selected=Number(x.dataset.textScale)===saved;x.classList.toggle('current',selected);x.setAttribute('aria-pressed',String(selected));});$('displayStatus').textContent=`已儲存字體比例 ${saved}%`;}
  catch{$('displayStatus').textContent='設定未確認，請等待車機連線後重試；不會自動重送。';}
  finally{savingDisplay=false;buttons.forEach(x=>x.disabled=false);}
});
$('closePanel').onclick=()=>{if(view==='vision'&&document.body.classList.contains('advanced-vision'))advancedVision(false);else panel(primary);};$('miniNav').onclick=()=>panel('navigation');
$('routeOpen').onclick=()=>{$('vehicleDetails').close();panel('navigation');};$('routeSearch').onclick=()=>{$('vehicleDetails').close();panel('navigation');$('searchNav').onclick();};
$('routeEnd').onclick=async()=>{const api=navigationView();if(!api){$('routeFeedback').textContent='導航頁尚未就緒，請先開啟導航。';return;}
  if(api.snapshot().busy)return;$('routeFeedback').textContent='正在結束當前導航…';
  try{const result=await api.end();$('routeFeedback').textContent=result.ended?'已結束當前導航；外部導航須在來源 App 結束。':'目前沒有導航目的地。';}
  catch(error){$('routeFeedback').textContent=`未確認結束：${error.message||'請確認連線後重新查看導航狀態。'}`;}
};
// Read the local destination even when the wide-screen map is collapsed.
setInterval(() => {
  if (!paused && !document.hidden && (view === 'vision' || view === 'navigation')) void navigationView()?.refreshIfDue?.();
}, 5000);
function navigationView(){try{return nav.contentWindow.location.origin===location.origin?nav.contentWindow.CarrotNavigationView:null;}catch{return null;}}
applyAppearance();
$('fullscreen').onclick=()=>{$('apps').close();dismissed=false;const failed=()=>status('全螢幕請求未成功，請在 App 或瀏覽器選單開啟。');if(!document.fullscreenElement){if(document.documentElement.requestFullscreen)document.documentElement.requestFullscreen().catch(failed);else failed();}else document.exitFullscreen?.().catch(failed);};
function fullscreenState(){const active=Boolean(document.fullscreenElement),label=active?'離開全螢幕':'全螢幕';$('fullscreenLabel').textContent=label;$('fullscreen').setAttribute('aria-label',label);$('fullscreen').setAttribute('aria-pressed',String(active));}
document.addEventListener('fullscreenchange',fullscreenState);fullscreenState();
window.CarrotAndroidVision={sync:()=>!dismissed,exit:()=>{dismissed=true;return true;}};
window.CarrotSelfDiagnostics={open:()=>{panel('tools');return coreWindow()?.CarrotSelfDiagnostics?.open?.();}};
window.CarrotLocalVoice=new Proxy({}, {get(_target,key){
  const api=coreWindow()?.CarrotLocalVoice,fn=api?.[key];if(typeof fn!=='function')return undefined;
  return (...args)=>{if(['findSettings','setValue','setResultValue'].includes(key))panel('setting');return fn.apply(api,args);};
}});
function disconnect(){sceneActivity.release();epoch++;clearTimeout(retry);retry=null;guard?.stop();guard=null;const old=socket;socket=null;if(old){old.onclose=null;old.onerror=null;old.onmessage=null;try{old.close();}catch{}}state.clear();}
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
  if(document.hidden)return;vehicleSkin.refresh();const skin=paintedVehicle(vehicleSkin.current(),coreWindow()?.getWebSettingByKey?.("vision_vehicle_color"));$('vehicleSkinStatus').textContent=`本車外觀：${skin.identity||'車型未確認'} · ${skin.name}（示意）`;$('skinLabel').textContent=skin.name+' · 示意外觀';if(!savingPaint&&document.activeElement!==$('vehiclePaint'))$('vehiclePaint').value=skin.paintId;const t=telemetry(state),model=state.get('modelV2'),radar=state.get('radarState');
  const frameWindow=coreWindow();
  sceneActivity.sync(frameWindow,view==='vision'&&!document.hidden&&!paused&&!document.body.classList.contains('scene-full'));
  const report=cockpitPerceptionReport(frameWindow);
  if($('visionTools').textContent!=='視覺設定')$('visionTools').textContent='視覺設定';$('visionTools').dataset.attention=String(!report.camera||report.objects.enabled!==true||['load_error','inference_error','unsupported'].includes(report.objects.status));$('visionTools').title=report.summary;$('visionTools').setAttribute('aria-label',`視覺設定：${report.summary}`);$('advancedVisionTools').textContent=document.body.classList.contains('advanced-vision')?'收起進階影像工具':'進階影像工具';
  $('visionDiagnostic').textContent=report.summary;
  const cameraButton=frameWindow?.document.getElementById('btnStartVision');
  const visionState=frameWindow?.CarrotVisionState;
  const cameraProgress=visionState&&!['inactive','unavailable'].includes(visionState.phase)?[visionState.statusText,visionState.detailText].filter(Boolean).join(' · '):'';
  $('visionCameraStatus').textContent=report.camera?'已取得影像；辨識結果仍依下列模型狀態更新。':cameraButton?.disabled?(cameraButton.title||'車機尚未啟用 Carrot Vision，請至工具／診斷確認。'):cameraProgress||'尚未取得前鏡頭影像。請先按「連接前鏡頭」。';
  $('connectVision').disabled=!cameraButton||cameraButton.disabled||report.camera;
  $('connectVision').textContent=report.camera?'影像已連接':'連接前鏡頭';
  $('objectDetectionStatus').textContent=report.objects.text+(report.objects.count?` · 模型回報 ${report.objects.count} 項，其中 ${report.objects.positioned} 項可定位`: '')+(report.objects.classes?`（${report.objects.classes}）`:'');
  $('roadDetectionStatus').textContent=report.road.text+(report.road.count?` · 模型回報 ${report.road.count} 項`: '');
  if(!savingVision){$('detectionObjects').checked=report.objects.enabled===true;$('detectionRoad').checked=report.road.enabled===true;$('detectionObjects').disabled=report.objects.enabled===null;$('detectionRoad').disabled=report.road.enabled===null;}
  $('retryDetection').disabled=!report.objects.enabled&&!report.road.enabled;
  $('openBev').textContent=frameWindow?.CarrotWebSettingsState?.vision_presentation==='bev'?'切回道路視角':'切換俯視視角';
  $('resetView').disabled=!frameWindow?.CarrotVisionView||frameWindow?.CarrotWebSettingsState?.vision_presentation==='bev';$('resetViewSetting').disabled=$('resetView').disabled;
  if(view==='vision'&&!frameWindow?.CarrotVisionReplay?.isActive?.()&&frameWindow?.CarrotVisionReplay?.status?.()?.active!==true){
    const metric=frameWindow?.CarrotLiveRuntimeState?.runtime?.params?.IsMetric;
    const payload=cockpitHudPayload(state,metric==null?true:Boolean(Number(metric)),frameWindow?.CarrotHudDataBridge);
    if(frameWindow){
      const frame=$('features').getBoundingClientRect();let obstruction=0;
      for(const node of [document.querySelector('.dock'),$('workspaceTitle')]){const r=node?.getBoundingClientRect();
        if(r&&r.width&&r.height&&r.right>frame.left&&r.left<frame.right&&r.bottom>frame.top&&r.top<frame.bottom)obstruction=Math.max(obstruction,frame.bottom-r.top);
      }
      frameWindow.document.documentElement?.style?.setProperty('--cockpit-bottom-obstruction',`${Math.max(0,obstruction)}px`);
      // Parent instruments sit above the embedded Vision HUD. Reserve their
      // measured lower edge after font, viewport and panel changes.
      const instruments=$('visionInstruments').getBoundingClientRect();
      const noticeTop=instruments.width&&instruments.height?Math.max(0,instruments.bottom-frame.top+12):0;
      const frameStyle=frameWindow.document.documentElement?.style;
      const noticeValue=`${noticeTop}px`;
      if(frameStyle?.getPropertyValue('--cockpit-lane-notice-top')!==noticeValue)frameStyle?.setProperty('--cockpit-lane-notice-top',noticeValue);
      frameWindow.document.body.dataset.cockpitTelemetryFresh=String(Boolean(payload));
    }
    if(payload){frameWindow?.DriveVisionHudContent?.update?.(payload);hudHadData=true;}
    else if(hudHadData){frameWindow?.DriveVisionHudContent?.update?.({sourceStale:true,isMetric:metric==null?true:Boolean(Number(metric))});hudHadData=false;}
  }
  $('speed').textContent=t.speed??'—';$('limit').textContent=t.limit??'—';$('setSpeed').textContent=t.setSpeed>0&&t.setSpeed<250?t.setSpeed:'—';
  $('gear').textContent=({park:'P',reverse:'R',neutral:'N',drive:'D',sport:'S'})[t.gear]||'—';
  document.body.dataset.parked=String(t.parked);
  const controlLabels=assistStates(t);
  const controlSignature=controlLabels.map(item=>item.state).join(':');
  for(const id of ['assist','visionAssist']){const node=$(id);if(node.dataset.controlSignature===controlSignature)continue;node.dataset.controlSignature=controlSignature;node.replaceChildren(...controlLabels.map(item=>{const span=document.createElement('span');span.className='assist-axis';span.dataset.state=item.state;span.textContent=`${item.axis}：${item.text}`;return span;}));node.setAttribute('aria-label',controlLabels.map(item=>`${item.axis}：${item.text}`).join('；'));}
  $('visionGear').textContent=$('gear').textContent;$('visionSpeed').textContent=$('speed').textContent;$('visionLimit').textContent=$('limit').textContent;$('visionSetSpeed').textContent=$('setSpeed').textContent;$('compactSpeed').textContent=`${t.speed??'—'} km/h · ${$('gear').textContent}`;
  const connection = $('connection');
  const phase = t.gear ? 'connected' : transportPhase === 'connected' ? 'waiting' : transportPhase;
  const message = {connected:'車機已連線', waiting:'已連線 · 車況待更新', retrying:'正在重新連線', connecting:'正在連線'}[phase] || '正在連線';
  if (connection.textContent !== message || connection.dataset.state !== phase) {
    connection.dataset.state = phase;
    connection.textContent = message;
    connection.setAttribute('aria-label', message + '，查看連線狀態');
  }
  $('connectionSummary').textContent=transportPhase==='retrying'?'連線中斷，會保留目前裝置並自動重試。':t.gear?'車機資料持續更新。':transportPhase==='connecting'?'正在建立車機資料通道。':'通道已連接，等待車機提供新鮮車況。';$('connectionAttempts').textContent=String(failures);$('connectionReason').textContent=({'connect-timeout':'連線建立逾時','heartbeat-timeout':'通道無回應','network-error':'網路連線中斷','socket-closed':'通道已關閉','format-error':'資料格式不符，請更新車機','connect-failed':'無法建立資料通道'})[transportReason]||'—';$('driveStatusPill').textContent=t.latActive===null||t.longActive===null?'等待控制狀態':t.latActive&&t.longActive?'輔助駕駛介入中':t.latActive?'橫向控制介入中':t.longActive?'縱向控制介入中':'輔助駕駛未介入';$('driveStatusPill').dataset.active=String(t.latActive===true||t.longActive===true);document.querySelectorAll('[data-gear]').forEach(node=>node.classList.toggle('active',node.dataset.gear===t.gear));$('alert').textContent=t.alert;$('alert').hidden=!t.alert;
  $('sceneStatus').textContent=t.parked?'停車車況・車輛為示意繪圖':model?'模型／雷達觀測視覺・非環景實景':'模型資料尚未更新';
  $('lead').textContent=radar?.leadOne?.status&&Number.isFinite(radar.leadOne.dRel)?`前車 ${radar.leadOne.dRel.toFixed(1)} m`:'前車 —';
  const ds=state.get('deviceState'),temps=ds?.cpuTempC?.filter(Number.isFinite)||[];$('temperatures').textContent=temps.length?`車機 ${Math.round(Math.max(...temps))}°C`:'車機 —';$('storage').textContent=Number.isFinite(ds?.freeSpacePercent)?`可用空間 ${Math.round(ds.freeSpacePercent)}%`:'空間 —';
  tireLabels(state.get('carState')).forEach((v,i)=>{$(['tireFl','tireFr','tireRl','tireRr'][i]).textContent=v;});
  const route=navigationView()?.snapshot();$('routeName').textContent=route?.busy?'正在更新導航…':!route?.known?route?.error?'導航狀態無法確認，請開啟導航重試。':'正在讀取目前導航…':route.active?route.label:'尚未設定目的地';$('routeEnd').disabled=!route?.known||!route.active||route.busy;
  if(pendingMode!==null&&!t.parked){cancelMode();$('profileStatus').textContent='車況已變更，已取消待確認的模式；未送出設定。';}
  document.body.dataset.hasRoute=String(Boolean(route?.known && (route.active || route.mapReady)));
  applyAppearance();
  const c=$('scene'),r=c.getBoundingClientRect(),scale=Math.min(devicePixelRatio||1,1.5),w=Math.max(1,Math.round(r.width*scale)),h=Math.max(1,Math.round(r.height*scale));if(c.width!==w||c.height!==h){c.width=w;c.height=h;}ctx.setTransform(scale,0,0,scale,0,0);
  if(t.parked){
    ctx.clearRect(0,0,r.width,r.height);ctx.fillStyle=document.body.classList.contains('night')?'#101114':'#f3f4f5';ctx.fillRect(0,0,r.width,r.height);
    const unit=Math.min(r.width*.17,r.height*.17);
    drawCockpitVehicle(ctx,(x,y,z)=>[r.width*.5+(x*.48+y*.88)*unit,r.height*.66+(-x*.28-y*.16-z)*unit],{view:[-5,8,6],skin,lamps:vehicleLamps(state.get('carState'),false,performance.now())});
  }else drawDrivingScene(ctx,r.width,r.height,{model,radar},{night:document.body.classList.contains('night'),lift:view==='vision'?r.height*.06:0,drawEgo:(context,project)=>drawCockpitVehicle(context,project,{skin,lamps:vehicleLamps(state.get('carState'),false,performance.now())}),text:(k,f)=>({scene_kind_person:'行人',scene_kind_motorcycle:'機車',scene_kind_bicycle:'自行車',scene_kind_bus:'公車',scene_kind_truck:'貨車'})[k]||f});
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
window.CarrotCockpit={layoutVersion:12,back(){const dialog=document.querySelector('dialog[open]');if(dialog){dialog.close();return true;}if(view==='navigation'&&nav.contentDocument?.body.classList.contains('search-open')){closeNavigationSearch();return true;}if(view!=='navigation'&&closeEmbeddedDialog(coreWindow()))return true;if(view==='setting'&&coreWindow()?.CarrotCockpitControls?.back?.())return true;if(view==='vision'&&document.body.classList.contains('advanced-vision')){advancedVision(false);return true;}if(!['vision','navigation'].includes(view)){panel(primary);return true;}return false;},pause(){paused=true;disconnect();selectCore('setting');},resume(){paused=false;selectCore(view==='navigation'?'setting':view);connect();}};
const updateClock=()=>{$('clock').textContent=cockpitClock();};updateClock();setInterval(updateClock,1000);document.addEventListener('visibilitychange',updateClock);
panel(view);connect();setInterval(()=>{if(!paused)render();},100);render();
