import {readFileSync} from 'node:fs';
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {visionPresentation,cockpitTelemetryStale} from '../src/features/cockpit/presentation.js';
import {drawDetectedMesh} from '../src/features/drive/contents/vision/hud/object_mesh.js';
import {drawSceneObject} from '../src/features/drive/contents/vision/hud/driving_scene.js';
import {installCockpitHelp} from '../src/features/cockpit/embedded.js';

test('cockpit presentation is transient, preserves BEV and never rewrites regular preferences',()=>{
  for(const saved of ['carrot','live_view','tesla','bev',undefined]){
    const target={document:{body:{dataset:{}}},CarrotWebSettingsState:Object.freeze({vision_presentation:saved})};
    assert.equal(visionPresentation(target),saved);
    target.document.body.dataset.cockpitPanel='vision';assert.equal(visionPresentation(target),saved==='bev'?'bev':'tesla');
    target.document.body.dataset.cockpitPanel='setting';assert.equal(visionPresentation(target),saved);
    assert.equal(target.CarrotWebSettingsState.vision_presentation,saved);
  }
});
test('source expiry gates live cockpit instruments even when another HUD publisher replays old values',()=>{
  const target={document:{body:{dataset:{cockpitPanel:'vision',cockpitTelemetryFresh:'false'}}}};
  assert.equal(cockpitTelemetryStale(target),true);
  target.document.body.dataset.cockpitTelemetryFresh='true';assert.equal(cockpitTelemetryStale(target),false);
  target.document.body.dataset.cockpitTelemetryFresh='false';target.CarrotVisionReplay={isActive:()=>true};assert.equal(cockpitTelemetryStale(target),false);
  delete target.CarrotVisionReplay;target.document.body.dataset.cockpitPanel='setting';assert.equal(cockpitTelemetryStale(target),false);
});

function canvas(){
  const commands=[];
  const ctx=new Proxy({measureText:()=>({width:20})},{get:(t,k)=>t[k]??((...v)=>{for(const x of v)if(typeof x==='number')assert.ok(Number.isFinite(x));commands.push([k,...v]);}),set:(t,k,v)=>(commands.push([k,v]),t[k]=v,true)});
  return {ctx,commands};
}
const project=(x,y,z=0)=>[320+y*8,240-x*3-z*12];
test('fifteen grounded classes have finite, distinct original mesh silhouettes',()=>{
  const signatures=[];
  for(const kind of ['car','bus','truck','person','motorcycle','bicycle','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe']){
    const {ctx,commands}=canvas();drawDetectedMesh(ctx,project,{x:15,y:2,kind});
    assert.ok(commands.some(c=>c[0]==='fill'));signatures.push(JSON.stringify(commands));
  }
  assert.equal(new Set(signatures).size,15);
});
test('unknown radar targets remain neutral and invalid positions do not create a mesh',()=>{
  const a=canvas();drawSceneObject(a.ctx,project,{x:15,y:2,kind:'unknown'});
  assert.equal(a.commands.some(c=>c[0]==='ellipse'),false);assert.ok(a.commands.filter(c=>c[0]==='lineTo').length>=12);assert.equal(a.commands.some(c=>c[0]==='fill'),false);
  for(const point of [{x:NaN,y:0},{x:1,y:Infinity}]){const b=canvas();drawDetectedMesh(b.ctx,project,{...point,kind:'car'});assert.equal(b.commands.length,0);}
});
test('full existing description is retained under an idempotent disclosure',()=>{
  let observer;
  const descriptions=[],all=[];
  const element=()=>({children:[],append(...nodes){this.children.push(...nodes);for(const n of nodes)n.parent=this;}});
  const description={textContent:'繁中完整功能說明\n既有安全限制',closest(){return this.parent?.className==='cockpit-help'?this.parent:null;},before(node){all.push(node);}};
  descriptions.push(description);
  const doc={body:{},defaultView:{MutationObserver:class{constructor(fn){observer=fn;}observe(){}}},querySelectorAll:()=>descriptions,createElement:element};
  installCockpitHelp(doc);observer();installCockpitHelp(doc);
  assert.equal(all.length,1);assert.equal(all[0].children[0].textContent,'功能說明');
  assert.equal(all[0].children[1],description);assert.equal(description.textContent,'繁中完整功能說明\n既有安全限制');
});


test('Vision HUD selects the same cockpit-aware presentation as its scene',()=>{
  const source=readFileSync(new URL('../src/features/drive/contents/vision/hud/index.js',import.meta.url),'utf8');
  assert.match(source,/presentation = visionPresentation\(target\);/);
  assert.doesNotMatch(source,/presentation = target.CarrotWebSettingsState.vision_presentation/);
});
