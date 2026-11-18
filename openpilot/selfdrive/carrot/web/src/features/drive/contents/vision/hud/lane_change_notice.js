import {el,setText} from './dom.js';

const direction=value=>value==='left'||value===1?'left':value==='right'||value===2?'right':null;
const phases=['off','preLaneChange','laneChangeStarting','laneChangeFinishing'];
const sources={forecast_desire:'forecast',forecast_path:'forecast',model_desire:'forecast',model_path:'forecast',
  navigation_exit:'exit',lane_completed:'completed',lane_cancelled:'cancelled',lane_unverified:'unverified'};
export function laneChangeNotice(meta,{ready=false,car={},latActive=false,alertSize=null,offroad=false,replay=false}={}){
  if(!ready||offroad||replay||!latActive||(alertSize!=='none'&&alertSize!==0)||car.canValid!==true||car.canTimeout===true||!['drive','D'].includes(car.gearShifter)||
    !Number.isFinite(car.vEgo)||car.vEgo<30/3.6)return null;
  const phase=Number.isInteger(meta?.laneChangeState)?phases[meta.laneChangeState]:meta?.laneChangeState;
  const activeDirection=direction(meta?.laneChangeDirection);
  let kind,side;
  if(activeDirection&&['laneChangeStarting','laneChangeFinishing'].includes(phase)){
    side=activeDirection;kind='changing';
  }else{
    side=direction(meta?.indicatorPrepareDirection);kind=sources[meta?.indicatorPrepareSource];
    if(!['completed','cancelled','unverified'].includes(kind)&&phase==='preLaneChange'){
      if(meta?.indicatorPrepareSource==='lane_waiting_driver')return null;
      side=activeDirection;kind='prepare';
    }
  }
  if(!side||!kind||(['forecast','exit'].includes(kind)&&car.steeringPressed===true))return null;
  return {kind,direction:side,lampOn:(side==='left'?car.leftBlinker:car.rightBlinker)===true};
}

export function createLaneChangeNotice(doc,target){
  const root=el(doc,'div',{class:'chud-lane-notice',attrs:{role:'status','aria-live':'polite'}});
  const arrow=el(doc,'span',{class:'chud-lane-notice-arrow',attrs:{'aria-hidden':'true'}});
  const title=el(doc,'strong'),detail=el(doc,'span');
  root.appendChild(arrow);root.appendChild(el(doc,'div',{},[title,detail]));root.hidden=true;
  let timer=null,active=false,destroyed=false,lease=null,acquiring=false;
  const text=(key,fallback)=>target.getUIText?.(key,fallback)||fallback;
  function releaseData(){const previous=lease;lease=null;previous?.release?.();}
  function ensureData(){
    if(doc.hidden){releaseData();return;}
    if(!active||destroyed||lease||acquiring||target.document!==doc||!target.CarrotDriveDataActivity?.acquire)return;
    acquiring=true;
    try{
      // HUD-only camera mode does not otherwise subscribe to model metadata.
      // This is the existing display-data lease, never a camera/control request.
      const next=target.CarrotDriveDataActivity.acquire({owner:'lane_change_notice',hud:true,overlay:true});
      if(active&&!destroyed)lease=next;else next?.release?.();
    }finally{acquiring=false;}
  }
  function render(){
    ensureData();
    const now=target.performance?.now?.()??Date.now();
    const fresh=service=>{const t=target.CarrotStateReceivedAtMonotonic?.[service];return Number.isFinite(t)&&now>=t&&now-t<500;};
    const hud=target.CarrotHudState||{},overlay=target.CarrotOverlayState||{};
    const value=active&&!destroyed&&!doc.hidden?laneChangeNotice(overlay.modelV2?.meta,{
      ready:['carState','carControl','modelV2','selfdriveState'].every(fresh),car:hud.carState,
      latActive:overlay.carControl?.latActive,alertSize:hud.selfdriveState?.alertSize,
      offroad:target.CarrotDeviceRuntimeState?.isOffroad===true,replay:target.CarrotVisionReplay?.status?.()?.active===true}):null;
    root.hidden=!value;
    if(!value)return;
    const {kind,direction:side,lampOn}=value;
    root.dataset.kind=kind;root.dataset.direction=side;
    setText(arrow,kind==='completed'?'✓':side==='left'?'←':'→');
    setText(title,text(`lane_notice_${kind}_${side}`,`${kind}: ${side}`));
    const key=['completed','cancelled','unverified'].includes(kind)?'watch':kind==='exit'?'exit_detail':lampOn?'lamp_on':'signal';
    setText(detail,text(`lane_notice_${key}`,'Check traffic; operate indicators yourself'));
  }
  function syncTimer(){
    if(timer!=null)target.clearInterval?.(timer);
    timer=active&&!destroyed&&!doc.hidden&&target.document===doc?target.setInterval?.(render,100)??null:null;timer?.unref?.();
  }
  const onVisibility=()=>{if(doc.hidden)releaseData();syncTimer();render();};
  doc.addEventListener?.('visibilitychange',onVisibility);
  return {el:root,render,setActive(value){
    active=Boolean(value)&&!destroyed;
    if(!active)releaseData();
    syncTimer();render();
  },destroy(){destroyed=true;active=false;releaseData();syncTimer();doc.removeEventListener?.('visibilitychange',onVisibility);root.remove?.();}};
}

export const LANE_NOTICE_CSS=`
.chud-lane-notice{position:absolute;z-index:24;top:max(62px,16%,var(--cockpit-lane-notice-top,0px));left:50%;transform:translateX(-50%);width:min(540px,62%);box-sizing:border-box;display:flex;align-items:center;gap:12px;padding:10px 14px;background:#142132f2;color:#f6f8fb;border-radius:12px;border:1px solid #a5c7f866;pointer-events:none;box-shadow:0 4px 14px #0003;font-family:system-ui,sans-serif}
.chud-lane-notice[hidden]{display:none!important}.chud-lane-notice-arrow{font-size:clamp(24px,4cqh,40px);color:#ffd37b;flex:none}.chud-lane-notice strong{display:block;font-size:calc(clamp(15px,2.7cqh,23px) * var(--carrot-text-scale-chrome,1));line-height:1.3;overflow-wrap:anywhere}.chud-lane-notice div>span{display:block;margin-top:3px;font-size:calc(clamp(12px,2cqh,17px) * var(--carrot-text-scale-chrome,1));line-height:1.3;color:#d3dce8}.chud-lane-notice[data-kind=completed] .chud-lane-notice-arrow{color:#7ce4ac}
@container(max-width:600px){.chud-lane-notice{width:calc(100% - 24px);top:max(84px,21%,var(--cockpit-lane-notice-top,0px));gap:8px;padding:8px 10px}.chud-lane-notice strong{font-size:calc(15px * var(--carrot-text-scale-chrome,1))}.chud-lane-notice div>span{font-size:calc(12px * var(--carrot-text-scale-chrome,1))}}
`;
