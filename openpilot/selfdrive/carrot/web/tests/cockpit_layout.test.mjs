import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const css=readFileSync(new URL('../css/cockpit.css',import.meta.url),'utf8');
const native=readFileSync(new URL('../../../../../tools/carrot_android/src/me/shind0/carrotweb/CockpitLayout.java',import.meta.url),'utf8');
const script=JSON.parse(native.match(/SCRIPT = (".*");/)[1]);

test('viewport has a definite percentage and vh fallback when dvh is unsupported',()=>{
  const legacy=css.replace(/[^{};]+:[^{};]*dvh[^{};]*;?/g,'');
  assert.match(legacy,/html\{height:100%;overflow:hidden\}/);
  assert.match(legacy,/body\{[^}]*height:100%;height:100vh;min-height:0;/);
  assert.match(legacy,/grid-template-rows:calc\(var\(--status-size\)[^;]+minmax\(0,1fr\)[^;]+var\(--dock-size\)/);
});

test('APK repair is cockpit-only, idempotent and uses live viewport percentages',()=>{
  const nodes=new Map(),added=[];
  const document={getElementById:id=>nodes.get(id),createElement:()=>({}),head:{appendChild(node){nodes.set(node.id,node);added.push(node);}}};
  const context={document,location:{pathname:'/'}};
  vm.runInNewContext(script,context);assert.equal(added.length,0);
  context.location.pathname='/cockpit';vm.runInNewContext(script,context);vm.runInNewContext(script,context);
  assert.equal(added.length,1);
  assert.match(added[0].textContent,/html\{height:100%;overflow:hidden\}/);
  assert.match(added[0].textContent,/body\{height:100%!important;min-height:0!important\}/);
  assert.doesNotMatch(script,/fetch|localStorage|addJavascriptInterface|innerHeight|\d+px/);
});

test('native repair is behind the current-device and cockpit-package guards',()=>{
  const activity=readFileSync(new URL('../../../../../tools/carrot_android/src/me/shind0/carrotweb/MainActivity.java',import.meta.url),'utf8');
  assert.match(activity,/if \(!pageLoadFailed && view.getParent\(\) == content && isCurrent\(Uri.parse\(url\)\)\) \{\s*pageReady = true;\s*cancelDeviceReconnect\(\);\s*view.setKeepScreenOn\([^;]+;\s*if \(UpdatePolicy.cockpit\(getPackageName\(\)\)\)\s*view.evaluateJavascript\(onDevicePage\(CockpitLayout.SCRIPT\), null\)/);
});


test('cockpit host owns fullscreen independently of Vision JS dismissal',()=>{
  const activity=readFileSync(new URL('../../../../../tools/carrot_android/src/me/shind0/carrotweb/MainActivity.java',import.meta.url),'utf8');
  const poll=activity.slice(activity.indexOf('private void pollVisionHost()'),activity.indexOf('private void leaveVisionView()'));
  assert.ok(poll.indexOf('setVisionImmersive(true)')<poll.indexOf('web.evaluateJavascript'));
  assert.match(poll,/UpdatePolicy.cockpit\(getPackageName\(\)\) && "\/cockpit".equals/);
  assert.match(activity,/CarrotCockpit\?\.back\?\.\(\)/);
  assert.match(activity,/if\(!"true"\.equals\(handled\)\)title.performClick\(\)/);
});
