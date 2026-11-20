import test from 'node:test';
import assert from 'node:assert/strict';
import {installCockpitControlLayout} from '../src/features/cockpit/control_layout.js';

// Isolated DOM adapter; selectGroup is the real integration boundary. No
// driving parameters or browser storage are written by this composition.
async function fixture(options={},environment={}){
  const ids=new Map(),selected=[],media=[];
  const doc={body:{dataset:{cockpitPanel:'setting'}},getElementById:id=>ids.get(id),querySelector:()=>null};
  class Node{
    constructor(tag){this.tag=tag;this.nodeType=1;this.ownerDocument=doc;this.children=[];this.dataset={};this.attrs={};this.className='';this.classList={add:c=>{this.className+=' '+c;},contains:c=>this.className.split(' ').includes(c),remove:c=>{this.className=this.className.split(' ').filter(x=>x!==c).join(' ');},toggle:(c,on)=>on?this.classList.add(c):this.classList.remove(c)};}
    append(...nodes){for(const n of nodes){if(n.parentElement)n.parentElement.children=n.parentElement.children.filter(x=>x!==n);n.parentElement=this;this.children.push(n);}}
    prepend(n){this.children.unshift(n);n.parentElement=this;}
    replaceChildren(...nodes){this.children=[];this.append(...nodes);}
    setAttribute(k,v){this.attrs[k]=v;}addEventListener(){}focus(){doc.focused=this;}
    matches(selector){return selector[0]==='.'?this.classList.contains(selector.slice(1)):this.tag===selector;}
    querySelectorAll(selector){return this.children.flatMap(n=>[...(n.matches(selector)?[n]:[]),...n.querySelectorAll(selector)]);}
    querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
  }
  doc.createElement=tag=>new Node(tag);doc.createElementNS=(_ns,tag)=>new Node(tag);doc.documentElement=new Node('html');
  for(const id of ['pageSetting','settingScreenHost'])ids.set(id,new Node('div'));
  const target={AbortController,setTimeout,clearTimeout,MutationObserver:class{observe(){}},addEventListener(){},matchMedia:()=>({addEventListener:(_name,fn)=>media.push(fn)}),
    fetch:async()=>({ok:true,json:async()=>({categories:[{groups:[{id:'START_AUTO'},{id:'BUTTON_PRESET'},{id:'SYS_SOUND'}]}]})}),
    switchSettingTab:async()=>{},selectGroup:id=>selected.push(id),...environment};
  const api=installCockpitControlLayout(doc,target,options);await new Promise(setImmediate);
  return {doc,target,api,selected,media};
}

test('category changes preserve each last tab and dismiss the narrow navigation without writes',async()=>{
  const {api,selected,doc,media}=await fixture(),shell=api.shell;
  const byClass=cls=>shell.querySelector('.'+cls),section=id=>byClass('cockpit-control-nav-list').children.find(n=>n.dataset.section===id);
  byClass('cockpit-category-toggle').onclick();assert.equal(shell.dataset.navOpen,'true');assert.equal(byClass('cockpit-control-pane').inert,true);assert.equal(doc.focused,section('controls'));
  byClass('cockpit-control-tabs').children[1].onclick();await new Promise(setImmediate);assert.equal(selected.at(-1),'BUTTON_PRESET');assert.equal(shell.dataset.navOpen,'false');assert.equal(byClass('cockpit-control-pane').inert,false);
  section('sound').onclick();await new Promise(setImmediate);assert.equal(selected.at(-1),'SYS_SOUND');
  section('controls').onclick();await new Promise(setImmediate);assert.equal(selected.at(-1),'BUTTON_PRESET');
  byClass('cockpit-category-toggle').onclick();media[0]();assert.equal(shell.dataset.navOpen,'false');assert.equal(byClass('cockpit-control-pane').inert,false);
});

test('All settings opens the catalog directly, with a category picker on narrow screens',async()=>{
  const {api,selected}=await fixture({onAction(){}});
  const toggle=api.shell.querySelector('.cockpit-category-toggle');
  toggle.offsetWidth=44;
  api.openCatalog();await new Promise(setImmediate);
  assert.equal(api.shell.dataset.navOpen,'true');
  assert.equal(api.shell.dataset.overview,'false');
  assert.equal(selected.at(-1),'START_AUTO');
});
test('opening Device directly from the overview reveals the shared settings list',async()=>{
  const {api}=await fixture({onAction(){}});
  assert.equal(api.shell.dataset.overview,'true');
  const buttons=api.shell.querySelector('.cockpit-control-nav-list').children;
  await buttons.at(-1).onclick();
  assert.equal(api.shell.dataset.device,'true');
  assert.equal(api.shell.dataset.overview,'false');
  assert.equal(api.shell.querySelector('.cockpit-quick-controls').hidden,true);
});
test('a delayed tab switch cannot overwrite a newer category selection',async()=>{
  const {api,target,selected}=await fixture();const pending=[];target.switchSettingTab=()=>new Promise(resolve=>pending.push(resolve));
  const nav=api.shell.querySelector('.cockpit-control-nav-list');
  nav.children.find(n=>n.dataset.section==='sound').onclick();nav.children.find(n=>n.dataset.section==='controls').onclick();
  pending[1]();await new Promise(setImmediate);assert.equal(selected.at(-1),'START_AUTO');const count=selected.length;
  pending[0]();await new Promise(setImmediate);assert.equal(selected.length,count);assert.equal(api.shell.querySelector('h2').textContent,'控制');
});

test('touchscreen quick controls route only explicit actions and retain access to all settings',async()=>{
 const actions=[];const {api,selected}=await fixture({onAction:action=>actions.push(action)}),shell=api.shell;
 assert.equal(shell.dataset.overview,'true');const quick=shell.querySelector('.cockpit-quick-controls');assert.equal(quick.hidden,false);assert.equal(quick.children.length,7);
 quick.children[0].onclick();assert.deepEqual(actions,['profile']);assert.equal(selected.at(-1),'START_AUTO');
 quick.children[6].onclick();await new Promise(setImmediate);assert.equal(shell.dataset.overview,'false');assert.equal(quick.hidden,true);assert.equal(selected.at(-1),'START_AUTO');
 api.selectSection('sound');await new Promise(setImmediate);assert.equal(selected.at(-1),'SYS_SOUND');
});


test('Back closes a category drawer, then detail, then search without changing settings',async()=>{
 const {api,doc,target,selected}=await fixture();let detail=true,search=true,backs=0,clears=0;
 const oldGet=doc.getElementById;doc.getElementById=id=>id==='settingScreenItems'?{classList:{contains:()=>detail}}:id==='carrotTabContent'?{classList:{contains:()=>search}}:oldGet(id);
 target.history={back(){backs++;detail=false;}};target.exitSettingInlineSearchSurface=()=>{search=false;clears++;};const count=selected.length;
 api.shell.querySelector('.cockpit-category-toggle').onclick();assert.equal(api.back(),true);assert.equal(backs,0);assert.equal(api.shell.dataset.navOpen,'false');
 assert.equal(api.back(),true);assert.equal(backs,1);assert.equal(api.back(),true);assert.equal(clears,1);assert.equal(api.back(),false);assert.equal(selected.length,count);
});


test('a failed catalog offers a read-only retry without leaving the control page',async()=>{
 let calls=0;const {api,target,selected}=await fixture({}, {fetch:async()=>{calls++;throw Error('offline');}});
 const retry=api.shell.querySelector('.cockpit-control-retry');assert.equal(retry.hidden,false);assert.equal(selected.length,0);
 target.fetch=async()=>{calls++;return {ok:true,json:async()=>({categories:[{groups:[{id:'SYS_SOUND'}]}]})};};retry.onclick();await new Promise(setImmediate);
 assert.equal(calls,2);assert.equal(retry.hidden,true);assert.equal(selected.at(-1),'SYS_SOUND');
});
