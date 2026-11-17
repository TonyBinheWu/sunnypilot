import {drawVehicleMesh} from '../drive/contents/vision/hud/object_mesh.js';
// Original vector silhouettes, not manufacturer CAD assets or measured meshes.
const preset=(id,name,scale,roof,style='sedan')=>Object.freeze({id,name,scale:Object.freeze(scale),roof:Object.freeze(roof),style});
export const VEHICLE_SKINS=Object.freeze({
  generic:preset('generic','通用轎車',[1,1,1],[-.65,.65,1.42]),
  ev6:preset('ev6','Kia EV6',[1.06,1.04,1.06],[-.94,.55,1.43],'ev6'),
  ioniq5:preset('ioniq5','Hyundai IONIQ 5',[1,1.04,1.12],[-1.08,.75,1.43]),
  sorento:preset('sorento','Kia Sorento',[1.12,1.06,1.28],[-1.30,.85,1.45],'sorento'),
  sportage:preset('sportage','Kia Sportage',[1.04,1.04,1.20],[-1.12,.78,1.45],'sportage'),
  carnival:preset('carnival','Kia Carnival',[1.19,1.10,1.31],[-1.50,.84,1.45],'carnival'),
  ev9:preset('ev9','Kia EV9',[1.16,1.10,1.42],[-1.43,.82,1.45],'ev9'),
  model3:preset('model3','Tesla Model 3',[1.08,1.02,.97],[-.8,.65,1.42]),
  modely:preset('modely','Tesla Model Y',[1.09,1.05,1.16],[-1,.7,1.44]),
  suv:preset('suv','通用休旅車',[1.06,1.04,1.22],[-1.2,.8,1.45]),
});
const identity=value=>typeof value==='string'&&!/^(?:none|unknown|auto(?:matic)?|\[automatic\])$/i.test(value.trim())?value.trim().slice(0,160):'';
export function resolveVehicleSkin(values={}){
  const actual=identity(values.CarName),selected=identity(values.CarSelected3),name=actual||selected;
  const normalized=name.toUpperCase().replace(/[^A-Z0-9]+/g,' '),compact=normalized.replaceAll(' ','');
  let id='generic';
  if(compact.includes('KIAEV6'))id='ev6';
  else if(compact.includes('IONIQ5'))id='ioniq5';
  else if(compact.includes('SORENTO'))id='sorento';
  else if(compact.includes('SPORTAGE'))id='sportage';
  else if(compact.includes('CARNIVAL'))id='carnival';
  else if(compact.includes('KIAEV9'))id='ev9';
  else if(compact.includes('TESLAMODEL3'))id='model3';
  else if(compact.includes('TESLAMODELY'))id='modely';
  else if(/RAV4|HONDA CR V|HYUNDAI TUCSON/.test(normalized))id='suv';
  return Object.freeze({...VEHICLE_SKINS[id],identity:name||null,identitySource:actual?'CarName':selected?'CarSelected3':null,illustrative:true});
}
export function drawCockpitVehicle(ctx,project,{skin,...options}={}){
  // Accept preset IDs only: never turn parameter text into an asset URL/code.
  const preset=VEHICLE_SKINS[skin?.id]||VEHICLE_SKINS.generic;
  drawVehicleMesh(ctx,project,{...options,body:preset});
}
export function createVehicleSkinCache(target,onChange=()=>{}){
  let skin=resolveVehicleSkin(),attempt=-Infinity,busy=false,closed=false,request=null;
  const now=()=>target.performance?.now?.()??Date.now();
  return {current:()=>skin,refresh(){
    if(closed||busy||target.document?.hidden||typeof target.fetch!=='function'||typeof target.AbortController!=='function'||now()-attempt<30000)return;
    busy=true;attempt=now();request=new target.AbortController();
    const current=request,timer=target.setTimeout(()=>current.abort(),5000);
    Promise.resolve().then(()=>target.fetch('/api/params_bulk?names=CarName,CarSelected3',{cache:'no-store',credentials:'same-origin',signal:current.signal}))
      .then(r=>{if(!r.ok)throw Error('identity');return r.json();})
      .then(data=>{if(closed)return;const next=resolveVehicleSkin(data?.values);if(JSON.stringify(next)!==JSON.stringify(skin)){skin=next;onChange();}})
      .catch(()=>{}).finally(()=>{target.clearTimeout(timer);busy=false;request=null;});
  },destroy(){closed=true;request?.abort();}};
}
