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
      hidden: false, textContent: "", value: "", children: [], handlers: {}, options: [{},{}],
      addEventListener(name, handler) { this.handlers[name] = handler; },
      replaceChildren(...children) { this.children = children; }, append(...children) { this.children.push(...children); }, focus() {},
      async trigger(name) { await this.handlers[name]?.({preventDefault() {}}); await settle(); },
      removeAttribute(name) { delete this[name]; },
      setAttribute(name, value) { this[name] = value; },
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
      if (url.endsWith('/config')) return {ok:true,json:async()=>({provider:'mapbox',google_key:''})};
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

test('favorite editing saves only user text without an address lookup and keeps errors visible',async()=>{
  const saved={id:'a'.repeat(32),name:'家',place_name:'臺北地址',latitude:25,longitude:121},requests=[];
  const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
    requests.push({url,options});if(options.method==='PUT')return {error:'Favorites are unavailable. Please try again.'};
    return url.endsWith('favorites')?{favorites:[saved]}:{destination:null};
  });
  await p.element('favorites').children[0].children[2].children[0].trigger('click');
  assert.equal(p.element('favoriteName').value,'家');assert.equal(p.element('favoriteSearch').hidden,true);
  p.element('favoriteQuery').value='新竹市測試路';await p.element('favoriteQuery').trigger('input');
  assert.equal(p.element('saveFavorite').disabled,false);p.element('favoriteName').value='公司';await p.element('favoriteForm').trigger('submit');
  const body=JSON.parse(requests.find(r=>r.options.method==='PUT').options.body);
  assert.deepEqual(body,{provider:'query',name:'公司',query:'新竹市測試路'});assert.equal(requests.some(r=>r.url.includes('/search?')),false);
  assert.equal(p.element('favoriteForm').hidden,false);assert.match(p.element('editorStatus').textContent,/無法讀取或儲存最愛/);
});

test('favorite opens temporary Taiwan results and requires explicit selection before navigation',async()=>{
  const saved={id:'b'.repeat(32),provider:'query',name:'公司',query:'臺北自填地址'},requests=[];
  const place={place_name:'回傳的近似位置',latitude:25,longitude:121,feature_type:'street'};
  const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
    requests.push({url,options});
    if(url.includes(`/favorites/${saved.id}/query`))return {query:saved.query,requires_selection:true};
    if(url.includes('/search?'))return {results:[place]};
    if(url==='/api/navigation/destination')return {destination:options.method==='POST'?place:null};
    return {favorites:options.method==='DELETE'?[]:[saved]};
  });
  let row=p.element('favorites').children[0];await row.children[0].trigger('click');
  assert.ok(requests.some(r=>r.url.includes('country=tw&language=zh-Hant')));
  assert.equal(requests.some(r=>r.url==='/api/navigation/destination'&&r.options.method==='POST'),false);
  assert.match(p.element('results').children[0].children[1].textContent,/不是精確門牌/);
  await p.element('results').children[0].children[0].trigger('click');
  assert.equal(requests.filter(r=>r.url==='/api/navigation/destination'&&r.options.method==='POST').length,1);
  await row.children[2].children[1].trigger('click');assert.equal(requests.some(r=>r.options.method==='DELETE'),false);
  row=p.element('favorites').children[0];await row.children[2].children[1].trigger('click');
  assert.equal(requests.filter(r=>r.options.method==='DELETE').length,1);assert.equal(p.element('favorites').children.length,0);
});

test('legacy Google favorite retains its name and converts to text without geocoding',async()=>{
  const old={id:'c'.repeat(32),provider:'google',google_place_id:'legacy_id',name:'我的家'},requests=[];
  const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
    requests.push({url,options});return url.endsWith('/destination')?{destination:null}:{favorites:[old]};
  });
  await p.element('favorites').children[0].children[0].trigger('click');assert.equal(p.element('favoriteForm').hidden,false);
  assert.equal(p.element('favoriteName').value,'我的家');assert.equal(p.element('saveFavorite').disabled,true);
  p.element('favoriteQuery').value='使用者自己輸入的地址';await p.element('favoriteQuery').trigger('input');await p.element('favoriteForm').trigger('submit');
  const update=requests.find(r=>r.options.method==='PUT');assert.ok(update.url.endsWith(old.id));
  assert.deepEqual(JSON.parse(update.options.body),{provider:'query',name:'我的家',query:'使用者自己輸入的地址'});
  assert.equal(requests.some(r=>r.url.includes('/search?')),false);
});

test('saving a temporary result persists the original query and no returned provider data',async()=>{
  const requests=[],p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
    requests.push({url,options});if(url.includes('/search?'))return {results:[{latitude:25,longitude:121,place_name:'不得儲存的回傳地址',accuracy:'interpolated'}]};
    return url.endsWith('favorites')?{favorites:[]}:{destination:null};
  });
  p.element('query').value='我自己輸入的路名';await p.element('form').trigger('submit');
  await p.element('results').children[0].children[2].trigger('click');assert.equal(p.element('favoriteQuery').value,'我自己輸入的路名');
  await p.element('favoriteForm').trigger('submit');const body=JSON.parse(requests.find(r=>r.options.method==='POST').options.body);
  assert.deepEqual(body,{provider:'query',name:'我自己輸入的路名',query:'我自己輸入的路名'});
  assert.equal(JSON.stringify(body).includes('不得儲存'),false);assert.equal(requests.some(r=>r.url.includes('permanent=true')),false);
});

test('a late search cannot replace newer results or a changed search region',async()=>{
  const pending=[];
  const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url)=>{
    if(url.includes('/search?'))return await new Promise(resolve=>pending.push(resolve));
    return url.endsWith('favorites')?{favorites:[]}:{destination:null};
  });
  p.element('query').value='第一個地址';const first=p.element('form').trigger('submit');
  p.element('query').value='第二個地址';const second=p.element('form').trigger('submit');
  pending[1]({results:[{place_name:'新結果'}]});await second;
  pending[0]({results:[{place_name:'舊結果'}]});await first;
  assert.equal(p.element('results').children[0].children[0].textContent,'新結果');
  p.element('searchRegion').value='';await p.element('searchRegion').trigger('change');assert.equal(p.element('results').children.length,0);
});
