import {initTheme} from './theme.js?v=0.6.0';
import {healthValue} from './health-ui.js?v=0.6.0';
import {deviceSettings} from './device-settings.js?v=0.6.1';
import {translations} from './i18n.js?v=0.6.1';
import {parsePairingFragment,validatePairing,readPending,savePending,clearPending} from './pairing.js?v=0.6.0';
const $ = id => document.getElementById(id);
let language = 'zh-TW';
try { language = localStorage.getItem('formosalink-language') || 'zh-TW'; } catch {}
if (!translations[language]) language = 'zh-TW';
let account = null, githubEnabled = null;
let authEpoch = 0;
let signedIn = false, devices = [], lastRefresh = null, networkFailed = false, busy = false;
let pairStorage;
try{pairStorage=sessionStorage;}catch{}
let pendingPair=readPending(pairStorage), qrPresented=false, pairingNotice=null;
function consumePairingHash(){
  if(!new URLSearchParams(location.hash.slice(1)).has('pair'))return false;
  pendingPair=parsePairingFragment(location.hash);
  qrPresented=false;pairingNotice=null;
  history.replaceState(null,'',location.pathname+location.search);
  if(pendingPair){if(!savePending(pairStorage,pendingPair))pairingNotice='qrStorageUnavailable';}
  else{clearPending(pairStorage);pairingNotice='qrExpired';}
  return true;
}
consumePairingHash();
const t = key => translations[language][key] || key;
const applyTheme=initTheme(t);
const date = seconds => seconds ? new Intl.DateTimeFormat(language,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date(seconds*1000)) : '—';

function notify(key, error=false) { $('message').textContent=t(key); $('message').dataset.key=key; $('message').hidden=false; $('message').classList.toggle('error',error); }
async function api(path, body) {
  let response;
  try { response = await fetch('/api/v1'+path,{method:body===undefined?'GET':'POST',credentials:'same-origin',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(12000),cache:'no-store'}); }
  catch { throw {key:'networkError'}; }
  if (!response.ok) {
    const key=response.status===429?'rateLimit':response.status===401?(path==='/login'?'invalidLogin':'expired'):path==='/pair'&&response.status===400?'invalidPair':[400,403].includes(response.status)?'transportError':'serverError';
    let reason;try{reason=(await response.json()).detail;}catch{}
    throw {key,status:response.status,reason:typeof reason==='string'?reason:undefined};
  }
  try {return await response.json();} catch {throw {key:'serverError'};}
}
function element(tag, text, className) { const node=document.createElement(tag); if(text!==undefined)node.textContent=text;if(className)node.className=className;return node; }
function metric(container,key,value,unit) {const item=element('div',undefined,'metric');item.append(element('label',t(key)),element('strong',value===null||value===undefined?'—':String(Math.round(value))));if(unit)item.append(element('small',unit));container.append(item);}
const settings=deviceSettings({api,t,language:()=>language,element,date,notify,getDevices:()=>devices,getAccount:()=>account,onPair:openPair});
function render() {
  $('device-count').textContent=String(devices.filter(d=>d.state==='paired').length);
  $('online-count').textContent=String(devices.filter(d=>d.online&&!networkFailed).length);
  $('empty').hidden=devices.length>0;
  $('refresh-label').textContent=networkFailed?t('offline'):lastRefresh?`${t('updated')} ${date(lastRefresh)}`:t('waiting');
  $('device-grid').replaceChildren();
  for(const device of devices) {
    const stale=networkFailed||device.stale, m=device.snapshot?.metrics||{}, hidden=stale||device.state==='revoked';
    const card=element('article',undefined,'device-card'), heading=element('div',undefined,'device-heading'), title=element('div');
    title.append(element('h2',device.name),element('span',m.device_type?.startsWith('DEMO')?t('demo'):(m.device_type||'FormosaPilot'),'device-type'));
    const state=device.state==='revoked'?'revokedState':networkFailed||!device.online?'offline':stale?'stale':'connected';
    heading.append(title,element('span',t(state),'badge '+(state==='connected'?'':state==='stale'?'stale':'offline')));card.append(heading);
    const status=element('div',undefined,'device-state');status.append(element('span',hidden||m.started===null||m.started===undefined?t('unknown'):m.started?t('driving'):t('parked')),element('strong',!hidden&&m.speed_kph!==null&&m.speed_kph!==undefined?`${Math.round(m.speed_kph)} km/h`:'—'));card.append(status);
    const metrics=element('div',undefined,'metrics');metric(metrics,'cpu',hidden?null:m.cpu_temp_c,'°C');metric(metrics,'gpu',hidden?null:m.gpu_temp_c,'°C');metric(metrics,'memory',hidden?null:m.memory_percent,'%');metric(metrics,'storage',hidden?null:m.free_space_percent,'%');card.append(metrics);
    const details=element('dl',undefined,'device-details');const h=device.health||{},hf=device.health_fresh&&h.health_valid;
    for(const [key,value] of [['info_vehicle_platform',h.vehicle_platform],['vehicleSoc',device.health_fresh&&h.soc_status==='available'?healthValue(h.vehicle_soc_percent,' %'):t(h.soc_status==='unsupported'?(h.soc_detection?'tractionSocUnverified':'socUnsupported'):'unknown')],['egpu',hf?(h.egpu_status==='available'?healthValue(h.egpu_temp_c,' °C'):t('egpu_'+(h.egpu_status||'unknown'))):t('unknown')]])details.append(element('dt',t(key)),element('dd',value||'—'));
    for(const [key,value] of [['version',m.software_version],['branch',m.branch],['commit',m.commit?.slice(0,12)],['thermal',hidden?null:translations[language]['thermal_'+m.thermal_status]],['sampleTime',date(device.snapshot?.sampled_at)]]){details.append(element('dt',t(key)),element('dd',value||'—'));}card.append(details);
    const bottom=element('div',undefined,'card-bottom');bottom.append(element('span',`${t('received')} ${date(device.last_seen)}`));
    if(device.state==='paired'){const detail=element('button',t('deviceSettings'),'secondary');detail.type='button';detail.addEventListener('click',()=>settings.open(device));bottom.append(detail);const revoke=element('button',t('revoke'),'quiet revoke');revoke.type='button';revoke.addEventListener('click',async()=>{if(!confirm(t('confirmRevoke')))return;revoke.disabled=true;try{await api('/devices/'+encodeURIComponent(device.id)+'/revoke',{});notify('revoked');await refresh();}catch(e){notify(e.key||'serverError',true);}finally{revoke.disabled=false;}});bottom.append(revoke);}card.append(bottom);$('device-grid').append(card);
  }
}
function session(value){signedIn=value;$('login-view').hidden=value;$('dashboard').hidden=!value;$('logout').hidden=!value;$('public-nav').hidden=value;$('nav-signin').hidden=value;if(!value){settings.reset(!!account);devices=[];lastRefresh=null;$('device-grid').replaceChildren();$('pair-dialog').close();}}
async function refresh(){
  if(busy)return;
  busy=true;
  const epoch=authEpoch;
  try{
    let auth;
    try{auth=await api('/auth/me');}
    catch(e){
      // Keep the existing password screen usable while IIS assets and the private runtime are updated separately.
      if(e.status!==404)throw e;
      auth={user:{id:'local-admin',name:''},github_enabled:false};
    }
    if(epoch!==authEpoch)return;
    if(account?.id!==auth.user?.id){settings.reset(!!account);devices=[];lastRefresh=null;$('device-grid').replaceChildren();}
    account=auth.user;githubEnabled=auth.github_enabled;
    $('github-login').disabled=!githubEnabled;
    $('github-note').textContent=t(githubEnabled===null?'waiting':githubEnabled?(pendingPair?'qrLoginFirst':'githubReady'):'githubUnavailable');
    $('github-link').hidden=!githubEnabled||account?.id!=='local-admin'||!!account?.github_login;
    $('account-name').textContent=account?.github_login?'GitHub · '+account.github_login:account?.id==='local-admin'?t('adminAccount'):account?.name||'';
    if(!account){session(false);return;}
    const data=await api('/devices');
    if(epoch!==authEpoch)return;
    devices=data.devices;lastRefresh=data.server_time;networkFailed=false;session(true);
    if(['networkError','serverError','transportError','expired'].includes($('message').dataset.key))$('message').hidden=true;
    render();settings.update();settings.route();if(!location.hash&&!pendingPair){const first=devices.find(d=>d.state==='paired');if(first)settings.open(first,'home');}
    if(pendingPair&&!qrPresented){qrPresented=true;openPair();}
  }catch(e){
    if(epoch!==authEpoch)return;
    if(e.status===401){session(false);if(e.key!=='expired')notify(e.key,true);}
    else{networkFailed=true;render();notify(e.key||'serverError',true);}
  }finally{busy=false;if(epoch!==authEpoch)refresh();}
}
function applyLanguage(){applyTheme();document.documentElement.lang=language==='zh-TW'?'zh-Hant':language;$('language').setAttribute('aria-label',t('language'));$('language').textContent={'zh-TW':'繁體中文',en:'English',ja:'日本語'}[language];document.querySelectorAll('[data-language]').forEach(node=>node.setAttribute('aria-pressed',String(node.dataset.language===language)));settings.translate();document.querySelectorAll('[data-i18n]').forEach(node=>node.textContent=t(node.dataset.i18n));document.querySelectorAll('[data-i18n-aria]').forEach(node=>node.setAttribute('aria-label',t(node.dataset.i18nAria)));$('github-note').textContent=t(githubEnabled===null?'waiting':githubEnabled?(pendingPair?'qrLoginFirst':'githubReady'):'githubUnavailable');if(account?.id==='local-admin'&&!account.github_login)$('account-name').textContent=t('adminAccount');if(signedIn)render();$('message').hidden=true;}
document.querySelectorAll('[data-language]').forEach(button=>button.addEventListener('click',()=>{language=button.dataset.language;try{localStorage.setItem('formosalink-language',language);}catch{}$('language-menu').open=false;applyLanguage();}));
document.addEventListener('click',event=>{if(!$('language-menu').contains(event.target))$('language-menu').open=false;});
document.addEventListener('keydown',event=>{if(event.key==='Escape')$('language-menu').open=false;});
$('logout').addEventListener('click',async()=>{try{await api('/logout',{});authEpoch++;session(false);$('message').hidden=true;}catch(e){notify(e.key||'serverError',true);}});
function openPair(){
  pendingPair=validatePairing(pendingPair);
  if(!pendingPair)clearPending(pairStorage);
  $('pair-scan-help').hidden=!!pendingPair;
  $('pair-details').hidden=!pendingPair;
  $('confirm-pair').hidden=!pendingPair;
  $('device-name').disabled=!pendingPair;
  if(!$('pair-dialog').open)$('pair-dialog').showModal();
  (pendingPair?$('confirm-pair'):$('close-pair')).focus();
}
$('open-pair').addEventListener('click',openPair);$('empty-pair').addEventListener('click',openPair);$('sidebar-pair').addEventListener('click',openPair);$('close-pair').addEventListener('click',()=>$('pair-dialog').close());
$('pair-form').addEventListener('submit',async event=>{event.preventDefault();pendingPair=validatePairing(pendingPair);if(!pendingPair){clearPending(pairStorage);openPair();notify('qrExpired',true);return;}const button=event.submitter;button.disabled=true;try{await api('/pair',{code:pendingPair.code,fingerprint:pendingPair.fingerprint,name:$('device-name').value});clearPending(pairStorage);pendingPair=null;$('pair-dialog').close();notify('paired');await refresh();}catch(e){if(e.status===400){clearPending(pairStorage);pendingPair=null;openPair();}if(e.status===401)session(false);notify(e.key||'serverError',true);}finally{button.disabled=false;}});
function expirePairing(){if(pendingPair&&!validatePairing(pendingPair)){pendingPair=null;clearPending(pairStorage);if($('pair-dialog').open)openPair();$('github-note').textContent=t(githubEnabled?'githubReady':'githubUnavailable');notify('qrExpired',true);}}
$('refresh').addEventListener('click',refresh);document.addEventListener('visibilitychange',()=>{if(!document.hidden){expirePairing();if(signedIn)refresh();}});
$('github-login').addEventListener('click',()=>{location.assign('/api/v1/auth/github/start');});
$('github-link').addEventListener('click',async()=>{if(!confirm(t('githubConfirm')))return;try{const result=await api('/auth/github/link',{});const target=new URL(result.url);if(target.origin!=='https://github.com')throw {};location.assign(target.href);}catch(e){notify(e.key||'serverError',true);}});
window.addEventListener('popstate',()=>{if(signedIn)settings.route();});
window.addEventListener('hashchange',()=>{if(signedIn)settings.route();if(consumePairingHash()){applyLanguage();if(signedIn){qrPresented=true;openPair();}if(pairingNotice)notify(pairingNotice,true);}});
applyLanguage();if(pairingNotice)notify(pairingNotice,true);if(new URLSearchParams(location.search).has('auth')){notify('oauthFailed',true);history.replaceState(null,'','/');}refresh();setInterval(()=>{if(!document.hidden){expirePairing();if(signedIn)refresh();}},5000);
if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});
