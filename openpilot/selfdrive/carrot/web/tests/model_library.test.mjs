import assert from 'node:assert/strict';
import test from 'node:test';
import { renderLibrary } from '../src/features/tools/model_library.js';
class Element {
  constructor(tag) { this.tag = tag; this.children = []; this.dataset = {}; this.events = {}; this.style = {}; this.attributes = {}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(k, v) { this.attributes[k] = v; }
  removeAttribute(k) { delete this.attributes[k]; }
  addEventListener(name, callback) { this.events[name] = callback; }
  querySelector(tag) { return this.children.find(e => e.tag === tag) || this.children.map(e => e.querySelector?.(tag)).find(Boolean); }
  querySelectorAll(tag) { return this.children.flatMap(e => [...(e.tag === tag ? [e] : []), ...e.querySelectorAll(tag)]); }
}
const data = { effective: 'n16', selected: 'flip-flop', reboot_required: true, models: [
  { id: 'n16', name: 'N16 Nav', noo: true, hidden: false, protected: true, egpu_bytes: 100, jetson_bytes: null },
  { id: 'flip-flop', name: 'Flip Flop', noo: false, hidden: false, protected: true, egpu_bytes: 200, jetson_bytes: 300 },
] };

test('shared tools render both model catalogs without an eGPU and submit the selected device field', async t => {
  const old = {document: globalThis.document, postJson: globalThis.postJson, getJson: globalThis.getJson};
  t.after(() => Object.assign(globalThis, old));
  const root = new Element('section');
  globalThis.document = {getElementById: () => root, createElement: tag => new Element(tag)};
  const choices = [
    ['cd210', 'CD210', 'small', 'carrot-wip'], ['sunny-s', 'SP small', 'small', 'sunnypilot'],
    ['n16', 'N16', 'large', 'carrot-wip'], ['sunny-b', 'SP large', 'large', 'sunnypilot'],
  ];
  let loads = 0;
  globalThis.getJson = async url => {
    assert.equal(url, '/api/driving-models/catalog');
    loads++;
    return {models: choices.map(([id, name, size, source]) => ({id, name, size, source}))};
  };
  const calls = [];
  globalThis.postJson = async (url, body) => { calls.push([url, body]); return {ok: true}; };
  const boot = {small: 'cd210', large: 'n16', primary: 'auto'};
  const selector = {boot, next: {...boot, small: 'sunny-s'}, offroad: true, scene: -1, job: {}};
  await renderLibrary({...data, selector});
  const [small, large, primary, scene] = root.querySelectorAll('select');
  assert.deepEqual([small.value, large.value, primary.value, scene.value], ['sunny-s', 'n16', 'auto', -1]);
  assert.deepEqual(small.children.map(e => e.label), ['carrot-wip (1)', 'sunnypilot (1)']);
  assert.deepEqual(large.children.map(e => e.children[0].value), ['n16', 'sunny-b']);
  assert.ok(root.children.every(e => !e.textContent?.includes('PhysicalAI-reason-VLA')));
  assert.deepEqual(root.querySelectorAll('select').map(e => e.dataset.field), ['small', 'large', 'primary', 'scene']);
  scene.value = '2';
  await scene.events.change();
  assert.deepEqual(calls, [['/api/driving-models/selection', {field: 'scene', value: 2}]]);
  async function progress(received, total, phase = 'downloading') {
    await renderLibrary({...data, selector: {...selector, job: {state: 'preparing', model: 'sunny-b', progress: {phase, file: 'model.pkl', received, total}}}});
  }
  await progress(1048576, 4194304);
  const track = root.querySelectorAll('div').find(e => e.attributes.role === 'progressbar');
  const selected = root.querySelector('select');
  assert.equal(track.attributes['aria-valuenow'], '25');
  await progress(2097152, 4194304);
  assert.equal(track.attributes['aria-valuenow'], '50');
  assert.equal(root.querySelector('select'), selected);
  await progress(2097152, null);
  assert.equal(track.attributes['aria-valuenow'], undefined);
  assert.match(root.querySelectorAll('small').at(-1).textContent, /2 MiB received/);
  await progress(4194304, 4194304, 'verifying');
  assert.equal(root.querySelectorAll('small').at(-1).hidden, true);
  await renderLibrary({...data, selector: {...selector, offroad: false}});
  assert.ok(root.querySelectorAll('select').every(e => e.disabled));
  assert.equal(loads, 1);
});
test('model choice distinguishes current/pending/NOO and preserves in-flight choice across polls', t => {
  const old = globalThis.document;
  t.after(() => { globalThis.document = old; });
  const root = new Element('section');
  globalThis.document = { getElementById: () => root, createElement: tag => new Element(tag) };
  renderLibrary(data);
  const select = root.querySelector('select');
  assert.equal(select.value, 'flip-flop');
  assert.deepEqual(select.children.map(x => x.value), ['n16', 'flip-flop']);
  assert.match(select.children[0].textContent, /NOO supported/);
  assert.match(select.children[1].textContent, /NOO not supported/);
  assert.match(root.children.find(x => x.textContent?.startsWith('This boot')).textContent, /N16/);
  assert.equal(root.querySelector('button'), undefined);
  assert.equal(root.children.some(x => x.className === 'model-library__row'), false);
  select.value = 'n16';
  select.disabled = true;
  renderLibrary({ ...data, jetson_inventory_fresh: true });
  assert.equal(root.querySelector('select').value, 'n16');
  renderLibrary(data, true);
  assert.equal(root.querySelector('select').value, 'flip-flop');
});

test('selection alone saves next boot and exposes no deletion action', async t => {
  const old = { document: globalThis.document, postJson: globalThis.postJson };
  t.after(() => Object.assign(globalThis, old));
  const root = new Element('section');
  globalThis.document = { getElementById: () => root, createElement: tag => new Element(tag) };
  const calls = [];
  globalThis.postJson = async (url, body) => { calls.push({url, body}); return {library: {...data, selected: body.model}}; };
  renderLibrary(data, true);
  const select = root.querySelector('select');
  select.value = 'n16';
  await select.events.change();
  assert.deepEqual(calls, [{url: '/api/egpu/model/library', body: {action:'select',model:'n16'}}]);
  assert.equal(root.querySelector('button'), undefined);
  assert.equal(root.querySelector('select').value, 'n16');
});

test('failed selection restores the saved choice', async t => {
  const old = { document: globalThis.document, postJson: globalThis.postJson };
  t.after(() => Object.assign(globalThis, old));
  const root = new Element('section');
  globalThis.document = { getElementById: () => root, createElement: tag => new Element(tag) };
  globalThis.postJson = async () => { throw new Error('offline'); };
  renderLibrary(data, true);
  const select = root.querySelector('select');
  select.value = 'n16';
  await select.events.change();
  assert.equal(root.querySelector('select').value, 'flip-flop');
  assert.ok(!root.querySelector('select').disabled);
});
