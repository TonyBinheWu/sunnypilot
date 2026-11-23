import vehicleScales from './vehicle_scales.json' with {type:'json'};
import {drawVehicleMesh} from '../drive/contents/vision/hud/object_mesh.js';
// Original vector silhouettes, not manufacturer CAD assets or measured meshes.
const preset=(id,name,scale,roof,style='sedan')=>Object.freeze({id,name,scale:Object.freeze(scale),roof:Object.freeze(roof),style});
export const VEHICLE_SKINS=Object.freeze({
  generic:preset('generic','通用跨界休旅車',vehicleScales.generic,[-.76,.70,1.53]),
  ev6:preset('ev6','Kia EV6',vehicleScales.ev6,[-.94,.55,1.43],'ev6'),
  ioniq5:preset('ioniq5','Hyundai IONIQ 5',vehicleScales.ioniq5,[-1.12,.75,1.43],'ioniq5'),
  sorento:preset('sorento','Kia Sorento',vehicleScales.sorento,[-1.30,.85,1.45],'sorento'),
  sportage:preset('sportage','Kia Sportage',vehicleScales.sportage,[-1.12,.78,1.45],'sportage'),
  carnival:preset('carnival','Kia Carnival',vehicleScales.carnival,[-1.50,.84,1.45],'carnival'),
  ev9:preset('ev9','Kia EV9',vehicleScales.ev9,[-1.43,.82,1.45],'ev9'),
  ev3:preset('ev3','Kia EV3',vehicleScales.ev3,[-1.26,.80,1.45],'ev3'),
  ev5:preset('ev5','Kia EV5',vehicleScales.ev5,[-1.36,.82,1.45],'ev5'),
  niro:preset('niro','Kia Niro',vehicleScales.niro,[-1.20,.75,1.44],'niro'),
  seltos:preset('seltos','Kia Seltos',vehicleScales.seltos,[-1.28,.77,1.44],'seltos'),
  k5:preset('k5','Kia K5',vehicleScales.k5,[-.85,.65,1.41],'k5'),
  ioniq6:preset('ioniq6','Hyundai IONIQ 6',vehicleScales.ioniq6,[-.91,.67,1.42],'ioniq6'),
  tucson:preset('tucson','Hyundai TUCSON L',vehicleScales.tucson,[-1.26,.78,1.44],'tucson'),
  santafe:preset('santafe','Hyundai SANTA FE',vehicleScales.santafe,[-1.47,.86,1.45],'santafe'),
  kona:preset('kona','Hyundai KONA',vehicleScales.kona,[-1.18,.72,1.45],'kona'),
  palisade:preset('palisade','Hyundai PALISADE',vehicleScales.palisade,[-1.47,.85,1.45],'palisade'),
  staria:preset('staria','Hyundai STARIA',vehicleScales.staria,[-1.58,.98,1.48],'staria'),
  custin:preset('custin','Hyundai CUSTIN',vehicleScales.custin,[-1.44,.84,1.45],'custin'),
  venue:preset('venue','Hyundai VENUE',vehicleScales.venue,[-1.20,.72,1.44],'venue'),
  inster:preset('inster','Hyundai INSTER',vehicleScales.inster,[-1.23,.76,1.45],'inster'),
  mufasa:preset('mufasa','Hyundai MUFASA',vehicleScales.mufasa,[-1.31,.8,1.45],'mufasa'),
  model3:preset('model3','Tesla Model 3',vehicleScales.model3,[-.8,.65,1.42]),
  modely:preset('modely','Tesla Model Y',vehicleScales.modely,[-1,.7,1.44]),
  suv:preset('suv','通用休旅車',vehicleScales.suv,[-1.2,.8,1.45]),
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
  else if(compact.includes('IONIQ6'))id='ioniq6';
  else if(compact.includes('KIAEV3'))id='ev3';
  else if(compact.includes('KIAEV5'))id='ev5';
  else if(compact.includes('NIRO'))id='niro';
  else if(compact.includes('SELTOS'))id='seltos';
  else if(compact.includes('KIAK5'))id='k5';
  else if(compact.includes('TUCSON'))id='tucson';
  else if(compact.includes('SANTAFE'))id='santafe';
  else if(compact.includes('PALISADE'))id='palisade';
  else if(compact.includes('STARIA'))id='staria';
  else if(compact.includes('CUSTIN'))id='custin';
  else if(compact.includes('KONA'))id='kona';
  else if(compact.includes('VENUE'))id='venue';
  else if(compact.includes('INSTER'))id='inster';
  else if(compact.includes('MUFASA'))id='mufasa';
  else if(/RAV4|HONDA CR V/.test(normalized))id='suv';
  return Object.freeze({...VEHICLE_SKINS[id],identity:name||null,identitySource:actual?'CarName':selected?'CarSelected3':null,illustrative:true});
}
export function selectedSkin(detected, choice){
  return Object.hasOwn(VEHICLE_SKINS,choice)?{...VEHICLE_SKINS[choice],manual:true}:detected;
}
export function drawCockpitVehicle(ctx,project,{skin,...options}={}){
  // Accept preset IDs only: never turn parameter text into an asset URL/code.
  const preset=VEHICLE_SKINS[skin?.id]||VEHICLE_SKINS.generic;
  drawVehicleMesh(ctx,project,{...options,body:{...preset,paint:skin?.paint}});
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
