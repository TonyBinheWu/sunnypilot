import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const bundle=readFileSync(new URL('../js/generated/cockpit.js',import.meta.url),'utf8');
const html=readFileSync(new URL('../cockpit.html',import.meta.url),'utf8');
function harness(){
  const nodes=new Map(),writes=[],pages=[],hud=[],intervals=[];let mode=3,clock=0,seq=0,rejectPost=false;
  function element(id=''){
    const classes=new Set(),listeners={};
    return {id,hidden:false,dataset:{},textContent:'',disabled:false,href:'/css/cockpit-embedded.css',
      classList:{contains:x=>classes.has(x),toggle(x,force){const next=force??!classes.has(x);if(next)classes.add(x);else classes.delete(x);return next;},add:x=>classes.add(x),remove:x=>classes.delete(x)},
      addEventListener:(name,fn)=>{listeners[name]=fn;},emit:name=>listeners[name]?.(),append(){},focus(){},
      close(){this.open=false;listeners.close?.();},showModal(){this.open=true;},getBoundingClientRect:()=>({width:480,height:320}),getContext:()=>new Proxy({measureText:()=>({width:20})},{get:(t,k)=>t[k]??(()=>{}),set:(t,k,v)=>(t[k]=v,true)})};
  }
  for(const [,id] of html.matchAll(/id="([^"]+)"/g))nodes.set(id,element(id));
  const buttons=[1,2,3,4].map(mode=>Object.assign(element(),{dataset:{mode:String(mode)}}));
  const panels=['navigation','vision','logs','setting','tools'].map(panel=>Object.assign(element(),{dataset:{panel}}));
  const document={hidden:false,body:element(),documentElement:{...element(),style:{setProperty(){}}},head:element(),
    getElementById:id=>nodes.get(id),querySelectorAll:s=>s==='[data-mode]'?buttons:s==='[data-panel]'?panels:[],
    addEventListener(){},createElement:()=>element()};
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
    addEventListener(){},setTimeout:()=>1,clearTimeout(){},setInterval:fn=>(intervals.push(fn),1),
    WebSocket:class {constructor(){sockets.push(this);}close(){this.onclose?.();}},
    CarrotVisionCompact:{decodeFrames:data=>data.frames},
    async fetch(url,options){
      if(options?.method==='POST'){const body=JSON.parse(options.body);writes.push(body);mode=body.value;if(rejectPost)throw Error('lost response');}
      return {ok:true,json:async()=>({values:{MyDrivingMode:mode,MyDrivingModeAuto:0}})};
    },
    confirm(){throw Error('Native confirm dialogs must not be used');}};
  context.window=context;vm.runInNewContext(bundle,context);
  nodes.get('features').emit('load');
  function send(service,decoded){const data=new Uint8Array(1);data.frames=[{service,decoded,sequence:seq++}];sockets[0].onmessage({data});}
  function park(){send('carState',{gearShifter:'park',vEgo:0,vEgoCluster:0});send('selfdriveState',{enabled:false});send('carControl',{latActive:false,longActive:false});}
  return {el:id=>nodes.get(id),mode:n=>buttons[n-1],panel:p=>panels.find(b=>b.dataset.panel===p),writes,pages,send,park,context,
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
