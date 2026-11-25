import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const source = await readFile(new URL("../js/pages/navigation_map.js", import.meta.url), "utf8");
const traditionalSource = await readFile(new URL("../js/pages/navigation_zh_tw.js", import.meta.url), "utf8");
const settle = () => new Promise((resolve) => setImmediate(resolve));

test("cockpit shows a verified approach and clears the route row after evidence expires", async () => {
  const script = await readFile(new URL("../js/planner_status.js", import.meta.url), "utf8");
  const elements = new Map();
  const get = (id) => {
    if (!elements.has(id)) elements.set(id, {previousElementSibling: {}});
    return elements.get(id);
  };
  const responses = [{routeCheck: "matched", approachManeuver: "branch right"}, {routeCheck: "instructionConflict"}, {}];
  let next;
  const target = {
    document: {getElementById: get, body: {dataset: {panel: "vision"}}, addEventListener() {}},
    MutationObserver: class {observe() {}}, AbortSignal, clearTimeout() {},
    setTimeout(fn) { next = fn; }, fetch: async () => ({ok: true, json: async () => responses.shift()}),
  };
  vm.runInNewContext(script, target);
  await settle();
  const row = get("plannerRouteCheck");
  assert.equal(row.textContent, "目前定位符合導航路線 · 前方靠右分岔");
  assert.equal(row.hidden, false);
  await next();
  assert.equal(row.textContent, "轉向提示與路線彎向不一致");
  await next();
  assert.equal(row.textContent, "");
  assert.equal(row.hidden, true);
  assert.equal(row.previousElementSibling.hidden, true);
});

async function page(responses, language = "en", handleApi = null, search = "") {
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
  const target = {
    document: { documentElement: {}, hidden: false, getElementById: element, createElement: makeElement },
    localStorage: { getItem: () => language }, navigator: {}, location: {search}, URLSearchParams,
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
  };
  vm.runInNewContext(traditionalSource + "\n" + source, target);
  await settle();
  return { target, element, revoked, blobs: () => blobs, next: async () => { await timers.shift()(); } };
}

test('one high-confidence exact address starts the existing destination flow once after explicit search',async()=>{
  const writes=[];
  const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
    if(url.includes('/search?'))return {results:[{latitude:25,longitude:121,place_name:'唯一完整地址',feature_type:'address',match_confidence:'high',accuracy:'rooftop'}]};
    if(options.method==='POST'){writes.push(JSON.parse(options.body));return {destination:writes.at(-1)};}
    if(url.endsWith('favorites'))return {favorites:[]};return {destination:null};
  });
  p.element('query').value='完整測試地址';await p.element('form').trigger('submit');assert.equal(writes.length,1);assert.equal(writes[0].place_name,'唯一完整地址');assert.equal(p.target.CarrotNavigationView.snapshot().active,true);
});
test('approximate single address and multiple addresses still require a location selection',async()=>{
  for(const results of [[{feature_type:'address',match_confidence:'medium',accuracy:'interpolated'}],[{feature_type:'address',match_confidence:'high'},{feature_type:'address',match_confidence:'high'}]]){
    let writes=0;
    const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
      if(url.includes('/search?'))return {results:results.map(v=>({...v,latitude:25,longitude:121,place_name:'待確認地址'}))};
      if(options.method==='POST')writes++;if(url.endsWith('favorites'))return {favorites:[]};return {destination:null};
    });
    p.element('query').value='待確認地址';await p.element('form').trigger('submit');assert.equal(writes,0);assert.equal(p.element('results').children.length,results.length);
  }
});
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


test('opening navigation restores an existing destination and ending reports the actual response',async()=>{
 const place={place_name:'既有目的地',latitude:25,longitude:121},calls=[];
 const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
  if(url.endsWith('favorites'))return {favorites:[]};calls.push(options.method||'GET');return {destination:options.method==='DELETE'?null:place};
 });
 const api=p.target.CarrotNavigationView;assert.equal(api.snapshot().active,true);assert.equal(api.snapshot().label,'既有目的地');assert.equal(p.element('clear').disabled,false);
 assert.equal((await api.end()).ended,true);assert.equal(api.snapshot().active,false);assert.equal(p.element('clear').disabled,true);assert.match(p.element('status').textContent,/已結束/);assert.deepEqual(calls,['GET','DELETE']);
});

test('late initial read cannot overwrite a new destination and duplicate writes are blocked',async()=>{
 let read,write;const calls=[],old={place_name:'舊位置'},place={place_name:'新位置',latitude:25,longitude:121};
 const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
  if(url.endsWith('favorites'))return {favorites:[]};if(url.includes('/search?'))return {results:[place]};
  calls.push(options.method||'GET');if(options.method==='POST')return await new Promise(r=>write=r);return await new Promise(r=>read=r);
 });
 p.element('query').value='自填地址';await p.element('query').trigger('input');await p.element('form').trigger('submit');
 const request=p.element('results').children[0].children[0].trigger('click');await settle();assert.equal(p.target.CarrotNavigationView.snapshot().busy,true);
 await assert.rejects(p.target.CarrotNavigationView.end());read({destination:old});await settle();assert.equal(p.target.CarrotNavigationView.snapshot().known,false);
 write({destination:place});await request;assert.equal(p.target.CarrotNavigationView.snapshot().label,'新位置');assert.deepEqual(calls,['GET','POST']);
});

test('lost end response is unknown, never automatically replayed, and can be reconciled with a read',async()=>{
 let destination={place_name:'測試目的地'},writes=0;
 const p=await page([{status:204,reason:'offroad'}],'zh-TW',async(url,options)=>{
  if(url.endsWith('favorites'))return {favorites:[]};if(options.method==='DELETE'){writes++;destination=null;throw Error('lost');}return {destination};
 });
 const api=p.target.CarrotNavigationView;await assert.rejects(api.end());assert.equal(api.snapshot().known,false);assert.equal(p.element('clear').disabled,false);assert.equal(p.element('clear').textContent,'重新讀取導航狀態');
 await assert.rejects(api.end());assert.equal(writes,1);await p.element('clear').trigger('click');assert.equal(api.snapshot().known,true);assert.equal(api.snapshot().active,false);assert.equal(writes,1);
});

test('embedded cockpit supplies Traditional Chinese before a language preference is saved',async()=>{
  const p=await page([{status:204,reason:'offroad'}],null,null,'?cockpit=1&lang=zh-tw');
  assert.equal(p.element('clear').textContent,'結束當前導航');
});
