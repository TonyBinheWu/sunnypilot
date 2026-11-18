import test from 'node:test';
import assert from 'node:assert/strict';
import {sampleAt,attachDrivingSei} from '../src/features/logs/player/driving_sei.js';
import {bindPlayerChrome} from '../src/features/logs/player/chrome.js';

test('SEI follows video PTS through seeks, gaps and missing first frames without future data',()=>{
 const rows=[{time_s:.35,speed_mps:20},{time_s:.4,speed_mps:0},{time_s:1,cruise_enabled:false}];
 assert.equal(sampleAt(rows,0),null);assert.equal(sampleAt(rows,.349),null);
 assert.equal(sampleAt(rows,.38).speed_mps,20);assert.equal(sampleAt(rows,.5).speed_mps,0);
 assert.equal(sampleAt(rows,.8),null);assert.equal(sampleAt(rows,1.1).cruise_enabled,false);
 assert.equal(sampleAt(rows,9),null);assert.equal(sampleAt(rows,.36).speed_mps,20);assert.equal(sampleAt(rows,NaN),null);
});

test('idle touch wakes controls without toggling playback; paused and focused controls stay visible',()=>{
 const events={},handlers={},classes=new Set();let focused=false,shown=0;
 const frame={classList:{add:c=>classes.add(c),remove:c=>classes.delete(c),contains:c=>classes.has(c)},querySelector:()=>focused?{}:null,
 addEventListener:(n,f)=>events[n]=f,removeEventListener:n=>delete events[n]};
 const player={paused:false,ended:false,on:(n,f)=>handlers[n]=f,off:n=>delete handlers[n],toggleControls:()=>shown++};
 const destroy=bindPlayerChrome(frame,player);handlers.controlshidden();assert.ok(classes.has('is-player-idle'));
 events.pointerdown({target:{closest:()=>null}});let prevented=false;
 events.click({preventDefault(){prevented=true},stopImmediatePropagation(){}});assert.ok(prevented);assert.equal(shown,2);
 player.paused=true;handlers.controlshidden();assert.ok(!classes.has('is-player-idle'));
 player.paused=false;focused=true;handlers.controlshidden();assert.ok(!classes.has('is-player-idle'));
 destroy();assert.deepEqual(Object.keys(events),[]);assert.deepEqual(Object.keys(handlers),[]);
});

test('closing an SEI view aborts work and late responses cannot overwrite the next clip',async()=>{
 const pending=[];
 class Element {
  constructor(){this.children=[];this.dataset={};this.attrs={};this.classList={add(){},remove(){}};this.style={setProperty(){},removeProperty(){}};}
  append(...nodes){this.children.push(...nodes);}
  setAttribute(k,v){this.attrs[k]=v;}
  remove(){this.removed=true;}
  getBoundingClientRect(){return {height:60};}
 }
 const win={setTimeout,clearTimeout,matchMedia:()=>({matches:true}),fetch:(_url,opts)=>new Promise(resolve=>pending.push({resolve,signal:opts.signal}))};
 const doc={defaultView:win,createElement:()=>new Element()};
 const parent=()=>Object.assign(new Element(),{ownerDocument:doc});
 const media=()=>({paused:true,ended:false,currentTime:.4,listeners:new Map(),addEventListener(n,f){this.listeners.set(n,f);},removeEventListener(n){this.listeners.delete(n);}});
 const oldVideo=media(),newVideo=media(),old=attachDrivingSei(oldVideo,parent(),{segment:'old'});
 old.destroy();assert.ok(pending[0].signal.aborted);assert.equal(oldVideo.listeners.size,0);
 const current=attachDrivingSei(newVideo,parent(),{segment:'new'});
 pending[1].resolve({ok:true,json:async()=>({status:'no_sei',samples:[]})});
 await new Promise(resolve=>setImmediate(resolve));
 pending[0].resolve({ok:true,json:async()=>({status:'ready',samples:[{time_s:.4,speed_mps:90}]})});
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(current.panel.dataset.state,'no_sei');assert.equal(old.panel.removed,true);
 assert.equal(current.panel.children[0].children[2].attrs['aria-expanded'],'false');
 current.destroy();assert.equal(newVideo.listeners.size,0);assert.ok(pending[1].signal.aborted);
});
