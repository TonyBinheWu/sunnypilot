export const SERVICES=Object.freeze(['carState','carControl','selfdriveState','carrotMan','modelV2','radarState','deviceState']);
export const MODES=Object.freeze({1:'節能',2:'安全',3:'一般',4:'高速'});
export function createCockpitState(now=()=>performance.now()) {
  const samples=new Map();
  return {accept(frame){
    if(!SERVICES.includes(frame?.service)||!frame.decoded||!Number.isInteger(frame.sequence)||frame.sequence<0||frame.sequence>65535)return false;
    if(samples.get(frame.service)?.sequence===frame.sequence)return false;
    samples.set(frame.service,{value:frame.decoded,sequence:frame.sequence,at:now()});return true;
  },get(service){const s=samples.get(service);return s&&now()-s.at<=1500?s.value:null;},clear(){samples.clear();}};
}
export function telemetry(state){
  const cs=state.get('carState'),cc=state.get('carControl'),sd=state.get('selfdriveState'),cm=state.get('carrotMan');
  const number=(v,scale=1)=>typeof v==='number'&&Number.isFinite(v)&&v>=0?Math.round(v*scale):null;
  return {speed:cs?number(cs.vEgoCluster,3.6):null,setSpeed:cs?number(cs.vCruiseCluster):null,
    limit:cm&&cm.nRoadLimitSpeed>0?number(cm.nRoadLimitSpeed):null,gear:cs?.gearShifter||null,
    enabled:typeof sd?.enabled==='boolean'?sd.enabled:null,
    latActive:typeof cc?.latActive==='boolean'?cc.latActive:null,longActive:typeof cc?.longActive==='boolean'?cc.longActive:null,
    alert:sd?[sd.alertText1,sd.alertText2].filter(x=>typeof x==='string'&&x).join('\n'):'',
    parked:Boolean(cs&&cs.gearShifter==='park'&&Number.isFinite(cs.vEgo)&&cs.vEgo>=0&&cs.vEgo<.1
      &&sd?.enabled===false&&cc?.latActive===false&&cc?.longActive===false)};
}
