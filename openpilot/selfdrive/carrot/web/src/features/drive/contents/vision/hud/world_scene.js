export function vehicleInferenceOnly(settings,bootstrap) {
  const mode=settings?.vision_compute_source;
  return mode==='vehicle'||(mode!=='viewer'&&bootstrap?.vehicleGpuPreferred===true);
}

// Vehicle clocks are never compared to browser clocks. Charge the full HTTP round
// trip and server cache age to each independent sensor's remaining lifetime.
export function worldSource(target) {
  let pending=null, last=-Infinity, body=null, origin=0;
  const now=()=>target.performance.now();
  function clear() { pending?.abort(); pending=null; body=null; last=-Infinity; }
  async function read(request,start) {
    const timer=target.setTimeout(()=>request.abort(),500);
    try {
      const response=await target.fetch('/api/vision/world-scene',{cache:'no-store',signal:request.signal});
      if(!response.ok)throw Error();
      const row=await response.json();
      if(pending===request && Number.isFinite(row.ageMs) && row.ageMs>=0) {
        body=row;origin=start-row.ageMs;
      }
    } catch {if(pending===request)body=null;}
    finally {target.clearTimeout(timer);if(pending===request)pending=null;}
  }
  const sample=()=>body?currentWorld(body,now()-origin):null;
  return {clear,sample,update(enabled) {
    if(!enabled){clear();return null;}
    const start=now();
    if(!pending && start-last>=120 && target.fetch && target.AbortController){
      last=start;pending=new target.AbortController();void read(pending,start);
    }
    return sample();
  }};
}

export function currentWorld(row,age) {
  if(!Number.isFinite(age)||age<0||age>=300)return null;
  const valid=ttl=>Number.isFinite(ttl)&&age<ttl&&ttl<=300;
  const contact=p=>p && valid(p.ttlMs) && ['frontRadar','corner235','corner180'].includes(p.source)
    && typeof p.nativeId==='string' && /^\d{1,20}$/.test(p.nativeId) && Number.isFinite(p.x) && p.x>.2 && p.x<=75
    && Number.isFinite(p.y) && Math.abs(p.y)<=20 && Number.isFinite(p.vRel);
  return {contacts:(Array.isArray(row.contacts)?row.contacts:[]).slice(0,48).filter(contact),
    following:contact(row.following)?row.following:null,
    closing:contact(row.closing)&&row.closing.source==='frontRadar'&&row.closing.vRel<0?row.closing:null,
    signals:['plannerFcw','leftBlindspot','rightBlindspot','pathBeyondLeftEdge','pathBeyondRightEdge'].filter(k=>valid(row.signals?.[k])),
    cameras:valid(row.model?.ttlMs)&&row.model.backend==='drivingModelUsbGpu'&&Array.isArray(row.model.cameras)?
      row.model.cameras.filter(k=>['road','wide'].includes(k)):[]};
}

export function withWorldContacts(tracks,world,allowFollowing=true) {
  if(!world)return tracks;
  const result=[...tracks];
  const close=(a,b)=>Math.abs(a.x-b.x)<2&&Math.abs(a.y-b.y)<.65;
  for(const p of world.contacts){
    const near=tracks.filter(t=>close(t,p));
    const lock=world.following;
    const following=allowFollowing&&lock?.nativeId===p.nativeId&&lock.source===p.source&&close(lock,p);
    if(near.length){
      const match=near[0];
      const id=match.nativeReference??(match.radarUsed===true?match.trackId:null);
      if(following && near.length===1 && match.state==='confirmed' && id!=null && String(id)===p.nativeId){
        result[tracks.indexOf(match)]={...match,following:true};
      }
      continue;
    }
    result.push({id:'can:'+p.source+':'+p.nativeId,source:'liveTracks.'+p.source,origin:'radar_contact',
      kind:'unknown',state:'confirmed',x:p.x,y:p.y,vRel:p.vRel,following});
  }
  return result;
}

export function worldNotice(world) {
  const messages={plannerFcw:'前方碰撞警示',leftBlindspot:'左側盲點警示',rightBlindspot:'右側盲點警示',
    pathBeyondLeftEdge:'預測路徑超出左側估計路緣',pathBeyondRightEdge:'預測路徑超出右側估計路緣'};
  const notices=(world?.signals??[]).map(k=>messages[k]);
  const p=world?.closing;
  if(p&&!world.signals.includes('plannerFcw'))notices.push('前方雷達目標接近 · 約 '+Math.round(p.x)+' m · 相對接近速度 '+(-p.vRel*3.6).toFixed(0)+' km/h');
  return notices.join(' · ');
}
