import test from 'node:test';
import assert from 'node:assert/strict';
import {workerLabel,pipelineNotice,collectionMessage,teacherMessage} from '../web/status.mjs';
test('active download is not displayed as training or a disconnected worker',()=>{
  const value={enabled:true,worker:{fresh:true,state:'collecting'},pipeline:{blockers:['缺少 validation, test']},collection_progress:{filename:'rlog.zst',bytes:1048576,total:2097152}};
  assert.equal(workerLabel(value),'同步行車資料');
  assert.match(pipelineNotice(value),/下載/);
  assert.match(pipelineNotice(value),/validation, test/);
  assert.match(collectionMessage(value),/1.0 \/ 2.0 MiB/);
  value.worker.state='train';
  assert.equal(workerLabel(value),'正在訓練');
  assert.equal(collectionMessage(value),null);
});
test('dead worker stays distinguishable from paused or waiting for data',()=>{
  assert.match(pipelineNotice({worker:{fresh:false}}),/未回報/);
  assert.equal(workerLabel({worker:{fresh:false}}),'未連線');
  assert.match(pipelineNotice({worker:{fresh:true},enabled:false}),/已暫停/);
});
test('teacher validation failure and inference progress are explicit, without fake loss',()=>{
  const value={time:100,teacher:{updated:99,connected:true,qualified:false,gpu:'GB10',qualification:{state:'failed',scenario:'red_light',done:1,total:11,plan:21,simulation_time_s:23,inference_s:1.1,failures:['red_stop_not_sustained']}}};
  const text=teacherMessage(value);
  assert.match(text.connection,/已連線/);
  assert.match(text.progress,/資格未通過/);
  assert.match(text.progress,/22 次模型推論/);
  assert.match(text.progress,/red_stop_not_sustained/);
  value.time=200;
  assert.match(teacherMessage(value).connection,/過期/);
});
