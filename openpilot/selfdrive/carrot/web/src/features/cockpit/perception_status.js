import {surroundingTargets} from '../drive/contents/vision/hud/scene_objects.js';
import {OBJECT_NAMES} from '../drive/contents/vision/hud/object_classes.js';
const STATES=Object.freeze({off:'未啟用',paused:'已暫停',waiting:'等待前鏡頭影像',loading:'正在載入模型',
  ready:'辨識中',calibration:'已有影像辨識；3D 定位資料不足或影像規格不符',stale:'影像或辨識結果已過期',slow:'辨識運算超過時限；請先關閉道路附加辨識與其他高負載 App',
  unsupported:'此 WebView 缺少辨識所需功能',load_error:'模型載入失敗',inference_error:'模型運算失敗'});
export function modelPerceptionSource(model,stamp,now){
  if(!model||model._sourceInvalid||!Number.isFinite(stamp)||stamp>now||now-stamp>=350)return '';
  const lens={road:'前方遠距',wide:'前方廣角',roadWide:'前方遠距＋廣角'}[model.visionCameraInputs];
  const compute={usbGpu:'USB eGPU',nonUsb:'未使用 USB eGPU'}[model.visionCompute];
  return lens&&compute?`駕駛模型前車來源：${lens}（${compute}）`:'';
}
export function radarObservationSummary(radar, stamp, now) {
  if (!Number.isFinite(stamp) || now < stamp || now - stamp >= 350) return '';
  const count = surroundingTargets(radar).filter(target => target.radarUsed === true).length;
  return count ? `原車雷達有回報的目標：${count} 個` : '';
}
export function cockpitPerceptionReport(frame){
  let snapshot;try{snapshot=frame?.CarrotVisionPerception?.snapshot?.();}catch{}
  const settings=frame?.CarrotWebSettingsState||{},video=frame?.document?.getElementById?.('carrotRoadVideo');
  const camera=Boolean(video&&video.readyState>=2&&video.videoWidth>0&&video.videoHeight>0);
  function row(key){
    const raw=settings[key==='objects'?'vision_object_detection':'vision_road_detection'];
    const enabled=typeof raw==='boolean'?raw:null;
    const value=snapshot?.[key]||{},status=enabled===null?'unknown':enabled===false?'off':value.status||(camera?'loading':'waiting');
    const count=Number.isSafeInteger(value.count)&&value.count>=0?value.count:0;
    const classes=enabled&&['ready','calibration'].includes(status)?Object.entries(value.classes||{}).filter(([kind,n])=>OBJECT_NAMES[kind]&&Number.isSafeInteger(n)&&n>0&&n<=24).map(([kind,n])=>`${OBJECT_NAMES[kind]} ${n}`).join('、'):'';
    const reasons={telemetry:'車機校正／相機資料未更新',calibration:'相機尚未完成校正',height:'相機高度資料不足',sensor:'相機型號尚未確認',profile:'串流比例不符，請更新車機並重新連線'};
    let detail=status==='calibration'?reasons[value.geometryReason]:null;
    if(status==='stale')detail=value.awaitingResult?'上一幀已過期，正在處理下一幀':'上一幀已過期，等待下一次有效辨識';
    if(status==='ready'&&count===0)detail='模型已完成這一幀辨識，沒有達到信心門檻的物件';
    return {enabled,status,count,classes,text:detail||STATES[status]||'狀態待確認',positioned:Number.isSafeInteger(value.positioned)?value.positioned:0};
  }
  const objects=row('objects'),road=row('road');
  const enabled=settings.vision_environment_occupancy,env=snapshot?.environment;
  const status=enabled===false?'off':env?.status;
  const environment={enabled:typeof enabled==='boolean'?enabled:null,text:status==='ready'?`前方推估 ${env.cells} 格 · 畫面 ${env.drawn??0} 格 · 估距範圍 ${env.ranges??0} 條`:
    status==='missing'?'環境模型未就緒，請確認車機已更新且可連上 GitHub，再按重試。':status==='calibration'?'等待有效前鏡頭校正':STATES[status]||'等待車機資料'};
  return {camera,objects,road,environment,summary:objects.enabled===null?'辨識設定尚未確認':!objects.enabled?'物件辨識未啟用':!camera?'物件辨識：等待前鏡頭':objects.status==='ready'?`影像辨識 · ${objects.count} 個結果`:`物件辨識：${objects.text}`};
}
