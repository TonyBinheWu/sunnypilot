import test from 'node:test';
import assert from 'node:assert/strict';
import {SettingsEdits,controlValue} from '../web/settings-edits.js';
const snapshot=(values={A:1,B:false},extra={})=>({values,session:'s1',revision:'r1',catalog_revision:'c1',catalog:[{key:'A',enabled:true,type:'INT',min:0,max:10,step:1},{key:'B',enabled:true,type:'BOOL'}],...extra});
const state=(s,commands=[],fresh=true)=>({snapshot:s,commands,fresh});
const setup=()=>{const e=new SettingsEdits();e.scope('owner');return e;};

test('drafts survive polling, other-key changes and device switches without sending',()=>{
 const e=setup(),s=snapshot();e.edit('d1','A',3,s);e.edit('d2','A',8,s);
 e.reconcile('d1',state(snapshot({A:1,B:true},{revision:'r2'})));
 assert.equal(e.get('d1','A').value,3);assert.equal(e.get('d2','A').value,8);
 assert.equal(e.get('d1','A').status,'draft');assert.equal(e.get('d1','A').command,null);
 const command=e.begin('d1','A',snapshot({A:1,B:true},{revision:'r2'}),1000);
 assert.equal(command.expected_revision,'r2');assert.equal(command.value,3);
});
test('matching snapshot, HTTP acceptance and delivery never imply applied',()=>{
 const e=setup(),s=snapshot();e.edit('d','A',3,s);e.begin('d','A',s,1000);e.queued('d','A',{id:'cmd',status:'queued'});
 e.reconcile('d',state(snapshot({A:3,B:false}),[{id:'cmd',status:'delivered'}]),2000);
 assert.equal(e.get('d','A').status,'delivered');
 e.reconcile('d',state(snapshot({A:3,B:false}),[{id:'other',status:'applied'}]),3000);
 assert.equal(e.get('d','A').status,'delivered');
 e.reconcile('d',state(snapshot({A:3,B:false}),[{id:'cmd',status:'applied'}]),4000);
 assert.equal(e.get('d','A').status,'applied');
 e.reconcile('d',state(snapshot({A:4,B:false})),5000);assert.equal(e.get('d','A'),undefined);
});
test('device drift preserves mine and requires explicit rebase then Save',()=>{
 const e=setup(),s=snapshot();e.edit('d','A',3,s);const newer=snapshot({A:2,B:false},{revision:'r2'});
 e.reconcile('d',state(newer));assert.equal(e.get('d','A').status,'conflict');
 assert.equal(e.begin('d','A',newer),null);assert.equal(e.get('d','A').value,3);
 assert.equal(e.rebase('d','A',newer),true);assert.equal(e.get('d','A').status,'draft');assert.equal(e.get('d','A').command,null);
 assert.deepEqual(e.begin('d','A',newer),{key:'A',value:3,expected_revision:'r2',session:'s1'});
});
test('matching externally changed value still conflicts, never confirms a write',()=>{
 const e=setup();e.edit('d','A',3,snapshot());e.reconcile('d',state(snapshot({A:3,B:false})));
 assert.equal(e.get('d','A').status,'conflict');e.discard('d','A');assert.equal(e.get('d','A'),undefined);
});
test('session changes, schema changes and removed settings require review',()=>{
 for(const change of [{session:'s2'},{catalog_revision:'c2'},{catalog:[]}]){
  const e=setup();e.edit('d','A',3,snapshot());const s=snapshot(undefined,change);e.reconcile('d',state(s));assert.equal(e.get('d','A').status,'conflict');assert.equal(e.begin('d','A',s),null);
 }
});
test('signed rejection is a row failure; conflict rejection preserves the draft',()=>{
 for(const reason of ['write_failed','conflict']){
  const e=setup(),s=snapshot();e.edit('d','A',3,s);e.begin('d','A',s);e.queued('d','A',{id:'cmd',status:'queued'});
  e.reconcile('d',state(s,[{id:'cmd',status:'rejected',reason}]));
  assert.equal(e.get('d','A').status,reason==='conflict'?'conflict':'failed');assert.equal(e.get('d','A').value,3);
 }
});
test('lost response blocks retry and discard until a fresh reconciliation after expiry',()=>{
 const e=setup(),s=snapshot();e.edit('d','A',3,s);e.begin('d','A',s,1000);e.failed('d','A',{});
 e.discard('d','A');assert.equal(e.get('d','A').status,'uncertain');assert.equal(e.begin('d','A',s,2000),null);
 e.reconcile('d',state(s,[],false),62000);assert.equal(e.get('d','A').status,'uncertain');
 e.reconcile('d',state(s),62000);assert.equal(e.get('d','A').status,'conflict');assert.equal(e.get('d','A').reason,'receipt_missing');
});
test('pending command is not erased by another edit or by discard',()=>{
 const e=setup(),s=snapshot();e.edit('d','A',3,s);e.begin('d','A',s);e.edit('d','A',5,s);e.discard('d','A');assert.equal(e.get('d','A').value,3);assert.equal(e.get('d','A').status,'sending');
});
test('logout and account changes erase edits and receipts',()=>{
 const e=setup();e.edit('d','A',3,snapshot());e.scope('other');assert.equal(e.get('d','A'),undefined);
 e.edit('d','A',4,snapshot());e.reset();assert.equal(e.devices.size,0);assert.equal(e.owner,null);
});
test('typed controls reject empty, non-finite, fractional integer, step and disabled option values',()=>{
 const n={type:'INT',min:0,max:10,step:2};
 for(const raw of ['',NaN,Infinity,'1.5',3,12])assert.equal(controlValue(n,raw),undefined);
 assert.equal(controlValue(n,'0'),0);assert.equal(controlValue(n,'4'),4);
 assert.equal(controlValue({type:'BOOL'},false),false);assert.equal(controlValue({type:'BOOL'},'false'),undefined);
 const options={type:'INT',options:[{value:0,enabled:true},{value:1,enabled:false}]};assert.equal(controlValue(options,0),0);assert.equal(controlValue(options,1),undefined);
 assert.equal(controlValue({type:'STRING'},'abc\n'),undefined);
});

test('navigation keeps device-confirmed status across native JSON ordering and validates partial drafts',()=>{
 const e=setup(),entry={key:'NavDestination',type:'STRING',widget:'navigation',enabled:true};
 const value=JSON.stringify({place_name:'DEMO',latitude:25,longitude:121});
 const canonical=JSON.stringify({latitude:25,longitude:121,place_name:'DEMO'});
 const s=snapshot({NavDestination:''},{catalog:[entry]});
 assert.equal(controlValue(entry,JSON.stringify({place_name:'DEMO',latitude:null,longitude:121})),undefined);
 assert.equal(controlValue(entry,value),value);
 e.edit('d',entry.key,value,s);e.begin('d',entry.key,s);e.queued('d',entry.key,{id:'nav',status:'queued'});
 e.reconcile('d',state({...s,values:{NavDestination:canonical}},[{id:'nav',status:'applied'}]));
 assert.equal(e.get('d',entry.key).status,'applied');
});
