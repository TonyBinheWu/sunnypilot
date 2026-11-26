import assert from 'node:assert/strict';
import test from 'node:test';
import {exportProfile,readProfile,profilePlan,restoreProfile} from '../web/settings-profile.js';

const base={session:'device-session',revision:'1',remote_enabled:true,offroad:true,info:{},catalog:[
  {key:'QuietMode',type:'BOOL',widget:'toggle',enabled:true},{key:'Count',type:'INT',widget:'option',min:0,max:5,step:1,enabled:true},
  {key:'DeviceSerial',type:'STRING',widget:'info'}, {key:'NavDestination',type:'STRING',widget:'navigation'},
  {key:'DrivingModelAction',type:'STRING',widget:'option',options:[]}],
  values:{QuietMode:false,Count:1,DeviceSerial:'private',NavDestination:'coordinates',DrivingModelAction:'clear'}};
test('portable settings omit identities, location and actions, reject incompatible values',()=>{
  assert.deepEqual(readProfile(exportProfile(base)),{QuietMode:false,Count:1});
  assert.throws(()=>readProfile(JSON.stringify({format:'other',version:1,values:{}})));
  assert.throws(()=>readProfile('x'.repeat(131073)));
  assert.deepEqual(profilePlan({Count:7,QuietMode:true,Unknown:'x'},base).map(r=>r.status),['unsupported','different','unsupported']);
  assert.equal(profilePlan({Count:'3'},base)[0].status,'unsupported');
});
test('restore waits for each device reply and uses the next revision; retry skips confirmed values',async()=>{
  const snap=structuredClone(base), commands=[];
  const transport={active:()=>true, update:()=>{}, pause:async()=>{},read:async()=>({snapshot:snap,fresh:true,commands}),
    write:async c=>{assert.equal(c.expected_revision,snap.revision);snap.values[c.key]=c.value;snap.revision+='1';
      const id=String(commands.length+1);commands.push({id,status:'applied'});return {id,status:'queued'};}};
  const values={QuietMode:true,Count:4,Unknown:2};
  assert.deepEqual(await restoreProfile(values,transport),{applied:2,skipped:1});
  assert.deepEqual(await restoreProfile(values,transport),{applied:0,skipped:1});
  snap.offroad=false;
  await assert.rejects(restoreProfile(values,transport),/profileStopped/);
});
test('paged model slots restore through their own option lists and wait for each model download', async()=>{
  const snap=structuredClone(base), writes=[];
  const add=(key,choices,current)=>{
    snap.catalog.push({key,type:'STRING',widget:'option',enabled:true,options:choices.map(value=>({value,enabled:true}))});
    snap.values[key]=current;
  };
  add('DrivingModelSmall',['','first'],'first');
  add('DrivingModelSmallPage2',['','second'],'first');
  add('DrivingModelBig',['','third'],'');
  const values={DrivingModelSmall:'second',DrivingModelBig:'third'};
  let pending=null, waits=0;
  const transport={active:()=>true,update:()=>{},read:async()=>({fresh:true,snapshot:snap,commands:[]}),
    write:async command=>{
      assert.equal(pending,null);
      writes.push(command.key);pending=command;
      return {id:String(writes.length),status:'applied'};
    },
    pause:async()=>{
      waits++;
      snap.values[pending.key]=pending.value;
      if(pending.key==='DrivingModelSmallPage2')snap.values.DrivingModelSmall=pending.value;
      pending=null;
    }};
  assert.deepEqual(await restoreProfile(values,transport),{applied:2,skipped:0});
  assert.deepEqual(writes,['DrivingModelSmallPage2','DrivingModelBig']);
  assert.equal(waits,2);
  assert.equal(readProfile(exportProfile(snap)).DrivingModelSmall,'second');
  assert.equal(readProfile(exportProfile(snap)).DrivingModelSmallPage2,undefined);
});
