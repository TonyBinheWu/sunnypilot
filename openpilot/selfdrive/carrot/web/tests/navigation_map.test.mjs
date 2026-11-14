import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const source = await readFile(new URL("../js/pages/navigation_map.js", import.meta.url), "utf8");
const traditionalSource = await readFile(new URL("../js/pages/navigation_zh_tw.js", import.meta.url), "utf8");
const settle = () => new Promise((resolve) => setImmediate(resolve));

async function page(responses, language = "en", handleApi = null) {
  const elements = new Map(), timers = [], revoked = [];
  let blobs = 0;
  const makeElement = () => ({
      hidden: false, textContent: "", value: "", children: [], handlers: {},
      addEventListener(name, handler) { this.handlers[name] = handler; },
      replaceChildren(...children) { this.children = children; }, append(...children) { this.children.push(...children); }, focus() {},
      async trigger(name) { await this.handlers[name]?.({preventDefault() {}}); await settle(); },
      removeAttribute(name) { delete this[name]; },
    });
  const element = (id) => {
    if (!elements.has(id)) elements.set(id, makeElement());
    return elements.get(id);
  };
  vm.runInNewContext(traditionalSource + "\n" + source, {
    document: { documentElement: {}, hidden: false, getElementById: element, createElement: makeElement },
    localStorage: { getItem: () => language }, navigator: {},
    URL: { createObjectURL: () => `blob:${++blobs}`, revokeObjectURL: (url) => revoked.push(url) },
    setTimeout: (callback) => timers.push(callback),
    fetch: async (url, options) => {
      if (handleApi && !url.endsWith('map.png')) {
        const result = await handleApi(url, options || {});
        return {ok: !result.error, json: async () => result};
      }
      if (url.endsWith("destination")) return { ok: true, json: async () => ({ destination: null }) };
      if (url.endsWith("favorites")) return { ok: true, json: async () => ({ favorites: [] }) };
      const response = responses.shift();
      if (response instanceof Error) throw response;
      assert.ok(response, "unexpected map request");
      return { status: response.status, headers: { get: () => response.reason }, blob: async () => ({}) };
    },
  });
  await settle();
  return { element, revoked, blobs: () => blobs, next: async () => { await timers.shift()(); } };
}

test("keys without a route show destination instructions instead of a black image", async () => {
  const p = await page([{ status: 200, reason: "route" }]);
  assert.equal(p.element("map").hidden, true);
  assert.equal(p.element("mapStatus").hidden, false);
  assert.match(p.element("mapStatus").textContent, /select a destination below/);
  assert.match(p.element("mapStatus").textContent, /Saving keys alone/);
  assert.equal(p.blobs(), 0);
});

test("offroad explains when the route map becomes available", async () => {
  const p = await page([{ status: 204, reason: "offroad" }]);
  assert.equal(p.element("mapStatus").hidden, false);
  assert.match(p.element("mapStatus").textContent, /driving screen is active/);
  assert.equal(p.element("map").hidden, true);
});

test("ready map replaces instructions and GPS loss removes the stale image", async () => {
  const p = await page([{ status: 200, reason: "ready" }, { status: 200, reason: "position" }]);
  assert.equal(p.element("map").hidden, false);
  assert.equal(p.element("map").src, "blob:1");
  assert.equal(p.element("mapStatus").hidden, true);
  await p.next();
  assert.equal(p.element("map").hidden, true);
  assert.equal(p.element("map").src, undefined);
  assert.equal(p.element("mapStatus").hidden, false);
  assert.match(p.element("mapStatus").textContent, /GPS/);
  assert.deepEqual(p.revoked, ["blob:1"]);
});

test("network failure displays a localized connection message", async () => {
  const p = await page([new Error("offline")], "ko");
  assert.equal(p.element("map").hidden, true);
  assert.equal(p.element("mapStatus").hidden, false);
  assert.match(p.element("mapStatus").textContent, /차량과의 연결/);
});


test("Traditional navigation explains route and network problems", async () => {
  const p = await page([{ status: 200, reason: "route" }, new Error("offline")], "zh-Hant-TW");
  assert.equal(p.element("title").textContent, "Carrot 導航");
  assert.match(p.element("mapStatus").textContent, /搜尋並選擇目的地/);
  await p.next();
  assert.match(p.element("mapStatus").textContent, /檢查與車輛的連線/);
  assert.equal(p.element("clear").textContent, "結束當前導航");
});

test("favorites edit requires a newly selected address and keeps errors in the editor", async () => {
  const saved = {id:'a'.repeat(32), name:'家', place_name:'臺北地址', latitude:25, longitude:121};
  const requests = [];
  const p = await page([{status:204, reason:'offroad'}], 'zh-TW', async (url, options) => {
    requests.push({url, options});
    if (url.includes('search?')) return {results:[{place_name:'新竹地址', latitude:24, longitude:120, permanent:true}]};
    if (options.method === 'PUT') return {error:'Favorites are unavailable. Please try again.'};
    return url.endsWith('favorites') ? {favorites:[saved]} : {destination:null};
  });
  const row = p.element('favorites').children[0];
  await row.children[2].children[0].trigger('click');
  assert.equal(p.element('favoriteName').value, '家');
  assert.equal(p.element('saveFavorite').disabled, false);
  p.element('favoriteQuery').value = '新竹';
  await p.element('favoriteQuery').trigger('input');
  assert.equal(p.element('saveFavorite').disabled, true);
  await p.element('favoriteForm').trigger('submit');
  assert.equal(requests.some(r => r.options.method === 'PUT'), false);
  await p.element('favoriteSearch').trigger('click');
  assert.ok(requests.some(r => r.url.endsWith('&permanent=true')));
  await p.element('favoriteResults').children[0].children[0].trigger('click');
  p.element('favoriteName').value = '公司';
  await p.element('favoriteForm').trigger('submit');
  const body = JSON.parse(requests.find(r => r.options.method === 'PUT').options.body);
  assert.equal(body.name, '公司'); assert.equal(body.latitude, 24); assert.equal(body.longitude, 120);
  assert.equal(p.element('favoriteForm').hidden, false);
  assert.match(p.element('editorStatus').textContent, /無法讀取或儲存最愛/);
  assert.equal(p.element('saveFavorite').disabled, false);
});

test("favorite navigation uses its ID and deletion requires an explicit second click", async () => {
  const saved = {id:'b'.repeat(32), name:'公司', place_name:'地址', latitude:25, longitude:121};
  const requests = [];
  const p = await page([{status:204,reason:'offroad'}], 'zh-TW', async (url, options) => {
    requests.push({url, options});
    if (url.endsWith('/destination')) return {destination:options.method === 'POST' ? saved : null};
    return {favorites:options.method === 'DELETE' ? [] : [saved]};
  });
  let row = p.element('favorites').children[0];
  await row.children[0].trigger('click');
  assert.ok(requests.some(r => r.url.endsWith(`/favorites/${saved.id}/destination`) && r.options.method === 'POST'));
  await row.children[2].children[1].trigger('click');
  assert.equal(requests.some(r => r.options.method === 'DELETE'), false);
  row = p.element('favorites').children[0];
  assert.equal(row.children[2].children[1].textContent, '確認刪除');
  await row.children[2].children[1].trigger('click');
  assert.equal(requests.filter(r => r.options.method === 'DELETE').length, 1);
  assert.equal(p.element('favorites').children.length, 0);
  assert.match(p.element('favoritesStatus').textContent, /尚未加入最愛/);
});
