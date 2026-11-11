// Full-page, owner-scoped device workspace. Only device receipts confirm writes.
export const sections=['home','device','toggles','models','steering','cruise','visuals','display','maps','vehicle','software','developer'];
export function category(entry){const group=entry.group?.en?.toLowerCase();return sections.includes(group)?group:'device';}
export function routeFor(device,section){return '#device='+encodeURIComponent(device)+'&tab='+section;}
export function parseRoute(hash){const p=new URLSearchParams(hash.replace(/^#/,''));return p.has('device')?{device:p.get('device'),section:sections.includes(p.get('tab'))?p.get('tab'):'device'}:null;}
export function filterEntries(catalog,section,query=''){
  const q=query.trim().toLocaleLowerCase();
  return catalog.filter(entry=>q?Object.values(entry.title||{}).join(' ').concat(' ',entry.key).toLocaleLowerCase().includes(q):category(entry)===section);
}
const paths={home:'m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z',devices:'M8 2h8v20H8z M11 18h2',device:'m4 8 2-4h12l2 4v10H4Z M4 11h16 M8 15h1m6 0h1',toggles:'M8 7h8a5 5 0 0 1 0 10H8A5 5 0 0 1 8 7Z M8 10v4',models:'M5 8h14v12H5Z M9 8V5h6v3 M9 12v4m6-4v4 M10 2h4',steering:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z M4 9h16 M12 10v11 M8 7h8',cruise:'M3 7h12a3 3 0 1 0-3-3 M3 12h16a3 3 0 1 1-3 3 M3 17h6',visuals:'M12 3a9 9 0 1 0 0 18h2a2 2 0 0 0 1-4 2 2 0 0 1 1-4h2a3 3 0 0 0 3-3c0-4-4-7-9-7Z M7 9h.01M11 6h.01M16 7h.01M6 14h.01',display:'M3 3h18v14H3Z M12 17v4 M8 21h8',maps:'m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2Z M9 3v16 M15 5v16',vehicle:'m5 8 2-4h10l2 4 2 3v7H3v-7Z M3 11h18 M6 18v3m12-3v3 M6 14h2m8 0h2',software:'m12 2 9 5v10l-9 5-9-5V7Z M3 7l9 5 9-5 M12 12v10 M7 4l10 6',developer:'m14 6 4 4 3-3a6 6 0 0 1-8 8l-7 7-4-4 7-7a6 6 0 0 1 8-8Z',search:'M16 10a6 6 0 1 1-12 0 6 6 0 0 1 12 0Z m-2 4 7 7',switch:'M3 7h17l-4-4 M21 17H4l4 4',pair:'M12 4v16 M4 12h16',menu:'M4 6h16 M4 12h16 M4 18h16',retry:'M20 7v6h-6 M20 12a8 8 0 1 0-2 6',close:'m5 5 14 14 M19 5 5 19'};
function icon(name){const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg'),path=document.createElementNS(ns,'path');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.setAttribute('fill','none');svg.setAttribute('stroke','currentColor');svg.setAttribute('stroke-width','1.6');svg.setAttribute('stroke-linecap','round');svg.setAttribute('stroke-linejoin','round');path.setAttribute('d',paths[name]||paths.device);svg.append(path);return svg;}

export function deviceSettings({api,t,language,element:el,date,notify,getDevices,getAccount,onPair}) {
  const workspace=document.getElementById('settings-workspace'),$=id=>document.getElementById(id),body=$('settings-body');
  let selected=null,state=null,timer=null,epoch=0,writing=false,section='device',query='',previousFocus=null;
  const label=value=>value?.[language()]||value?.en||'';
  const setRoute=()=>{const hash=routeFor(selected.id,section);if(location.hash!==hash)history.pushState(null,'',hash);};
  function close(updateRoute=true){selected=null;state=null;epoch++;clearTimeout(timer);body.replaceChildren();workspace.hidden=true;document.body.classList.remove('settings-open');workspace.classList.remove('menu-open');if(updateRoute&&parseRoute(location.hash))history.pushState(null,'','#dashboard');if(previousFocus?.isConnected)previousFocus.focus();}
  function button(key,name,callback,className=''){const b=el('button',undefined,className);b.type='button';b.append(icon(name),el('span',t(key)));b.addEventListener('click',callback);return b;}
  function selectSection(next){section=next;query='';$('settings-search').value='';setRoute();nav();draw();workspace.classList.remove('menu-open');$('settings-title').focus();}
  function nav(){
    const links=$('settings-nav');links.replaceChildren();
    links.append(button('section_home','home',()=>selectSection('home')),button('myDevices','devices',()=>close()),el('div',t('deviceSettingsNav'),'workspace-nav-label'));
    for(const item of sections.filter(x=>x!=='home')){const b=button('section_'+item,item,()=>selectSection(item));b.dataset.section=item;b.classList.toggle('active',section===item);b.setAttribute('aria-current',section===item?'page':'false');links.append(b);}
    links.append(el('div',undefined,'workspace-nav-divider'),button('pairDevice','pair',onPair));
    const account=getAccount();$('settings-account').textContent=account?.github_login||account?.name||'FormosaLink';
    $('settings-device-label').textContent=selected.name;
    const choices=$('settings-device-options');choices.replaceChildren();
    for(const device of getDevices().filter(x=>x.state==='paired')){const b=el('button',device.name);b.type='button';b.setAttribute('aria-pressed',String(device.id===selected.id));b.addEventListener('click',()=>{open(device,section);$('settings-device-picker').open=false;});choices.append(b);}
    $('settings-search').placeholder=t('searchSettings');$('settings-search').setAttribute('aria-label',t('searchSettings'));
    $('settings-language').textContent={'zh-TW':'繁體中文',en:'English',ja:'日本語'}[language()];$('settings-language').setAttribute('aria-label',t('language'));const languages=$('settings-language-options');languages.replaceChildren();for(const [code,name] of Object.entries({'zh-TW':'繁體中文',en:'English',ja:'日本語'})){const choice=el('button',name);choice.type='button';choice.setAttribute('aria-pressed',String(language()===code));choice.addEventListener('click',()=>{document.querySelector(`[data-language="${code}"]`).click();$('settings-languages').open=false;});languages.append(choice);}
    $('settings-menu').setAttribute('aria-label',t('openMenu'));$('settings-menu-close').setAttribute('aria-label',t('close'));
    $('settings-change-label').textContent=t('changeDevice');$('settings-nav-title').textContent=t('deviceSettingsNav');
  }
  function info(snapshot){
    const card=el('section',undefined,'workspace-card information');card.append(el('h2',t('deviceInfo')));
    const dl=el('dl',undefined,'device-details');
    for(const [key,value] of Object.entries(snapshot.info))dl.append(el('dt',t('info_'+key)),el('dd',Array.isArray(value)?value.join(', '):String(value??'—')));
    if(!dl.childElementCount)card.append(el('p',t('settingsWaiting'),'workspace-muted'));else card.append(dl);body.append(card);
  }
  function draw(){
    if(!selected)return;body.replaceChildren();
    $('settings-title').textContent=query?t('searchResults'):t('section_'+section);
    $('settings-subtitle').textContent=query?`${t('searchSettings')} · ${query}`:t('sectionDesc_'+section);
    const snapshot=state?.snapshot,fresh=state?.fresh===true;
    $('settings-connection').textContent=t(fresh?'connected':'offline');$('settings-connection').classList.toggle('is-online',fresh);
    const status=!snapshot?'settingsWaiting':!fresh?'settingsOffline':!snapshot.offroad?'settingsDriving':!snapshot.remote_enabled?'settingsLocalDisabled':'settingsReady';
    $('settings-banner').classList.toggle('is-ready',fresh&&snapshot?.offroad&&snapshot?.remote_enabled);
    $('settings-banner-text').textContent=t(status);$('settings-last-seen').textContent=`${t('received')} ${date(state?.received_at)}`;$('settings-retry-label').textContent=t('refresh');
    if(!snapshot){body.append(el('div',t('settingsWaiting'),'workspace-card workspace-empty'));return;}
    if(!query&&['device','home'].includes(section))info(snapshot);
    if(state.commands.length){const latest=state.commands[0];const receipt=el('p',`${t('command_'+latest.status)}${latest.reason&&latest.reason!=='applied'?' · '+t('reason_'+latest.reason):''}`,'workspace-receipt');receipt.setAttribute('role','status');body.append(receipt);}
    if(!query&&['models','maps'].includes(section)){const card=el('section',undefined,'workspace-card workspace-empty');card.append(icon(section),el('h2',t('section_'+section)),el('p',t('featureUnavailable'),'workspace-muted'));body.append(card);return;}
    const entries=filterEntries(snapshot.catalog||[],section,query);
    if(!entries.length){if(query||!['device','home'].includes(section))body.append(el('div',t(query?'noSearchResults':'noSectionSettings'),'workspace-card workspace-empty'));return;}
    const editable=fresh&&snapshot.offroad&&snapshot.remote_enabled&&!writing&&!state.commands.some(c=>['queued','delivered'].includes(c.status));
    const list=el('section',undefined,'workspace-card settings-list');list.append(el('h2',t(query?'searchResults':'availableSettings')));body.append(list);
    for(const entry of entries){
      const row=el('form',undefined,'setting-row');row.dataset.key=entry.key;
      const description=el('div',undefined,'setting-label');description.append(el('strong',label(entry.title)));
      if(query)description.append(el('small',label(entry.group),'workspace-muted'));
      if(label(entry.description))description.append(el('p',label(entry.description),'workspace-muted'));row.append(description);
      const current=snapshot.values[entry.key];
      if(entry.widget==='info'){row.append(el('span',String(current??'—')));list.append(row);continue;}
      let input,read;
      if(entry.type==='BOOL'){input=el('input');input.type='checkbox';input.checked=current===true;read=()=>input.checked;}
      else if(entry.options){input=el('select');entry.options.forEach((option,index)=>{const node=el('option',label(option.label));node.value=String(index);node.disabled=!option.enabled;node.selected=option.value===current;input.append(node);});read=()=>entry.options[Number(input.value)].value;}
      else {input=el('input');input.type=entry.type==='STRING'?'text':'number';input.value=String(current??'');input.required=true;for(const bound of ['min','max','step'])if(entry[bound]!==undefined)input[bound]=String(entry[bound]);read=()=>entry.type==='STRING'?input.value:Number(input.value);}
      input.setAttribute('aria-label',label(entry.title));input.disabled=!editable||!entry.enabled;
      const controls=el('div',undefined,'setting-controls'),save=el('button',t('save'),'workspace-save');save.type='submit';save.disabled=input.disabled;
      controls.append(input);if(entry.unit)controls.append(el('small',entry.unit));controls.append(save);row.append(controls);
      row.addEventListener('submit',async event=>{event.preventDefault();if(!editable||writing||!selected)return;const deviceId=selected.id,requestEpoch=epoch;writing=true;workspace.querySelectorAll('.setting-controls button,.setting-controls input,.setting-controls select').forEach(node=>node.disabled=true);
        try{await api('/devices/'+encodeURIComponent(deviceId)+'/settings',{key:entry.key,value:read(),expected_revision:snapshot.revision,session:snapshot.session});if(requestEpoch===epoch)notify('settingsQueued');}
        catch(e){if(requestEpoch===epoch)notify('reason_'+(e.reason||'write_failed'),true);}
        finally{writing=false;if(selected){draw();await poll();}}
      });list.append(row);
    }
  }
  async function poll(){
    clearTimeout(timer);if(!selected||writing)return;const currentEpoch=epoch;
    try{const result=await api('/devices/'+encodeURIComponent(selected.id)+'/settings');if(currentEpoch!==epoch)return;
      const focused=body.contains(document.activeElement)&&['INPUT','SELECT'].includes(document.activeElement.tagName);
      const changed=!state||result.fresh!==state.fresh||result.snapshot?.revision!==state.snapshot?.revision||result.snapshot?.offroad!==state.snapshot?.offroad||result.snapshot?.remote_enabled!==state.snapshot?.remote_enabled||JSON.stringify(result.commands)!==JSON.stringify(state.commands)||!focused&&JSON.stringify(result.snapshot?.info)!==JSON.stringify(state.snapshot?.info);state=result;
      if(changed||!body.childElementCount)draw();else $('settings-last-seen').textContent=`${t('received')} ${date(state.received_at)}`;
    }catch(e){if(currentEpoch!==epoch)return;if([401,404].includes(e.status)){close();notify('settingsServiceUnavailable',true);return;}if(state)state.fresh=false;draw();}
    if(selected)timer=setTimeout(poll,3000);
  }
  function open(device,next='device',updateRoute=true){
    if(!selected)previousFocus=document.activeElement;
    close(false);selected=device;section=sections.includes(next)?next:'device';query='';$('settings-search').value='';workspace.hidden=false;document.body.classList.add('settings-open');
    if(updateRoute)setRoute();nav();draw();poll();$('settings-title').focus();
  }
  $('settings-device-picker').addEventListener('toggle',()=>{if(selected&&$('settings-device-picker').open)nav();});
  $('settings-search').addEventListener('input',event=>{query=event.target.value;draw();});
  $('settings-menu').append(icon('menu'));$('settings-menu-close').append(icon('close'));$('settings-search-icon').append(icon('search'));$('settings-change-icon').append(icon('switch'));$('settings-retry').prepend(icon('retry'));
  $('settings-menu').addEventListener('click',()=>workspace.classList.add('menu-open'));
  $('settings-menu-close').addEventListener('click',()=>{workspace.classList.remove('menu-open');$('settings-menu').focus();});
  $('settings-scrim').addEventListener('click',()=>workspace.classList.remove('menu-open'));
  $('settings-back').addEventListener('click',()=>close());$('settings-retry').addEventListener('click',poll);
  document.addEventListener('keydown',event=>{if(!selected)return;if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k'){event.preventDefault();$('settings-search').focus();}if(event.key==='Escape'){workspace.classList.remove('menu-open');$('settings-device-picker').open=false;}});
  document.addEventListener('click',event=>{if(!$('settings-device-picker').contains(event.target))$('settings-device-picker').open=false;});
  return {open,close,translate(){if(selected){nav();draw();}},route(){const route=parseRoute(location.hash);if(!route){if(selected)close(false);return;}const device=getDevices().find(d=>d.id===route.device&&d.state==='paired');if(!device){if(selected)close(false);return;}if(selected?.id!==device.id)open(device,route.section,false);else if(section!==route.section){section=route.section;query='';$('settings-search').value='';nav();draw();}},update(){if(selected){const device=getDevices().find(d=>d.id===selected.id&&d.state==='paired');if(!device)close();else{selected=device;$('settings-device-label').textContent=device.name;}}}};
}
