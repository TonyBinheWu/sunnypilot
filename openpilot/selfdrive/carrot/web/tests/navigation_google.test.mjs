import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../js/pages/navigation_google.js',import.meta.url),'utf8');
test('cached Google entry points reject with migration guidance and perform no SDK/network work',async()=>{
  const forbidden=()=>{throw Error('Google transport must not be used');};
  const target={fetch:forbidden,document:{createElement:forbidden},google:new Proxy({},{get:forbidden})};
  vm.runInNewContext(code,target);
  const view=target.CarrotNavigationGoogle.create({key:'old-browser-key'});
  for(const call of [()=>view.showMap({}),()=>view.search('臺北車站',{}),()=>view.resolveFavorite({},{})])
    await assert.rejects(call(),/Mapbox.*OpenStreetMap/);
  assert.throws(()=>target.CarrotNavigationGoogle.reference({},'家'),/重新載入/);
  view.updateRoute({});view.recenter();
});
test('new navigation page has native-map attribution and no Google SDK or key entry',()=>{
  const html=readFileSync(new URL('../navigation.html',import.meta.url),'utf8');
  assert.match(html,/mapAttribution/);assert.match(html,/OpenStreetMap/);
  assert.doesNotMatch(html,/navigation_google\.js|maps\.google|googleapis|googleKey|googleMap|<select id="mapProvider"/);
});
