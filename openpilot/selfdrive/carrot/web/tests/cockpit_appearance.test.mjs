import {test} from 'node:test';
import assert from 'node:assert/strict';
import {scaledFontSize} from '../src/shared/web/display_preferences.js';
import {nightAppearance,readAppearance,setCockpitTextScale,tireLabels} from '../src/features/cockpit/appearance.js';
import {drawDrivingScene} from '../src/features/drive/contents/vision/hud/driving_scene.js';
test('appearance migrates existing day/night preferences and automatic hours are bounded',()=>{
  assert.equal(readAppearance({getItem:()=>null}),'light');
  for(const [old,expected] of [['true','dark'],['false','light']])assert.equal(readAppearance({getItem:k=>k==='carrot_cockpit_night'?old:null}),expected);
  assert.equal(readAppearance({getItem:k=>k==='carrot_cockpit_appearance'?'auto':'true'}),'auto');
  assert.equal(readAppearance({getItem:()=>{throw Error();}}),'light');
  for(const hour of [0,6,18,23])assert.equal(nightAppearance('auto',hour),true);
  for(const hour of [7,12,17])assert.equal(nightAppearance('auto',hour),false);
  assert.equal(nightAppearance('light',22),false);assert.equal(nightAppearance('dark',12),true);
});
test('font selection uses the original setter and checks stored value before updating the outer cockpit',async()=>{
  const calls=[],applied=[];let saved=100;
  const frame={setWebSettingByKey:async(k,v)=>{calls.push([k,v]);saved=v;},getWebSettingByKey:()=>saved};
  const target={CarrotDisplayPreferences:{apply:v=>applied.push(v)}};
  assert.equal(await setCockpitTextScale(frame,target,125),125);assert.deepEqual(calls,[['web_text_scale',125]]);assert.deepEqual(applied,[{web_text_scale:125}]);
  await assert.rejects(setCockpitTextScale(frame,target,999));assert.equal(calls.length,1);
  frame.setWebSettingByKey=async()=>{throw Error('lost response');};await assert.rejects(setCockpitTextScale(frame,target,150));assert.equal(applied.length,1);
  frame.setWebSettingByKey=async()=>{};await assert.rejects(setCockpitTextScale(frame,target,150),/readback/);assert.equal(applied.length,1);
});
test('tire card rejects missing, zero and nonfinite values and never invents units or readings',()=>{
  assert.deepEqual(tireLabels(null),['—','—','—','—']);assert.deepEqual(tireLabels({tpms:{fl:35.12,fr:0,rl:NaN,rr:Infinity}}),['35.1','—','—','—']);
});
test('night palette is a supplied presentation option; both scenes use the selected road surface',()=>{
  for(const [night,color] of [[true,'#222b35'],[false,'#f4f4f6']]){
    const fills=[];const ctx=new Proxy({},{get:(t,k)=>t[k]??((...args)=>{if(k==='fillRect')fills.push([t.fillStyle,...args]);}),set:(t,k,v)=>(t[k]=v,true)});
    drawDrivingScene(ctx,800,400,{}, {night,drawEgo:()=>{}});assert.equal(fills[0][0],color);
  }
});
test('cockpit body and chrome font formulas are scaled exactly once',()=>{
  assert.equal(scaledFontSize('calc(var(--control-font) * var(--carrot-text-scale,1))'),null);
  assert.equal(scaledFontSize('calc(15px * var(--carrot-text-scale-chrome))'),null);
  assert.equal(scaledFontSize('calc(15px * clamp(.9,var(--carrot-text-scale,1),1.05))'),null);
});
