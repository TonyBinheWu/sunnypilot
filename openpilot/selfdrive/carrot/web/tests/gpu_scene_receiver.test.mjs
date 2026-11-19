import test from 'node:test';
import assert from 'node:assert/strict';
import {createGpuSceneReceiver} from '../src/features/drive/contents/vision/hud/gpu_scene_receiver.js';

function viewer(decodeDelay = 15) {
  let time = 0, draws = 0, closes = 0;
  const timers = new Map();
  const requests = [];
  const target = {
    performance: {now: () => time},
    setTimeout(fn, delay) { timers.set(fn, time + delay); return fn; },
    clearTimeout(fn) { timers.delete(fn); },
    async fetch(path) {
      requests.push(path);
      if (path.endsWith('?after=7')) return new Response(null, {status:304});
      return new Response(new Uint8Array([1]), {headers:{
        'Content-Type':'image/jpeg', 'Content-Length':'1', 'X-Scene-Frame':'7',
        'X-Scene-Age-Ms':'800', 'X-Scene-Cells':'3', 'X-Scene-Raised':'2'}});
    },
    async createImageBitmap() { time += decodeDelay; return {width:72,height:50,close(){closes++;}}; },
  };
  const context = {drawImage(){draws++;},clearRect(){}};
  const canvas = {style:{},getContext:()=>context};
  const receiver = createGpuSceneReceiver(target,canvas);
  const tick = delay => {
    const fn = [...timers.keys()].find(id=>timers.get(id)===time+delay);
    assert.ok(fn); timers.delete(fn); time+=delay; return fn();
  };
  return {receiver,requests,tick,timers,counts:()=>[draws,closes]};
}

test('GPU viewer deduplicates reads and clears a displayed frame at its capture deadline',async()=>{
  const v=viewer();
  v.receiver.update(true);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(v.receiver.snapshot().cells,3);
  await v.tick(45);
  assert.ok(v.requests.at(-1).endsWith('?after=7'));
  assert.deepEqual(v.counts(),[1,1]);
  await v.tick(40);
  assert.equal(v.receiver.snapshot().status,'stale');
  assert.equal(v.receiver.snapshot().cells,0);
  v.receiver.destroy();
  assert.equal(v.timers.size,0);
});

test('a frame that expires during decode is disposed without being displayed',async()=>{
  const v=viewer(101);
  v.receiver.update(true);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(v.receiver.snapshot().status,'stale');
  assert.deepEqual(v.counts(),[0,1]);
  v.receiver.update(false);
  assert.equal(v.receiver.snapshot().status,'paused');
  assert.equal(v.timers.size,0);
});


test('the GPU producer receives an explicit parking projection and a return to driving',async()=>{
  const views=[],timers=new Map();
  const target={performance:{now:()=>500},setTimeout(fn,ms){timers.set(fn,ms);return fn;},clearTimeout(fn){timers.delete(fn);},
    async fetch(url,options){if(url.endsWith('/view'))views.push(JSON.parse(options.body));return new Response(null,{status:204});}};
  const receiver=createGpuSceneReceiver(target,{style:{},getContext:()=>({clearRect(){}})});
  for(const parking of [true,false]){
    receiver.setView(1920,720,{view:{parking,pitch:parking?82:25}});
    receiver.update(true);await new Promise(resolve=>setImmediate(resolve));receiver.update(false);
  }
  assert.deepEqual(views.map(v=>[v.parking,v.pitch]),[[true,82],[false,25]]);
  receiver.destroy();assert.equal(timers.size,0);
});


test('a previous driving image cannot populate the parked overhead viewer',async()=>{
  let painted=0,decoded=0;
  const timers=new Set();
  const target={performance:{now:()=>10},setTimeout(fn){timers.add(fn);return fn;},clearTimeout(fn){timers.delete(fn);},
    async fetch(url){return url.endsWith('/view')?new Response(null,{status:204}):new Response(new Uint8Array([1]),{headers:{
      'X-Scene-Frame':'1','X-Scene-Age-Ms':'0','X-Scene-Parking':'0','Content-Length':'1','Content-Type':'image/jpeg'
    }});},async createImageBitmap(){decoded++;return {close(){}};}};
  const receiver=createGpuSceneReceiver(target,{style:{},getContext:()=>({clearRect(){},drawImage(){painted++;}})});
  receiver.setView(1024,768,{view:{parking:true,pitch:82}});receiver.update(true);
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(receiver.snapshot().status,'waiting');assert.equal(painted,0);assert.equal(decoded,0);
  receiver.destroy();assert.equal(timers.size,0);
});
