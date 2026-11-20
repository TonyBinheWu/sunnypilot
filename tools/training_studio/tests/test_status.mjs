import test from 'node:test';
import assert from 'node:assert/strict';
import {closedLoopSummary,teacherLossScale,teacherExperiment,teacherExperimentSummary,eventMessage,workerLabel,pipelineNotice,collectionMessage,teacherMessage,teacherLossHistory,teacherValidationSummary,reasoningSummary,teacherBatchObservation,teacherTrainingLoss} from '../web/status.mjs';

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
  value.teacher.qualification.batch='/teacher-cycles/cycle-056/qualification-completed-early-epoch002';
  assert.match(teacherMessage(value).progress,/第 56 輪 · 固定epoch候選 · Epoch 2 固定快照/);
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
  value.teacher_training={optimization_profile:'grouped_six_task_unit_descent_sgd_v6',phase:'training',stop_loss_before_step:2,stop_loss:1,go_loss_before_step:4,go_loss:3};
  assert.match(teacherValidationSummary(value),/六類共同更新/);
  assert.doesNotMatch(teacherValidationSummary(value),/本組三類停止 loss/);
  assert.doesNotMatch(teacherValidationSummary(value),/本對/);
  value.teacher_training.optimization_profile='grouped_six_task_correction_replay_sgd_v7';
  assert.match(teacherValidationSummary(value),/修正樣本優先重播/);
});

test('group substeps cannot relabel a previous completed loss as the next batch',()=>{
  const value={teacher_training:{cycle:56,epoch:1,phase:'training',optimization_profile:'grouped_six_task_unit_descent_sgd_v6',group_stage:'gradient',group_task:2,group_tasks:6,batch:2,loss:99,loss_before_step:100}};
  value.teacher_training.backtracks=3;
  assert.doesNotMatch(teacherValidationSummary(value),/回退/);
  value.teacher_training.group_stage='verify';
  assert.match(teacherValidationSummary(value),/回退 3 次/);
  value.teacher_training.group_stage='gradient';
  assert.equal(teacherBatchObservation(value).entries.length,0);
  assert.equal(teacherBatchObservation(value,{cycle:56,epoch:1,objective:'',entries:[{batch:2,loss:99,before:100}]}).entries.length,0);
  assert.equal(teacherTrainingLoss(value).value,undefined);
  value.teacher_training.history=[{train_loss:12}];
  assert.deepEqual(teacherTrainingLoss(value),{label:'最近完整 epoch loss',value:12});
  value.teacher_training.task_count=6;
  assert.deepEqual(teacherTrainingLoss(value),{label:'最近回報組 loss',value:99});
  value.teacher_training.batch_history=[{batch:1,loss:4,loss_before_step:5}];
  let observed=teacherBatchObservation(value);
  assert.deepEqual(observed.entries,[{batch:1,loss:4,before:5}]);
  assert.deepEqual(teacherTrainingLoss(value),{label:'最近完成組 loss',value:4});
  value.teacher_training.stage='validation';
  value.teacher_training.batch_history.push({batch:2,loss:3,loss_before_step:4});
  observed=teacherBatchObservation(value,observed);
  assert.deepEqual(observed.entries.map(row=>row.batch),[1,2]);
  assert.match(observed.label,/工作程序已記錄/);
  assert.doesNotMatch(teacherValidationSummary(value),/計算梯度/);
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


test('current grouped optimizer reports measured guard backtracks and separate fixed validation metrics',()=>{
  const value={teacher_training:{optimization_profile:'grouped_six_task_recent5_correction_fp64_projection_sgd_v11',phase:'training',group_stage:'verify',group_task:4,group_tasks:6,backtracks:3}};
  assert.match(teacherValidationSummary(value),/檢查更新 4 \/ 6 · 回退 3 次/);
  assert.doesNotMatch(teacherValidationSummary(value),/固定壓力驗證/);
  value.teacher_training.history=[{validation_guard:{validation_samples:6,validation_loss:10.5,lateral_trajectory_mse:2.25}}];
  assert.match(teacherValidationSummary(value),/固定壓力驗證 6 筆 · loss 10.50000 · 車道 MSE 2.25000/);
  value.teacher_training.stage='validation';assert.doesNotMatch(teacherValidationSummary(value),/回退/);
});


test('nine-task safety profile keeps measured group substeps and loss labels',()=>{
  const value={teacher_training:{cycle:163,phase:'training',epoch:1,loss_convention:'mean_primary_objectives_v2',optimization_profile:'grouped_nine_task_separate_stop_safety_fp64_projection_sgd_v12',group_stage:'verify',group_task:8,group_tasks:9,batch_history:[{batch:1,loss:12,loss_before_step:13}]}};
  assert.match(teacherValidationSummary(value),/三項獨立停止安全約束/);
  assert.match(teacherValidationSummary(value),/8 \/ 9/);
  assert.deepEqual(teacherTrainingLoss(value),{label:'最近完成組 loss',value:12});
});


test('isolated teacher telemetry keeps real losses separate and marks stale reports',()=>{
  const p={experiment_only:true,cycle:163,phase:'training',epoch:1,epochs:1,batch:2,batches:37,updated:100,batch_history:[{batch:1,loss:4,loss_before_step:5}],history:[]};
  const value={time:300,events:[{message:'unrelated'},{message:'teacher_experiment_progress:'+JSON.stringify(p)}]};
  assert.deepEqual(teacherExperiment(value),{...p,loss_convention:'mean_primary_objectives_v2'});
  assert.match(teacherExperimentSummary(value),/5.00000 → 4.00000/);
  assert.match(teacherExperimentSummary(value),/回報已過期/);
  assert.match(eventMessage(value.events[1],value),/原11關驗收為準/);
  assert.equal(teacherExperiment({events:[{message:'teacher_experiment_progress:{broken'}]}),null);
  p.batch_history[0].loss='fake';
  assert.equal(teacherExperiment({events:[{message:'teacher_experiment_progress:'+JSON.stringify(p)}]}),null);
});


test('legacy twelve-task reporting is corrected without changing validation or stored records',()=>{
  const p={experiment_only:true,cycle:171,phase:'training_complete',epoch:1,updated:100,optimization_profile:'grouped_twelve_task_separate_stop_lateral_safety_fp64_projection_sgd_v13',batch_history:[{batch:1,loss:5,loss_before_step:6}],history:[{train_loss:7,validation_loss:8,red_safe_count:2,red_samples:3,lateral_trajectory_mse:4}]};
  const value={events:[{message:'teacher_experiment_progress:'+JSON.stringify(p)}]};
  const displayed=teacherExperiment(value);assert.equal(displayed.batch_history[0].loss,10);assert.equal(displayed.history[0].train_loss,14);assert.equal(displayed.history[0].validation_loss,8);assert.equal(p.batch_history[0].loss,5);assert.equal(teacherLossScale(displayed),1);
  assert.match(closedLoopSummary({time:110,closed_loop:{active:true,phase:'waiting_real_data',updated:100,missing_splits:['validation']}}),/不呼叫 Codex／OpenAI API/);
  assert.match(closedLoopSummary({time:110,closed_loop:{active:false,phase:'stopped',updated:100}}),/已停止/);
});
