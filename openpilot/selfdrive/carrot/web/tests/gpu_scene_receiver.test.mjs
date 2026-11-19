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
