import {Matrix4} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

export function createEgoVehicle3D(target,doc,onChange){
  let asset=null,request=null,closed=false,retryAt=0,spin=0,lastAt=null,materialKey='';
  let levels=[],wheels=[],materials=new Map();
  function free(root){
    const geometries=new Set(),paints=new Set();
    root.traverse(n=>{if(n.isMesh){geometries.add(n.geometry);paints.add(n.material);}});
    for(const g of geometries)g.dispose();
    for(const m of paints)m.dispose();
  }
  async function load(){
    if(request||closed||asset||!doc.baseURI||!target.fetch||Date.now()<retryAt)return;
    request=new AbortController();
    try{
      const response=await target.fetch(new URL('assets/ego-cuv-v1.glb',doc.baseURI),{signal:request.signal,cache:'no-cache'});
      if(!response.ok)throw Error('ego asset unavailable');
      const {scene}=await new GLTFLoader().parseAsync(await response.arrayBuffer(),'');
      if(closed){free(scene);return;}
      levels=[0,1,2].map(i=>scene.getObjectByName('CUV_LOD'+i));
      if(levels.some(n=>!n)){free(scene);throw Error('ego LOD unavailable');}
      scene.traverse(n=>{if(n.isMesh)materials.set(n.material.name,n.material);});
      wheels=levels.map(level=>level.children.filter(n=>/^(Front|Rear)(Left|Right)_/.test(n.name)));
      scene.matrixAutoUpdate=false;
      scene.matrix.copy(new Matrix4().set(0,0,1,0,-1,0,0,0,0,1,0,0,0,0,0,1));
      asset=scene;onChange();
    }catch{retryAt=Date.now()+15000;}finally{request=null;}
  }
  function update({skin,lamps={},quality,range,at,speed,reverse,steer}){
    if(skin?.id&&skin.id!=='generic'){lastAt=null;return null;}
    if(!asset){void load();return null;}
    const level=quality==='low'||range>=24?2:quality==='standard'||range>=17?1:0;
    levels.forEach((m,i)=>{m.visible=i===level;});
    const key=[skin?.paint,lamps.brake,lamps.left,lamps.right,lamps.lowBeam,lamps.highBeam,lamps.tail].join('/');
    if(key!==materialKey){
      materialKey=key;materials.get('Paint').color.set(skin?.paint||'#e7edf4');
      for(const [name,color,intensity] of [
        ['RearLens',0xff2028,lamps.brake ? 2.4 : lamps.tail ? 0.6 : 0],
        ['IndicatorLeft',0xffa200,lamps.left?2.1:0],['IndicatorRight',0xffa200,lamps.right?2.1:0],
        ['Headlamp',0xd2eaff,lamps.highBeam ? 2 : lamps.lowBeam ? 0.85 : 0]
      ]){const m=materials.get(name);m.emissive.setHex(color);m.emissiveIntensity=intensity;}
    }
    if(Number.isFinite(speed)&&Number.isFinite(at)&&lastAt!==null&&at-lastAt>=0&&at-lastAt<250){
      spin=(spin+Math.abs(speed)*(reverse?-1:1)*(at-lastAt)/340)%(2*Math.PI);
    }
    lastAt=Number.isFinite(speed)?at:null;
    for(const pivot of wheels[level]){
      pivot.rotation.y=pivot.name.startsWith('Front')&&Number.isFinite(steer)?steer*Math.PI/180:0;
      pivot.children[0].rotation.x=spin;
    }
    return asset;
  }
  return {update,dispose(){closed=true;request?.abort();asset?.removeFromParent();if(asset)free(asset);asset=null;}};
}
