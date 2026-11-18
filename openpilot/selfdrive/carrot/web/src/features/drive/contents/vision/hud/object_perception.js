import {cameraGeometry,cameraTargets,unpositionedTargets,roadCameraTargets,roadImageTargets} from './scene_objects.js';

import {captureIdentity,sceneContributor} from './scene_contribution.js';

export const DETECTION_TTL_MS=1200;
export function createObjectPerception(doc,target,{onChange=()=>{},road=false}={}) {
  let worker=null,generation=0,ready=false,busy=false,failed=false,wasEnabled=false,warmed=false,lastAttempt=-Infinity;
  let lastTime=null,lastSource=null,lastReplay=null,request=null,timeout=null,revision=0,interval=250;
  let state={status:'off',objects:[],imageObjects:[],count:0,capturedAt:null,revision};
  const contribute=sceneContributor(target,road?'road':'efficientdet');
  const now=()=>target.performance?.now?.()??Date.now();
  const clearTimeout=()=>{if(timeout!==null)target.clearTimeout(timeout);timeout=null;};
  const publish=(status,extra={})=>{state={status,objects:[],imageObjects:[],count:0,capturedAt:null,...extra,revision:++revision};onChange();};
  function stop(status='off'){
    generation++;worker?.terminate();worker=null;ready=false;busy=false;warmed=false;request=null;clearTimeout();
    lastTime=null;lastSource=null;lastReplay=null;lastAttempt=-Infinity;interval=250;
    if(state.status!==status||state.objects.length||state.imageObjects.length)publish(status);
  }
  const fail=status=>{failed=true;stop(status);};
  function start(){
    if(typeof target.Worker!=='function'||typeof target.WebAssembly!=='object'||typeof target.createImageBitmap!=='function'||typeof target.OffscreenCanvas!=='function'){
      fail('unsupported');return;
    }
    const url=target.CarrotAssetUrl?.resolve?.(road?'vision.road-detector-worker':'vision.object-detector-worker');
    if(!url){fail('load_error');return;}
    try{
      worker=new target.Worker(url);const current=generation;
      worker.onerror=()=>{if(current===generation)fail('load_error');};
      worker.onmessage=({data})=>{
        if(current!==generation)return;
        clearTimeout();
        if(data.type==='ready'){ready=true;publish('waiting');return;}
        if(data.type==='error'){fail(data.stage==='load'?'load_error':'inference_error');return;}
        if(data.type!=='result'||!request||data.id!==request.id)return;
        busy=false;warmed=true;
        const captured=request;request=null;
        interval=Math.min(1200,Math.max(250,Number(data.durationMs||0)*3));
        if(now()-captured.capturedAt>DETECTION_TTL_MS){publish('slow',{
          durationMs:data.durationMs,delegate:data.delegate||null,geometryReason:captured.geometryReason,
        });return;}
        const objects=(road?roadCameraTargets:cameraTargets)(data.detections,captured.geometry)
          .map(o=>({...o,capturedAt:captured.capturedAt,videoTime:captured.videoTime}));
        publish(captured.geometry?'ready':'calibration',{
          objects,count:Array.isArray(data.detections)?data.detections.length:0,capturedAt:captured.capturedAt,
          imageObjects:road?roadImageTargets(data.detections,captured.width,captured.height)
            :unpositionedTargets(data.detections,captured.geometry,captured.width,captured.height),
          videoTime:captured.videoTime,durationMs:data.durationMs,camera:captured.geometry?.sensor||null,
          delegate:data.delegate||null,geometryReason:captured.geometryReason,frameSize:[captured.width,captured.height],
        });
        void contribute(captured.identity,state,now());
      };
      timeout=target.setTimeout(()=>fail('load_error'),90000);
      worker.postMessage({type:'init'});publish('loading');
    }catch{fail('load_error');}
  }
  function update({active=true,frozen=false}={}){
    const enabled=target.CarrotWebSettingsState?.[road?'vision_road_detection':'vision_object_detection']===true;
    if(!enabled){failed=false;wasEnabled=false;stop();return;}
    if(!wasEnabled){failed=false;wasEnabled=true;}
    if(!active||frozen||doc.hidden){if(!failed)stop('paused');return;}
    if(failed)return;
    const video=doc.getElementById?.('carrotRoadVideo');
    if(!video||video.readyState<2||!video.videoWidth||!video.videoHeight||video.seeking){
      if(state.objects.length||state.imageObjects.length||busy)stop('waiting');else if(state.status!=='loading'&&state.status!=='waiting')publish('waiting');
      return;
    }
    const replay=target.CarrotVisionReplay?.status?.()?.active===true;
    const source=video.srcObject||video.currentSrc||video.src;
    if(worker&&(source!==lastSource||lastReplay!==replay||lastTime!==null&&video.currentTime<lastTime))stop('waiting');
    if(!worker){lastSource=source;lastReplay=replay;start();return;}
    if(!ready||busy||now()-lastAttempt<interval||lastTime===video.currentTime)return;
    const current=generation,capturedAt=now(),videoTime=video.currentTime;
    lastAttempt=capturedAt;lastTime=videoTime;busy=true;
    const width=Math.min(640,video.videoWidth),height=Math.round(video.videoHeight*width/video.videoWidth);
    const raw=target.CarrotOverlayState||{},stamps=target.CarrotStateReceivedAtMonotonic||{};
    // A replay source is historical by design. Live calibration/profile must be fresh.
    const fresh=key=>replay||Number.isFinite(stamps[key])&&capturedAt-stamps[key]>=0&&capturedAt-stamps[key]<2000;
    const geometry=fresh('liveCalibration')&&fresh('roadCameraState')?cameraGeometry(raw,width,height):null;
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
      try{worker.postMessage({type:'frame',bitmap,id:request.id},[bitmap]);}
      catch{bitmap.close();fail('unsupported');}
    }).catch(()=>{if(current===generation)fail('unsupported');});
  }
  return {update,
    retry(){failed=false;stop(wasEnabled?'waiting':'off');},
    scene(){
      if(state.capturedAt!==null&&now()-state.capturedAt>DETECTION_TTL_MS)
        return {...state,status:'stale',objects:[],imageObjects:[],count:0};
      return state;
    },
    destroy(){stop();},
  };
}
