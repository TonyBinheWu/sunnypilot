const finite = Number.isFinite;
const point = p => Array.isArray(p) && p.length === 2 && p.every(finite);

export function vehicleParkingSource(target) {
  let controller=null, last=-Infinity, expires=-Infinity, latest=null, lastId=null;
  const now=()=>target.performance.now();
  let receipt=null;
  function reset(){
    controller?.abort();controller=null;receipt=latest=lastId=null;expires=last=-Infinity;
  }
  async function read(request,start) {
    const timer=target.setTimeout(()=>request.abort(),800);
    try {
      const headers=receipt?{'X-Carrot-Parking-Draw':receipt}:{};
      receipt=null;
      const response=await target.fetch('/api/vision/parking-scene',{cache:'no-store',signal:request.signal,headers});
      if(!response.ok)throw Error();
      const row=await response.json();
      if(controller!==request)return;
      if(row.backend!=='drivingModelUsbGpu'||!Number.isInteger(row.frameId)||!finite(row.ageMs)||row.ageMs<0||row.ageMs>=650){
        latest=null;return;
      }
      // An identical capture can never extend its own validity on a later poll.
      const until=start+650-row.ageMs;
      expires=lastId===row.frameId?Math.min(expires,until):until;
      lastId=row.frameId;
      const slots=(Array.isArray(row.slots)?row.slots:[]).slice(0,12).filter(s=>point(s?.center)&&
        s.corners?.length===4&&s.corners.every(p=>point(p)&&p[0]>=1&&p[0]<=18.01&&Math.abs(p[1])<=8));
      const lead=point(row.target)&&row.target[0]>1.52&&Math.hypot(...row.target)<=12?row.target:null;
      latest={frame:row.frameId,slots,lead,status:row.status};
    }catch{if(controller===request)latest=null;}
    finally{target.clearTimeout(timer);if(controller===request)controller=null;}
  }
  return {update(active){
    if(!active){reset();return;}
    const start=now();
    if(!controller&&start-last>=240&&target.fetch&&target.AbortController){
      last=start;controller=new target.AbortController();void read(controller,start);
    }
  },sample(){return now()<expires?latest:null;},drawn(frame,scene){
    if(!frame||frame!==latest||now()>=expires||target.document?.hidden||!target.navigator?.userAgent?.includes('CarrotWebAndroid/'))return;
    // Both APK editions share a WebView UA. Only the cockpit entry and its same-origin driving panel count.
    try{if(target.top.location.pathname!=='/cockpit')return;}catch{return;}
    receipt=[frame.frame,Number(scene.parkingCue?.backend==='drivingModelUsbGpu'),frame.slots.length].join(',');
  },destroy:reset};
}

export function combineParking(scene,vehicle) {
  if(!vehicle)return;
  const local=scene.parking||[];
  scene.parking=[...vehicle.slots,...local.filter(s=>!vehicle.slots.some(p=>point(s.center)&&Math.hypot(s.center[0]-p.center[0],s.center[1]-p.center[1])<.9))].slice(0,12);
  if(vehicle.lead){
    const [x,y]=vehicle.lead,distance=Math.hypot(x,y);
    if(!scene.parkingCue||distance<=scene.parkingCue.distance){
      scene.parkingCue={source:'target',x:x-1.52,y,distance,bearing:Math.atan2(y,x)*180/Math.PI,
        color:distance<=4?'#ef584d':distance<=8?'#e7a326':'#7895ab',backend:'drivingModelUsbGpu'};
    }
  }
}
