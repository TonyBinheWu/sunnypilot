const API='/api/device/training_data';
const MESSAGES={
  'zh-tw':{title:'訓練資料授權',enable:'同意並自動上傳',disable:'停止未來上傳',close:'關閉',on:'已授權上傳',off:'尚未授權',pendingOn:'等待連線同步授權',pendingOff:'本機已停止上傳，等待雲端同步',completed:'已完成上傳片段',receiver:'接收服務',pair:'請先完成 FormosaLink 配對，再授權訓練資料上傳。',park:'請停車後再啟用授權；停止上傳不受此限制。',saved:'選擇已儲存。背景服務連線後會同步；僅在停車、有網路時上傳。',failed:'無法讀取訓練授權。請確認車機已更新並重啟網頁服務。',consent_changed:'授權狀態已變更，請關閉後重新開啟。',policy_changed:'授權說明已更新，請重新開啟閱讀。'},
  en:{title:'Training data upload',enable:'Agree and upload automatically',disable:'Stop future uploads',close:'Close',on:'Uploads authorized',off:'Not authorized',pendingOn:'Waiting to sync authorization',pendingOff:'Local uploads stopped; waiting for cloud sync',completed:'Uploaded segments',receiver:'Receiving service',pair:'Pair this device with FormosaLink before authorizing training uploads.',park:'Park before enabling. You can stop future uploads while driving.',saved:'Choice saved. The background service will sync when connected; uploads run only while parked with Internet.',failed:'Training consent is unavailable. Update the device and restart its web service.',consent_changed:'Consent changed. Close and reopen this dialog.',policy_changed:'The notice changed. Reopen it before choosing.'},
  ko:{title:'학습 데이터 제공 동의',enable:'동의하고 자동 업로드',disable:'향후 업로드 중지',close:'닫기',on:'업로드 동의됨',off:'동의하지 않음',pendingOn:'동의 동기화 대기',pendingOff:'본체 업로드 중지됨 · 서버 동기화 대기',completed:'업로드 완료 구간',receiver:'수신 서비스',pair:'학습 업로드에 동의하기 전에 FormosaLink에 기기를 등록하세요.',park:'주차 후 동의할 수 있습니다. 업로드 중지는 주행 중에도 가능합니다.',saved:'선택을 저장했습니다. 연결 후 동기화하며, 주차 중 인터넷 연결 시에만 업로드합니다.',failed:'학습 동의를 불러올 수 없습니다. 기기 업데이트 후 웹 서비스를 재시작하세요.'},
  zh:{title:'训练数据授权',enable:'同意并自动上传',disable:'停止未来上传',close:'关闭',on:'已授权上传',off:'尚未授权',pendingOn:'等待连接同步授权',pendingOff:'本机已停止上传，等待云端同步',completed:'已完成上传片段',receiver:'接收服务',pair:'请先完成 FormosaLink 配对，再授权训练数据上传。',park:'请停车后再启用授权；停止上传不受此限制。',saved:'选择已保存。联网后由后台同步，仅停车有网络时上传。',failed:'无法读取训练授权，请更新设备并重启网页服务。'},
};
export function trainingText(locale){return MESSAGES[String(locale||'').toLowerCase()]||MESSAGES.en;}
const escape=value=>String(value??'').replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
function locale(){return globalThis.CarrotWebSettingsState?.web_language||globalThis.document?.documentElement.lang||'en';}
export function trainingProgressHtml(upload,language){
  const zh=String(language).toLowerCase().startsWith('zh');
  const names=zh?{waiting_parked:'等待停車',waiting_consent:'等待同步有效授權',missing_logs:'找不到行車記錄目錄',hashing:'正在計算檔案校驗碼',uploading:'正在上傳',completed:'上一個片段已完成上傳',waiting_recordings:'等待符合條件的新錄影',error:'上傳器錯誤，稍後自動重試'}:{waiting_parked:'Waiting until parked',waiting_consent:'Waiting for valid consent',missing_logs:'Recording directory unavailable',hashing:'Verifying file',uploading:'Uploading',completed:'Last segment uploaded',waiting_recordings:'Waiting for eligible new recordings',error:'Upload error; retrying automatically'};
  const state=upload?.fresh?names[upload.state]:(zh?'尚無近期上傳器狀態，請確認已更新並重啟車機':'No recent uploader status; update and restart the device');
  const counts=upload?.counts;
  const detail=counts?(zh?`錄影中 ${counts.recording||0}／等待結束滿 2 分鐘 ${counts.settling||0}／授權前 ${counts.before_consent||0}／缺少 rlog 或雙鏡頭 ${counts.incomplete||0}／無法解析記錄 ${counts.invalid_log||0}`:`Recording ${counts.recording||0}; settling for 2 minutes ${counts.settling||0}; before consent ${counts.before_consent||0}; missing log/cameras ${counts.incomplete||0}; unreadable logs ${counts.invalid_log||0}`):'';
  const bytes=Number.isFinite(upload?.bytes)&&Number.isFinite(upload?.total)?`${(upload.bytes/1048576).toFixed(1)} / ${(upload.total/1048576).toFixed(1)} MiB`:'';
  const error=upload?.fresh&&upload.state==='error'?`${upload.error_type||''} ${upload.http_status||''}`:'';
  const note=zh?'只收授權後的新行車片段；停車且片段結束滿 2 分鐘後自動上傳。「紀錄 → 手動傳送」是原有分享服務，不會送進訓練資料庫。重新開啟此視窗可更新進度。':'Only new recordings after consent qualify. Automatic upload starts while parked, 2 minutes after a segment closes. Logs → manual send uses the separate sharing service. Reopen this dialog to refresh progress.';
  return `<p>${escape(state||upload?.state||'')}</p><p>${escape([upload?.filename,bytes,error].filter(Boolean).join(' · '))}</p>${detail?`<p>${escape(detail)}</p>`:''}<p>${escape(note)}</p>`;
}
export function trainingConsentHtml(status,language){
  const text=trainingText(language);
  const state=status.pending_enabled===true?text.pendingOn:status.pending_enabled===false?text.pendingOff:status.enabled?text.on:text.off;
  const notice=status.notice?.[String(language).toLowerCase()==='zh-tw'?'zh-TW':language]||status.notice?.en||'';
  return `<p><strong>${escape(state)}</strong></p><p>${escape(notice)}</p><p>${escape(text.receiver)}: ${escape(status.receiver||'FormosaLink')}</p><p>${escape(text.completed)}: ${Number.isInteger(status.uploaded_segments)?status.uploaded_segments:0}</p>${trainingProgressHtml(status.upload,language)}${!status.configured?`<p>${escape(text.pair)}</p>`:!status.offroad&&!status.enabled?`<p>${escape(text.park)}</p>`:''}`;
}
export async function trainingRequest(body){
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),7000);
  try{
    const response=await fetch(API,{method:body?'POST':'GET',credentials:'same-origin',cache:'no-store',signal:controller.signal,
      headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});
    const value=await response.json();
    if(!response.ok||value.ok!==true)throw new Error(value.error||'unavailable');
    return value;
  }finally{clearTimeout(timeout);}
}
export function localizeTrainingData(){const button=globalThis.document?.getElementById('btnTrainingData');if(button)button.textContent=trainingText(locale()).title;}
export async function openTrainingData(){
  const language=locale(),text=trainingText(language);
  try{
    const status=await trainingRequest();
    const desired=status.pending_enabled??status.enabled;
    const messageHtml=trainingConsentHtml(status,language);
    if(!desired&&!status.can_enable){await globalThis.appAlert('',{title:text.title,html:true,messageHtml});return;}
    const agreed=await globalThis.openAppDialog({mode:'confirm',title:text.title,html:true,messageHtml,
      confirmLabel:desired?text.disable:text.enable,cancelLabel:text.close});
    if(!agreed)return;
    const saved=await trainingRequest({policy:status.policy,enabled:!desired,revision:status.revision});
    await globalThis.appAlert('',{title:text.title,html:true,messageHtml:trainingConsentHtml(saved,language)+`<p>${escape(text.saved)}</p>`});
  }catch(error){await globalThis.appAlert(text[error.message]||text.failed,{title:text.title});}
}
globalThis.addEventListener?.('carrot:languagechange',localizeTrainingData);
