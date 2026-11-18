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
  const state={running:'資格驗證中',failed:'資格未通過',passed:'資格驗證通過',error:'驗證程序錯誤',interrupted:'驗證已中斷'}[q.state]||'等待資格驗證';
  const reasons={lane_envelope:'超出車道邊界 (lane_envelope)',red_stop_not_sustained:'紅燈停等未持續達標 (red_stop_not_sustained)',red_hold_not_maintained:'紅燈期間未保持停車 (red_hold_not_maintained)'};
  const fields=[state,q.scenario,Number.isFinite(q.done)?`${q.done} / ${q.total} 關卡`:null,
    Number.isFinite(q.plan)?`已完成 ${q.plan+1} 次模型推論`:null,
    Number.isFinite(q.simulation_time_s)?`模擬 ${q.simulation_time_s.toFixed(1)} 秒`:null,
    Number.isFinite(q.inference_s)?`單次推論 ${q.inference_s.toFixed(3)} 秒`:null,
    Number.isFinite(q.red_wait_audit?.longest_contiguous_red_stop_s)?`連續紅燈停等 ${q.red_wait_audit.longest_contiguous_red_stop_s.toFixed(2)} 秒`:null,
    ...(q.failures||[]).map(reason=>reasons[reason]||reason),q.error].filter(Boolean);
  return {connection,progress:fields.join(' · ')};
}
