// Presentation only. Each view owns its camera state; no vehicle commands,
// subscriptions, settings writes or object coordinates are changed here.
const clamp=(n,lo,hi)=>Math.max(lo,Math.min(hi,n));
export function sceneSpeedKph(data,unit,stale){
  const value=data?.speed;
  if(stale||typeof value!=='number'||!Number.isFinite(value)||value<0)return null;
  const kph=unit==='mph'?value*1.609344:value;
  return kph<=300?kph:null;
}
export function speedZoomTarget(kph){
  if(typeof kph!=='number'||!Number.isFinite(kph)||kph<0||kph>300)return null;
  const t=clamp((kph-15)/80,0,1);
  return t*t*(3-2*t);
}
export function createSpeedZoom(){
  let progress=0,previousAt=null,previousSource=null;
  return {update(kph,at,{active=true,source='live'}={}){
    const goal=speedZoomTarget(kph),valid=goal!==null&&Number.isFinite(at)&&active;
    if(source!==previousSource){previousAt=null;previousSource=source;}
    const dt=valid&&previousAt!==null&&at>=previousAt?Math.min(.1,(at-previousAt)/1000):0;
    previousAt=valid?at:null;
    if(valid&&dt>0){
      const step=clamp((goal-progress)*(1-Math.exp(-dt/1.2)),-.45*dt,.45*dt);
      progress=clamp(progress+step,0,1);
      if(Math.abs(goal-progress)<.001)progress=goal;
    }
    return {progress,moving:valid&&Math.abs(goal-progress)>=.001,
      camera:{distance:9+7*progress,height:6+6*progress,anchorY:.78+.07*progress}};
  }};
}
