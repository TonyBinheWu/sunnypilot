import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const connection=readFileSync(new URL('../js/realtime/compact_connection.js',import.meta.url),'utf8');
const bundle=readFileSync(new URL('../js/generated/cockpit.js',import.meta.url),'utf8');
const html=readFileSync(new URL('../cockpit.html',import.meta.url),'utf8');
function harness(){
  const nodes=new Map(),writes=[],pages=[],hud=[],intervals=[],timers=new Map(),events={},docEvents={};let timerId=0;let mode=3,clock=0,seq=0,rejectPost=false;
  function element(id=''){
    const classes=new Set(),listeners={};
    return {id,hidden:false,dataset:{},textContent:'',disabled:false,href:'/css/cockpit-embedded.css',
      classList:{contains:x=>classes.has(x),toggle(x,force){const next=force??!classes.has(x);if(next)classes.add(x);else classes.delete(x);return next;},add:x=>classes.add(x),remove:x=>classes.delete(x)},
      addEventListener:(name,fn)=>{listeners[name]=fn;},emit:name=>listeners[name]?.(),append(){},replaceChildren(...children){this.children=children;},setAttribute(name,value){this[name]=value;},focus(){},
      close(){this.open=false;listeners.close?.();},showModal(){this.open=true;},getBoundingClientRect:()=>({width:480,height:320}),getContext:()=>new Proxy({measureText:()=>({width:20})},{get:(t,k)=>t[k]??(()=>{}),set:(t,k,v)=>(t[k]=v,true)})};
  }
  for(const [,id] of html.matchAll(/id="([^"]+)"/g))nodes.set(id,element(id));
  const buttons=[1,2,3,4].map(mode=>Object.assign(element(),{dataset:{mode:String(mode)}}));
  const panels=['navigation','vision','logs','setting','tools'].map(panel=>Object.assign(element(),{dataset:{panel}}));
  const document={hidden:false,body:element(),documentElement:{...element(),style:{setProperty(){}}},head:element(),
    getElementById:id=>nodes.get(id),querySelector:()=>null,querySelectorAll:s=>s==='[data-mode]'?buttons:s==='[data-panel]'?panels:[],
    addEventListener:(name,fn)=>{docEvents[name]=fn;},createElement:()=>element()};
  const innerDocument={...document,documentElement:{...element(),hasAttribute:()=>true}};
  nodes.get('features').contentWindow={location:{origin:'http://fixture'},document:innerDocument,showPage:p=>pages.push(p),
    DriveVisionHudContent:{update:p=>hud.push(p)},
    CarrotLocalVoice:{findSettings:(...a)=>a.join('|'),cruise:(...a)=>a.join('|'),result:id=>id}};
  for(const p of panels)if(['logs','tools'].includes(p.dataset.panel))p.closest=()=>nodes.get('apps');
  nodes.get('navigation').contentWindow={location:{origin:'http://fixture'}};
  nodes.get('navigation').contentDocument=innerDocument;
  const sockets=[];
  const context={document,location:{origin:'http://fixture',host:'fixture',protocol:'http:'},performance:{now:()=>clock},
    devicePixelRatio:1,console,Date,Proxy,localStorage:{getItem:()=>null,setItem(){}},
    addEventListener:(name,fn)=>{events[name]=fn;},setTimeout:(fn,ms)=>{const id=++timerId;timers.set(id,{fn,at:clock+ms});return id;},clearTimeout:id=>timers.delete(id),setInterval:fn=>(intervals.push(fn),1),
    WebSocket:class {readyState=1;listeners={};sent=[];constructor(){sockets.push(this);}addEventListener(n,f){this.listeners[n]=f;}removeEventListener(n){delete this.listeners[n];}send(data){this.sent.push(data);}close(){this.readyState=3;this.onclose?.();}},
    CarrotVisionCompact:{decodeFrames:data=>data.frames},
    async fetch(url,options){
      if(options?.method==='POST'){const body=JSON.parse(options.body);writes.push(body);mode=body.value;if(rejectPost)throw Error('lost response');}
      return {ok:true,json:async()=>({values:{MyDrivingMode:mode,MyDrivingModeAuto:0}})};
    },
    confirm(){throw Error('Native confirm dialogs must not be used');}};
  context.window=context;vm.runInNewContext(connection,context);vm.runInNewContext(bundle,context);
  nodes.get('features').emit('load');
  function send(service,decoded){const data=new Uint8Array(1);data.frames=[{service,decoded,sequence:seq++}];sockets.at(-1).onmessage({data});}
  function park(){send('carState',{gearShifter:'park',vEgo:0,vEgoCluster:0});send('selfdriveState',{enabled:false});send('carControl',{latActive:false,longActive:false});}
  return {docEvents,frame:nodes.get('features').contentWindow,register:(id,node)=>nodes.set(id,node),sockets,events,timers,run(ms){for(let end=clock+ms;clock<end;){clock=Math.min(end,clock+1000);for(const [id,t] of [...timers])if(t.at<=clock){timers.delete(id);t.fn();}}},el:id=>nodes.get(id),mode:n=>buttons[n-1],panel:p=>panels.find(b=>b.dataset.panel===p),writes,pages,send,park,context,
    advance:ms=>{clock+=ms;},tick:()=>intervals.forEach(fn=>fn()),hud,reject:()=>{rejectPost=true;},flush:()=>new Promise(setImmediate)};
}
test('camera-independent cockpit sends one explicit expiry and never retains its last speed',()=>{
  const h=harness();h.send('carState',{gearShifter:'drive',vEgoCluster:10,vCruiseCluster:90});h.tick();
  assert.equal(h.hud.at(-1).vEgoKph,36);
  h.advance(1600);h.tick();assert.equal(h.hud.at(-1).sourceStale,true);assert.equal(h.hud.at(-1).vEgoKph,undefined);
  const count=h.hud.length;h.tick();assert.equal(h.hud.length,count);
  h.send('carState',{gearShifter:'park',vEgoCluster:0,vCruiseCluster:90});h.tick();assert.equal(h.hud.at(-1).vEgoKph,0);assert.equal(h.hud.at(-1).sourceStale,undefined);
});
test('leaving navigation closes its search sheet before it becomes a mini map',()=>{
  const h=harness(),body=h.el('navigation').contentDocument.body;
  body.classList.add('search-open');h.panel('vision').onclick();
  assert.equal(body.classList.contains('search-open'),false);assert.equal(h.writes.length,0);
});
test('mobile navigation search closes without refocusing its hidden input; Back and panel changes dismiss it',()=>{
  const h=harness();let focused=0,blurred=0;h.register('query',{focus:()=>focused++,blur:()=>blurred++});
  h.panel('navigation').onclick();h.el('searchNav').onclick();assert.equal(focused,1);assert.equal(h.el('searchNav')['aria-expanded'],'true');
  h.el('searchNav').onclick();assert.equal(focused,1);assert.equal(blurred,1);assert.equal(h.el('searchNav')['aria-expanded'],'false');
  h.el('searchNav').onclick();assert.equal(h.context.CarrotCockpit.back(),true);assert.equal(blurred,2);assert.equal(h.context.document.body.dataset.panel,'navigation');
  h.el('searchNav').onclick();h.panel('vision').onclick();assert.equal(blurred,3);assert.equal(h.el('searchNav')['aria-expanded'],'false');assert.equal(h.writes.length,0);
});

test('road shortcuts and preview expansion retain the classified Vision renderer and its preferences',()=>{
  const h=harness();
  h.frame.CarrotWebSettingsState={vision_object_detection:true,vision_presentation:'bev'};
  let cameraStarts=0;h.register('btnStartVision',{disabled:false,click:()=>cameraStarts++});
  for(const entry of ['expand','sceneMode']){
    h.panel('navigation').onclick();h.el('appsButton').onclick();h.el(entry).onclick();h.tick();
    assert.equal(h.context.document.body.dataset.panel,'vision');
    assert.equal(h.context.document.body.classList.contains('scene-full'),false);
    assert.equal(h.el('features').hidden,false);assert.equal(h.pages.at(-1),'carrot');
    assert.equal(h.el('apps').open,false);
    assert.equal(h.frame.CarrotWebSettingsState.vision_object_detection,true);
    assert.equal(h.frame.CarrotWebSettingsState.vision_presentation,'bev');
  }
  assert.equal(h.writes.length,0);assert.equal(cameraStarts,0);
});
test('profile selection stages, cancel does not write, apply verifies one absolute existing setting',async()=>{
  const h=harness();h.park();h.el('profile').onclick();await h.flush();h.mode(1).onclick();
  assert.equal(h.el('modeConfirm').hidden,false);assert.equal(h.writes.length,0);
  h.el('modeCancel').onclick();await h.el('modeApply').onclick();assert.equal(h.writes.length,0);
  h.mode(2).onclick();await h.el('modeApply').onclick();
  assert.deepEqual(h.writes,[{name:'MyDrivingMode',value:2,source:'cockpit'}]);
  assert.match(h.el('profileStatus').textContent,/已確認儲存/);
});
test('drive transition and stale state cancel a pending mode without a POST',async()=>{
  const h=harness();h.park();h.mode(1).onclick();h.send('carState',{gearShifter:'drive',vEgo:0});
  await h.el('modeApply').onclick();assert.equal(h.writes.length,0);
  h.park();h.mode(1).onclick();h.advance(1501);await h.el('modeApply').onclick();assert.equal(h.writes.length,0);
});
test('lost response is reported unknown and never automatically resubmitted',async()=>{
  const h=harness();h.park();h.mode(1).onclick();h.reject();await h.el('modeApply').onclick();
  assert.match(h.el('profileStatus').textContent,/結果未確認/);await h.el('modeApply').onclick();assert.equal(h.writes.length,1);
});
test('existing feature pages and the complete native voice API stay routed to the same origin',()=>{
  const h=harness();h.panel('tools').onclick();h.panel('vision').onclick();
  assert.deepEqual(h.pages.slice(-2),['tools','carrot']);
  assert.equal(h.context.CarrotLocalVoice.findSettings('速度','id'),'速度|id');
  assert.equal(h.context.CarrotLocalVoice.cruise('set',80),'set|80');
  assert.equal(h.context.CarrotLocalVoice.result('id'),'id');
});


test('controls toggles its panel and the app drawer launches existing pages without settings writes',()=>{
  const h=harness();h.panel('setting').onclick();assert.equal(h.context.document.body.dataset.panel,'setting');
  h.panel('setting').onclick();assert.equal(h.context.document.body.dataset.panel,'vision');
  h.panel('navigation').onclick();h.panel('setting').onclick();h.el('closePanel').onclick();
  assert.equal(h.context.document.body.dataset.panel,'navigation');
  h.el('appsButton').onclick();assert.equal(h.el('apps').open,true);
  h.panel('logs').onclick();assert.equal(h.el('apps').open,false);assert.equal(h.context.document.body.dataset.panel,'logs');
  h.el('appsButton').onclick();h.panel('tools').onclick();assert.equal(h.el('apps').open,false);
  assert.equal(h.context.document.body.dataset.panel,'tools');assert.equal(h.writes.length,0);
});

// A half-open WebSocket may never emit close. Recovery must not depend on it.
test('silent socket is detached and replaced without reloading features or replaying writes',()=>{
 const h=harness();h.park();const old=h.sockets[0],late=old.onmessage,count=h.pages.length;
 h.run(14000);assert.equal(h.sockets.length,2);assert.equal(old.readyState,3);assert.equal(old.onmessage,null);
 assert.equal(h.writes.length,0);assert.equal(h.pages.length,count);
 const data=new Uint8Array(1);data.frames=[{service:'carState',sequence:999,decoded:{vEgoCluster:99,gearShifter:'drive'}}];late({data});h.tick();assert.equal(h.el('speed').textContent,'—');
 h.park();h.tick();assert.equal(h.el('gear').textContent,'P');
});
test('native pause and online/pageshow events cannot reopen background sockets',()=>{
 const h=harness();h.context.CarrotCockpit.pause();const count=h.sockets.length;
 h.events.online();h.events.pageshow();h.run(60000);assert.equal(h.sockets.length,count);assert.equal(h.timers.size,0);
 h.context.CarrotCockpit.resume();assert.equal(h.sockets.length,count+1);h.park();h.tick();assert.equal(h.el('gear').textContent,'P');assert.equal(h.writes.length,0);
});

test('object detection settings require explicit action and never start a camera or write driving parameters',async()=>{
 const h=harness(),saved=[];let cameraStarts=0;
 h.frame.CarrotWebSettingsState={vision_object_detection:false,vision_road_detection:false};
 h.frame.setWebSettingByKey=async(key,value)=>{saved.push([key,value]);h.frame.CarrotWebSettingsState[key]=value;return value;};
 const camera={disabled:false,click:()=>{cameraStarts++;}};h.register('btnStartVision',camera);
 h.tick();assert.equal(cameraStarts,0);assert.equal(saved.length,0);assert.equal(h.el('visionTools').textContent,'視覺設定');assert.match(h.el('visionTools')['aria-label'],/未啟用/);
 h.el('detectionObjects').checked=true;await h.el('detectionObjects').onchange();h.tick();
 assert.deepEqual(saved,[['vision_object_detection',true]]);assert.equal(cameraStarts,0);assert.match(h.el('visionDiagnostic').textContent,/等待前鏡頭/);
 h.el('connectVision').onclick();assert.equal(cameraStarts,1);
 camera.disabled=true;h.el('connectVision').onclick();assert.equal(cameraStarts,1);
 h.el('detectionObjects').checked=false;await h.el('detectionObjects').onchange();assert.equal(h.writes.length,0);
});

test('font storage updates reach the same-origin navigation frame without writes',()=>{
  const h=harness(),applied=[];h.el('navigation').contentWindow.CarrotDisplayPreferences={apply:value=>applied.push(value.web_text_scale)};
  h.context.localStorage.getItem=key=>key==='carrot_web_text_scale'?'125':null;
  h.events.storage({key:'carrot_web_text_scale'});assert.deepEqual(applied,[125]);assert.equal(h.writes.length,0);
  h.el('navigation').contentWindow.location.origin='https://other.example';h.events.storage({key:'carrot_web_text_scale'});assert.deepEqual(applied,[125]);
});

test('tools navigation returns to the cockpit while modified link clicks keep native behavior',()=>{
  const h=harness(),link={};h.frame.document.querySelector=selector=>selector==='#toolsPrimaryActions a[href="/navigation"]'?link:null;h.el('features').emit('load');
  let prevented=0;link.onclick({button:0,preventDefault(){prevented++;}});assert.equal(prevented,1);assert.equal(h.context.document.body.dataset.panel,'navigation');
  h.panel('tools').onclick();link.onclick({button:0,metaKey:true,preventDefault(){prevented++;}});assert.equal(prevented,1);assert.equal(h.context.document.body.dataset.panel,'tools');assert.equal(h.writes.length,0);
});


test('Back consumes an embedded drawer/detail before leaving controls',()=>{
 const h=harness();let pending=2;h.frame.CarrotCockpitControls={back:()=>pending-->0};h.panel('setting').onclick();
 assert.equal(h.context.CarrotCockpit.back(),true);assert.equal(h.context.document.body.dataset.panel,'setting');
 assert.equal(h.context.CarrotCockpit.back(),true);assert.equal(h.context.document.body.dataset.panel,'setting');
 assert.equal(h.context.CarrotCockpit.back(),true);assert.equal(h.context.document.body.dataset.panel,'vision');assert.equal(h.writes.length,0);
});
test('a parked confirmation is visibly withdrawn as soon as telemetry expires',()=>{
 const h=harness();h.park();h.mode(1).onclick();assert.equal(h.el('modeConfirm').hidden,false);h.advance(1501);h.tick();
 assert.equal(h.el('modeConfirm').hidden,true);assert.match(h.el('profileStatus').textContent,/已取消/);assert.equal(h.writes.length,0);
});
test('navigation card awaits the real end result and does not infer destination from a save button',async()=>{
 const h=harness();let finish;const api={snapshot:()=>({known:true,busy:false,active:true,label:'現有目的地'}),end:()=>new Promise(r=>finish=r)};
 h.el('navigation').contentWindow.CarrotNavigationView=api;h.tick();assert.equal(h.el('routeName').textContent,'現有目的地');assert.equal(h.el('routeEnd').disabled,false);
 const request=h.el('routeEnd').onclick();assert.match(h.el('routeFeedback').textContent,/正在結束/);finish({ended:true});await request;assert.match(h.el('routeFeedback').textContent,/已結束/);
 api.end=async()=>{throw Error('連線中斷');};await h.el('routeEnd').onclick();assert.match(h.el('routeFeedback').textContent,/未確認結束：連線中斷/);assert.equal(h.writes.length,0);
 api.snapshot=()=>({known:true,busy:true,active:true,label:'現有目的地'});h.tick();assert.equal(h.el('routeEnd').disabled,true);assert.equal(h.context.document.body.dataset.hasRoute,'true');
});
test('full screen labels reflect the current browser state and waiting telemetry is not green',()=>{
 const h=harness();assert.equal(h.el('fullscreenLabel').textContent,'全螢幕');
 h.context.document.fullscreenElement={};h.docEvents.fullscreenchange();assert.equal(h.el('fullscreenLabel').textContent,'離開全螢幕');assert.equal(h.el('fullscreen')['aria-pressed'],'true');
 h.context.document.fullscreenElement=null;h.docEvents.fullscreenchange();assert.equal(h.el('fullscreenLabel').textContent,'全螢幕');
 h.sockets[0].onmessage({data:JSON.stringify({mode:'carrot-state-v1'})});h.tick();assert.equal(h.el('connection').dataset.state,'waiting');assert.equal(h.writes.length,0);
});


test('feature bootstrap timeout exposes a read-only retry and first-run setup owns the layout',()=>{
 const h=harness();h.frame.showPage=undefined;h.el('features').emit('load');h.run(41000);
 assert.equal(h.el('retryPanel').hidden,false);assert.match(h.el('panelStatusText').textContent,/尚未就緒/);
 h.panel('tools').onclick();assert.equal(h.el('retryPanel').hidden,false);assert.equal(h.writes.length,0);
 h.el('features').src='http://fixture/?cockpit_embed=1';h.el('retryPanel').onclick();assert.equal(h.el('features').src,'http://fixture/?cockpit_embed=1');assert.equal(h.writes.length,0);
 h.frame.__CARROT_BOOTSTRAP__={intro:{shouldShow:true}};h.el('features').emit('load');assert.equal(h.context.document.body.dataset.panel,'setting');assert.equal(h.el('panelStatus').hidden,true);assert.equal(h.el('panelTitle').textContent,'首次引導設定');
});


test('phone app shortcuts retain sound controls and camera-view reset without driving writes',()=>{
 const h=harness(),sections=[];let resets=0;
 h.frame.CarrotCockpitControls={selectSection:id=>sections.push(id)};h.frame.CarrotVisionView={reset:()=>resets++};
 h.el('appsButton').onclick();h.el('soundShortcut').onclick();assert.equal(h.el('apps').open,false);assert.equal(h.context.document.body.dataset.panel,'setting');assert.deepEqual(sections,['sound']);
 h.el('resetViewSetting').onclick();assert.equal(resets,1);assert.match(h.el('visionSettingFeedback').textContent,/回到前方/);assert.equal(h.writes.length,0);
});
