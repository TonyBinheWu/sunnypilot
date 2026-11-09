import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {translations} from '../web/i18n.js';
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
