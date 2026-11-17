// Owner consent uses the existing authenticated same-origin API, not monitoring consent.
export async function contributionDialog(device, api, language='zh-TW') {
  const labels = {
    'zh-TW':['訓練資料授權','同意並自動上傳','停止未來上傳','關閉','已授權','未授權','已上傳'],
    en:['Training data','Agree and upload','Stop future uploads','Close','Authorized','Disabled','Uploaded'],
    ja:['学習データ提供','同意して自動送信','今後の送信を停止','閉じる','同意済み','未同意','送信済み'],
  }[language] || ['Training data','Agree and upload','Stop future uploads','Close','Authorized','Disabled','Uploaded'];
  const path='/devices/'+encodeURIComponent(device.id)+'/training';
  const dialog=document.createElement('dialog');
  const title=document.createElement('h2'), notice=document.createElement('p'), state=document.createElement('p');
  title.textContent=labels[0];
  const status=await api(path);
  notice.textContent=status.notice[language]||status.notice.en;
  state.textContent=`${status.consent.enabled?labels[4]:labels[5]} · ${labels[6]} ${(status.uploads.bytes/1024**2).toFixed(1)} MiB`;
  dialog.append(title,notice,state);
  for(const [text,enabled] of [[labels[1],true],[labels[2],false],[labels[3],null]]) {
    const button=document.createElement('button');button.type='button';button.textContent=text;
    button.addEventListener('click',async()=>{
      if(enabled===null){dialog.close();return;}
      button.disabled=true;
      try{await api(path,{policy:status.policy,enabled,expected_revision:status.consent.revision});dialog.close();}
      catch(error){state.textContent=error.reason||'Unable to update; close and refresh.';}
      finally{button.disabled=false;}
    });dialog.append(button);
  }
  dialog.addEventListener('close',()=>dialog.remove(),{once:true});
  document.body.append(dialog);dialog.showModal();
}
