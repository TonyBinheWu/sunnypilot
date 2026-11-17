import test from 'node:test';
import assert from 'node:assert/strict';
import {cockpitControlSections,composeCockpitControl} from '../src/features/cockpit/control_layout.js';

test('new settings categories keep every available group including future groups',()=>{
  const ids=['START_AUTO','SYS_SOUND','STEER','VEH_RADAR','NEXT_UPSTREAM_GROUP'];
  const result=cockpitControlSections({categories:[{groups:ids.map(id=>({id,'zh-tw':'繁中'+id}))}]});
  assert.deepEqual(result.flatMap(s=>s.groups.map(g=>g.id)).sort(),ids.sort());
  assert.equal(result.find(s=>s.id==='other').groups[0].label,'繁中NEXT_UPSTREAM_GROUP');
  assert.equal(result.find(s=>s.id==='sound').title,'聲音');
});
test('dedicated card preserves original control, handler, description, reset and history entry',()=>{
  const doc={createElement:tag=>new Node(tag)};
  class Node{
    constructor(tag,cls=''){this.tag=tag;this.className=cls;this.children=[];this.ownerDocument=doc;this.dataset={};this.attrs={};this.classList={add:c=>{this.className+=' '+c;}};}
    append(...nodes){for(const n of nodes){if(n.parent)n.parent.children=n.parent.children.filter(x=>x!==n);n.parent=this;this.children.push(n);}}
    replaceChildren(...nodes){this.children=[];this.append(...nodes);}
    querySelector(selector){return this.children.find(n=>n.className.split(' ').includes(selector.slice(1)))||this.children.map(n=>n.querySelector(selector)).find(Boolean)||null;}
    closest(selector){return this.parent?.className.split(' ').includes(selector.slice(1))?this.parent:null;}
    setAttribute(k,v){this.attrs[k]=v;}
    addEventListener(){}
    click(){this.onclick?.();}
  }
  const row=new Node('div','setting'),top=new Node('div','settingTop'),copy=new Node('div','setting-copy'),title=new Node('div','setting-title-row'),ctrl=new Node('div','ctrl'),input=new Node('input'),descr=new Node('div','descr'),actions=new Node('div','setting-actions'),reset=new Node('button'),other=new Node('section','setting-context');
  let changes=0,opened=null;input.onchange=()=>changes++;descr.textContent='完整繁中指南與既有警告';row.dataset.settingName='SoundLanguageVolume';row.onclick=()=>{opened=row.dataset.settingName;};
  ctrl.append(input);copy.append(title);top.append(copy,ctrl);actions.append(reset);row.append(top,descr,actions,other);
  assert.equal(composeCockpitControl(row,{openAssistantSetting:name=>{opened=name;}}),true);
  assert.equal(row.querySelector('.ctrl'),ctrl);assert.equal(ctrl.children[0],input);input.onchange();assert.equal(changes,1);
  assert.equal(row.querySelector('.descr'),descr);assert.equal(descr.textContent,'完整繁中指南與既有警告');
  assert.equal(row.querySelector('.setting-actions').children[0],reset);assert.equal(row.querySelector('.setting-context'),other);
  const details=row.querySelector('.cockpit-help');row.querySelector('.cockpit-control-info-button').onclick({stopPropagation(){}});assert.equal(details.open,true);
  row.querySelector('.cockpit-control-more').onclick({stopPropagation(){}});assert.equal(opened,'SoundLanguageVolume');
  assert.equal(composeCockpitControl(row,{}),false);assert.equal(row.children.length,3);
});
