export function workerLabel(value){
  if(!value.worker?.fresh)return '未連線';
  return {waiting_teacher:'等待教師資格',collecting:'同步行車資料',importing:'驗證匯入資料',prepare:'資料對齊',teacher:'教師標註',train:'正在訓練',evaluate:'獨立評估',compile:'裝置編譯',paused:'已暫停'}[value.worker.state]||(value.enabled?'監看中':'已暫停');
}
export function pipelineNotice(value){
  if(!value.worker?.fresh)return '工作程序未回報，請檢查 worker.log。';
  if(!value.enabled)return '持續訓練已暫停；既有版本及資料快照已保留。';
  const parts=[];
  if(value.worker.state==='collecting')parts.push('正在從接收服務下載行車片段；下載完成後驗證匯入。');
  parts.push(...(value.pipeline?.blockers||[]));
  return parts.join(' ')||'持續監看新資料，符合條件後建立下一輪訓練。';
}
export function collectionMessage(value){
  const p=value.collection_progress;
  if(value.worker?.state==='collecting'&&p?.filename&&Number.isFinite(p.bytes)&&Number.isFinite(p.total)){
    return `工作站同步 ${p.filename} · ${(p.bytes/1048576).toFixed(1)} / ${(p.total/1048576).toFixed(1)} MiB`;
  }
  return null;
}

export function teacherMessage(value){
  const t=value.teacher||{},q=t.qualification||{};
  const fresh=Number.isFinite(t.updated)&&Math.abs(value.time-t.updated)<20;
  const connection=fresh&&t.connected?`教師接口已連線 · ${t.gpu||'GPU'} · ${t.qualified?'完整資格已通過':'尚未取得完整資格'}`:'教師接口尚未連通或心跳過期';
  const stale=q.state==='running'&&Number.isFinite(q.updated)&&Number.isFinite(value.time)&&value.time-q.updated>20;
  const state=stale?'驗收回報已過期，請檢查驗收程序':({running:'資格驗證中',failed:'資格未通過',passed:'資格驗證通過',error:'驗證程序錯誤',interrupted:'驗證已中斷'}[q.state]||'等待資格驗證');
  const batch=String(q.batch||'').replaceAll('\\','/').match(/cycle-(\d+)\/qualification-(safety|balanced|latest)(?:-early-epoch(\d+))?(?:-policy-([a-z0-9-]+))?(?:-stage-(visual-decision|small-batch))?$/);
  const candidate=batch?`第 ${Number(batch[1])} 輪 · ${{safety:'安全優先候選',balanced:'綜合損失候選',latest:'最近完整epoch候選'}[batch[2]]}${batch[3]?` · Epoch ${Number(batch[3])} 固定快照`:''}${batch[4]==='crossing-v1'?' · 行人全程停讓指令':batch[4]?' · 輸入設定 '+batch[4]:''}${batch[5]==='visual-decision'?' · 視覺決策微調':batch[5]==='small-batch'?' · 小批次權重更新':''}`:null;
  const reasons={lane_envelope:'超出車道邊界 (lane_envelope)',red_stop_not_sustained:'紅燈停等未持續達標 (red_stop_not_sustained)',red_hold_not_maintained:'紅燈期間未保持停車 (red_hold_not_maintained)',insufficient_progress:'行駛進度不足 (insufficient_progress)',crossed_before_permission:'允許通行前越線 (crossed_before_permission)',stop_not_observed:'未在有效區內形成停等 (stop_not_observed)',resume_not_observed:'未觀察到恢復行駛 (resume_not_observed)'};
  const fields=[candidate,state,q.scenario,Number.isFinite(q.done)?`${q.done} / ${q.total} 關卡`:null,
    Number.isFinite(q.plan)?`已完成 ${q.plan+1} 次模型推論`:null,
    Number.isFinite(q.simulation_time_s)?`模擬 ${q.simulation_time_s.toFixed(1)} 秒`:null,
    Number.isFinite(q.inference_s)?`單次推論 ${q.inference_s.toFixed(3)} 秒`:null,
    Number.isFinite(q.red_wait_audit?.longest_contiguous_red_stop_s)?`連續紅燈停等 ${q.red_wait_audit.longest_contiguous_red_stop_s.toFixed(2)} 秒`:null,
    ...(q.failures||[]).map(reason=>reasons[reason]||reason),q.error].filter(Boolean);
  return {connection,progress:fields.join(' · ')};
}

export function teacherValidationSummary(value){
  const progress=value.teacher_training||{},row=progress.history?.at(-1);
  const parts=[];
  if(row?.stop_metric==='valid_stop_zone_v2'&&Number.isFinite(row.red_safe_count)&&Number.isFinite(row.red_samples))parts.push(`停止區樣本 ${row.red_safe_count} / ${row.red_samples}`);
  if(Number.isFinite(row?.go_velocity_mse))parts.push(`放行速度 MSE ${row.go_velocity_mse.toFixed(4)}`);
  if(['paired_stop_go_pcgrad_sgd_v1','paired_unit_gradient_pcgrad_sgd_v2','paired_balanced_stop_modes_pcgrad_sgd_v3','paired_balanced_cross_task_pcgrad_sgd_v4','grouped_six_task_unit_descent_sgd_v6'].includes(progress.optimization_profile)){
    const grouped=progress.optimization_profile==='grouped_six_task_unit_descent_sgd_v6';
    if(grouped&&Number.isFinite(progress.group_task)&&Number.isFinite(progress.group_tasks))parts.push(`${progress.group_stage==='gradient'?'計算梯度':'檢查更新'} ${progress.group_task} / ${progress.group_tasks}${progress.backtracks?` · 回退 ${progress.backtracks} 次`:''}`);
    parts.push(grouped?'六類共同更新／逐類損失檢查':progress.optimization_profile==='paired_balanced_cross_task_pcgrad_sgd_v4'?'停止狀態 × 通行方向九種交錯配對':progress.optimization_profile==='paired_balanced_stop_modes_pcgrad_sgd_v3'?'停等／接近／提早停車恢復均衡配對':'停止／通行成對最佳化');
    if(progress.phase==='training'&&progress.stage!=='validation'&&Number.isFinite(progress.stop_loss_before_step)&&Number.isFinite(progress.go_loss_before_step)){
      parts.push(`${grouped?'本組三類':'本對'}停止 loss ${progress.stop_loss_before_step.toFixed(3)} → ${progress.stop_loss.toFixed(3)}`);
      parts.push(`${grouped?'本組三向':'本對'}通行 loss ${progress.go_loss_before_step.toFixed(3)} → ${progress.go_loss.toFixed(3)}`);
      if(Number.isFinite(progress.step_scale))parts.push(progress.step_scale===0?'本次更新已撤回':`採用步幅 ${progress.step_scale}`);
    }
  }
  const qualified=progress.qualified_candidate;
  if(progress.phase==='qualified'&&qualified)parts.push(`採用第 ${qualified.cycle} 輪 Epoch ${qualified.training_epoch} 固定快照 · 最佳化實際完成 ${progress.optimizer_completed_epochs} 個 epoch`);
  return parts.join(' · ');
}

export function teacherLossHistory(value){
  const current=value.teacher_training||{};
  if(current.history?.length)return {history:current.history,label:`第 ${current.cycle} 輪實際訓練／驗證 loss`};
  const saved=value.teacher_runs?.find(row=>row.history?.length);
  return saved?{history:saved.history,label:`顯示第 ${saved.cycle} 輪${saved.completed===false?'中斷前的實際':'已完成的'} loss；第 ${current.cycle||'—'} 輪尚無完成的 epoch。`}:{history:[],label:'本輪尚無實際 loss'};
}

export function teacherBatchObservation(value,previous={}){
  const p=value.teacher_training||{},cycle=p.cycle,epoch=p.epoch,objective=p.objective_revision||'';
  const valid=Number.isInteger(cycle)&&cycle>0&&Number.isInteger(epoch)&&epoch>0;
  const same=valid&&previous.cycle===cycle&&previous.epoch===epoch&&previous.objective===objective;
  const entries=same&&Array.isArray(previous.entries)?previous.entries.filter(row=>Number.isInteger(row.batch)&&row.batch>0&&Number.isFinite(row.loss)&&Number.isFinite(row.before)).slice(-200):[];
  if(valid&&p.phase==='training'&&p.stage!=='validation'&&Number.isInteger(p.batch)&&p.batch>0&&Number.isFinite(p.loss)&&Number.isFinite(p.loss_before_step)&&!entries.some(row=>row.batch===p.batch)){
    entries.push({batch:p.batch,loss:p.loss,before:p.loss_before_step});
  }
  entries.sort((a,b)=>a.batch-b.batch);
  const retained=entries.slice(-200);
  return {cycle,epoch,objective,entries:retained,label:retained.length?`第 ${cycle} 輪 Epoch ${epoch} · 本瀏覽器實際觀測 ${retained.length} 個 batch（${retained[0].batch}–${retained.at(-1).batch}）；顯示更新前／後損失，不是完整 epoch 平均或驗證 loss。`:'等待本瀏覽器觀測到實際 batch 更新'};
}


export function reasoningSummary(value){
  const p=value.teacher_reasoning;
  if(!p?.experiment_only)return null;
  const last=p.history?.at(-1),phase={training:'更新視覺決策權重',validation:'獨立樣本驗證',generation:'檢查實際生成',completed:'本次實驗完成',interrupted:'已封存未完成的實驗'}[p.phase]||'準備中';
  const fresh=Number.isFinite(p.updated)&&Math.abs(value.time-p.updated)<120;
  const counter=Number.isFinite(p.batch)&&p.phase==='training'?`batch ${p.batch} / ${p.batches}`:Number.isFinite(p.sample)?`樣本 ${p.sample} / ${p.samples}`:'';
  const loss=Number.isFinite(last?.ce)?`獨立驗證 CE ${last.ce.toFixed(5)}`:'尚無完整獨立驗證結果';
  const navigation=['balanced_Wait_Proceed_Left_Right_first_decision_CE_v2','balanced_scene_sampled_Wait_Proceed_Left_Right_CE_v3'].includes(p.objective);
  const classes=navigation?Object.entries({wait:'停等',straight:'直行',left:'左轉',right:'右轉'}).map(([key,label])=>last?.maneuver_classes?.[key]?`${label}首字 ${last.maneuver_classes[key].correct}/${last.maneuver_classes[key].samples}`:null).filter(Boolean).join(' · '):'';
  return `隔離視覺決策實驗${navigation?' · 四類均衡導航決策':''} · ${phase} · Epoch ${p.epoch||0} / ${p.epochs||'—'} · ${counter} · ${loss}${Number.isFinite(last?.decision_correct)?` · 首決策 token 命中 ${last.decision_correct} / ${last.decision_samples} · 決策 CE ${last.decision_ce.toFixed(5)}`:''}${classes?' · '+classes:''}${!fresh&&!['completed','interrupted'].includes(p.phase)?' · 回報已過期':''} · 此處不是完整行車資格結果`;
}
