import {cameraGeometry,cameraTargets,unpositionedTargets,roadCameraTargets,roadImageTargets} from './scene_objects.js';

import {captureIdentity,sceneContributor} from './scene_contribution.js';
import {createSignalHistory} from '../signal_history.js';
import {OCCUPANCY_TTL_MS} from '../occupancy_grid.js';

export const DETECTION_TTL_MS=1200;
export function createObjectPerception(doc,target,{onChange=()=>{},road=false,occupancy=false}={}) {
  const ttl=occupancy?OCCUPANCY_TTL_MS:DETECTION_TTL_MS;
  const setting=occupancy?'vision_environment_occupancy':road?'vision_road_detection':'vision_object_detection';
  let expiry=null;
  const profiles=[];
  const signalHistory=createSignalHistory();
  let worker=null,generation=0,ready=false,busy=false,failed=false,wasEnabled=false,warmed=false,lastAttempt=-Infinity;
  let lastDecoded=null,lastProfile=null,lastTime=null,lastSource=null,lastReplay=null,request=null,timeout=null,revision=0,interval=250;
  let state={status:'off',objects:[],imageObjects:[],count:0,capturedAt:null,revision};
  let watchedVideo=null,frameCallback=null,presented=null,lastPresented=null;
  function observeFrame(video){
    frameCallback=video.requestVideoFrameCallback?.((stamp,meta)=>{
      if(video!==watchedVideo)return;
      presented={time:meta.mediaTime,at:stamp};observeFrame(video);
    });
  }
  function timelineChanged(){presented=lastPresented=null;lastDecoded=null;if(worker||state.capturedAt!==null)stop('waiting');}
  function watch(video){
    if(video===watchedVideo)return;
    for(const event of ['seeking','emptied','ended'])watchedVideo?.removeEventListener?.(event,timelineChanged);
    if(frameCallback!=null)watchedVideo?.cancelVideoFrameCallback?.(frameCallback);
    watchedVideo=video;presented=lastPresented=null;frameCallback=null;
    if(video)observeFrame(video);
    for(const event of ['seeking','emptied','ended'])watchedVideo?.addEventListener?.(event,timelineChanged);
  }
  const contribute=sceneContributor(target,road?'road':'efficientdet');
  const now=()=>target.performance?.now?.()??Date.now();
  const clearTimeout=()=>{if(timeout!==null)target.clearTimeout(timeout);timeout=null;};
  const publish=(status,extra={})=>{state={status,objects:[],imageObjects:[],count:0,capturedAt:null,...extra,revision:++revision};onChange();};
  function stop(status='off'){
    profiles.length=0;signalHistory.clear();
    if(expiry!==null){target.clearTimeout(expiry);expiry=null;}
    generation++;worker?.terminate();worker=null;ready=false;busy=false;warmed=false;request=null;clearTimeout();
    lastDecoded=null;lastTime=null;lastSource=null;lastReplay=null;lastAttempt=-Infinity;interval=250;
    if(state.status!==status||state.objects.length||state.imageObjects.length)publish(status);
  }
  const fail=status=>{failed=true;stop(status);};
  function start(){
    if(typeof target.Worker!=='function'||typeof target.WebAssembly!=='object'||typeof target.createImageBitmap!=='function'||typeof target.OffscreenCanvas!=='function'){
      fail('unsupported');return;
    }
    const url=target.CarrotAssetUrl?.resolve?.(occupancy?'vision.occupancy-worker':road?'vision.road-detector-worker':'vision.object-detector-worker');
    if(!url){fail('load_error');return;}
    try{
      worker=new target.Worker(url);const current=generation;
      worker.onerror=()=>{if(current===generation)fail('load_error');};
      worker.onmessage=({data})=>{
        if(current!==generation)return;
        clearTimeout();
        if(data.type==='ready'){ready=true;publish('waiting');return;}
        if(data.type==='error'){fail(occupancy&&data.stage==='missing'?'missing':data.stage==='load'?'load_error':'inference_error');return;}
        if(data.type!=='result'||!request||data.id!==request.id)return;
        busy=false;warmed=true;
        const captured=request;request=null;
        interval=Math.min(1200,Math.max(250,Number(data.durationMs||0)*3));
        if(occupancy)interval=Math.max(240,Math.min(600,Number(data.durationMs)||240));
        if(now()-captured.capturedAt>=ttl){publish('slow',{
          durationMs:data.durationMs,delegate:data.delegate||null,geometryReason:captured.geometryReason,
        });return;}
        if(occupancy){
          if(!(data.positions instanceof Float32Array)||data.positions.length>64*36*3||data.positions.length%3){fail('inference_error');return;}
          if(!(data.ranges instanceof Float32Array)||data.ranges.length>16*9*6||data.ranges.length%6){fail('inference_error');return;}
          if(expiry!==null)target.clearTimeout(expiry);
          expiry=target.setTimeout(()=>{expiry=null;if(current===generation&&state.capturedAt===captured.capturedAt)publish('stale');},
            Math.max(0,ttl-(now()-captured.capturedAt)));
          publish('ready',{positions:data.positions,ranges:data.ranges,count:data.positions.length/3,raisedCells:data.raisedCells,supportedRays:data.supportedRays,
            visibleEmpty:data.visibleEmpty,capturedAt:captured.capturedAt,videoTime:captured.videoTime,
            durationMs:data.durationMs,geometry:captured.geometry});
          return;
        }
        const objects=(road?roadCameraTargets:cameraTargets)(data.detections,captured.geometry)
          .map(o=>({...o,capturedAt:captured.capturedAt,videoTime:captured.videoTime}));
        const imageObjects=road?roadImageTargets(data.detections,captured.width,captured.height)
          :unpositionedTargets(data.detections,captured.geometry,captured.width,captured.height);
        if(!road){
          const heads=imageObjects.filter(o=>o.kind==='traffic light');
          const confirmed=signalHistory.confirm(heads.map(h=>({box:h.box,lamps:h.signalState||[]})),captured.capturedAt);
          heads.forEach((h,i)=>{h.signalState=confirmed[i];});
          if(expiry!==null){target.clearTimeout(expiry);expiry=null;}
          if(heads.length){
            expiry=target.setTimeout(()=>{
              expiry=null;
              if(current===generation&&state.capturedAt===captured.capturedAt){signalHistory.clear();publish('stale');}
            },Math.max(0,ttl-(now()-captured.capturedAt)));
          }
        }
        publish(captured.geometry?'ready':'calibration',{
          objects,count:Array.isArray(data.detections)?data.detections.length:0,capturedAt:captured.capturedAt,
          imageObjects,signalReader:data.signalReader||null,
          generation,geometry:captured.geometry,videoTime:captured.videoTime,durationMs:data.durationMs,camera:captured.geometry?.sensor||null,
          delegate:data.delegate||null,geometryReason:captured.geometryReason,frameSize:[captured.width,captured.height],
        });
        void contribute(captured.identity,state,now());
      };
      timeout=target.setTimeout(()=>fail('load_error'),90000);
      worker.postMessage({type:'init'});publish('loading');
    }catch{fail('load_error');}
  }
  function update({active=true,frozen=false}={}){
    const enabled=target.CarrotWebSettingsState?.[setting]===true;
    if(!enabled){watch(null);failed=false;wasEnabled=false;stop();return;}
    if(!wasEnabled){failed=false;wasEnabled=true;}
    if(!active||frozen||doc.hidden){watch(null);if(!failed)stop('paused');return;}
    if(failed){watch(null);return;}
    const video=doc.getElementById?.('carrotRoadVideo');
    watch(video);
    const stream=video?.srcObject, track=stream?.getVideoTracks?.()[0];
    if(!video||video.ended||occupancy&&video.paused||stream?.active===false||track?.readyState==='ended'||track?.muted||video.readyState<2||!video.videoWidth||!video.videoHeight||video.seeking){
      if(state.objects.length||state.imageObjects.length||state.positions||busy)stop('waiting');else if(state.status!=='loading'&&state.status!=='waiting')publish('waiting');
      return;
    }
    const replay=target.CarrotVisionReplay?.status?.()?.active===true;
    if(occupancy&&(replay||target.CarrotVisionCompactStateActive===false)){stop('waiting');return;}
    const source=video.srcObject||video.currentSrc||video.src;
    if(worker&&(source!==lastSource||lastReplay!==replay||lastTime!==null&&video.currentTime<lastTime))stop('waiting');
    if(!worker){lastSource=source;lastReplay=replay;start();return;}
    if(occupancy){
      const raw=target.CarrotOverlayState,stamps=target.CarrotStateReceivedAtMonotonic||{};
      const at=Math.max(stamps.liveCalibration,stamps.roadCameraState);
      const valid=['liveCalibration','roadCameraState'].every(k=>Number.isFinite(stamps[k])&&now()>=stamps[k]&&now()-stamps[k]<2000);
      const width=Math.min(640,video.videoWidth),height=Math.round(video.videoHeight*width/video.videoWidth);
      const g=valid&&cameraGeometry(raw,width,height);
      if(!g){if(busy||state.positions)stop('calibration');else {profiles.length=0;if(state.status!=='calibration')publish('calibration');}return;}
      const prior=profiles.at(-1);
      if(prior&&(prior.geometry.sensor!==g.sensor||prior.geometry.width!==width||prior.geometry.height!==height)){
        stop('calibration');return;
      }
      if(!prior||prior.at!==at){
        profiles.push({at,oldest:Math.min(stamps.liveCalibration,stamps.roadCameraState),geometry:g});
        if(profiles.length>12)profiles.shift();
      }
    }
    if(state.geometry&&!replay){
      const raw=target.CarrotOverlayState, stamps=target.CarrotStateReceivedAtMonotonic||{};
      if(raw?.liveCalibration?._sourceInvalid||raw?.roadCameraState?._sourceInvalid||![1,'calibrated'].includes(raw?.liveCalibration?.calStatus)||raw?.roadCameraState?.sensor!==lastProfile||
        !['liveCalibration','roadCameraState'].every(k=>now()-stamps[k]>=0&&now()-stamps[k]<2000)){
        stop('calibration');return;
      }
    }
    // currentTime can advance while the RTC decoder repeats its last image.
    const decoded=video.getVideoPlaybackQuality?.().totalVideoFrames??video.webkitDecodedFrameCount;
    const newPresented=presented && presented!==lastPresented && now()-presented.at<=ttl;
    // A covered video element may suppress frame callbacks on a head unit while its decoder still advances.
    if(!ready||busy||now()-lastAttempt<interval||lastTime===video.currentTime||
      (!newPresented && (decoded>0?decoded===lastDecoded:!!video.requestVideoFrameCallback)))return;
    lastDecoded=decoded;lastPresented=presented;
    const current=generation,capturedAt=newPresented?presented.at:now(),videoTime=newPresented?presented.time:video.currentTime;
    lastAttempt=now();lastTime=video.currentTime;busy=true;
    const width=Math.min(640,video.videoWidth),height=Math.round(video.videoHeight*width/video.videoWidth);
    const raw=target.CarrotOverlayState||{},stamps=target.CarrotStateReceivedAtMonotonic||{};
    // A replay source is historical by design. Live calibration/profile must be fresh.
    const fresh=key=>replay||Number.isFinite(stamps[key])&&capturedAt-stamps[key]>=0&&capturedAt-stamps[key]<2000;
    const geometry=occupancy?profiles.slice().reverse().find(p=>p.at<=capturedAt&&capturedAt-p.oldest<2000)?.geometry:
      fresh('liveCalibration')&&fresh('roadCameraState')?cameraGeometry(raw,width,height):null;
    if(occupancy&&!geometry){busy=false;if(state.status!=='calibration')publish('calibration');return;}
    lastProfile=raw.roadCameraState?.sensor;
    const geometryReason=geometry?null:!fresh('liveCalibration')||!fresh('roadCameraState')?'telemetry'
      :!['calibrated',1].includes(raw.liveCalibration?.calStatus)?'calibration'
      :!Number.isFinite(raw.liveCalibration?.height?.[0])||raw.liveCalibration.height[0]<.5||raw.liveCalibration.height[0]>3?'height'
      :!['os04c10','ar0231','ox03c10'].includes(String(raw.roadCameraState?.sensor||'').toLowerCase())?'sensor':'profile';
    request={identity:captureIdentity(target,replay),id:revision+1,capturedAt,geometry,geometryReason,videoTime,width,height};
    // First use can initialize kernels after createFromOptions resolves.
    // Let that one warm-up finish; the original capture TTL STILL rejects its
    // old result. Subsequent frames retain the bounded inference deadline.
    timeout=target.setTimeout(()=>fail('inference_error'),warmed?4000:20000);
    let capture;
    try{capture=target.createImageBitmap(video,{resizeWidth:width,resizeHeight:height,resizeQuality:'low'});}
    catch{fail('unsupported');return;}
    Promise.resolve(capture).then(bitmap=>{
      if(current!==generation){bitmap.close();return;}
      if(bitmap.width!==width||bitmap.height!==height){bitmap.close();fail('unsupported');return;}
      try{worker.postMessage({type:'frame',bitmap,id:request.id,...(occupancy?{geometry}: {})},[bitmap]);}
      catch{bitmap.close();fail('unsupported');}
    }).catch(()=>{if(current===generation)fail('unsupported');});
  }
  return {update,
    retry(){failed=false;stop(wasEnabled?'waiting':'off');},
    scene(){
      if(state.capturedAt!==null&&now()-state.capturedAt>=ttl)
        return {...state,status:'stale',positions:undefined,ranges:undefined,supportedRays:0,objects:[],imageObjects:[],count:0};
      return state;
    },
    destroy(){watch(null);stop();},
  };
}
