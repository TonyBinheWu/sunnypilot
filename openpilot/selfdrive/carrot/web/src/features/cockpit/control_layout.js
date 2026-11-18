// Dedicated cockpit controls composition. Existing input nodes and commit
// handlers are retained so validation, confirmation and readback stay shared.
export const CONTROL_SECTIONS=Object.freeze([
  {id:'controls',title:'控制',icon:'M4 10 7 4h10l3 6v9H4Zm0 4h16M7 19v2m10-2v2',groups:['START_AUTO','BUTTON_PRESET']},
  {id:'assist',title:'輔助駕駛',icon:'M4 19 10 4m10 15L14 4m-2 2v3m0 4v3',groups:['CRUISE','SPEED','TESLA']},
  {id:'steering',title:'轉向',icon:'M20 12a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM4 10h16m-8 2v8',groups:['STEER']},
  {id:'vehicle',title:'車輛',icon:'M3 15V9l3-4h12l3 4v6M3 12h18M6 15v4m12-4v4',groups:['VEH_HYUNDAI','VEH_CANFD','VEH_RADAR','VEH_AUX']},
  {id:'display',title:'顯示',icon:'M3 4h18v13H3Zm5 17h8m-4-4v4',groups:['DISP_SCREEN','DISP_PATH','DISP_BRIGHT','DISP_HUD']},
  {id:'navigation',title:'導航',icon:'m12 3 8 18-8-5-8 5Z',groups:['SYS_NET']},
  {id:'safety',title:'安全',icon:'m12 3 8 3v6c0 5-8 9-8 9S4 17 4 12V6Zm-4 9 3 3 5-6',groups:['VEH_DM']},
  {id:'recording',title:'行車紀錄',icon:'M3 5h13v14H3Zm13 5 5-3v10l-5-3',groups:['SYS_RECORD','SYS_CAMERA']},
  {id:'sound',title:'聲音',icon:'m3 9 5 0 5-5v16l-5-5H3Zm13-2c4 3 4 7 0 10',groups:['SYS_SOUND']},
  {id:'service',title:'服務',icon:'m4 20 8-8m-1-8a6 6 0 0 0 8 8l-4-4 3-4a6 6 0 0 0-7 0Z',groups:['VEH_DEVICE']},
  {id:'software',title:'軟體',icon:'M12 3v13m-5-5 5 5 5-5M4 18v3h16v-3',groups:['SYS_SW']},
]);
const label=g=>g?.['zh-tw']||g?.tgroup||g?.en||g?.egroup||g?.ko||g?.group||g?.id||'';
export function cockpitControlSections(catalog={}){
  const groups=new Map((catalog.categories||[]).flatMap(c=>c.groups||[]).map(g=>[g.id,{id:g.id,label:label(g)}]));
  const used=new Set();
  const sections=CONTROL_SECTIONS.flatMap(section=>{
    const entries=section.groups.filter(id=>groups.has(id)).map(id=>{used.add(id);return groups.get(id);});
    return entries.length?[{...section,groups:entries}]:[];
  });
  const extras=[...groups.values()].filter(g=>!used.has(g.id));
  if(!groups.size)for(const g of catalog.groups||[])if(g?.group)extras.push({id:g.group,label:label(g)});
  if(extras.length)sections.push({id:'other',title:'其他設定',icon:'M5 5h14v14H5Zm4 4h6m-6 6h6',groups:extras});
  return sections;
}
const decorated=new WeakSet();
export function composeCockpitControl(row,target){
  if(decorated.has(row))return false;
  const doc=row.ownerDocument,top=row.querySelector('.settingTop'),copy=top?.querySelector('.setting-copy'),ctrl=top?.querySelector('.ctrl');
  if(!copy||!ctrl)return false;
  decorated.add(row);row.classList.add('cockpit-control-row');
  const title=copy.querySelector('.setting-title-row'),description=row.querySelector('.descr'),oldHelp=description?.closest('.cockpit-help'),actions=row.querySelector('.setting-actions');
  const remaining=[...row.children].filter(n=>![top,description,oldHelp,actions].includes(n));
  const create=(tag,cls,text)=>{const n=doc.createElement(tag);n.className=cls;if(text)n.textContent=text;return n;};
  const main=create('div','cockpit-control-main'),head=create('div','cockpit-control-heading'),buttons=create('div','cockpit-control-tools');
  if(title)head.append(title);else head.append(create('h3','',row.dataset.settingName));
  const info=create('button','cockpit-control-info-button','ⓘ');info.type='button';info.setAttribute('aria-label','功能說明');info.setAttribute('aria-expanded','false');
  const more=create('button','cockpit-control-more','⋯');more.type='button';more.setAttribute('aria-label','詳細指南、熱門值與修改歷史');
  const details=create('details','cockpit-help cockpit-control-info'),summary=create('summary','','功能說明與還原');
  summary.addEventListener('click',e=>e.stopPropagation());details.append(summary,copy);if(description)details.append(description);if(actions)details.append(actions);
  info.onclick=e=>{e.stopPropagation();details.open=!details.open;};
  details.addEventListener('toggle',()=>info.setAttribute('aria-expanded',String(details.open)));
  // Dispatch the original row action: it knows the real originating group,
  // search/detail state and how to load description/popular/history tabs.
  more.onclick=e=>{e.stopPropagation();if(typeof row.onclick==='function')row.click();else doc.getElementById('items')?.querySelector('.setting-context')?.scrollIntoView({block:'nearest'});};
  buttons.append(info,more);head.append(buttons);main.append(head,ctrl);row.replaceChildren(main,details,...remaining);
  return true;
}
const installed=new WeakMap();
export function installCockpitControlLayout(doc,target=doc.defaultView,{onAction}={}){
  if(installed.has(doc))return installed.get(doc);
  const page=doc.getElementById('pageSetting'),host=doc.getElementById('settingScreenHost');
  if(!page||!host||doc.documentElement?.nodeType!==1)return null;
  const create=(tag,cls,text)=>{const n=doc.createElement(tag);n.className=cls;if(text)n.textContent=text;return n;};
  const shell=create('div','cockpit-controls'),nav=create('nav','cockpit-control-nav'),pane=create('section','cockpit-control-pane');
  nav.setAttribute('aria-label','座艙設定分類');
  const navTitle=create('div','cockpit-control-brand','CARROT'),navList=create('div','cockpit-control-nav-list');nav.append(navTitle,navList);
  const header=create('header','cockpit-control-header'),heading=create('h2','','控制'),searchSlot=create('div','setting-inline-search-slot cockpit-control-search-slot');
  const categoryToggle=create('button','cockpit-category-toggle','☰ 分類');categoryToggle.type='button';categoryToggle.setAttribute('aria-label','開啟設定分類');categoryToggle.setAttribute('aria-expanded','false');
  const dismissNav=create('button','cockpit-nav-dismiss');dismissNav.type='button';dismissNav.setAttribute('aria-label','關閉設定分類');
  const setNav=open=>{const wasOpen=shell.dataset.navOpen==='true';shell.dataset.navOpen=String(open);categoryToggle.setAttribute('aria-expanded',String(open));pane.inert=open;
    if(open)(navList.querySelector('.selected')||navList.querySelector('button'))?.focus();else if(wasOpen)categoryToggle.focus();};
  categoryToggle.onclick=()=>setNav(shell.dataset.navOpen!=='true');dismissNav.onclick=()=>setNav(false);
  target.matchMedia?.('(max-width: 820px)').addEventListener?.('change',()=>setNav(false));
  shell.addEventListener('keydown',event=>{if(event.key==='Escape'&&shell.dataset.navOpen==='true'){setNav(false);categoryToggle.focus();event.stopPropagation();}});
  const back=create('button','cockpit-control-back','‹');back.type='button';back.hidden=true;back.setAttribute('aria-label','返回設定列表');back.onclick=()=>target.history.back();
  const searchForm=doc.getElementById('settingInlineSearch');if(searchForm)searchSlot.append(searchForm);
  const menu=doc.getElementById('btnSettingSearch')||create('button','cockpit-control-menu','⋯');menu.classList.add('cockpit-control-menu');menu.type='button';menu.setAttribute('aria-label','設定檔、收藏與其他操作');
  header.append(categoryToggle,back,heading,searchSlot,menu);
  const tabs=create('div','cockpit-control-tabs'),results=create('div','cockpit-control-results'),message=create('p','cockpit-control-message');
  const overview=create('section','cockpit-quick-controls');overview.hidden=true;overview.setAttribute('aria-label','常用控制');
  const quick=[['profile','駕駛模式','選擇既有行車模式','M4 18a8 8 0 1 1 16 0M12 14l4-5'],['vision','鏡頭與辨識','連線與辨識狀態','M3 5h18v14H3ZM16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z'],['vehicle','車況','胎壓與目前導航','M3 15V9l3-4h12l3 4v6M3 12h18M6 15v4m12-4v4'],['display','顯示','外觀與文字大小','M3 4h18v13H3Zm5 17h8m-4-4v4'],['connection','連線','裝置狀態與重新連線','M3 9a14 14 0 0 1 18 0M6 12a9 9 0 0 1 12 0m-8 4a3 3 0 0 1 4 0M12 20h.01'],['diagnostics','診斷與工具','檢查問題與服務','M4 20l8-8m-1-8a6 6 0 0 0 8 8l-4-4 3-4a6 6 0 0 0-7 0Z']];
  if(onAction)for(const [action,title,subtitle,path] of quick){const b=create('button','cockpit-quick-control');b.type='button';b.setAttribute('aria-label',title);const svg=doc.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');const p=doc.createElementNS(svg.namespaceURI,'path');p.setAttribute('d',path);svg.append(p);b.append(svg,create('strong','',title),create('small','',subtitle));b.onclick=()=>onAction(action);overview.append(b);}
  const start=create('button','cockpit-quick-settings','啟動與按鈕設定　›');start.type='button';start.onclick=()=>{const group=current?.groups[0];if(group)void selectGroup(group);};overview.append(start);
  results.hidden=true;message.setAttribute('role','status');
  const device=doc.getElementById('deviceTabContent'),deviceNav=create('div','cockpit-control-device');if(device)deviceNav.append(device);
  pane.append(header,tabs,message,results,overview,deviceNav,host);shell.append(dismissNav,nav,pane);page.prepend(shell);doc.documentElement.classList.add('cockpit-controls-mode');
  let catalog=null,sections=[],current=null,loading=false,selection=0,pendingSection=null;
  const lastGroups=new Map();
  const clearSearch=()=>{target.exitSettingInlineSearchSurface?.();results.hidden=true;host.hidden=false;};
  async function selectGroup(group){
    shell.dataset.overview='false';overview.hidden=true;
    const token=++selection;clearSearch();setNav(false);shell.dataset.device='false';searchSlot.hidden=false;await target.switchSettingTab?.('carrot');if(token!==selection)return;
    if(current)lastGroups.set(current.id,group.id);target.selectGroup?.(group.id,false);
    tabs.querySelectorAll('button').forEach(b=>{const active=b.dataset.group===group.id;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));});
  }
  function choose(section){
    current=section;setNav(false);heading.textContent=section.title;tabs.replaceChildren();
    navList.querySelectorAll('button').forEach(b=>{const active=b.dataset.section===section.id;b.classList.toggle('selected',active);b.setAttribute('aria-current',active?'page':'false');});
    for(const group of section.groups){const button=create('button','',group.label);button.type='button';button.dataset.group=group.id;button.onclick=()=>{void selectGroup(group);};tabs.append(button);}
    const group=section.groups.find(g=>g.id===lastGroups.get(section.id))||section.groups[0];if(group)void selectGroup(group);
    if(section.id==='controls'&&onAction){shell.dataset.overview='true';overview.hidden=false;}
  }
  function renderNav(){
    navList.replaceChildren();
    for(const section of sections){
      const button=create('button','');button.type='button';button.dataset.section=section.id;
      const svg=doc.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');const path=doc.createElementNS(svg.namespaceURI,'path');path.setAttribute('d',section.icon);svg.append(path);
      button.append(svg,create('span','',section.title));button.onclick=()=>choose(section);navList.append(button);
    }
    const favorite=create('button','','收藏');favorite.type='button';favorite.dataset.section='favorites';favorite.onclick=()=>choose({id:'favorites',title:'收藏',groups:[{id:'__setting_favorites__',label:'收藏設定'}]});navList.append(favorite);
    const deviceButton=create('button','','裝置');deviceButton.type='button';deviceButton.onclick=async()=>{
      const token=++selection;clearSearch();setNav(false);shell.dataset.device='true';searchSlot.hidden=true;heading.textContent='裝置';tabs.replaceChildren();
      navList.querySelectorAll('button').forEach(b=>{b.classList.remove('selected');b.setAttribute('aria-current','false');});deviceButton.classList.add('selected');deviceButton.setAttribute('aria-current','page');await target.switchSettingTab?.('device');if(token!==selection)return;
      doc.querySelector('#deviceGroupList button')?.click();
    };navList.append(deviceButton);
  }
  async function load(){
    if(loading||catalog)return;loading=true;message.textContent='正在讀取可用設定…';
    const controller=new target.AbortController(),timer=target.setTimeout(()=>controller.abort(),5000);
    try{
      const response=await target.fetch('/api/settings',{cache:'no-store',credentials:'same-origin',signal:controller.signal});if(!response.ok)throw Error();
      catalog=await response.json();sections=cockpitControlSections(catalog);renderNav();message.textContent='';
      if(sections.length)choose(sections.find(s=>s.id===pendingSection)||sections[0]);else message.textContent='車機尚未提供可用設定。';pendingSection=null;
    }catch{message.textContent='無法讀取設定分類，請確認車機連線後重新開啟控制面板。';}
    finally{target.clearTimeout(timer);loading=false;}
  }
  // Keep the canonical search form/input and its voice/search state. On narrow
  // screens, move the original result surface out of the retired group list.
  const syncSearch=()=>{
    const nativeResults=doc.getElementById('settingInlineSearchResults');
    if(nativeResults&&nativeResults.parentElement!==pane){pane.insertBefore(nativeResults,host);observer.observe(nativeResults,{childList:true,subtree:true});decorate(nativeResults);}
    const detail=doc.getElementById('settingScreenItems')?.classList.contains('setting-screen-items--detail')===true;
    back.hidden=!detail;
    const inline=!detail&&doc.getElementById('carrotTabContent')?.classList.contains('is-inline-search')===true;
    shell.dataset.search=String(inline);if(nativeResults)nativeResults.hidden=!inline;
    overview.hidden=shell.dataset.overview!=='true'||inline||detail;
  };
  const decorate=node=>{if(node.nodeType!==1)return;if(node.matches('.setting'))composeCockpitControl(node,target);for(const row of node.querySelectorAll('.setting'))composeCockpitControl(row,target);};
  const observer=new target.MutationObserver(records=>{for(const record of records)for(const node of record.addedNodes)decorate(node);syncSearch();});observer.observe(host,{childList:true,subtree:true});const nativeSearch=doc.getElementById('carrotTabContent');if(nativeSearch)observer.observe(nativeSearch,{childList:true,subtree:true,attributes:true,attributeFilter:['class']});const itemsScreen=doc.getElementById('settingScreenItems');if(itemsScreen)observer.observe(itemsScreen,{attributes:true,attributeFilter:['class']});decorate(host);syncSearch();
  const active=()=>{if(doc.body.dataset.cockpitPanel==='setting')void load();};target.addEventListener('carrot:cockpitpanelchange',active);active();
  const api={shell,refresh:active,selectSection(id){const section=sections.find(s=>s.id===id);if(section)choose(section);else pendingSection=id;}};installed.set(doc,api);target.CarrotCockpitControls=api;return api;
}
