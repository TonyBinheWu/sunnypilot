import {createObjectTracker} from './object_tracker.js';
import {surroundingTargets,createModelLeadSource,mergeModelLead} from './scene_objects.js';

// Draw one classified model when a measured radar target and a camera track
// uniquely agree. Ambiguous neighbours and unclassified model leads stay independent.
function combineReferences(items, aliases) {
  const cameras=items.filter(o=>['car','bus','truck','motorcycle','bicycle'].includes(o.kind));
  const radars=items.filter(o=>o.radarUsed===true && o.trackId!=null && o.kind==='unknown');
  const neighbours=new Map(), reverse=new Map(), byId=new Map(items.map(o=>[o.trackingId,o]));
  for(const camera of cameras){
    for(const radar of radars){
      if(Math.abs(camera.x-radar.x)>Math.min(2,.6+camera.x*.03)||Math.abs(camera.y-radar.y)>.65)continue;
      if(Math.abs(camera.measurementAt-radar.measurementAt)>350||Math.abs(camera.vx-radar.vx)>4)continue;
      const ids=neighbours.get(camera.trackingId)??[];ids.push(radar);neighbours.set(camera.trackingId,ids);
      reverse.set(radar.trackingId,(reverse.get(radar.trackingId)??0)+1);
    }
  }
  const hidden=new Set(),display=new Map();
  for(const [cam,reference] of aliases)if(!byId.has(cam)||byId.has(reference)&&!neighbours.get(cam)?.some(r=>r.trackingId===reference))aliases.delete(cam);
  for(const camera of cameras){
    const candidates=neighbours.get(camera.trackingId)||[], r=candidates[0];
    if(candidates.length===1 && reverse.get(r.trackingId)===1 &&
       ((r.state==='confirmed'&&camera.state==='confirmed')||aliases.get(camera.trackingId)===r.trackingId)){
      aliases.set(camera.trackingId,r.trackingId);hidden.add(r.trackingId);
      // Keep the camera's class, position method and prediction state together.
      display.set(camera.trackingId,{...camera,id:r.id,nativeReference:r.trackId});
    }else if(r || byId.has(aliases.get(camera.trackingId)))aliases.delete(camera.trackingId);
    else if(aliases.has(camera.trackingId))display.set(camera.trackingId,{...camera,id:'track-'+aliases.get(camera.trackingId)});
  }
  return items.filter(o=>!hidden.has(o.trackingId)).map(o=>display.get(o.trackingId)??o);
}

export function createPerceptionScene(target) {
  const tracker=createObjectTracker(), stamps=new Map(), aliases=new Map();
  let session=null, autoStarted=false, retryAfter=0, lastVideo=null, replaySample=null, poseLease=null, acquiring=false;
  const modelLead=createModelLeadSource(tracker);
  let lastMotion=null;
  function releasePose(){const lease=poseLease;poseLease=null;lease?.release?.();}
  function syncPose(enabled){
    if(!enabled){releasePose();return;}
    if(poseLease||acquiring||!target.CarrotDriveDataActivity?.acquire)return;
    acquiring=true;
    try {poseLease=target.CarrotDriveDataActivity.acquire({owner:'perception_pose',hud:true,overlay:true,ar:true});}
    finally {acquiring=false;}
  }
  function clear() {modelLead.clear();tracker.reset();stamps.clear();aliases.clear();lastVideo=null;replaySample=null;lastMotion=null;}
  function update(scene,now,active,replay) {
    if(!active) {clear();releasePose();session=null;return [];}
    syncPose(!replay && target.CarrotDeviceRuntimeState?.isOffroad!==true);
    if(session!==replay){clear();session=replay;}
    if(replay){
      const playback=target.CarrotVisionReplay?.status?.();
      if(Number.isFinite(playback?.currentTime)){
        const delta=playback.currentTime-(replaySample?.time??playback.currentTime);
        const elapsed=(now-(replaySample?.at??now))/1000*Math.max(1,playback.playbackRate||1);
        if(replaySample && (playback.segment!==replaySample.segment || delta<-.04 || delta>elapsed+.6))clear();
        replaySample={segment:playback.segment,time:playback.currentTime,at:now};
      }
    }
    const videoTime=scene.vision?.videoTime??scene.road?.videoTime;
    if(replay && Number.isFinite(videoTime) && lastVideo!==null && (videoTime<lastVideo||videoTime-lastVideo>2))clear();
    if(Number.isFinite(videoTime))lastVideo=videoTime;
    const mono=target.CarrotStateReceivedAtMonotonic||{};
    const fresh=k=>Number.isFinite(mono[k])&&now>=mono[k]&&now-mono[k]<750;
    const car=target.CarrotHudState?.carState, overlay=target.CarrotOverlayState;
    const pose=overlay?.livePose, angular=pose?.angularVelocityDevice;
    const speed=!car?._sourceInvalid&&fresh('carState')&&Number.isFinite(car?.vEgo)?car.vEgo:null;
    let yaw=!car?._sourceInvalid&&fresh('carState')&&Number.isFinite(car?.yawRate)?car.yawRate:null;
    // Device and calibrated vehicle use forward/right/down axes. Apply the transpose of
    // device-from-calibration to gyro readings before taking vehicle yaw.
    const rpy=overlay?.liveCalibration?.rpyCalib;
    if(yaw===null && fresh('livePose') && fresh('liveCalibration') && [1,'calibrated'].includes(overlay?.liveCalibration?.calStatus)
      &&!pose?._sourceInvalid&&!overlay?.liveCalibration?._sourceInvalid&&pose?.inputsOK&&pose?.sensorsOK&&angular?.valid&&[angular.x,angular.y,angular.z].every(Number.isFinite)
      &&rpy?.length===3&&rpy.every(Number.isFinite)){
      const [r,p,h]=rpy, sr=Math.sin(r), cr=Math.cos(r), sp=Math.sin(p);
      yaw=(Math.cos(h)*sp*cr+Math.sin(h)*sr)*angular.x+(Math.sin(h)*sp*cr-Math.cos(h)*sr)*angular.y+Math.cos(p)*cr*angular.z;
    }
    const motion={speed,yaw:Math.abs(yaw??0)<2?yaw:null};
    lastMotion=motion;
    const connected=replay||target.CarrotVisionCompactStateActive!==false;
    if(scene.radar && !scene.radar._sourceInvalid && connected) {
      const wall=target.CarrotStateUpdatedAt?.radarState;
      // The fallback epoch timestamp must keep its identity on repeated renders.
      const token=scene.radar._sourceSequence??mono.radarState??wall??(replay?scene.radar:null);
      if(token!=null && token!==stamps.get('radar')){
        stamps.set('radar',token);
        const at=mono.radarState??(Number.isFinite(wall)?now-(Date.now()-wall):now);
        tracker.ingest('radar',{stamp:at,objects:surroundingTargets(scene.radar)},now,motion);
      }
    } else tracker.drop('radar');
    for(const key of ['vision','road']) {
      const result=scene[key];
      if(connected && result?.status==='ready') {
        tracker.ingest(key,{stamp:result.capturedAt,epoch:result.generation,objects:result.objects,geometry:result.geometry},now,motion);
      } else tracker.drop(key);
    }
    modelLead.update(connected?scene.model:null,mono.modelV2,now,motion);
    const tracks=combineReferences(tracker.sample(now,motion),aliases);
    return mergeModelLead(tracks,now);
  }
  function startConfigured(active,settings) {
    const cockpit=target.document?.body?.dataset?.cockpitPanel==='vision';
    const configured=cockpit||settings.vision_object_detection===true||settings.vision_road_detection===true||settings.vision_environment_occupancy===true;
    if(!configured || ![1,true].includes(target.CarrotDeviceRuntimeState?.carrotVisionEnabled) || !target.CarrotVisionState?.available){autoStarted=false;return;}
    if(!active || autoStarted || Date.now()<retryAfter
      ||target.CarrotVisionReplay?.status?.()?.active || !target.CarrotVisionStart)return;
    autoStarted=true;
    // Never take over another viewer's camera, request full screen or write a camera setting.
    if(!target.CarrotVisionState.active)Promise.resolve(target.CarrotVisionStart({automaticPerception:true})).catch(()=>{autoStarted=false;retryAfter=Date.now()+3000;});
  }
  return {update,startConfigured,clear(){clear();releasePose();},tracker,get motion(){return lastMotion;}};
}

// Count real draws, including fallback. Browser clocks measure submission time, not GPU utilisation.
export function createRenderMeter(){
  let start=null,frames=0,last=null,fps=null,ms=null,slow=0,fast=0,reduced=false;
  return {frame(at,cost){
    if(!Number.isFinite(cost)||cost<0)return;
    if(last===null||at-last>1200){start=at;frames=0;fps=null;} else frames++;
    last=at;ms=ms===null?cost:ms*.9+cost*.1;
    if(at-start>=1000){fps=frames*1000/(at-start);start=at;frames=0;}
    slow=ms>25?slow+1:0;fast=ms<12?fast+1:0;
    if(slow>=8)reduced=true;if(fast>=90)reduced=false;
  },quality(request){return (!request||request==='auto')&&reduced?'low':request;},
  snapshot(now){return {fps:last!==null&&now-last<1200?fps:null,submitMs:ms,reduced};}};
}

export function trackingReport(s) {
  if(!s)return '等待感知資料';
  const number=(v,d=0)=>Number.isFinite(v)?v.toFixed(d):'—';
  const labels={model:'駕駛模型前車',radar:'原生目標',vision:'鏡頭物件',road:'道路辨識',tentative:'待確認',confirmed:'已確認',predicted:'短暫預測',lost:'遺失'};
  const rows=Object.entries(s.sources).map(([name,f])=>labels[name]+'　'+number(f.fps,1)+' FPS　'+
    (['radar','model'].includes(name)?'收到後經過 '+number(f.ageMs):'擷取至結果 '+number(f.latencyMs))+' ms');
  rows.push('畫面 '+number(s.render.fps,1)+' FPS　繪製提交 '+number(s.render.submitMs,1)+' ms',
    '有效 '+s.active+'　新增 '+s.created+'　遺失 '+s.lost+'　移除 '+s.removed,
    '模型建立 '+(s.render.allocated??0)+'　重用 '+(s.render.reused??0)+'　釋放 '+(s.render.discarded??0),
    'GPU 幾何 '+number(s.render.geometries)+'　紋理 '+number(s.render.textures)+'　JS 堆積 '+number(s.heapMiB,1)+' MiB',
    '車機 CPU '+number(s.cpu)+'%　GPU '+number(s.gpu)+'%　記憶體 '+number(s.memory)+'%（— 表示無回報）',
    ...s.tracks.map(t=>'#'+t.id+' '+(labels[t.source]||t.source)+' · '+(labels[t.state]||t.state)+' · 信心 '+number(t.confidence,2)));
  if(s.world?.radarSources?.length)rows.push('有效 CAN 量測 '+s.world.contacts+' · '+s.world.radarSources.join('、'));
  if(s.world?.cameras?.length)rows.push('駕駛模型 USB eGPU · '+s.world.cameras.map(k=>k==='road'?'前方遠距':'前方廣角').join('、'));
  return rows.join('\n');
}
