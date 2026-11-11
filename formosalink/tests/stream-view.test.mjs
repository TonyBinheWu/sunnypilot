import test from 'node:test';
import assert from 'node:assert/strict';
import {mediaViewer} from '../web/media-view.js';
import {translations} from '../web/i18n.js';

test('live viewer acknowledges decoded frames, switches cameras, discards old callbacks and stops sockets',async()=>{
 const original={};for(const key of ['document','location','WebSocket','Image','fetch'])original[key]=globalThis[key];
 const sockets=[],draws=[];
 class Node{
  constructor(tag,text){this.tag=tag;this.textContent=text;this.dataset={};this.children=[];this.listeners={};this.isConnected=true;}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  setAttribute(){} addEventListener(name,fn){this.listeners[name]=fn;}
  querySelectorAll(){return [];} querySelector(){return null;}
  getContext(){return {fillRect(){},fillText(){},drawImage(image){draws.push(image.src);}};}
  remove(){this.isConnected=false;} pause(){} load(){} removeAttribute(){}
 }
 class Socket{
  static OPEN=1;
  constructor(url){this.url=url;this.readyState=1;this.sent=[];sockets.push(this);}
  send(value){this.sent.push(JSON.parse(value));}
  close(){this.readyState=3;this.closed=true;}
 }
 globalThis.document={hidden:false,pictureInPictureEnabled:false};globalThis.location={origin:'https://link.example.test'};
 globalThis.WebSocket=Socket;globalThis.Image=class{async decode(){}};
 globalThis.fetch=async url=>{assert.equal(url,'/api/v1/health');return {ok:true,headers:{get:()=>new Date().toUTCString()}};};
 const viewer=mediaViewer({api:()=>{throw Error('HTTP polling must not be used');},t:key=>key,el:(tag,text)=>new Node(tag,text)});
 try{
  const parent=new Node('main');viewer.open(parent,'device');const root=parent.children[0];
  const actions=root.children.find(node=>node.tag==='div');actions.children.find(node=>node.textContent==='mediaStart').listeners.click();
  await new Promise(resolve=>setImmediate(resolve));
  const wide=sockets[0];assert.match(wide.url,/camera=wide-road$/);
  const message=camera=>({data:JSON.stringify({type:'frame',frame:{source:camera,stream:'one',sequence:1,width:640,height:360,jpeg:'fixture',sampled_at:Date.now()/1000}})});
  await wide.onmessage(message('wide-road'));assert.equal(draws.length,1);assert.deepEqual(wide.sent,[{type:'ack'}]);
  const select=root.children.find(node=>node.tag==='select');select.value='driver';select.listeners.change();
  await new Promise(resolve=>setImmediate(resolve));
  const driver=sockets[1];assert.ok(wide.closed);assert.match(driver.url,/camera=driver$/);
  await wide.onmessage(message('wide-road'));assert.equal(draws.length,1);
  await driver.onmessage(message('driver'));assert.equal(draws.length,2);assert.deepEqual(driver.sent,[{type:'ack'}]);
  globalThis.Image=class{async decode(){throw Error('fixture codec failure');}};
  await driver.onmessage(message('driver'));
  const status=root.children.find(node=>node.dataset.mediaI18n==='mediaError_decode_failed');
  assert.ok(status);assert.ok(driver.closed);
  driver.onclose({code:1000});assert.equal(status.textContent,'mediaError_decode_failed');
  actions.children.find(node=>node.textContent==='mediaStop').listeners.click();assert.ok(driver.closed);
 }finally{
  viewer.close();for(const [key,value] of Object.entries(original)){if(value===undefined)delete globalThis[key];else globalThis[key]=value;}
 }
});

test('all three languages describe live streaming and connection recovery',()=>{
 for(const locale of ['zh-TW','en','ja'])for(const key of ['mediaLive','mediaStreamError','mediaPhase','mediaWide','mediaDriver'])assert.ok(translations[locale][key]);
});
