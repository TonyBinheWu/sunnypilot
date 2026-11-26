import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../remote-screen.js", import.meta.url), "utf8");
const settle = () => new Promise(resolve => setImmediate(resolve));

function connect() {
  const images = [], draws = [], sent = [], revoked = [], handlers = {}, timers = new Map();
  const form = {}, input = {value: "123456"}, status = {}, end = {};
  const pair = {querySelector: id => id === "form" ? form : input};
  const canvas = {
    hidden: true,
    getContext: () => ({drawImage: image => draws.push(image.src), clearRect() {}}),
    getBoundingClientRect: () => ({width: 200, height: 100, left: 0, top: 0}),
    setPointerCapture() {},
    addEventListener: (name, callback) => { handlers[name] = callback; },
  };
  let sampled;
  const probe = {getContext: () => ({
    drawImage: image => { sampled = image; },
    getImageData: () => ({data: [0, sampled.black ? 0 : 42, 0, 255]}),
  })};
  const time = {now: 100};
  let ws, counter = 0;
  class Socket {
    static OPEN = 1;
    readyState = 1;
    constructor() { ws = this; }
    send(text) { sent.push(JSON.parse(text)); }
    close() { this.readyState = 3; }
  }
  vm.runInNewContext(source, {
    document: {querySelector: id => ({"#display":canvas, "#pair":pair, "#status":status, "#disconnect":end})[id],
      createElement: () => probe, addEventListener() {}},
    window: {addEventListener() {}}, location: {protocol:"http:", host:"localhost"},
    Image: class { constructor() { images.push(this); } naturalWidth = 200; naturalHeight = 100; },
    URL: {createObjectURL: () => String(++counter), revokeObjectURL: url => revoked.push(url)},
    WebSocket: Socket, setInterval: (callback, ms) => { timers.set(ms, callback); return ms; },
    clearInterval: id => timers.delete(id), setTimeout, clearTimeout, performance: {now: () => time.now},
    cancelAnimationFrame() {}, ArrayBuffer, DataView, Blob,
  });
  form.onsubmit({preventDefault() {}});
  ws.onmessage({data: "ready"});
  const frame = (epoch, blank = false) => {
    const data = new ArrayBuffer(blank ? 4 : 8);
    new DataView(data).setUint32(0, epoch);
    ws.onmessage({data});
  };
  const point = {pointerId:1, button:0, clientX:50, clientY:20};
  const press = () => canvas.onpointerdown(point);
  const release = () => canvas.onpointerup({...point, type:"pointerup"});
  return {images, draws, sent, revoked, frame, press, release, ws, status, handlers, timers, time, end};
}

test("blackout cancels a held touch, preserves the last image and recovers on the same socket", async () => {
  const v = connect();
  v.frame(4);
  v.press();
  assert.equal(v.sent.length, 0);
  v.images[0].onload();
  await settle();
  v.press();
  v.frame(8, true);
  v.release();
  v.press();
  assert.deepEqual(v.sent.map(e => e.type), ["down","cancel"]);
  assert.match(v.status.textContent, /暫停/);
  assert.deepEqual(v.draws, ["1"]);
  v.frame(8);
  v.images[1].onload();
  await settle();
  v.press();
  v.release();
  assert.deepEqual(v.sent.slice(2).map(e => [e.type,e.epoch]), [["down",8],["up",8]]);
  assert.equal(v.ws.readyState, 1);
});

test("one decode in flight and only the newest pending PNG survive slow decoding", async () => {
  const v = connect();
  for (let i = 0; i < 20; ++i) v.frame(5);
  assert.equal(v.images.length, 1);
  v.images[0].onload();
  await settle();
  assert.equal(v.images.length, 2);
  v.images[1].onload();
  await settle();
  assert.deepEqual(v.draws, ["1","2"]);
  assert.deepEqual(v.revoked, v.draws);
});

test("a legacy opaque black PNG cannot replace the visible frame or accept clicks", async () => {
  const v = connect();
  v.frame(4);
  v.images[0].onload();
  await settle();
  v.frame(4);
  v.images[1].black = true;
  v.images[1].onload();
  await settle();
  v.press();
  assert.deepEqual(v.draws, ["1"]);
  assert.deepEqual(v.sent, []);
  assert.match(v.status.textContent, /暫停/);
  v.frame(4);
  v.images[2].onload();
  await settle();
  v.press();
  assert.equal(v.sent[0].type, "down");
});

test("late, corrupt, expired and context-lost frames cannot enable touches", async () => {
  const v = connect();
  v.frame(4);
  v.frame(9, true);
  v.images[0].onload();
  await settle();
  v.press();
  assert.deepEqual(v.draws, []);
  v.frame(9);
  v.images[1].onerror();
  await settle();
  v.press();
  assert.equal(v.sent.length, 0);
  v.frame(9);
  v.time.now += 1500;
  v.images[2].onload();
  await settle();
  assert.deepEqual(v.draws, []);
  v.frame(9);
  v.images[3].onload();
  await settle();
  v.press();
  v.time.now += 1600;
  v.timers.get(400)();
  v.press();
  assert.deepEqual(v.sent.map(e => e.type), ["down","cancel"]);
  v.frame(9);
  v.handlers.contextlost({preventDefault() {}});
  v.images[4].onload();
  await settle();
  v.press();
  assert.deepEqual(v.draws, ["4"]);
  assert.equal(v.sent.length, 2);
  v.frame(9);
  v.end.onclick();
  v.images[5].onload();
  await settle();
  assert.deepEqual(v.draws, ["4"]);
});
