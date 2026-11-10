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
