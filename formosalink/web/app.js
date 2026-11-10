import {translations} from './i18n.js';
const $ = id => document.getElementById(id);
let language = 'zh-TW';
try { language = localStorage.getItem('formosalink-language') || 'zh-TW'; } catch {}
if (!translations[language]) language = 'zh-TW';
let account = null, githubEnabled = false;
let authEpoch = 0;
let signedIn = false, devices = [], lastRefresh = null, networkFailed = false, busy = false;
const t = key => translations[language][key] || key;
const date = seconds => seconds ? new Intl.DateTimeFormat(language,{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit',second:'2-digit'}).format(new Date(seconds*1000)) : '—';

function notify(key, error=false) { $('message').textContent=t(key); $('message').hidden=false; $('message').classList.toggle('error',error); }
async function api(path, body) {
  let response;
  try { response = await fetch('/api/v1'+path,{method:body===undefined?'GET':'POST',credentials:'same-origin',headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(12000),cache:'no-store'}); }
  catch { throw {key:'networkError'}; }
  if (!response.ok) {
    const key=response.status===429?'rateLimit':response.status===401?(path==='/login'?'invalidLogin':'expired'):path==='/pair'&&response.status===400?'invalidPair':[400,403].includes(response.status)?'transportError':'serverError';
    throw {key,status:response.status};
  }
  try {return await response.json();} catch {throw {key:'serverError'};}
}
function element(tag, text, className) { const node=document.createElement(tag); if(text!==undefined)node.textContent=text;if(className)node.className=className;return node; }
function metric(container,key,value,unit) {const item=element('div',undefined,'metric');item.append(element('label',t(key)),element('strong',value===null||value===undefined?'—':String(Math.round(value))));if(unit)item.append(element('small',unit));container.append(item);}
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
    const details=element('dl',undefined,'device-details');
    for(const [key,value] of [['version',m.software_version],['branch',m.branch],['commit',m.commit?.slice(0,12)],['thermal',hidden?null:translations[language]['thermal_'+m.thermal_status]],['sampleTime',date(device.snapshot?.sampled_at)],['fingerprint',device.fingerprint]]){details.append(element('dt',t(key)),element('dd',value||'—'));}card.append(details);
    const bottom=element('div',undefined,'card-bottom');bottom.append(element('span',`${t('received')} ${date(device.last_seen)}`));
    if(device.state==='paired'){const revoke=element('button',t('revoke'),'quiet revoke');revoke.type='button';revoke.addEventListener('click',async()=>{if(!confirm(t('confirmRevoke')))return;revoke.disabled=true;try{await api('/devices/'+encodeURIComponent(device.id)+'/revoke',{});notify('revoked');await refresh();}catch(e){notify(e.key||'serverError',true);}finally{revoke.disabled=false;}});bottom.append(revoke);}card.append(bottom);$('device-grid').append(card);
  }
}
function session(value){signedIn=value;$('login-view').hidden=value;$('dashboard').hidden=!value;$('logout').hidden=!value;if(!value){devices=[];lastRefresh=null;$('device-grid').replaceChildren();$('pair-dialog').close();}}
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
    if(account?.id!==auth.user?.id){devices=[];lastRefresh=null;$('device-grid').replaceChildren();}
    account=auth.user;githubEnabled=auth.github_enabled;
    $('github-login').disabled=!githubEnabled;
    $('github-note').textContent=t(githubEnabled?'githubReady':'githubUnavailable');
    $('github-link').hidden=!githubEnabled||account?.id!=='local-admin'||!!account?.github_login;
    $('account-name').textContent=account?.github_login?'GitHub · '+account.github_login:account?.id==='local-admin'?t('adminAccount'):account?.name||'';
    if(!account){session(false);return;}
    const data=await api('/devices');
    if(epoch!==authEpoch)return;
    devices=data.devices;lastRefresh=data.server_time;networkFailed=false;session(true);
    if($('message').classList.contains('error'))$('message').hidden=true;
    render();
  }catch(e){
    if(epoch!==authEpoch)return;
    if(e.status===401){session(false);if(e.key!=='expired')notify(e.key,true);}
    else{networkFailed=true;render();notify(e.key||'serverError',true);}
  }finally{busy=false;if(epoch!==authEpoch)refresh();}
}
function applyLanguage(){document.documentElement.lang=language==='zh-TW'?'zh-Hant':language;$('language').value=language;document.querySelectorAll('[data-i18n]').forEach(node=>node.textContent=t(node.dataset.i18n));$('github-note').textContent=t(githubEnabled?'githubReady':'githubUnavailable');if(signedIn)render();$('message').hidden=true;}
$('language').addEventListener('change',()=>{language=$('language').value;try{localStorage.setItem('formosalink-language',language);}catch{}applyLanguage();});
$('login-form').addEventListener('submit',async event=>{event.preventDefault();const button=event.submitter;button.disabled=true;try{await api('/login',{password:$('password').value});authEpoch++;$('password').value='';$('message').hidden=true;await refresh();}catch(e){notify(e.key||'serverError',true);}finally{button.disabled=false;}});
$('logout').addEventListener('click',async()=>{try{await api('/logout',{});authEpoch++;session(false);$('message').hidden=true;}catch(e){notify(e.key||'serverError',true);}});
function openPair(){$('pair-dialog').showModal();$('pair-code').focus();}
$('open-pair').addEventListener('click',openPair);$('empty-pair').addEventListener('click',openPair);$('close-pair').addEventListener('click',()=>$('pair-dialog').close());
$('pair-form').addEventListener('submit',async event=>{event.preventDefault();const button=event.submitter;button.disabled=true;try{await api('/pair',{code:$('pair-code').value,fingerprint:$('fingerprint').value,name:$('device-name').value});$('pair-dialog').close();$('pair-code').value='';$('fingerprint').value='';notify('paired');await refresh();}catch(e){notify(e.key||'serverError',true);}finally{button.disabled=false;}});
$('refresh').addEventListener('click',refresh);document.addEventListener('visibilitychange',()=>{if(!document.hidden&&signedIn)refresh();});
$('github-login').addEventListener('click',()=>{location.assign('/api/v1/auth/github/start');});
$('github-link').addEventListener('click',async()=>{if(!confirm(t('githubConfirm')))return;try{const result=await api('/auth/github/link',{});const target=new URL(result.url);if(target.origin!=='https://github.com')throw {};location.assign(target.href);}catch(e){notify(e.key||'serverError',true);}});
applyLanguage();if(new URLSearchParams(location.search).has('auth')){notify('oauthFailed',true);history.replaceState(null,'','/');}refresh();setInterval(()=>{if(signedIn&&!document.hidden)refresh();},5000);
if('serviceWorker' in navigator)navigator.serviceWorker.register('/sw.js').catch(()=>{});
