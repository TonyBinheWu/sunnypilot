import {OBJECT_NAMES} from '../drive/contents/vision/hud/object_classes.js';
const STATES=Object.freeze({off:'未啟用',paused:'已暫停',waiting:'等待前鏡頭影像',loading:'正在載入模型',
  ready:'辨識中',calibration:'已有影像辨識；3D 定位資料不足或影像規格不符',stale:'影像或辨識結果已過期',
  unsupported:'此 WebView 缺少辨識所需功能',load_error:'模型載入失敗',inference_error:'模型運算失敗'});
export function cockpitPerceptionReport(frame){
  let snapshot;try{snapshot=frame?.CarrotVisionPerception?.snapshot?.();}catch{}
  const settings=frame?.CarrotWebSettingsState||{},video=frame?.document?.getElementById?.('carrotRoadVideo');
  const camera=Boolean(video&&video.readyState>=2&&video.videoWidth>0&&video.videoHeight>0);
  function row(key){
    const raw=settings[key==='objects'?'vision_object_detection':'vision_road_detection'];
    const enabled=typeof raw==='boolean'?raw:null;
    const value=snapshot?.[key]||{},status=enabled===null?'unknown':enabled===false?'off':value.status||(camera?'loading':'waiting');
    const count=Number.isSafeInteger(value.count)&&value.count>=0?value.count:0;
    const classes=enabled&&status==='ready'?Object.entries(value.classes||{}).filter(([kind,n])=>OBJECT_NAMES[kind]&&Number.isSafeInteger(n)&&n>0&&n<=24).map(([kind,n])=>`${OBJECT_NAMES[kind]} ${n}`).join('、'):'';
    return {enabled,status,count,classes,text:STATES[status]||'狀態待確認',positioned:Number.isSafeInteger(value.positioned)?value.positioned:0};
  }
  const objects=row('objects'),road=row('road');
  return {camera,objects,road,summary:objects.enabled===null?'辨識設定尚未確認':!objects.enabled?'物件辨識未啟用':!camera?'物件辨識：等待前鏡頭':objects.status==='ready'?`影像辨識 · ${objects.count} 個結果`:`物件辨識：${objects.text}`};
}
