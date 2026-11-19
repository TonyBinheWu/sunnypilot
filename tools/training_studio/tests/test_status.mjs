import test from 'node:test';
import assert from 'node:assert/strict';
import {workerLabel,pipelineNotice,collectionMessage,teacherMessage,teacherLossHistory,teacherValidationSummary,reasoningSummary,teacherBatchObservation} from '../web/status.mjs';

test('a connected teacher does not make a stale qualification controller look active',()=>{
  const value={time:100,teacher:{updated:99,connected:true,qualified:false,qualification:{state:'running',updated:50,done:0,total:11}}};
  assert.match(teacherMessage(value).connection,/已連線/);
  assert.match(teacherMessage(value).progress,/驗收回報已過期/);
  assert.doesNotMatch(teacherMessage(value).progress,/資格驗證中/);
  value.teacher.qualification.updated=99;
  assert.match(teacherMessage(value).progress,/資格驗證中/);
  value.teacher.qualification.state='failed';value.teacher.qualification.updated=50;
  assert.match(teacherMessage(value).progress,/資格未通過/);
  assert.doesNotMatch(teacherMessage(value).progress,/回報已過期/);
});

test('batch observations retain measured updates without inventing missing batches or validation',()=>{
  const value={teacher_training:{cycle:24,epoch:1,phase:'training',objective_revision:'v2',batch:3,loss:12,loss_before_step:15}};
  let observed=teacherBatchObservation(value);
  assert.equal(observed.entries.length,1);
  observed=teacherBatchObservation(value,observed);
  assert.equal(observed.entries.length,1);
  value.teacher_training.batch=7;value.teacher_training.loss=9;
  observed=teacherBatchObservation(value,observed);
  assert.deepEqual(observed.entries.map(row=>row.batch),[3,7]);
  assert.match(observed.label,/實際觀測 2 個 batch/);
  assert.match(observed.label,/不是完整 epoch 平均或驗證 loss/);
  value.teacher_training.stage='validation';value.teacher_training.batch=8;
  observed=teacherBatchObservation(value,observed);
  assert.deepEqual(observed.entries.map(row=>row.batch),[3,7]);
  value.teacher_training.epoch=2;
  assert.equal(teacherBatchObservation(value,observed).entries.length,0);
  value.teacher_training.epoch=1;value.teacher_training.cycle=25;
  assert.equal(teacherBatchObservation(value,observed).entries.length,0);
});
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
  value.teacher.qualification.batch='/teacher-cycles/cycle-008/qualification-balanced';
  value.teacher_training={cycle:9,phase:'generating'};
  assert.match(teacherMessage(value).progress,/第 8 輪 · 綜合損失候選/);
  value.teacher.qualification.batch='/teacher-cycles/cycle-011/qualification-safety-early-epoch006';
  assert.match(teacherMessage(value).progress,/第 11 輪 · 安全優先候選 · Epoch 6 固定快照/);
  value.teacher.qualification.batch='/teacher-cycles/cycle-026/qualification-latest-early-epoch001';
  assert.match(teacherMessage(value).progress,/第 26 輪 · 最近完整epoch候選 · Epoch 1 固定快照/);
  value.teacher.qualification.batch='/teacher-cycles/cycle-026/qualification-latest-early-epoch001-stage-small-batch';
  assert.match(teacherMessage(value).progress,/Epoch 1 固定快照 · 小批次權重更新/);
  value.teacher.qualification.batch='/teacher-cycles/cycle-013/qualification-balanced-early-epoch004-policy-crossing-v1';
  assert.match(teacherMessage(value).progress,/第 13 輪 · 綜合損失候選 · Epoch 4 固定快照 · 行人全程停讓指令/);
  value.teacher.qualification.batch='/teacher-cycles/cycle-019/qualification-balanced-early-epoch002-stage-visual-decision';
  assert.match(teacherMessage(value).progress,/第 19 輪 · 綜合損失候選 · Epoch 2 固定快照 · 視覺決策微調/);
  value.teacher.qualification.failures=['insufficient_progress'];
  assert.match(teacherMessage(value).progress,/行駛進度不足/);
  value.time=200;
  assert.match(teacherMessage(value).connection,/過期/);
});
test('stop-zone and permitted-motion diagnostics only show measured compatible metrics',()=>{
  assert.equal(teacherValidationSummary({}), '');
  assert.equal(teacherValidationSummary({teacher_training:{history:[{red_safe_count:39,red_samples:39}]}}), '');
  const value={teacher_training:{history:[{stop_metric:'valid_stop_zone_v2',red_safe_count:24,red_samples:39,go_velocity_mse:1.2345}]}};
  assert.equal(teacherValidationSummary(value),'停止區樣本 24 / 39 · 放行速度 MSE 1.2345');
  value.teacher_training.history[0].go_velocity_mse=null;
  assert.equal(teacherValidationSummary(value),'停止區樣本 24 / 39');
});

test('cross-task sampling is shown only for its measured optimizer profile',()=>{
  const value={teacher_training:{optimization_profile:'paired_balanced_cross_task_pcgrad_sgd_v4'}};
  assert.match(teacherValidationSummary(value),/九種交錯配對/);
  value.teacher_training.optimization_profile='paired_balanced_stop_modes_pcgrad_sgd_v3';
  assert.doesNotMatch(teacherValidationSummary(value),/九種交錯配對/);
  assert.match(teacherValidationSummary(value),/均衡配對/);
});
test('previous real losses stay clearly labeled while a new round has no optimizer results',()=>{
  const value={teacher_training:{phase:'generating',cycle:4},teacher_runs:[{cycle:3,history:[{train_loss:2,validation_loss:3}]}]};
  assert.match(teacherLossHistory(value).label,/第 3 輪已完成/);
  assert.equal(teacherLossHistory(value).history[0].train_loss,2);
  value.teacher_runs[0].completed=false;
  assert.match(teacherLossHistory(value).label,/中斷前的實際 loss/);
  value.teacher_training.history=[{train_loss:1,validation_loss:2}];
  assert.match(teacherLossHistory(value).label,/第 4 輪實際/);
});

test('visual decision experiment remains distinct from actual driving qualification and stale jobs',()=>{
  assert.equal(reasoningSummary({}),null);
  const value={time:100,teacher_reasoning:{experiment_only:true,updated:99,phase:'training',epoch:4,epochs:6,batch:12,batches:188,history:[{epoch:3,ce:1.23456}]}};
  assert.match(reasoningSummary(value),/隔離視覺決策實驗/);assert.match(reasoningSummary(value),/Epoch 4 \/ 6/);assert.match(reasoningSummary(value),/1.23456/);assert.match(reasoningSummary(value),/不是完整行車資格結果/);
  value.teacher_reasoning.history[0]={ce:.5,decision_correct:98,decision_samples:100,decision_ce:.25};assert.match(reasoningSummary(value),/首決策 token 命中 98 \/ 100/);
  value.time=500;assert.match(reasoningSummary(value),/回報已過期/);
  value.teacher_reasoning.phase='completed';assert.doesNotMatch(reasoningSummary(value),/回報已過期/);
});
