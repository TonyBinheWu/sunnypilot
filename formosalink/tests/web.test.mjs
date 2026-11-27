import test from 'node:test';
import './settings-edits.test.mjs';
import './media.test.mjs';
import {hudText, plotPoints, tripRecords} from '../web/drive-view.js';
import {isModelSlot} from '../web/model-picker.js';

test('model search matches native model names across pages',()=>{
  const entry={key:'DrivingModelSmallPage2',title:{en:'Small model'},options:[{value:'a',label:{en:'Dragonfruit'}}]};
  assert.ok(isModelSlot(entry.key));
  assert.deepEqual(filterEntries([entry],'display','dragon'),[entry]);
  assert.deepEqual(filterEntries([entry],'display','missing'),[]);
});

test('trip routes handle the date line and HUD distinguishes zero from missing data',()=>{
  const points=[[25,179.99],[25,-179.99]];
  const trip={route:'r',start:1,last:10,m:55,points:[...points,[91,0]]};
  assert.deepEqual(tripRecords(['bad',JSON.stringify(trip)])[0].points,points);
  const [start,end]=plotPoints(points,240,110);
  assert.ok(start[0]<end[0] && start[0]>=0 && end[0]<=240);
  assert.equal(hudText({speed_kph:0,engaged:false},k=>k),'0 km/h · hudInactive');
  assert.equal(hudText({speed_kph:null,engaged:null},k=>k),'');
});
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
import {sections,category,filterEntries,parseRoute,routeFor,settingBlockReason} from '../web/device-settings.js';

test('settings distinguish global offroad/permission gates from per-setting conditions',()=>{
 const state={fresh:true,snapshot:{offroad:true,remote_enabled:true,info:{settings_guard:'ready'}}};
 assert.equal(settingBlockReason(state,{enabled:true}),null);
 assert.equal(settingBlockReason(state,{enabled:false,disabled_reason:'capability_required'}),'settingCapabilityRequired');
 assert.equal(settingBlockReason(state,{enabled:false,disabled_reason:'dependency_required'}),'settingDependencyRequired');
 state.snapshot.remote_enabled=false;
 assert.equal(settingBlockReason(state,{enabled:false}),'settingsLocalDisabled');
 state.snapshot.offroad=false;state.snapshot.info.settings_guard='waiting_device_state';
 assert.equal(settingBlockReason(state),'settingsStateWaiting');
 state.snapshot.info.settings_guard='onroad';
 assert.equal(settingBlockReason(state),'settingsDriving');
 state.fresh=false;
 assert.equal(settingBlockReason(state),'settingsOffline');
 assert.equal(settingBlockReason(null),'settingsWaiting');
});
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
import {healthValue} from '../web/health-ui.js';
import {themePreference} from '../web/theme.js';
import {textSizePreference} from '../web/text-size.js';
import {matchingVehicles} from '../web/vehicle-picker.js';
import {controlValue} from '../web/settings-edits.js';

test('text size restores a supported percentage or the browser default',()=>{
  for (const value of [75, 137, 200, 250]) assert.equal(textSizePreference({getItem:()=>String(value)}),value);
  for (const raw of [null,'','NaN','999','0','-1','100.5']) assert.equal(textSizePreference({getItem:()=>raw}),100);
  assert.equal(textSizePreference({getItem(){throw Error();}}),100);
});

test('searching the vehicle catalog retains the installed bundle name and HDA qualifier',()=>{
  const name='Kia Sorento (without HDA II) 2024-25', older='Kia Sorento Hybrid 2021-23';
  const vehicles={[older]:'KIA_SORENTO_HEV_4TH_GEN',[name]:'KIA_SORENTO_2024'};
  const entry={key:'CarPlatformBundle',type:'STRING',vehicles,group:{en:'Vehicle'},title:{en:'Select vehicle'}};
  for(const query of ['sorento hev 2025','2025 Kia Sorento Hybrid','2025 油電','KIA_SORENTO_2024']){
    assert.deepEqual(matchingVehicles(vehicles,query),[name]);
    assert.deepEqual(filterEntries([entry],'home',query),[entry]);
  }
  assert.deepEqual(matchingVehicles(vehicles,'2022 HEV'),[older]);
  assert.deepEqual(matchingVehicles({[older]:vehicles[older]},'2025 Sorento HEV'),[]);
  assert.equal(controlValue(entry,name),name);
  assert.equal(controlValue(entry,''),'');
  for(const raw of ['KIA_SORENTO_2024','Kia Sorento Hybrid 2025','__proto__',{}])assert.equal(controlValue(entry,raw),undefined);
});
test('health and theme keep unknown readings distinct from real zero',()=>{
 assert.equal(healthValue(0,' %'),'0 %');assert.equal(healthValue(null,' %'),'—');assert.equal(healthValue(NaN),'—');
 assert.equal(themePreference({getItem:()=> 'dark'}),'dark');assert.equal(themePreference({getItem:()=> 'invalid'}),'system');assert.equal(themePreference({getItem:()=>{throw Error();}}),'system');
 assert.equal(parseRoute('#device=a&tab=maps').section,'navigation');
});
import {parseCoordinates} from '../web/navigation-input.js';
test('navigation accepts explicit coordinates without opening external URLs',()=>{
 assert.deepEqual(parseCoordinates('25.03,121.56'),{latitude:25.03,longitude:121.56});
 assert.deepEqual(parseCoordinates('https://www.google.com/maps/@25.03,121.56,15z'),{latitude:25.03,longitude:121.56});
 assert.deepEqual(parseCoordinates('https://www.openstreetmap.org/#map=16/25.03/121.56'),{latitude:25.03,longitude:121.56});
 assert.equal(parseCoordinates('https://maps.app.goo.gl/short'),null);assert.equal(parseCoordinates('91,181'),null);assert.equal(parseCoordinates('javascript:alert(1)'),null);
});
import './settings-profile.test.mjs';
