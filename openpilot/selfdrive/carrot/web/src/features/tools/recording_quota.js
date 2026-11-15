export function quotaSummary(data,text,now=Date.now()) {
  if(data?.available===false||!data)return text('recording_quota_wait','Waiting for storage status');
  if(data.enabled!==true)return text('recording_quota_off','Quota disabled');
  const rows=[`${text('recording_quota_percent','Recording quota')}: ${data.percent??'—'}%`];
  const age=now/1000-data.updatedAt;
  if(!Number.isFinite(age)||age<0||age>90)rows.push(text('recording_quota_stale','Status is outdated'));
  if(data.error)rows.push(text('recording_quota_error','Scan failed; quota cleanup skipped'));
  for(const group of data.groups||[]){
    rows.push(`${text('recording_quota_usage','Recordings / total storage')}: ${Number.isFinite(group.usedPercent)?group.usedPercent:'—'}%`);
    if(group.overQuota)rows.push(text('recording_quota_blocked','Over quota; cleanup continues in bounded batches, while active/protected recordings are retained.'));
  }
  rows.push(text('recording_quota_status_hint','Refresh after 30 seconds. Quota deletes eligible recordings only; the existing low-space protection remains active.'));
  return rows.join('\n\n');
}
export async function openRecordingQuota(){
  const text=(key,fallback)=>globalThis.getUIText?.(key,fallback)||fallback;
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5000);
  try{
    const response=await fetch('/api/recording_quota',{cache:'no-store',signal:controller.signal});
    if(!response.ok)throw new Error();
    await globalThis.appAlert(quotaSummary(await response.json(),text),{title:text('recording_quota_status','Recording storage status')});
  }catch{await globalThis.appAlert(text('recording_quota_wait','Waiting for storage status'));}
  finally{clearTimeout(timer);}
}
