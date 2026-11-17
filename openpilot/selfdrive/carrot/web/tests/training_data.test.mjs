import assert from 'node:assert/strict';
import test from 'node:test';
import {openTrainingData,trainingConsentHtml,trainingText,trainingProgressHtml} from '../src/features/tools/training_data.js';

test('uploader progress explains exclusions, stale heartbeat and acknowledged bytes',()=>{
  assert.match(trainingProgressHtml({fresh:true,state:'uploading',bytes:1048576,total:2097152},'zh-tw'),/1.0 \/ 2.0 MiB/);
  assert.match(trainingProgressHtml({fresh:true,state:'waiting_recordings',counts:{before_consent:3,incomplete:2}},'zh-tw'),/授權前 3／缺少 rlog 或雙鏡頭 2/);
  assert.match(trainingProgressHtml({fresh:false,state:'uploading'},'zh-tw'),/尚無近期上傳器狀態/);
});

test('consent view shows actual pending and completed values and escapes server text',()=>{
  const html=trainingConsentHtml({pending_enabled:true,enabled:false,configured:true,offroad:true,
    notice:{'zh-TW':'<script>bad</script>'},receiver:'https://example.test',uploaded_segments:3},'zh-tw');
  assert.match(html,/等待連線同步授權/);
  assert.match(html,/已完成上傳片段: 3/);
  assert.ok(!html.includes('<script>'));
  assert.equal(trainingText('en').title,'Training data upload');
  assert.equal(trainingText('ko').title,'학습 데이터 제공 동의');
});

test('opening or cancelling the native Carrot dialog never authorizes uploads',async()=>{
  const saved={fetch:globalThis.fetch,appAlert:globalThis.appAlert,openAppDialog:globalThis.openAppDialog};
  const calls=[];
  try{
    globalThis.fetch=async(_url,options)=>{calls.push(options);return {ok:true,json:async()=>({ok:true,enabled:false,
      can_enable:true,configured:true,offroad:true,revision:'a',policy:'policy',notice:{en:'Explicit contribution notice'}})};};
    globalThis.appAlert=async()=>{};
    globalThis.openAppDialog=async options=>{assert.match(options.messageHtml,/Explicit contribution notice/);return false;};
    await openTrainingData();
    assert.equal(calls.length,1);
    assert.equal(calls[0].method,'GET');
  }finally{Object.assign(globalThis,saved);}
});

test('only the explicit confirmation posts the policy and exact revision to the vehicle API',async()=>{
  const saved={fetch:globalThis.fetch,appAlert:globalThis.appAlert,openAppDialog:globalThis.openAppDialog};
  const calls=[];
  try{
    globalThis.fetch=async(_url,options)=>{calls.push(options);return {ok:true,json:async()=>({ok:true,enabled:false,
      pending_enabled:calls.length>1?true:null,can_enable:true,configured:true,offroad:true,revision:'r1',policy:'v1',notice:{en:'Notice'}})};};
    globalThis.appAlert=async()=>{};
    globalThis.openAppDialog=async()=>true;
    await openTrainingData();
    assert.deepEqual(JSON.parse(calls[1].body),{policy:'v1',enabled:true,revision:'r1'});
    assert.equal(calls[1].credentials,'same-origin');
  }finally{Object.assign(globalThis,saved);}
});
