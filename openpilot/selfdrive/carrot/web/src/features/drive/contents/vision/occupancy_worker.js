import {sha256} from '../../../../../vendor/road-detector/hashes/sha256.js';
import {GRID,opticalCrop,visibleVoxels} from './occupancy_grid.js';
import {MODEL_BYTES,MODEL_HASH} from './occupancy_model.js';

const runtime=new URL('../../vendor/road-detector/ort/',self.location.href).href;
let session,canvas,ctx;
async function initialize(){
  const response=await fetch('/api/vision/occupancy/model?v='+MODEL_HASH,{credentials:'same-origin'});
  if(response.status===404||response.status===503){self.postMessage({type:'error',stage:'missing'});return;}
  const length=response.headers.get('Content-Length');
  if(!response.ok||(length!==null&&Number(length)!==MODEL_BYTES)||!response.body)throw Error('model size');
  const bytes=new Uint8Array(MODEL_BYTES),reader=response.body.getReader();
  let offset=0;
  try{
    for(;;){
      const {value,done}=await reader.read();
      if(done)break;
      if(value.length>bytes.length-offset){await reader.cancel();throw Error('oversize model');}
      bytes.set(value,offset);offset+=value.length;
    }
  } finally {reader.releaseLock();}
  if(offset!==MODEL_BYTES||Array.from(sha256(bytes),x=>x.toString(16).padStart(2,'0')).join('')!==MODEL_HASH)throw Error('model integrity');
  importScripts(runtime+'ort.wasm.min.js');
  ort.env.wasm.numThreads=1;ort.env.wasm.wasmPaths=runtime;ort.env.wasm.proxy=false;
  session=await ort.InferenceSession.create(bytes,{executionProviders:['wasm'],graphOptimizationLevel:'all'});
  if(String(session.inputNames)!=='rgb'||String(session.outputNames)!=='occupied,visible_free')throw Error('model contract');
  canvas=new OffscreenCanvas(224,126);ctx=canvas.getContext('2d',{willReadFrequently:true});
  self.postMessage({type:'ready'});
}
self.onmessage=async({data})=>{
  if(data.type==='init'){
    try{await initialize();}catch{self.postMessage({type:'error',stage:'load'});}
    return;
  }
  if(data.type!=='frame')return;
  let input,outputs;
  try {
    const start=performance.now(),g=data.geometry,crop=opticalCrop(g);
    if(!crop||data.bitmap.width!==g.width||data.bitmap.height!==g.height)throw Error('camera profile');
    ctx.drawImage(data.bitmap,crop.x,crop.y,crop.width,crop.height,0,0,224,126);
    const rgba=ctx.getImageData(0,0,224,126).data,plane=224*126,rgb=new Float32Array(3*plane);
    for(let i=0;i<plane;i++){
      rgb[i]=(rgba[4*i]/255-.485)/.229;
      rgb[i+plane]=(rgba[4*i+1]/255-.456)/.224;
      rgb[i+2*plane]=(rgba[4*i+2]/255-.406)/.225;
    }
    input=new ort.Tensor('float32',rgb,[1,3,126,224]);
    outputs=await session.run({rgb:input});
    for(const t of Object.values(outputs))if(String(t.dims)!==[1,GRID.bins,GRID.height,GRID.width].join(','))throw Error('output dimensions');
    const result=visibleVoxels(outputs.occupied.data,outputs.visible_free.data,g);
    self.postMessage({type:'result',id:data.id,...result,durationMs:performance.now()-start},[result.positions.buffer,result.ranges.buffer]);
  }catch{self.postMessage({type:'error',stage:'inference'});}
  finally{data.bitmap.close();input?.dispose();for(const t of Object.values(outputs||{}))t.dispose();}
};
