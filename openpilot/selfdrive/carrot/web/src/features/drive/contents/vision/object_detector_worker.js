import { FilesetResolver, ObjectDetector } from '../../../../../vendor/bev-detector/vision_bundle.mjs';
import {DETECTOR_CLASSES} from './hud/object_classes.js';

import {createSignalReader} from './signal_reader.js';

// A classic worker is intentional: MediaPipe's pinned WASM loader uses importScripts.
// All assets are served locally; image pixels never leave the viewing device.
let detector=null,reader=null,readerStatus='idle';
function readSignals(bitmap,detections){
  const heads=detections.filter(d=>d.categories?.[0]?.categoryName==='traffic light'&&d.categories[0].score>=.5&&
    Math.min(d.boundingBox?.width,d.boundingBox?.height)>=8)
    .sort((a,b)=>b.boundingBox.width*b.boundingBox.height-a.boundingBox.width*a.boundingBox.height);
  if(!heads.length)return;
  if(readerStatus==='unavailable')return;
  try{
    reader??=createSignalReader();readerStatus='ready';
    for(const head of heads.slice(0,6))head.lamps=reader(bitmap,head.boundingBox);
  }catch{readerStatus='unavailable';}
}
self.onmessage=async({data})=>{
  if(data.type==='init'){
    try{
      const root=new URL('../../vendor/bev-detector/',self.location.href).href;
      const files=await FilesetResolver.forVisionTasks(`${root}wasm`);
      detector=await ObjectDetector.createFromOptions(files,{
        baseOptions:{modelAssetPath:`${root}efficientdet_lite0.tflite`,delegate:'CPU'},
        runningMode:'IMAGE',maxResults:24,scoreThreshold:.5,
        categoryAllowlist:[...DETECTOR_CLASSES],
      });
      self.postMessage({type:'ready',delegate:'CPU'});
    }catch{self.postMessage({type:'error',stage:'load'});}
    return;
  }
  if(data.type!=='frame')return;
  try{
    if(!detector)throw new Error('not ready');
    const started=performance.now(),result=detector.detect(data.bitmap);
    readSignals(data.bitmap,result.detections);
    self.postMessage({type:'result',id:data.id,signalReader:readerStatus,detections:result.detections,durationMs:performance.now()-started,delegate:'CPU'});
  }catch{self.postMessage({type:'error',stage:'inference'});}
  finally{data.bitmap?.close();}
};
