import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

// glTF metres (+Z forward, -X right, +Y up) to the renderer's vehicle coordinates.
const vehicleBasis=new T.Matrix4().set(0,0,1,0,-1,0,0,0,0,1,0,0,0,0,0,1);
export const ROAD_MODEL_FILE='assets/road-models-v1.glb';

export async function parseRoadLibrary(bytes) {
  const gltf=await new GLTFLoader().parseAsync(bytes,'');
  const assets=new Map(), materials=new Set(), geometries=new Set();
  for(const scene of gltf.scenes)for(const mesh of scene.children){
    if(!mesh.isMesh || !mesh.name.match(/^[a-z]+_lod[012]$/))continue;
    const geometry=mesh.geometry;
    geometry.applyMatrix4(vehicleBasis);
    const index=geometry.index.array;
    for(let i=0;i<index.length;i+=3)[index[i+1],index[i+2]]=[index[i+2],index[i+1]];
    geometry.computeBoundingBox();
    const size=geometry.boundingBox.getSize(new T.Vector3());
    assets.set(mesh.name,{geometry,material:mesh.material,size});
    materials.add(mesh.material);geometries.add(geometry);
  }
  const focus=assets.get('sedan_lod0').material.clone();
  focus.color.setRGB(.28,1.03,2.1);
  materials.add(focus);
  return {get:(kind,level)=>assets.get(kind+'_lod'+level),focus,
    dispose(){for(const g of geometries)g.dispose();for(const m of materials)m.dispose();}};
}

export function createRoadLibrary(target,doc,onChange) {
  let assets,request,closed=false,retryAt=0,status='idle';
  function ensure(){
    if(closed || assets || request || !target.fetch || !doc.baseURI || Date.now()<retryAt)return;
    request=new AbortController();status='loading';
    (async()=>{
      try{
        const response=await target.fetch(new URL(ROAD_MODEL_FILE,doc.baseURI),{signal:request.signal});
        if(!response.ok)throw Error('model library unavailable');
        const loaded=await parseRoadLibrary(await response.arrayBuffer());
        if(closed){loaded.dispose();return;}
        assets=loaded;status='ready';onChange();
      }catch{if(!closed){status='fallback';retryAt=Date.now()+15000;}}
      finally{request=null;}
    })();
  }
  return {ensure,get:(kind,level)=>assets?.get(kind,level),get focus(){return assets?.focus;},
    get status(){return status;},dispose(){closed=true;request?.abort();assets?.dispose();}};
}
