import {cameraGeometry} from './scene_objects.js';
export function createParkingPerception(doc,target,onChange=()=>{}){
  let worker=null,generation=0,busy=false,at=-Infinity,captured=-Infinity,sequence=0,lastTime=null,source=null,request=null,timer=null;
  let slots=[],previous=[],status='off';
  const now=()=>target.performance?.now?.()??Date.now();
  const clear=()=>{generation++;worker?.terminate();worker=null;busy=false;target.clearTimeout(timer);timer=null;captured=at=-Infinity;slots=previous=[];request=null;source=null;lastTime=null;status='off';};
  return {update(active){
    if(!active||doc.hidden){if(worker)clear();return;}
    const video=doc.getElementById('carrotRoadVideo'),raw=target.CarrotOverlayState||{},stamps=target.CarrotStateReceivedAtMonotonic||{},time=now();
    if(!video||video.paused||video.ended||video.readyState<2||video.seeking||video.srcObject?.active===false||video.srcObject?.getVideoTracks?.()?.some(t=>t.muted||t.readyState==='ended')){if(worker||request)clear();status='waiting';return;}
    const currentSource=video.srcObject||video.currentSrc||video.src;
    if(source!==currentSource||lastTime!==null&&video.currentTime<lastTime){clear();source=currentSource;}
    const width=Math.min(480,video.videoWidth),height=Math.round(video.videoHeight*width/video.videoWidth);
    const fresh=key=>Number.isFinite(stamps[key])&&time-stamps[key]>=0&&time-stamps[key]<1000;
    const geometry=fresh('liveCalibration')&&fresh('roadCameraState')?cameraGeometry(raw,width,height):null;
    if(!geometry){if(worker||request)clear();status='calibration';return;}
    if(busy||time-at<500||lastTime===video.currentTime)return;
    if(!target.Worker||!target.createImageBitmap||!target.OffscreenCanvas){status='unsupported';return;}
    if(!worker){const url=target.CarrotAssetUrl?.resolve?.('vision.parking-detector-worker');if(!url){status='unsupported';return;}
      worker=new target.Worker(url);worker.onerror=()=>{clear();status='error';onChange();};
      worker.onmessage=({data})=>{if(!request||data.id!==request.id)return;target.clearTimeout(timer);busy=false;
        const sample=request;request=null;
        if(data.error||now()-sample.at>=1000){slots=previous=[];status=data.error?'error':'stale';return;}
        const next=(Array.isArray(data.slots)?data.slots:[]).slice(0,12);
        slots=now()-captured<1000?next.filter(s=>previous.some(p=>Math.hypot(p.center[0]-s.center[0],p.center[1]-s.center[1])<.7)):[];
        previous=next;captured=sample.at;status='ready';onChange();};
    }
    at=time;lastTime=video.currentTime;busy=true;request={id:++sequence,at:time};const current=generation;
    timer=target.setTimeout(()=>{clear();status='error';onChange();},1500);
    Promise.resolve().then(()=>target.createImageBitmap(video,{resizeWidth:width,resizeHeight:height,resizeQuality:'low'})).then(bitmap=>{
      if(current!==generation||!request){bitmap.close();return;}
      if(bitmap.width!==width||bitmap.height!==height){bitmap.close();clear();status='unsupported';return;}
      worker.postMessage({type:'frame',id:request.id,bitmap,geometry},[bitmap]);
    }).catch(()=>{if(current===generation){clear();status='error';onChange();}});
  },scene(){return {status:now()-captured>1000&&status==='ready'?'stale':status,slots:now()-captured<=1000?slots:[],revision:sequence};},destroy:clear};
}
