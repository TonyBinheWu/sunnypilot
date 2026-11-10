// Owner-scoped details. A queued request is never presented as an applied value.
export function deviceSettings({api,t,language,element:el,date,notify}) {
  const dialog=document.getElementById('settings-dialog'), body=document.getElementById('settings-body');
  let selected=null, state=null, timer=null, epoch=0, writing=false;
  const label=value=>value?.[language()]||value?.en||'';
  const close=()=>{selected=null;state=null;epoch++;clearTimeout(timer);body.replaceChildren();if(dialog.open)dialog.close();};
  document.getElementById('close-settings').addEventListener('click',close);
  dialog.addEventListener('close',close);
  function draw() {
    body.replaceChildren();
    document.getElementById('settings-title').textContent=selected.name;
    const snapshot=state?.snapshot;
    if(!snapshot){body.append(el('p',t('settingsWaiting'),'caption'));return;}
    const editable=state.fresh&&snapshot.offroad&&snapshot.remote_enabled&&!writing&&!state.commands.some(c=>['queued','delivered'].includes(c.status));
    const status=!state.fresh?'settingsOffline':!snapshot.offroad?'settingsDriving':!snapshot.remote_enabled?'settingsLocalDisabled':'settingsReady';
    body.append(el('p',t(status),'settings-status'),el('p',`${t('received')} ${date(state.received_at)}`,'caption'));
    const information=el('details',undefined,'information');information.open=true;
    information.append(el('summary',t('deviceInfo')));
    const dl=el('dl',undefined,'device-details');
    for(const [key,value] of Object.entries(snapshot.info))dl.append(el('dt',t('info_'+key)),el('dd',Array.isArray(value)?value.join(', '):String(value??'—')));
    information.append(dl);body.append(information);
    if(state.commands.length){const latest=state.commands[0];body.append(el('p',`${t('command_'+latest.status)}${latest.reason&&latest.reason!=='applied'?' · '+t('reason_'+latest.reason):''}`,'command-status'));}
    const search=el('input');search.type='search';search.placeholder=t('searchSettings');search.setAttribute('aria-label',t('searchSettings'));body.append(search);
    const list=el('div',undefined,'settings-list');body.append(list);
    let group='';
    for(const entry of snapshot.catalog||[]){
      const groupLabel=label(entry.group);
      if(group!==groupLabel){group=groupLabel;const h=el('h3',group);list.append(h);}
      const row=el('form',undefined,'setting-row');row.dataset.search=(label(entry.title)+' '+entry.key).toLocaleLowerCase();
      const description=el('div',undefined,'setting-label');description.append(el('strong',label(entry.title)));
      if(label(entry.description))description.append(el('p',label(entry.description),'caption'));
      row.append(description);
      const current=snapshot.values[entry.key];
      if(entry.widget==='info'){row.append(el('span',String(current??'—')));list.append(row);continue;}
      let input,read;
      if(entry.type==='BOOL'){
        input=el('input');input.type='checkbox';input.checked=current===true;read=()=>input.checked;
      }else if(entry.options){
        input=el('select');entry.options.forEach((option,index)=>{const node=el('option',label(option.label));node.value=String(index);node.disabled=!option.enabled;node.selected=option.value===current;input.append(node);});
        read=()=>entry.options[Number(input.value)].value;
      }else{
        input=el('input');input.type=entry.type==='STRING'?'text':'number';input.value=String(current??'');
        input.required=true;
        for(const bound of ['min','max','step'])if(entry[bound]!==undefined)input[bound]=String(entry[bound]);
        read=()=>entry.type==='STRING'?input.value:Number(input.value);
      }
      input.setAttribute('aria-label',label(entry.title));input.disabled=!editable||!entry.enabled;
      const controls=el('div',undefined,'setting-controls'),save=el('button',t('save'),'secondary');save.type='submit';save.disabled=input.disabled;
      controls.append(input);if(entry.unit)controls.append(el('small',entry.unit));controls.append(save);row.append(controls);
      row.addEventListener('submit',async event=>{event.preventDefault();if(!editable||writing)return;writing=true;input.disabled=true;save.disabled=true;
        try{await api('/devices/'+encodeURIComponent(selected.id)+'/settings',{key:entry.key,value:read(),expected_revision:snapshot.revision,session:snapshot.session});notify('settingsQueued');}
        catch(e){notify('reason_'+(e.reason||'write_failed'),true);}
        finally{writing=false;await poll();}
      });list.append(row);
    }
    search.addEventListener('input',()=>{for(const row of list.querySelectorAll('.setting-row'))row.hidden=!row.dataset.search.includes(search.value.toLocaleLowerCase());});
  }
  async function poll(){
    clearTimeout(timer);if(!selected||writing)return;const currentEpoch=epoch;
    try{const result=await api('/devices/'+encodeURIComponent(selected.id)+'/settings');if(currentEpoch!==epoch)return;
      // Preserve edits and focus while polling an unchanged snapshot.
      const focused=body.contains(document.activeElement)&&['INPUT','SELECT'].includes(document.activeElement.tagName);
      const changed=!state||result.fresh!==state.fresh||result.snapshot?.revision!==state.snapshot?.revision||result.snapshot?.offroad!==state.snapshot?.offroad||result.snapshot?.remote_enabled!==state.snapshot?.remote_enabled||JSON.stringify(result.commands)!==JSON.stringify(state.commands)||!focused&&JSON.stringify(result.snapshot?.info)!==JSON.stringify(state.snapshot?.info);state=result;
      if(changed||!body.childElementCount)draw();
    }catch(e){if(currentEpoch!==epoch)return;if([401,404].includes(e.status)){close();notify('settingsServiceUnavailable',true);return;}if(state)state.fresh=false;draw();}
    if(selected)timer=setTimeout(poll,3000);
  }
  return {open(device){close();selected=device;document.getElementById('settings-title').textContent=device.name;dialog.showModal();body.append(el('p',t('settingsWaiting')));poll();},close,translate(){if(selected)draw();}};
}
