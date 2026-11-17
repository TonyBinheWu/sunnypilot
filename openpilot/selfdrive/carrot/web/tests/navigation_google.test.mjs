import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
const code=readFileSync(new URL('../js/pages/navigation_google.js',import.meta.url),'utf8');
function fixture(key='test-browser-key-000000000000'){
  const elements=[],scripts=[],maps=[],lines=[],circles=[];
  class Element extends EventTarget{
    constructor(tag){super();this.tag=tag;this.children=[];this.places=[];this.attrs={};}
    append(...nodes){this.children.push(...nodes);}
    replaceChildren(...nodes){this.children=nodes;}
    setAttribute(k,v){this.attrs[k]=v;}
    remove(){}
  }
  const target={setTimeout,clearTimeout,google:{maps:{
    importLibrary:async()=>{},
    Map:class{constructor(){maps.push(this);this.zoom=7;}addListener(){}fitBounds(b){this.bounds=b;}panTo(p){this.center=p;}getZoom(){return this.zoom;}setZoom(z){this.zoom=z;}},
    Polyline:class{constructor(){lines.push(this);}setPath(p){this.path=p;}},
    Circle:class{constructor(){circles.push(this);}setCenter(p){this.center=p;}setVisible(v){this.visible=v;}},
    LatLngBounds:class{constructor(){this.points=[];}extend(p){this.points.push(p);}}
  }}};
  const doc={createElement(tag){const e=new Element(tag);elements.push(e);return e;},head:{append(s){scripts.push(s);setImmediate(()=>target.__carrotGoogleMapsReady());}}};
  const scope={URLSearchParams,globalThis:{},document:doc,window:target};vm.runInNewContext(code,scope);
  const api=scope.globalThis.CarrotNavigationGoogle;
  return {api,view:api.create({doc,target,key}),doc,target,elements,scripts,maps,lines,circles};
}
const plain=x=>JSON.parse(JSON.stringify(x));
test('Google is lazy, missing key never contacts Google, map instance is reused',async()=>{
  const h=fixture();assert.equal(h.scripts.length,0);
  await h.view.showMap({});await h.view.showMap({});
  assert.equal(h.scripts.length,1);assert.equal(h.maps.length,1);
  const no=fixture('');await assert.rejects(no.view.showMap({}),/金鑰/);assert.equal(no.scripts.length,0);
});
test('display uses the exact Mapbox coordinate order and clears expired data',async()=>{
  const h=fixture();await h.view.showMap({});
  const route=Array.from({length:4096},(_,i)=>[121+i/1e5,25+i/1e5]);
  h.view.updateRoute({route_id:42,position:{lat:25,lng:121},coordinates:route});
  assert.equal(h.lines[0].path.length,4096);assert.deepEqual(plain(h.lines[0].path[2048]),{lat:route[2048][1],lng:route[2048][0]});
  assert.equal(h.circles[0].visible,true);
  h.view.updateRoute(null);assert.equal(h.lines[0].path.length,0);assert.equal(h.circles[0].visible,false);
  h.view.updateRoute({coordinates:[[121,25],[NaN,25]],position:{lat:NaN,lng:121}});
  assert.equal(h.lines[0].path.length,0);assert.equal(h.circles[0].visible,false);
});
test('manual UI Kit query returns selected coordinates without a second details call',async()=>{
  const h=fixture(),host=h.doc.createElement('div'),chosen=[];
  const pending=h.view.search('臺北車站',host,p=>chosen.push(p));
  await new Promise(setImmediate);await new Promise(setImmediate);
  const component=h.elements.find(e=>e.tag==='gmp-place-search');
  const request=h.elements.find(e=>e.tag==='gmp-place-text-search-request');
  assert.equal(request.textQuery,'臺北車站');assert.equal(request.attrs['max-result-count'],'5');
  component.places=[{id:'ChIJ_test'}];component.dispatchEvent(new Event('gmp-load'));assert.equal(await pending,1);
  const event=new Event('gmp-select');event.place={id:'ChIJ_test',location:{lat:()=>25,lng:()=>121},fetchFields(){throw Error('extra billing forbidden');}};
  component.dispatchEvent(event);await new Promise(setImmediate);
  assert.deepEqual(plain(chosen),[{latitude:25,longitude:121,place_name:'臺北車站',provider:'google',google_place_id:'ChIJ_test'}]);
  assert.equal(h.elements.some(e=>e.tag.includes('advanced')||e.tag.includes('autocomplete')),false);
});
test('Google favorite persistence excludes all coordinates and provider addresses',()=>{
  const h=fixture();const saved=h.api.reference({google_place_id:'ChIJ_test',latitude:25,longitude:121,place_name:'provider address'},'我命名的家');
  assert.deepEqual(plain(saved),{provider:'google',google_place_id:'ChIJ_test',name:'我命名的家'});
  assert.throws(()=>h.api.reference({google_place_id:'../bad'},'家'));
});
test('favorite coordinates are refreshed by a visible attributed UI Kit element',async()=>{
  const h=fixture(),host=h.doc.createElement('div');
  const pending=h.view.resolveFavorite({provider:'google',google_place_id:'ChIJ_test',name:'家'},host);
  await new Promise(setImmediate);await new Promise(setImmediate);
  const details=h.elements.find(e=>e.tag==='gmp-place-details-compact');
  assert.equal(host.children[0],details);assert.equal(details.children[1].place,'ChIJ_test');
  details.place={location:{lat:24,lng:120}};details.dispatchEvent(new Event('gmp-load'));
  assert.deepEqual(plain(await pending),{latitude:24,longitude:120,place_name:'家',provider:'google',google_place_id:'ChIJ_test'});
});
