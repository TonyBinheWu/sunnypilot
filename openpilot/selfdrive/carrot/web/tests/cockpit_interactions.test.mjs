import test from 'node:test';
import assert from 'node:assert/strict';
import {closeEmbeddedDialog} from '../src/features/cockpit/interactions.js';

test('Back uses canonical dialog cancellation and respects pending operations',()=>{
 let canceled=0;const app={hidden:false},cancel={disabled:false,click(){canceled++;}};
 const target={document:{getElementById:id=>id==='appDialog'?app:cancel}};
 assert.equal(closeEmbeddedDialog(target),true);assert.equal(canceled,1);cancel.disabled=true;
 assert.equal(closeEmbeddedDialog(target),true);assert.equal(canceled,1);
});
test('native child dialogs may veto cancellation and Back cannot force confirmation',()=>{
 let closed=0,allowed=false;const dialog={open:true,dispatchEvent(event){assert.equal(event.type,'cancel');assert.equal(event.cancelable,true);return allowed;},close(){closed++;}};
 const target={Event,document:{getElementById:()=>null,querySelector:()=>dialog}};
 assert.equal(closeEmbeddedDialog(target),true);assert.equal(closed,0);allowed=true;
 assert.equal(closeEmbeddedDialog(target),true);assert.equal(closed,1);assert.equal(closeEmbeddedDialog(null),false);
});

test('Back closes an embedded replay through its cleanup handler before leaving the page',()=>{
 let closed=0,present=true;
 const target={document:{getElementById:()=>null,querySelector:selector=>selector==='dialog[open]'?null:present?{click(){closed++;present=false;}}:null}};
 assert.equal(closeEmbeddedDialog(target),true);assert.equal(closed,1);
 assert.equal(closeEmbeddedDialog(target),false);assert.equal(closed,1);
});
