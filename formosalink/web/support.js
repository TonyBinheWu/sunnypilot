// Shared by the web dashboard and APK's web surface. Never inserts log HTML.
export function supportPanel({api,element,language,notify}){
 let dialog=null,generation=0,pendingAsk=null;
 const words={
  'zh-TW':{title:'診斷分享與行車紀錄',admin:'管理者診斷台',notice:'保留 30 天。診斷分享預設關閉；開啟後，管理者可查看可取得的安裝、啟動與錯誤文字日誌。未留下或未上傳的階段無法補回。完整行車紀錄另逐次同意，僅上傳最近已完成行程的 rlog（含位置與行車狀態，不含影片）。',enable:'開啟診斷分享',disable:'停用診斷分享',confirm:'同意將文字診斷日誌提供給 FormosaLink 管理者，保留 30 天？文字會先遮蔽常見憑證，但仍可能含有環境資訊。',route:'同意上傳最近完成行程',routeConfirm:'這次同意上傳最近已完成行程的完整 rlog，含位置、路線及行車狀態，提供給管理者保留 30 天？車機會等停車後處理，不含影片；每個檔案上限 64 MiB、每行程 512 MiB。',remove:'刪除全部並停用分享',removeConfirm:'刪除此裝置已上傳的日誌、取消待辦上傳，並停用診斷分享？',refresh:'重新整理',close:'關閉',empty:'尚未收到可用紀錄；不代表沒有錯誤。',search:'搜尋裝置代碼／檔名／類型',download:'下載',partial:'尚未完整上傳',expires:'到期',state:'最近行車上傳狀態',pending:'等待車機停車上傳',done:'已完成',no_completed_route:'沒有可用的已完成行程',size_limit:'行程超過上限，未自動省略檔案',upload_failed:'上傳失敗；已收到的檔案可能只有部分行程',sharing:'診斷分享',on:'已開啟',off:'已停用'},
  en:{title:'Diagnostics and driving logs',admin:'Administrator diagnostics',notice:'Retained for 30 days. Diagnostics sharing is off by default. Opt in to share available installation, startup and error text logs with the administrator. Unrecorded stages cannot be recovered. Each full rlog upload requires separate consent; it includes location and driving state, but no video.',enable:'Enable diagnostics sharing',disable:'Disable diagnostics sharing',confirm:'Share text diagnostics with the administrator for 30 days? Common credentials are redacted, but environment information may remain.',route:'Upload latest completed drive',routeConfirm:'Share the latest completed drive rlogs, including location and driving state, with the administrator for 30 days? Upload while parked, no video. Limit: 64 MiB/file and 512 MiB/drive.',remove:'Delete all and disable sharing',removeConfirm:'Delete this device’s uploaded logs, cancel pending uploads and disable diagnostics sharing?',refresh:'Refresh',close:'Close',empty:'No available reports received. This does not mean no errors.',search:'Search device ID / filename / type',download:'Download',partial:'Incomplete upload',expires:'Expires',state:'Latest drive upload',pending:'Waiting for parked device',done:'Complete',no_completed_route:'No completed drive available',size_limit:'Drive exceeds limits; files were not silently omitted',upload_failed:'Upload failed; received files may cover only part of the drive',sharing:'Diagnostics sharing',on:'Enabled',off:'Disabled'}
 };
 words['zh-TW'].expired='同意已到期，請重新提出上傳';words.en.expired='Consent expired; request another upload';
 const t=k=>(words[language()]||words.en)[k]||k;
 function close(){pendingAsk?.(false);generation++;dialog?.remove();dialog=null;}
 function ask(message){return new Promise(resolve=>{
  const box=element('dialog'),text=element('p',message);box.style.cssText='max-width:600px;width:85vw';
  const finish=value=>{pendingAsk=null;box.remove();resolve(value);};pendingAsk=finish;
  const yes=element('button',language()==='zh-TW'?'確認':'Confirm','primary'),no=element('button',language()==='zh-TW'?'取消':'Cancel','quiet');
  yes.type=no.type='button';yes.addEventListener('click',()=>finish(true));no.addEventListener('click',()=>finish(false));
  box.addEventListener('cancel',event=>{event.preventDefault();finish(false);});box.append(text,no,yes);document.body.append(box);box.showModal();no.focus();
 });}
 async function open(device=null){
  close();const mine=generation;dialog=element('dialog');dialog.style.cssText='max-width:950px;width:90vw;max-height:85vh;overflow:auto';document.body.append(dialog);
  const heading=element('h2',t(device?'title':'admin')),body=element('div'),tools=element('div');dialog.append(heading,tools,body);
  const button=(label,action)=>{const b=element('button',t(label),'secondary');b.type='button';b.addEventListener('click',async()=>{b.disabled=true;try{await action();}catch(e){notify(e.key||'serverError',true);}finally{b.disabled=false;}});return b;};
  dialog.append(button('close',close));dialog.addEventListener('cancel',()=>close());dialog.showModal();
  let query='';
  if(!device){const search=element('input');search.type='search';search.placeholder=t('search');search.setAttribute('aria-label',t('search'));search.addEventListener('change',()=>{query=search.value;load();});tools.append(search);}
  tools.append(button('refresh',load));
  async function load(){
   const data=await api(device?'/support/'+encodeURIComponent(device.id):'/admin/support?q='+encodeURIComponent(query));
   if(generation!==mine)return;body.replaceChildren();
   if(device){
    body.append(element('p',t('notice')),element('p',t('sharing')+': '+t(data.diagnostics?'on':'off')));
    body.append(button(data.diagnostics?'disable':'enable',async()=>{if(!data.diagnostics&&!await ask(t('confirm')))return;await api('/support/'+device.id+'/consent',{diagnostics:!data.diagnostics});await load();}));
    body.append(button('route',async()=>{if(!await ask(t('routeConfirm')))return;await api('/support/'+device.id+'/route',{consent:'latest-completed-rlog-with-location-v1'});await load();}));
    body.append(button('remove',async()=>{if(!await ask(t('removeConfirm')))return;await api('/support/'+device.id+'/delete',{});await load();}));
    if(data.latest_job)body.append(element('p',t('state')+': '+t(data.latest_job.state)));
   }
   if(!data.files.length)body.append(element('p',t('empty')));
   for(const file of data.files){
    const row=element('article',undefined,'panel');row.append(element('strong',file.name));
    row.append(element('p',[file.device_name||device?.name||file.device,file.kind,(file.size/1048576).toFixed(2)+' MiB',t('expires')+': '+new Date(file.expires*1000).toLocaleString()].join(' · ')));
    if(file.kind==='rlog')row.append(element('p',t('state')+': '+t(file.job_state||'upload_failed')));
    if(file.complete){const link=element('a',t('download'),'secondary');link.href='/api/v1/support-files/'+encodeURIComponent(file.id);link.download=file.name;row.append(link);}
    else row.append(element('p',t('partial')));
    body.append(row);
   }
  }
  try{await load();}catch(e){if(mine===generation)body.textContent=t('empty');notify(e.key||'serverError',true);}
 }
 return {open,close,label:()=>t('title'),adminLabel:()=>t('admin')};
}
