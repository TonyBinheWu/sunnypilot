import manifest from '../../../../../vendor/road-detector/manifest.json';
import {sha256} from '../../../../../vendor/road-detector/hashes/sha256.js';
import {resizePlan,rgbTensor,decodeRoadOutput} from './road_yolo.js';

const root=new URL('../../vendor/road-detector/',self.location.href).href;
const hex=bytes=>Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
let sessions=null,busy=false;
async function initialize(){
  importScripts(root+'ort/ort.wasm.min.js');
  ort.env.wasm.numThreads=1;ort.env.wasm.proxy=false;ort.env.wasm.wasmPaths=root+'ort/';
  const loaded=[];
  try{
    for(const model of manifest.models){
      const response=await fetch(root+model.file+'?v='+model.sha256,{credentials:'same-origin'});
      if(!response.ok||Number(response.headers.get('content-length')||model.bytes)>model.bytes)throw Error('model download');
      const bytes=new Uint8Array(await response.arrayBuffer());
      if(bytes.length!==model.bytes||hex(sha256(bytes))!==model.sha256)throw Error('model integrity');
      const session=await ort.InferenceSession.create(bytes,{executionProviders:['wasm'],graphOptimizationLevel:'all'});
      if(!session.inputNames.includes(model.input)||!session.outputNames.includes(model.output))throw Error('model contract');
      loaded.push({model,session});
    }
    sessions=loaded;
  }catch(error){for(const {session} of loaded)await session.release();throw error;}
}
self.onmessage=async({data})=>{
  if(data.type==='init'){
    try{await initialize();self.postMessage({type:'ready'});}catch(error){self.postMessage({type:'error',stage:'load',detail:String(error?.message||error).slice(0,200)});}return;
  }
  if(data.type!=='frame')return;
  if(busy){data.bitmap?.close();return;}busy=true;
  try{
    if(!sessions)throw Error('not ready');
    const started=performance.now(),detections=[];
    for(const {model,session} of sessions){
      const size=model.inputSize,canvas=new OffscreenCanvas(size,size),ctx=canvas.getContext('2d',{willReadFrequently:true});
      const plan=resizePlan(data.bitmap.width,data.bitmap.height,model.resize,size);
      ctx.fillStyle='rgb(114,114,114)';ctx.fillRect(0,0,size,size);ctx.drawImage(data.bitmap,plan.x,plan.y,plan.w,plan.h);
      const input=new ort.Tensor('float32',rgbTensor(ctx.getImageData(0,0,size,size).data,size),[1,3,size,size]);
      let outputs;
      try{outputs=await session.run({[model.input]:input});const result=outputs[model.output];detections.push(...decodeRoadOutput(result.data,result.dims,model,data.bitmap.width,data.bitmap.height,plan).slice(0,12));}
      finally{input.dispose?.();for(const value of Object.values(outputs||{}))value.dispose?.();}
    }
    self.postMessage({type:'result',id:data.id,detections,durationMs:performance.now()-started});
  }catch{self.postMessage({type:'error',stage:'inference'});}
  finally{data.bitmap?.close();busy=false;}
};
