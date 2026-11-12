import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {carrotUrl,isCarrotDevice,settingsStatus} from '../web/carrot-entry.js';
import {translations} from '../web/i18n.js';

const carrot={id:'device-a',snapshot:{metrics:{branch:'carrot-wip'}}};
test('Carrot settings use native web consent rather than the unused settings grant',()=>{
  const state={offroad:true,remote_enabled:false,catalog:[]};
  assert.equal(isCarrotDevice(carrot),true);
  assert.equal(settingsStatus(carrot,state,true),'carrotSettingsHelp');
  assert.equal(settingsStatus(carrot,state,false),'settingsOffline');
  assert.equal(settingsStatus(carrot,{...state,offroad:false},true),'settingsDriving');
  assert.equal(settingsStatus({},state,true),'settingsLocalDisabled');
  assert.equal(settingsStatus({},{...state,remote_enabled:true},true),'settingsReady');
  assert.equal(settingsStatus(carrot,null,false),'settingsWaiting');
});

test('native settings links retain per-device routing and encode device identifiers',()=>{
  assert.equal(carrotUrl('a',true),'/api/v1/devices/a/carrot/?formosa_page=setting');
  assert.equal(carrotUrl('b'),'/api/v1/devices/b/carrot/');
  assert.equal(carrotUrl('a/b?x#y',true),'/api/v1/devices/a%2Fb%3Fx%23y/carrot/?formosa_page=setting');
  for(const locale of ['zh-TW','en','ja'])for(const key of ['carrotSettings','carrotDeviceInfo','carrotSettingsHelp','carrotSearchHelp'])assert.ok(translations[locale][key]);
  assert.match(translations['zh-TW'].carrotSettingsHelp,/遠端 Carrot 網頁：關/);
});

test('the native page honors only the bridge navigation hint and keeps local preferences',()=>{
  const source=readFileSync(new URL('../../openpilot/selfdrive/carrot/web/js/shared/ui/navigation.js',import.meta.url),'utf8');
  const fn=source.match(/function resolveWebStartPage\(\) \{[\s\S]*?\n\}/)[0];
  const window={getWebStartPage:()=> 'tools'};
  const scope=vm.createContext({window,PAGE_ELEMENTS:{carrot:{},setting:{},tools:{}}});
  vm.runInContext(fn,scope);
  assert.equal(scope.resolveWebStartPage(),'tools');
  window.FormosaCarrotRemote={startPage:'setting'};
  assert.equal(scope.resolveWebStartPage(),'setting');
  assert.equal(window.getWebStartPage(),'tools');
  window.FormosaCarrotRemote={startPage:'terminal'};
  assert.equal(scope.resolveWebStartPage(),'tools');
});
