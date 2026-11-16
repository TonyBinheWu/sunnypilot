import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const bundle=readFileSync(new URL('../js/generated/cockpit.js',import.meta.url),'utf8');
const html=readFileSync(new URL('../cockpit.html',import.meta.url),'utf8');
function harness(){
  const nodes=new Map(),writes=[],pages=[];let mode=3,clock=0,seq=0,rejectPost=false;
  function element(id=''){
    const classes=new Set(),listeners={};
    return {id,hidden:false,dataset:{},textContent:'',disabled:false,href:'/css/cockpit-embedded.css',
      classList:{contains:x=>classes.has(x),toggle(x,force){const next=force??!classes.has(x);if(next)classes.add(x);else classes.delete(x);return next;},add:x=>classes.add(x),remove:x=>classes.delete(x)},
      addEventListener:(name,fn)=>{listeners[name]=fn;},emit:name=>listeners[name]?.(),append(){},focus(){},
      showModal(){this.open=true;},getBoundingClientRect:()=>({width:480,height:320}),getContext:()=>new Proxy({measureText:()=>({width:20})},{get:(t,k)=>t[k]??(()=>{}),set:(t,k,v)=>(t[k]=v,true)})};
  }
  for(const [,id] of html.matchAll(/id="([^"]+)"/g))nodes.set(id,element(id));
  const buttons=[1,2,3,4].map(mode=>Object.assign(element(),{dataset:{mode:String(mode)}}));
  const panels=['navigation','vision','logs','setting','tools'].map(panel=>Object.assign(element(),{dataset:{panel}}));
  const document={hidden:false,body:element(),documentElement:{...element(),style:{setProperty(){}}},head:element(),
    getElementById:id=>nodes.get(id),querySelectorAll:s=>s==='[data-mode]'?buttons:s==='[data-panel]'?panels:[],
    addEventListener(){},createElement:()=>element()};
  const innerDocument={...document,documentElement:{...element(),hasAttribute:()=>true}};
  nodes.get('features').contentWindow={location:{origin:'http://fixture'},document:innerDocument,showPage:p=>pages.push(p),
    CarrotLocalVoice:{findSettings:(...a)=>a.join('|'),cruise:(...a)=>a.join('|'),result:id=>id}};
  nodes.get('navigation').contentWindow={location:{origin:'http://fixture'}};
  nodes.get('navigation').contentDocument=innerDocument;
  const sockets=[];
  const context={document,location:{origin:'http://fixture',host:'fixture',protocol:'http:'},performance:{now:()=>clock},
    devicePixelRatio:1,console,Date,Proxy,localStorage:{getItem:()=>null,setItem(){}},
    addEventListener(){},setTimeout:()=>1,clearTimeout(){},setInterval:()=>1,
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
    advance:ms=>{clock+=ms;},reject:()=>{rejectPost=true;},flush:()=>new Promise(setImmediate)};
}
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
