export function workerLabel(value){
  if(!value.worker?.fresh)return '未連線';
  return {collecting:'同步行車資料',importing:'驗證匯入資料',prepare:'資料對齊',teacher:'教師標註',train:'正在訓練',evaluate:'獨立評估',compile:'裝置編譯',paused:'已暫停'}[value.worker.state]||(value.enabled?'監看中':'已暫停');
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
