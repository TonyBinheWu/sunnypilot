const finite=Number.isFinite;
export function insidePolygon(point,ring){
  if(!Array.isArray(point)||!point.every(finite)||!Array.isArray(ring)||ring.length<4)return false;
  let inside=false;
  for(let i=0,j=ring.length-1;i<ring.length;j=i++){
    const a=ring[i],b=ring[j];if(!a?.every(finite)||!b?.every(finite))return false;
    if((a[1]>point[1])!==(b[1]>point[1])&&point[0]<(b[0]-a[0])*(point[1]-a[1])/(b[1]-a[1])+a[0])inside=!inside;
  }return inside;
}
// Presentation only. Never request a gear change, parking manoeuvre or control.
export function createParkingView(){
  let previous=null,pending=null,spin=null,manual=null,context=false;
  return {interact(){pending=spin=null;manual=false;},toggle(){pending=spin=null;manual=!(manual??context);},
    update({enabled=false,fresh=false,speed=null,gear=null,inLot=false,active=true,reducedMotion=false,now=0}={}){
      const valid=enabled&&fresh&&active&&finite(speed)&&speed>=0&&['P','D','R','N','S'].includes(gear);
      if(!valid){previous=null;pending=spin=null;context=false;manual=null;return {overhead:false,spin:false,yaw:0};}
      const nextContext=speed<=15&&(inLot||gear==='R'||(gear==='P'&&speed<.36));
      if(nextContext!==context)manual=null;context=nextContext;
      if(previous&&previous!=='P'&&gear==='P'&&speed<.36)pending=now;
      previous=gear;
      if(gear!=='P'||speed>=.36){pending=spin=null;}
      if(pending!==null&&now-pending>=750){if(!reducedMotion)spin=now;pending=null;}
      if(spin!==null&&(now-spin>=4000||reducedMotion))spin=null;
      const progress=spin===null?0:Math.min(1,Math.max(0,(now-spin)/4000));
      return {overhead:speed<=20&&(manual??context),spin:spin!==null,yaw:360*(progress*progress*(3-2*progress))};
    }};
}

export function createParkingMap(target,onChange=()=>{}){
  let state={status:'off',areas:[]},at=-Infinity,busy=false,controller=null,generation=0,closed=false;
  const now=()=>target.performance?.now?.()??Date.now();
  return {update(active){
    if(!active||target.CarrotWebSettingsState?.vision_parking_map!==true){
      generation++;controller?.abort();controller=null;
      if(state.status!=='off')state={status:'off',areas:[]};return;
    }
    if(closed||busy||now()-at<5000||typeof target.AbortController!=='function')return;
    at=now();busy=true;controller=new target.AbortController();const current=generation;
    const timer=target.setTimeout(()=>controller?.abort(),9000);
    target.fetch('/api/navigation/parking',{credentials:'same-origin',cache:'no-store',signal:controller.signal})
      .then(r=>{if(!r.ok)throw Error();return r.json();}).then(value=>{if(!closed&&current===generation){state={status:value.status,areas:Array.isArray(value.areas)?value.areas.slice(0,80):[],position:value.position,received:now()};onChange();}})
      .catch(()=>{if(!closed&&current===generation){state={status:'unavailable',areas:[]};onChange();}})
      .finally(()=>{target.clearTimeout(timer);busy=false;controller=null;});
  },scene(){return now()-state.received>10000?{status:'stale',areas:[]}:state;},destroy(){closed=true;generation++;controller?.abort();}};
}
