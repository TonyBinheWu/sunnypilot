import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../js/pages/navigation_osm.js',import.meta.url),'utf8');
const settle=()=>new Promise(r=>setImmediate(r));
function fixture(installed=null){
 const elements=new Map(),calls=[],timers=[],layers=[],listeners={};let visible=true;
 const element=id=>{if(!elements.has(id))elements.set(id,{hidden:false,dataset:{}});return elements.get(id);};
 let center;
 const map={getCenter:()=>center,setView(p,z){center={lat:p[0],lng:p[1]};calls.push(['center',p,z]);return this;},getZoom:()=>16,on:(e,f)=>listeners[e]=f,removeLayer:l=>calls.push(['remove',l]),invalidateSize(){}};
 const layer={on(){return this;},addTo(){return this;}};
 const route={addTo(){return this;},setLatLngs(points){layers.push(points);}};
 let view={position:{lat:25,lng:121},route_id:1,coordinates:[[121,25],[121.1,25.1]]};
 const target={document:{hidden:false,getElementById:element},window:{addEventListener(){}},AbortController,setTimeout:f=>{timers.push(f);return f;},clearTimeout(){},L:{map:()=>map,control:{zoom:()=>layer},tileLayer:(url,options)=>{calls.push(['tiles',url,options]);return layer;},polyline:()=>route,circleMarker:(p)=>({addTo(){calls.push(['point',p]);return this;}})},fetch:async url=>{calls.push(['fetch',url]);return {ok:true,json:async()=>url.endsWith('/config')?{osm_tile_url:'/fixture-osm/{z}/{x}/{y}.png'}:view};}};
 if(installed)target.CarrotOfflineMap={start:()=>({info:()=>installed,refresh:async()=>{},layer:()=>{calls.push(['local',installed.version]);return layer;}})};
 vm.runInNewContext(source,target);
 const api=target.CarrotNavigationOsm.start({tr:(k,e)=>e,isVisible:()=>visible});
 return {api,calls,layers,timers,listeners,element,pan:(lat,lng)=>{center={lat,lng};listeners.moveend();},setVisible:v=>visible=v,setView:v=>view=v,next:async()=>{await timers.pop()();await settle();}};
}
test('OSM displays exactly the read-only route; model maps and destination writes are never requested',async()=>{
 const p=fixture();await settle();
 assert.deepEqual(JSON.parse(JSON.stringify(p.layers.at(-1))),[[25,121],[25.1,121.1]]);
 assert.ok(p.calls.some(c=>c[0]==='tiles'&&c[1].startsWith('/fixture-osm/')));
 assert.ok(p.calls.filter(c=>c[0]==='fetch').every(c=>['/api/navigation/config','/api/navigation/route_view'].includes(c[1])));
 const options=p.calls.find(c=>c[0]==='tiles')[2];assert.equal(options.keepBuffer,0);assert.equal(options.referrerPolicy,'strict-origin-when-cross-origin');
 p.setView({position:null,coordinates:[],route_id:0});await p.next();assert.equal(p.layers.at(-1).length,0);
});
test('hidden view stops polling; manual pan stops follow and the current-position action restores it',async()=>{
 const p=fixture();await settle();p.listeners.dragstart();assert.equal(p.element('mapFollow').hidden,false);
 const before=p.calls.filter(c=>c[0]==='center').length;await p.next();assert.equal(p.calls.filter(c=>c[0]==='center').length,before);
 p.element('mapFollow').onclick();assert.equal(p.element('mapFollow').hidden,true);
 p.setVisible(false);const reads=p.calls.filter(c=>c[0]==='fetch').length;await p.next();assert.equal(p.calls.filter(c=>c[0]==='fetch').length,reads);
});
test('malformed or unbounded geometry is removed instead of drawing arbitrary coordinates',async()=>{
 const p=fixture();const value=p.api.normalize({position:{lat:NaN,lng:121},route_id:1,coordinates:[[121,25],[999,25]]});assert.equal(value.point,null);assert.equal(value.route.length,0);
 assert.equal(p.api.normalize({route_id:1,coordinates:Array(4097).fill([121,25])}).route.length,0);await settle();
});
test('turn and remaining-distance cards are sourced from fresh route data and removed on expiry',async()=>{
 const p=fixture();await settle();p.setView({position:{lat:25,lng:121},route_id:4,coordinates:[[121,25]],instruction:{text:'實際測試路',modifier:'left',distance:230,remaining_m:4500,remaining_s:370}});await p.next();
 assert.equal(p.element('mapManeuver').hidden,false);assert.equal(p.element('mapTurn').textContent,'← 230 m');assert.equal(p.element('mapRemaining').textContent,'4.5 km · 7 min');assert.equal(p.element('mapRoad').textContent,'實際測試路');
 p.setView({position:null,coordinates:[],route_id:0});await p.next();assert.equal(p.element('mapManeuver').hidden,true);assert.equal(p.element('mapTrip').hidden,true);
});

test('installed Taiwan package survives panning and replaces the online layer inside its bounds',async()=>{
 const p=fixture({bounds:[118,20,123,27],version:'1'});await settle();
 const source=()=>p.element('osmMap').dataset.basemap;
 assert.equal(source(),'offline');
 assert.ok(!p.calls.some(c=>c[0]==='tiles'));
 p.pan(24,121);assert.equal(p.calls.filter(c=>c[0]==='local').length,1);
 p.pan(35,139);assert.equal(source(),'online');assert.equal(p.calls.filter(c=>c[0]==='tiles').length,1);
 p.pan(25,121);assert.equal(source(),'offline');assert.equal(p.calls.filter(c=>c[0]==='local').length,2);
});
