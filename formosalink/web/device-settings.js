import {mediaViewer} from './media-view.js?v=0.8.0';
import {parseCoordinates} from './navigation-input.js?v=0.6.0';
import {deviceHealth} from './health-ui.js?v=0.6.0';
import {SettingsEdits,pendingEdit,controlValue,sameValue,sameSettingValue} from './settings-edits.js?v=0.6.0';
// Full-page, owner-scoped device workspace. Only device receipts confirm writes.
export const sections=['home','live','device','toggles','models','steering','cruise','visuals','display','navigation','vehicle','software','developer'];
export function category(entry){const group=entry.group?.en?.toLowerCase();return sections.includes(group)?group:'device';}
export function routeFor(device,section){return '#device='+encodeURIComponent(device)+'&tab='+section;}
export function parseRoute(hash){const p=new URLSearchParams(hash.replace(/^#/,''));if(p.get('tab')==='maps')p.set('tab','navigation');return p.has('device')?{device:p.get('device'),section:sections.includes(p.get('tab'))?p.get('tab'):'device'}:null;}
export function filterEntries(catalog,section,query=''){
  const q=query.trim().toLocaleLowerCase();
  return catalog.filter(entry=>q?Object.values(entry.title||{}).join(' ').concat(' ',entry.key).toLocaleLowerCase().includes(q):category(entry)===section);
}
const paths={home:'m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z',devices:'M8 2h8v20H8z M11 18h2',device:'m4 8 2-4h12l2 4v10H4Z M4 11h16 M8 15h1m6 0h1',toggles:'M8 7h8a5 5 0 0 1 0 10H8A5 5 0 0 1 8 7Z M8 10v4',models:'M5 8h14v12H5Z M9 8V5h6v3 M9 12v4m6-4v4 M10 2h4',steering:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z M4 9h16 M12 10v11 M8 7h8',cruise:'M3 7h12a3 3 0 1 0-3-3 M3 12h16a3 3 0 1 1-3 3 M3 17h6',visuals:'M12 3a9 9 0 1 0 0 18h2a2 2 0 0 0 1-4 2 2 0 0 1 1-4h2a3 3 0 0 0 3-3c0-4-4-7-9-7Z M7 9h.01M11 6h.01M16 7h.01M6 14h.01',display:'M3 3h18v14H3Z M12 17v4 M8 21h8',maps:'m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2Z M9 3v16 M15 5v16',vehicle:'m5 8 2-4h10l2 4 2 3v7H3v-7Z M3 11h18 M6 18v3m12-3v3 M6 14h2m8 0h2',software:'m12 2 9 5v10l-9 5-9-5V7Z M3 7l9 5 9-5 M12 12v10 M7 4l10 6',developer:'m14 6 4 4 3-3a6 6 0 0 1-8 8l-7 7-4-4 7-7a6 6 0 0 1 8-8Z',search:'M16 10a6 6 0 1 1-12 0 6 6 0 0 1 12 0Z m-2 4 7 7',switch:'M3 7h17l-4-4 M21 17H4l4 4',pair:'M12 4v16 M4 12h16',menu:'M4 6h16 M4 12h16 M4 18h16',retry:'M20 7v6h-6 M20 12a8 8 0 1 0-2 6',close:'m5 5 14 14 M19 5 5 19'};
function icon(name){const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg'),path=document.createElementNS(ns,'path');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');svg.setAttribute('fill','none');svg.setAttribute('stroke','currentColor');svg.setAttribute('stroke-width','1.6');svg.setAttribute('stroke-linecap','round');svg.setAttribute('stroke-linejoin','round');path.setAttribute('d',paths[name==='navigation'?'maps':name]||paths.device);svg.append(path);return svg;}

export function deviceSettings({api,t,language,element:el,date,notify,getDevices,getAccount,onPair}) {
  const workspace=document.getElementById('settings-workspace'),$=id=>document.getElementById(id),body=$('settings-body');
  let selected=null,state=null,timer=null,epoch=0,writing=false,section='device',query='',previousFocus=null;
  const edits=new SettingsEdits();
  const viewer=mediaViewer({api,t,el});
  const label=value=>value?.[language()]||value?.en||'';
  const setRoute=()=>{const hash=routeFor(selected.id,section);if(location.hash!==hash)history.pushState(null,'',hash);};
  function close(updateRoute=true){viewer.close();selected=null;state=null;epoch++;clearTimeout(timer);body.replaceChildren();workspace.hidden=true;document.body.classList.remove('settings-open');workspace.classList.remove('menu-open');if(updateRoute&&parseRoute(location.hash))history.pushState(null,'','#dashboard');if(previousFocus?.isConnected)previousFocus.focus();}
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
    for(const [key,value] of Object.entries(snapshot.info).filter(([k])=>!["health_valid","soc_status","egpu_status","thermal_names","thermal_values","soc_detection","aux_soc_status"].includes(k)))dl.append(el('dt',t('info_'+key)),el('dd',Array.isArray(value)?value.join(', '):key==='cellular_data_enabled'?t(value?'cellularOn':'cellularOff'):key==='cellular_data_state'?t('cellularState_'+value):String(value??'—')));
    if(!dl.childElementCount)card.append(el('p',t('settingsWaiting'),'workspace-muted'));else card.append(dl);if('cellular_data_enabled' in snapshot.info)card.append(el('p',t('cellularLocalHelp'),'workspace-muted'));body.append(card);
  }
  function navigation(snapshot){
    const entry=(snapshot.catalog||[]).find(x=>x.key==='NavDestination'&&x.widget==='navigation');
    const card=el('section',undefined,'workspace-card');card.append(el('h2',t('navDestination')),el('p',t('navHelp'),'workspace-muted'));body.append(card);
    if(!entry){card.append(el('p',t('navUpgrade'),'workspace-muted'));return;}
    const deviceId=selected.id,key='NavDestination',draft=edits.get(deviceId,key);
    const form=el('form',undefined,'navigation-form');let current={};try{current=JSON.parse((draft&&draft.status!=='applied'?draft.value:snapshot.values[key])||'{}');}catch{}
    const pasteLabel=el('label',t('navPaste')),paste=el('input'),importButton=el('button',t('navImport'),'workspace-save');paste.type='text';paste.placeholder='25.0330, 121.5654';paste.setAttribute('aria-label',t('navPaste'));importButton.type='button';pasteLabel.append(paste);form.append(pasteLabel,importButton);
    const inputs={};for(const [key,type] of [['place_name','text'],['latitude','number'],['longitude','number']]){const label=el('label',t('nav_'+key)),input=el('input');input.type=type;input.required=true;input.setAttribute('aria-label',t('nav_'+key));input.value=current[key]??'';if(type==='number'){input.min=key==='latitude'?'-90':'-180';input.max=key==='latitude'?'90':'180';input.step='any';}else input.maxLength=120;label.append(input);form.append(label);inputs[key]=input;}
    const send=el('button',t('navSend'),'workspace-save');send.type='submit';
    const editable=state.fresh&&snapshot.offroad&&snapshot.remote_enabled&&entry.enabled;
    const enabled=editable&&!pendingEdit(draft)&&draft?.status!=='conflict';
    Object.entries(inputs).forEach(([name,n])=>{n.disabled=!enabled;n.dataset.field=name;});form.dataset.key=key;form.classList.add('setting-row');
    paste.disabled=!enabled;importButton.disabled=!enabled;
    const badge=el('span',undefined,'setting-sync');badge.setAttribute('role','status');card.append(badge);
    function status(){const d=edits.get(deviceId,key);badge.hidden=!d;badge.dataset.state=d?.status||'';badge.textContent=d?t('edit_'+d.status)+(d.reason&&['failed','uncertain'].includes(d.status)?' · '+t('reason_'+d.reason):''):'';send.disabled=!enabled||writing||state.commands.some(c=>['queued','delivered'].includes(c.status))||!d||!['draft','failed'].includes(d.status)||sameSettingValue(key,d.value,d.base)||controlValue(entry,d.value)===undefined;}
    function change(){edits.edit(deviceId,key,JSON.stringify({place_name:inputs.place_name.value,latitude:inputs.latitude.value===''?null:Number(inputs.latitude.value),longitude:inputs.longitude.value===''?null:Number(inputs.longitude.value)}),snapshot);status();}
    Object.values(inputs).forEach(n=>n.addEventListener('input',change));
    importButton.addEventListener('click',()=>{const value=parseCoordinates(paste.value);if(!value){notify('navInvalidCoordinates',true);return;}inputs.latitude.value=value.latitude;inputs.longitude.value=value.longitude;change();});
    form.append(send);card.append(form);if(!entry.enabled)card.append(el('p',t('navEnable'),'workspace-muted'));
    if(draft?.status==='conflict')card.append(conflictControls(deviceId,key,snapshot.values[key],draft,entry,editable));
    else if(draft&&!pendingEdit(draft)&&draft.status!=='applied'){const discard=el('button',t('editDiscard'));discard.type='button';discard.addEventListener('click',()=>{edits.discard(deviceId,key);draw();});card.append(discard);}
    card.append(el('p',t('editMemoryNote'),'settings-edit-note'));
    form.addEventListener('submit',event=>{event.preventDefault();if(!send.disabled)saveEdit(deviceId,key);});status();
  }
  function draw(){
    const active=document.activeElement, key=active?.closest('.setting-row')?.dataset.key, field=active?.dataset.field;
    const selection=active?.type==='text'?[active.selectionStart,active.selectionEnd]:null;
    renderBody();
    if(key&&field){const row=[...body.querySelectorAll('.setting-row')].find(n=>n.dataset.key===key);const target=row?.querySelector(`[data-field="${field}"]`);if(target&&!target.disabled){target.focus({preventScroll:true});if(selection)target.setSelectionRange(...selection);}}
  }
  function renderBody(){
    if(!selected)return;
    if(section==='live'&&!query){$('settings-title').textContent=t('section_live');$('settings-subtitle').textContent=t('sectionDesc_live');$('settings-banner-text').textContent=t('mediaPhase');$('settings-last-seen').textContent=t('received')+' '+date(state?.received_at);$('settings-retry-label').textContent=t('refresh');$('settings-connection').textContent=t(state?.fresh?'connected':'offline');viewer.open(body,selected.id);return;}
    viewer.close();body.replaceChildren();
    $('settings-title').textContent=query?t('searchResults'):t('section_'+section);
    $('settings-subtitle').textContent=query?`${t('searchSettings')} · ${query}`:t('sectionDesc_'+section);
    const snapshot=state?.snapshot,fresh=state?.fresh===true;
    $('settings-connection').textContent=t(fresh?'connected':'offline');$('settings-connection').classList.toggle('is-online',fresh);
    const status=!snapshot?'settingsWaiting':!fresh?'settingsOffline':!snapshot.offroad?'settingsDriving':!snapshot.remote_enabled?'settingsLocalDisabled':'settingsReady';
    $('settings-banner').classList.toggle('is-ready',fresh&&snapshot?.offroad&&snapshot?.remote_enabled);
    $('settings-banner-text').textContent=t(status);$('settings-last-seen').textContent=`${t('received')} ${date(state?.received_at)}`;$('settings-retry-label').textContent=t('refresh');
    if(!query&&section==='home'){$('settings-banner-text').textContent=t('fleetHealthNote');$('settings-banner').classList.remove('is-ready');deviceHealth(body,{devices:getDevices(),t,el,date,onOpen:d=>open(d,'device')});return;}
    if(!snapshot){body.append(el('div',t('settingsWaiting'),'workspace-card workspace-empty'));return;}
    if(!query&&['device','home'].includes(section))info(snapshot);
    if(!query&&['models'].includes(section)){const card=el('section',undefined,'workspace-card workspace-empty');card.append(icon(section),el('h2',t('section_'+section)),el('p',t('featureUnavailable'),'workspace-muted'));body.append(card);return;}
    if(!query&&section==='navigation'){navigation(snapshot);return;}
    const entries=filterEntries(snapshot.catalog||[],section,query);
    if(!entries.length){if(query||!['device','home'].includes(section))body.append(el('div',t(query?'noSearchResults':'noSectionSettings'),'workspace-card workspace-empty'));return;}
    const editable=fresh&&snapshot.offroad&&snapshot.remote_enabled;
    const list=el('section',undefined,'workspace-card settings-list');list.append(el('h2',t(query?'searchResults':'availableSettings')));body.append(list);
    for(const entry of entries.filter(x=>x.widget!=='navigation'))list.append(settingRow(entry,snapshot,editable));
    const note=el('p',t('editMemoryNote'),'settings-edit-note');body.append(note);
  }
  function settingRow(entry,snapshot,editable){
    const deviceId=selected.id,key=entry.key,current=snapshot.values[key],draft=edits.get(deviceId,key);
    const value=draft&&draft.status!=='applied'?draft.value:current;
    const row=el('form',undefined,'setting-row');row.dataset.key=key;
    const description=el('div',undefined,'setting-label');description.append(el('strong',label(entry.title)));
    if(query)description.append(el('small',label(entry.group),'workspace-muted'));
    if(label(entry.description)){const help=el('details',undefined,'setting-help');help.append(el('summary',t('settingDetails')),el('p',label(entry.description),'workspace-muted'));description.append(help);}
    if(entry.widget==='info'){row.append(description,el('span',String(current??'—')));return row;}
    const badge=el('span',undefined,'setting-sync');badge.setAttribute('role','status');description.append(badge);
    if(!entry.enabled)description.append(el('p',t('settingDisabled'),'workspace-muted'));
    const controls=el('div',undefined,'setting-controls'),editor=el('div',undefined,'setting-editor');
    const save=el('button',t('save'),'workspace-save');save.type='submit';save.dataset.field='save';
    const discard=el('button',t('editDiscard'),'setting-discard');discard.type='button';discard.dataset.field='discard';
    const blocked=!editable||!entry.enabled||pendingEdit(draft)||draft?.status==='conflict';
    const change=raw=>{const valid=controlValue(entry,raw);edits.edit(deviceId,key,valid===undefined?raw:valid,snapshot);refreshStatus();};
    function refreshStatus(){
      const d=edits.get(deviceId,key);badge.hidden=!d;badge.textContent=d?t('edit_'+d.status)+(d.reason&&['failed','uncertain'].includes(d.status)?' · '+t('reason_'+d.reason):''):'';badge.dataset.state=d?.status||'';
      save.disabled=!editable||!entry.enabled||writing||state.commands.some(c=>['queued','delivered'].includes(c.status))||!d||!['draft','failed'].includes(d.status)||sameSettingValue(key,d.value,d.base)||controlValue(entry,d.value)===undefined;
      discard.hidden=!d||d.status==='applied';discard.disabled=pendingEdit(d);
    }
    if(entry.type==='BOOL'){
      const input=el('input');input.type='checkbox';input.setAttribute('role','switch');input.checked=value===true;input.disabled=blocked;input.dataset.field='value';input.setAttribute('aria-label',label(entry.title));input.addEventListener('change',()=>change(input.checked));editor.append(input);
    }else if(entry.options&&entry.widget==='multiple_button'&&entry.options.length<=5){
      editor.classList.add('setting-segments');editor.setAttribute('role','group');editor.setAttribute('aria-label',label(entry.title));
      entry.options.forEach((option,index)=>{const b=el('button',label(option.label));b.type='button';b.dataset.field='option-'+index;b.disabled=blocked||!option.enabled;b.setAttribute('aria-pressed',String(sameValue(value,option.value)));b.addEventListener('click',()=>{change(option.value);for(const [i,node] of [...editor.children].entries())node.setAttribute('aria-pressed',String(i===index));});editor.append(b);});
    }else if(entry.options){
      const input=el('select');input.dataset.field='value';input.disabled=blocked;input.setAttribute('aria-label',label(entry.title));
      if(!entry.options.some(o=>sameValue(o.value,value))){const unknown=el('option',t('unknown'));unknown.value='';unknown.disabled=true;unknown.selected=true;input.append(unknown);}
      entry.options.forEach((option,index)=>{const node=el('option',label(option.label));node.value=String(index);node.disabled=!option.enabled;node.selected=sameValue(option.value,value);input.append(node);});
      input.addEventListener('change',()=>change(entry.options[Number(input.value)]?.value));editor.append(input);
    }else{
      const input=el('input');input.type=entry.type==='STRING'?'text':'number';input.value=String(value??'');input.required=true;input.disabled=blocked;input.dataset.field='value';input.setAttribute('aria-label',label(entry.title));
      if(entry.type==='STRING')input.maxLength=256;
      for(const bound of ['min','max','step'])if(entry[bound]!==undefined)input[bound]=String(entry[bound]);
      input.addEventListener('input',()=>change(input.value));
      if(entry.type!=='STRING'){
        editor.classList.add('setting-stepper');
        for(const [direction,text] of [[-1,'−'],[1,'+']]){const b=el('button',text);b.type='button';b.dataset.field=direction<0?'decrease':'increase';b.disabled=blocked;b.setAttribute('aria-label',t(direction<0?'settingDecrease':'settingIncrease')+' '+label(entry.title));b.addEventListener('click',()=>{const base=controlValue(entry,input.value);if(base===undefined)return;const next=Number(Math.min(entry.max,Math.max(entry.min,base+direction*entry.step)).toFixed(10));input.value=String(next);change(next);});editor.append(b);if(direction<0)editor.append(input);}
        description.append(el('small',`${t('settingRange')} ${entry.min} – ${entry.max} · ${t('settingStep')} ${entry.step}${entry.unit?' '+entry.unit:''}`,'workspace-muted'));
      }else editor.append(input);
    }
    if(entry.unit)editor.append(el('small',entry.unit));
    controls.append(editor,save,discard);row.append(description,controls);
    if(draft?.status==='conflict')row.append(conflictControls(deviceId,key,current,draft,entry,editable));
    discard.addEventListener('click',()=>{edits.discard(deviceId,key);draw();});
    row.addEventListener('submit',event=>{event.preventDefault();if(!save.disabled)saveEdit(deviceId,key);});
    refreshStatus();return row;
  }
  function conflictControls(deviceId,key,current,draft,entry,editable){
      const conflict=el('div',undefined,'setting-conflict');conflict.setAttribute('role','alert');
      const format=v=>{const option=entry.options?.find(o=>sameValue(o.value,v));return option?label(option.label):typeof v==='boolean'?t(v?'settingOn':'settingOff'):String(v??'—');};
      conflict.append(el('strong',t('editConflictTitle')),el('p',t('editDeviceValue')+' '+format(current)),el('p',t('editYourValue')+' '+format(draft.value)));
      const use=el('button',t('editUseDevice'));use.type='button';use.addEventListener('click',()=>{edits.discard(deviceId,key);draw();});
      const keep=el('button',t('editKeepMine'),'workspace-save');keep.type='button';keep.disabled=!editable||!entry.enabled;keep.addEventListener('click',()=>{edits.rebase(deviceId,key,state.snapshot);draw();});
      conflict.append(use,keep,el('small',t('editKeepHelp')));return conflict;
  }
  async function saveEdit(deviceId,key){
      if(writing||!selected||selected.id!==deviceId||!state?.fresh||!state.snapshot?.offroad||!state.snapshot?.remote_enabled||state.commands.some(c=>['queued','delivered'].includes(c.status)))return;
      const owner=edits.owner;const command=edits.begin(deviceId,key,state.snapshot);
      if(!command){draw();return;}const requestRow=edits.get(deviceId,key);writing=true;draw();
      try{const result=await api('/devices/'+encodeURIComponent(deviceId)+'/settings',command);if(edits.owner===owner&&edits.get(deviceId,key)===requestRow)edits.queued(deviceId,key,result);}
      catch(e){if(edits.owner===owner&&edits.get(deviceId,key)===requestRow)edits.failed(deviceId,key,e);}
      finally{writing=false;if(selected){draw();await poll();}}
  }
  async function poll(){
    clearTimeout(timer);if(!selected||writing)return;const currentEpoch=epoch;
    try{const result=await api('/devices/'+encodeURIComponent(selected.id)+'/settings');if(currentEpoch!==epoch)return;
      const focused=body.contains(document.activeElement)&&['INPUT','SELECT'].includes(document.activeElement.tagName);
      const before=JSON.stringify([...edits.rows(selected.id)]);edits.reconcile(selected.id,result);
      const changed=before!==JSON.stringify([...edits.rows(selected.id)])||!state||result.fresh!==state.fresh||result.snapshot?.revision!==state.snapshot?.revision||result.snapshot?.session!==state.snapshot?.session||result.snapshot?.offroad!==state.snapshot?.offroad||result.snapshot?.remote_enabled!==state.snapshot?.remote_enabled||JSON.stringify(result.commands)!==JSON.stringify(state.commands)||!focused&&JSON.stringify(result.snapshot?.info)!==JSON.stringify(state.snapshot?.info);state=result;
      if(changed||!body.childElementCount)draw();else $('settings-last-seen').textContent=`${t('received')} ${date(state.received_at)}`;
    }catch(e){if(currentEpoch!==epoch)return;if([401,404].includes(e.status)){if(e.status===401)edits.reset();else edits.devices.delete(selected.id);close();notify('settingsServiceUnavailable',true);return;}if(state)state.fresh=false;draw();}
    if(selected)timer=setTimeout(poll,3000);
  }
  function open(device,next='device',updateRoute=true){
    edits.scope(getAccount()?.id);
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
  return {open,close,reset(updateRoute=true){edits.reset();close(updateRoute);},translate(){if(selected){viewer.translate();nav();draw();}},route(){const route=parseRoute(location.hash);if(!route){if(selected)close(false);return;}const device=getDevices().find(d=>d.id===route.device&&d.state==='paired');if(!device){if(selected)close(false);return;}if(selected?.id!==device.id)open(device,route.section,false);else if(section!==route.section){section=route.section;query='';$('settings-search').value='';nav();draw();}},update(){edits.scope(getAccount()?.id);for(const id of edits.devices.keys())if(!getDevices().some(d=>d.id===id&&d.state==='paired'))edits.devices.delete(id);if(selected){const device=getDevices().find(d=>d.id===selected.id&&d.state==='paired');if(!device)close();else{selected=device;$('settings-device-label').textContent=device.name;if(section==='home'&&!query)draw();}}}};
}
