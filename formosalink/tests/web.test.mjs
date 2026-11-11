import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {translations} from '../web/i18n.js';
import {parsePairingFragment,validatePairing,readPending,savePending,clearPending} from '../web/pairing.js';
const html=readFileSync(new URL('../web/index.html',import.meta.url),'utf8');
test('all three languages have complete matching, nonempty dictionaries',()=>{
  const keys=Object.keys(translations['zh-TW']).sort();
  for(const lang of ['zh-TW','en','ja']){
    assert.deepEqual(Object.keys(translations[lang]).sort(),keys);
    for(const value of Object.values(translations[lang]))assert.ok(typeof value==='string'&&value.length>0);
    for(const match of html.matchAll(/data-i18n="([^"]+)"/g))assert.ok(translations[lang][match[1]],`${lang}: ${match[1]}`);
  }
});
test('dynamic device content cannot become HTML and private telemetry is not cached',()=>{
  const js=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
  assert.ok(!js.includes('innerHTML'));
  assert.ok(js.includes('textContent'));
  assert.ok(js.includes("cache:'no-store'"));
  const worker=readFileSync(new URL('../web/sw.js',import.meta.url),'utf8');
  assert.ok(!worker.includes('caches.')&&!worker.includes("'fetch'"));
});

test('QR pairing survives sign-in in this tab and expires without manual credential inputs',()=>{
  const now=1700000000, code='A1B2C3D4E5F6', fp='a'.repeat(24);
  const pending=parsePairingFragment(`#pair=${code}&fp=${fp}&expires=${now+600}`,now);
  assert.deepEqual(pending,{version:1,code,fingerprint:fp,expires_at:now+600});
  const values=new Map(),storage={getItem:k=>values.get(k),setItem:(k,v)=>values.set(k,v),removeItem:k=>values.delete(k)};
  assert.equal(savePending(storage,pending),true);
  assert.deepEqual(readPending(storage,now),pending);
  assert.equal(readPending(storage,now+600),null);
  assert.equal(values.size,0);
  savePending(storage,pending);clearPending(storage);assert.equal(values.size,0);
  assert.ok(!html.includes('type="password"')&&!html.includes('id="pair-code"')&&!html.includes('id="fingerprint"'));
});

test('QR parser rejects duplicate or forged fields, malformed input and unavailable storage',()=>{
  const now=1700000000, base='#pair=A1B2C3D4E5F6&fp='+ 'a'.repeat(24)+'&expires='+ (now+600);
  for(const fragment of [base+'&owner_id=local-admin',base+'&pair=AAAAAAAAAAAA',base.replace('A1B2C3D4E5F6','<script>'),base.replace('1700000600','Infinity'),base.replace('1700000600','1700000000'),'x'.repeat(257)])assert.equal(parsePairingFragment(fragment,now),null);
  assert.equal(validatePairing({version:1,code:123456789012,fingerprint:'a'.repeat(24),expires_at:now+600},now),null);
  assert.equal(readPending(undefined,now),null);
  assert.equal(savePending(undefined,{}),false);
  clearPending(undefined);
  const js=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
  assert.ok(js.includes("addEventListener('hashchange'"));
  assert.ok(!js.includes("localStorage.setItem('formosalink-pending"));
});
import {sections,category,filterEntries,parseRoute,routeFor} from '../web/device-settings.js';
test('device workspace routes and category search preserve native identities',()=>{
 const id='59bbc277-4ab4-4a1f-8fe0-4cb7b17d7947';
 assert.deepEqual(parseRoute(routeFor(id,'models')),{device:id,section:'models'});
 assert.equal(parseRoute('#dashboard'),null);
 assert.deepEqual(parseRoute('#device='+id+'&tab=unknown'),{device:id,section:'device'});
 const entries=[{key:'QuietMode',group:{en:'Display'},title:{'zh-TW':'安靜模式',en:'Quiet mode',ja:'静音モード'}},{key:'Mads',group:{en:'Steering'},title:{'zh-TW':'轉向輔助',en:'Steering assistance',ja:'操舵支援'}}];
 assert.equal(category(entries[0]),'display');
 assert.deepEqual(filterEntries(entries,'steering'),[entries[1]]);
 assert.deepEqual(filterEntries(entries,'steering','安靜'),[entries[0]]);
 assert.deepEqual(filterEntries(entries,'display','MADS'),[entries[1]]);
 assert.deepEqual(filterEntries(entries,'display','静音'),[entries[0]]);
 assert.deepEqual(filterEntries(entries,'display','unavailable'),[]);
 for(const lang of ['zh-TW','en','ja'])for(const section of sections){assert.ok(translations[lang]['section_'+section]);assert.ok(translations[lang]['sectionDesc_'+section]);}
});
