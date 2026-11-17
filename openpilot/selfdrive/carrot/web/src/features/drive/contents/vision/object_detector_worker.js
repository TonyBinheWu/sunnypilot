import { FilesetResolver, ObjectDetector } from '../../../../../vendor/bev-detector/vision_bundle.mjs';
import {DETECTOR_CLASSES} from './hud/object_classes.js';

// A classic worker is intentional: MediaPipe's pinned WASM loader uses importScripts.
// All assets are served locally; image pixels never leave the viewing device.
let detector=null;
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
      self.postMessage({type:'ready'});
    }catch{self.postMessage({type:'error',stage:'load'});}
    return;
  }
  if(data.type!=='frame')return;
  try{
    if(!detector)throw new Error('not ready');
    const started=performance.now(),result=detector.detect(data.bitmap);
    self.postMessage({type:'result',id:data.id,detections:result.detections,durationMs:performance.now()-started});
  }catch{self.postMessage({type:'error',stage:'inference'});}
  finally{data.bitmap?.close();}
};
