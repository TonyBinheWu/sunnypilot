export const TEXT_SCALES=Object.freeze([80,90,100,110,125,150,175,200]);
export function nightAppearance(preference,hour=new Date().getHours()){
  return preference==='dark'||preference==='auto'&&(hour<7||hour>=18);
}
export function readAppearance(storage){
  try{
    const saved=storage.getItem('carrot_cockpit_appearance');
    if(['light','dark','auto'].includes(saved))return saved;
    const old=storage.getItem('carrot_cockpit_night');
    if(old==='true'||old==='false')return old==='true'?'dark':'light';
  }catch{}
  return 'light';
}
export async function setCockpitTextScale(frame,target,percent){
  if(!TEXT_SCALES.includes(percent)||typeof frame?.setWebSettingByKey!=='function')throw Error('unavailable');
  // Reuse the actual web preference setter, validation and persistence.
  await frame.setWebSettingByKey('web_text_scale',percent);
  const saved=Number(frame.getWebSettingByKey?.('web_text_scale'));
  if(saved!==percent)throw Error('readback');
  target.CarrotDisplayPreferences?.apply({web_text_scale:saved});
  return saved;
}
export function tireLabels(carState){
  return ['fl','fr','rl','rr'].map(key=>{
    const n=carState?.tpms?.[key];
    return typeof n==='number'&&Number.isFinite(n)&&n>0&&n<1000?String(Math.round(n*10)/10):'—';
  });
}
