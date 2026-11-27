import {deviceSettings} from './device-settings.js?v=0.11.1';
import {translations} from './i18n.js?v=0.11.0';
import {initTextSize} from './text-size.js?v=0.11.0';
import {initTheme} from './theme.js?v=0.6.0';

const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
let language=localStorage.getItem('formosalink-language') || 'zh-TW';
const localStreamText={
  'zh-TW':'影像由車機透過同一個 Wi-Fi 傳到這支手機。',
  en:'The device streams video directly to this phone over Wi-Fi.',
  ja:'車載端末から同じ Wi-Fi でこのスマートフォンに映像を送信します。'
};
const t=key=>key==='mediaPhase' ? localStreamText[language] || localStreamText['zh-TW'] : (translations[language] || translations['zh-TW'])[key] || key;
const date=ts=>ts?new Date(ts*1000).toLocaleString(language):'—';
const pending=new Map();
let serial=0;
window.ccncReply=(id,status,json)=>{
  const call=pending.get(id);if(!call)return;
  pending.delete(id);
  let value;
  try {value=JSON.parse(json);} catch {call.reject({status:0});return;}
  if(status===200)call.resolve(value);
  else call.reject({status,reason:value.detail,key:'networkError'});
};
function request(path,body) {
  return new Promise((resolve,reject)=>{
    const id=++serial;
    pending.set(id,{resolve,reject});
    window.CcncDevice.request(id,path,body===undefined?'':JSON.stringify(body));
  });
}
const info=JSON.parse(window.CcncDevice.identity());
const device={id:info.device,name:'FormosaPilot · ccNC',state:'paired',online:true};
const workspace=deviceSettings({api:async(path,body)=>{
  if(path!=='/devices/'+device.id+'/settings')throw Error('unknown path');
  if(!body)return request('/v1/state');
  const receipt=await request('/v1/settings',body);
  return {id:receipt.id,status:'queued'};
},t,language:()=>language,element:el,date,notify:key=>{document.getElementById('message').textContent=t(key);},
  getDevices:()=>[device],getAccount:()=>({id:device.id,name:'Wi-Fi'}),onPair:()=>CcncDevice.connections(),
  localFrame:camera=>request('/v1/frame/'+camera)});
const applyTheme=initTheme(t);
initTextSize();
function translate() {
  language=localStorage.getItem('formosalink-language')||'zh-TW';
  document.documentElement.lang=language; applyTheme();
  document.querySelectorAll('[data-i18n]').forEach(n=>n.textContent=t(n.dataset.i18n));
  document.querySelectorAll('[data-i18n-aria]').forEach(n=>n.setAttribute('aria-label',t(n.dataset.i18nAria)));
  workspace.translate();
}
document.querySelectorAll('[data-language]').forEach(b=>b.onclick=()=>{
  localStorage.setItem('formosalink-language',b.dataset.language);translate();
});
document.getElementById('settings-nav').addEventListener('click',()=>{
  if(document.getElementById('settings-workspace').hidden)CcncDevice.connections();
});
document.getElementById('settings-back').addEventListener('click',e=>{e.preventDefault();CcncDevice.connections();});
window.addEventListener('hashchange',()=>{if(!location.hash.includes('device='))CcncDevice.connections();else workspace.route();});
document.body.classList.add('lan-app');
document.querySelector('body > main').hidden=true;
document.querySelector('.topbar').hidden=true;
document.querySelector('footer').hidden=true;
translate();
workspace.open(device,'device',false);
