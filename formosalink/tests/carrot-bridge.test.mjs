import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const code=readFileSync(new URL('../web/carrot-bridge.js',import.meta.url),'utf8');
const host='https://formosapilot.dinglu-t.com';
function storage(values=new Map()){
  return {getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,String(value)),removeItem:key=>values.delete(key),
    key:index=>[...values.keys()][index]??null,get length(){return values.size;}};
}
function browser(device,shared=storage()){
  const prefix=`/api/v1/devices/${device}/carrot/`,calls=[];
  class Element {setAttribute(name,value){this[name]=value;}}
  class Socket {constructor(url,protocols){this.url=url;this.protocols=protocols;}static OPEN=1;}
  class XHR {open(...args){calls.push(args);}}
  const types={};
  for(const name of ['HTMLImageElement','HTMLScriptElement','HTMLLinkElement','HTMLAnchorElement','HTMLMediaElement','HTMLSourceElement','HTMLFormElement']){
    types[name]=class extends Element {};
    for(const attribute of ['src','href','action'])Object.defineProperty(types[name].prototype,attribute,{configurable:true,
      get(){return this['_'+attribute];},set(value){this['_'+attribute]=value;}});
  }
  const sandbox={...types,URL,Request,Element,XMLHttpRequest:XHR,WebSocket:Socket,navigator:{},
    document:{currentScript:{src:host+prefix+'__formosa_bridge.js'}},location:new URL(host+prefix),
    Worker:class {constructor(url){this.url=url;}},
    FontFace:class {constructor(name,source){this.source=source;}},
    history:{pushState(){},replaceState(){}},localStorage:shared,sessionStorage:storage(),
    fetch:async(...args)=>{calls.push(args);return {ok:true};},open:(...args)=>calls.push(args)};
  sandbox.window=sandbox;
  const ctx=vm.createContext(sandbox);vm.runInContext(code,ctx);
  return {ctx,prefix,calls};
}

test('each tab routes HTTP, worker assets and WebSocket to its own device',async()=>{
  const a=browser('device-a'),b=browser('device-b');
  for(const {ctx,prefix,calls} of [a,b]){
    await ctx.fetch('/api/settings?q=繁體中文');
    assert.ok(calls[0][0].startsWith(host+prefix+'api/settings?'));
    const socket=new ctx.WebSocket('wss://formosapilot.dinglu-t.com/ws/terminal',['protocol']);
    assert.equal(socket.url,host.replace('https:','wss:')+prefix+'ws/terminal');
    assert.equal(ctx.WebSocket.OPEN,1);
    assert.equal(new ctx.Worker("/js/worker.js").url,host+prefix+"js/worker.js");
    assert.equal(new ctx.FontFace("Chinese",'url("/shared-assets/font.ttf")').source,'url("'+host+prefix+'shared-assets/font.ttf")');
    assert.equal(ctx.FormosaCarrotRemote.url(host+prefix+'already'),host+prefix+'already');
    assert.equal(ctx.FormosaCarrotRemote.url('https://api.mapbox.com/map'),'https://api.mapbox.com/map');
    assert.equal(ctx.FormosaCarrotRemote.url('blob:https://formosapilot.dinglu-t.com/image'),'blob:https://formosapilot.dinglu-t.com/image');
    assert.equal(ctx.FormosaCarrotRemote.url('#details'),'#details');
    const image=new ctx.HTMLImageElement();image.src='/shared-assets/icon.png';
    assert.equal(image.src,host+prefix+'shared-assets/icon.png');
    ctx.open('/download/file');assert.equal(calls.at(-1)[0],host+prefix+'download/file');
  }
});

test('device preferences and clear never change another tab or the Formosa portal',()=>{
  const shared=storage();shared.setItem('formosalink-language','zh-TW');
  const a=browser('a',shared),b=browser('b',shared);
  a.ctx.localStorage.setItem('language','zh-tw');b.ctx.localStorage.setItem('language','en');
  assert.equal(a.ctx.localStorage.getItem('language'),'zh-tw');
  assert.equal(b.ctx.localStorage.getItem('language'),'en');
  a.ctx.localStorage.clear();
  assert.equal(a.ctx.localStorage.length,0);
  assert.equal(b.ctx.localStorage.getItem('language'),'en');
  assert.equal(shared.getItem('formosalink-language'),'zh-TW');
});
