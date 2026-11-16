// No installer code is executed here. Only pinned configuration data changes.
export const TARGET='https://github.com/TonyBinheWu/sunnypilot.git';
export const UPSTREAM='https://i.carrotpilot.app/carrot-wip';
export const COMPAT='https://raw.githubusercontent.com/ajouatom/openpilot-installer-generator/df6f48de28e47afd6662e0a9184ac11d48733f26/agnos_compat/installer-agnos-19.6.3-carrot-base';
export const PROFILES=Object.freeze({
  legacy:{size:1270680,sha:'d0498d7da5458d2c963b2cda8419f6a3490c3a572e5c747d591e3fbde32148d9',repo:'https://github.com/ajouatom/openpilot.git?'},
  current:{size:2051392,sha:'ee2719d369d287b9f52d81dbd221ec16ab43d148da89d0b9bf2efe1bf52f20eb',repo:'https://github.com/ajouatom/openpilot.git?'},
  compat:{size:1401224,sha:'85f6d9e54286a3842920d6967b187478b4e43d6171c331d72d3fb3102106e101',repo:'https://github.com/commaai/openpilot.git?'},
});
const SNAPSHOT={'19.6.3':'legacy','19.8':'current','20.0':'current'};
const LIMIT=2100000,enc=new TextEncoder(),dec=new TextDecoder('latin1');
const digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),n=>n.toString(16).padStart(2,'0')).join('');
const EMBEDDED = {};

export function patchSlot(bytes,marker,value){
  const text=dec.decode(bytes),start=text.indexOf(marker),end=text.indexOf('\0',start);
  if(start<0||start!==text.lastIndexOf(marker)||end<start||end-start>256||value.length+1>end-start)throw Error('invalid_reserved_slot');
  bytes.fill(32,start,end);bytes.set(enc.encode(value+'?'),start);return [start,end];
}
export async function retarget(raw){
  const sha=await digest(raw),id=Object.keys(PROFILES).find(k=>PROFILES[k].sha===sha&&PROFILES[k].size===raw.length);
  if(!id||raw[0]!==127||raw[1]!==69||raw[2]!==76||raw[3]!==70||raw[4]!==2||raw[5]!==1||raw[18]!==183||raw[19]!==0)throw Error('unverified_template');
  const bytes=new Uint8Array(raw),slots=[patchSlot(bytes,PROFILES[id].repo,TARGET)];
  if(id==='compat')slots.push(patchSlot(bytes,'release3?','carrot-wip'));
  // Older templates fetch the factory cache's origin unchanged. Use a separate,
  // never-created cache marker so they clone TARGET instead of the factory repo.
  // This edits a same-size data literal; no cache file is moved or written.
  if(id!=='current'){
    const old='/data/.openpilot_cache\0',replacement='/data/.carrot_cache_v3\0';
    const text=dec.decode(bytes),start=text.indexOf(old);
    if(start<0||start!==text.lastIndexOf(old)||old.length!==replacement.length)throw Error('invalid_cache_literal');
    bytes.set(enc.encode(replacement),start);slots.push([start,start+old.length]);
  }
  // Explicitly verify that code, fonts, loader and all other bytes are intact.
  let cursor=0;for(const [a,b] of slots.slice().sort((x,y)=>x[0]-y[0])){for(let i=cursor;i<a;i++)if(raw[i]!==bytes[i])throw Error('outside_slot_change');cursor=b;}
  for(let i=cursor;i<raw.length;i++)if(raw[i]!==bytes[i])throw Error('outside_slot_change');
  return {id,bytes,sha:await digest(bytes),sourceSha:sha,slots};
}
function requestVersion(request){
  const ua=request.headers.get('user-agent')||'',device=request.headers.get('x-openpilot-device-type')||'';
  const match=/^AGNOSSetup-([A-Za-z0-9][A-Za-z0-9_.-]{0,47})$/.exec(ua);
  if(!match||device!=='mici')return null;
  return match[1];
}
const common={'Cache-Control':'no-store','Vary':'User-Agent, X-openpilot-device-type','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'};
function diagnostic(version,extra='Read-only check. No installer was executed.'){
  return new Response(`AGNOS: ${version||'unknown'}\nDevice: mici\n${extra}\n`,{status:409,headers:{...common,'Content-Type':'text/plain; charset=utf-8'}});
}
const guide=`<!doctype html><html lang="zh-TW"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CarrotPilot 安裝相容性</title><style>body{max-width:760px;margin:48px auto;padding:0 24px;font:18px/1.8 system-ui;background:#101a29;color:#edf5ff}a{color:#8bdafa}code{overflow-wrap:anywhere}h1{font-size:1.7em}section{border:1px solid #52667c;border-radius:16px;padding:20px;margin:22px 0}</style><h1>CarrotPilot 繁中分支安裝</h1><p>目標：TonyBinheWu/sunnypilot → carrot-wip</p><section><h2>在 C4 的自訂軟體網址使用</h2><p>本頁網址為安裝入口；加上 <code>/check</code> 則只檢查版本，不執行安裝。</p><p><a href="/manifest">檢視固定樣板與來源</a> · <a href="https://github.com/TonyBinheWu/sunnypilot/tree/carrot-wip/tools/carrot_installer">原始碼</a></p></section><p>服務依 AGNOS 版本選擇已核對雜湊的上游樣板，保留畫面與分支處理，替換目標倉庫；舊版樣板改用獨立快取識別字以重新下載，不修改或搬移工廠快取。19.6.3-carrot 使用上游在該版本驗證過的原生樣板。程式不儲存或轉送裝置序號，不接受任意倉庫、指令或上傳。</p><p>樣板驗證不等於你的 C4 已安裝成功；未知版本或更新的樣板會停止並顯示版本資訊。</p></html>`;

export function createGateway({fetchImpl=fetch,embedded=EMBEDDED,now=Date.now,timeoutMs=8000}={}){
  const cache=new Map(),flights=new Map();
  function embeddedRaw(id){
    if(!embedded[id])throw Error('template_unavailable');
    const value=atob(embedded[id]),bytes=new Uint8Array(value.length);
    for(let i=0;i<value.length;i++)bytes[i]=value.charCodeAt(i);
    return bytes;
  }
  async function download(version){
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeoutMs);
    try{
      // These are the complete upstream headers. No serial, cookie, incoming
      // authorization, IP-forwarding header or arbitrary URL is forwarded.
      const response=await fetchImpl(UPSTREAM,{redirect:'manual',signal:controller.signal,headers:{'User-Agent':'AGNOSSetup-'+version,'X-openpilot-device-type':'mici'}});
      if(response.status!==200)throw Error('upstream_unavailable');
      const reader=response.body.getReader();let length=0;const chunks=[];
      try{while(true){const item=await reader.read();if(item.done)break;length+=item.value.length;if(length>LIMIT)throw Error('template_too_large');chunks.push(item.value);}}
      finally{await reader.cancel().catch(()=>{});}
      const raw=new Uint8Array(length);let offset=0;for(const chunk of chunks){raw.set(chunk,offset);offset+=chunk.length;}return raw;
    }finally{clearTimeout(timer);}
  }
  async function prepare(version){
    if(version==='19.6.3-carrot')return {...await retarget(embeddedRaw('compat')),selection:'verified_agnos_compat'};
    let raw;
    try{raw=await download(version);}
    catch(error){
      // Only versions independently fetched during verification have an
      // offline fallback. Never guess a profile for an unknown OS version.
      const id=SNAPSHOT[version];if(!id)throw error;
      return {...await retarget(embeddedRaw(id)),selection:'pinned_verified_version_fallback'};
    }
    // Integrity failures never use a fallback: upstream changed; review first.
    return {...await retarget(raw),selection:'upstream_version_negotiation'};
  }
  async function selected(version){
    const previous=cache.get(version);if(previous&&now()-previous.at<600000)return previous.value;
    if(flights.has(version))return flights.get(version);
    if(flights.size>=2)throw Error('busy');
    const promise=prepare(version).then(value=>{if(cache.size>=6)cache.delete(cache.keys().next().value);cache.set(version,{value,at:now()});return value;}).finally(()=>flights.delete(version));
    flights.set(version,promise);return promise;
  }
  return async function handle(request){
    if(!['GET','HEAD'].includes(request.method))return new Response('Read only',{status:405,headers:{...common,Allow:'GET, HEAD'}});
    const path=new URL(request.url).pathname,version=requestVersion(request);
    if(path==='/manifest')return Response.json({target:TARGET,branch:'carrot-wip',profiles:PROFILES,compatSource:COMPAT,physicalDeviceAcceptance:false},{headers:common});
    if(path==='/check')return diagnostic(version);
    if(path!=='/'&&path!=='/c4')return new Response('Not found',{status:404,headers:common});
    if(!version){
      if((request.headers.get('user-agent')||'').startsWith('AGNOSSetup'))return diagnostic(null,'C4 device type and AGNOS version headers are required.');
      return new Response(request.method==='HEAD'?null:guide,{headers:{...common,'Content-Type':'text/html; charset=utf-8'}});
    }
    try{
      const value=await selected(version);
      return new Response(request.method==='HEAD'?null:value.bytes,{headers:{...common,'Content-Type':'application/octet-stream','Content-Length':String(value.bytes.length),'Content-Disposition':'attachment; filename="carrot-wip"','X-Carrot-Profile':value.id,'X-Carrot-Selection':value.selection,'X-Carrot-SHA256':value.sha}});
    }catch(error){return diagnostic(version,'Installation stopped: '+(['unverified_template','template_too_large','busy'].includes(error.message)?error.message:'template_unavailable')+'. No installer was executed.');}
  };
}
const handler=createGateway();
export default {fetch:request=>handler(request)};
