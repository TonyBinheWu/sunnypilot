export const VEHICLE_PAINTS=Object.freeze({white:'#e7edf4',silver:'#aab5c3',gray:'#616b78',black:'#242932',red:'#a72d39',blue:'#355d8b',green:'#526b61',beige:'#c9bda7',orange:'#c47a3d'});
export function vehiclePaint(value){
  if(Object.hasOwn(VEHICLE_PAINTS,value))return value;
  return typeof value==='string'&&/^#[a-f0-9]{6}$/i.test(value)?value.toLowerCase():'red';
}
export function paintedVehicle(skin,value){
  const paintId=vehiclePaint(value);
  return {...skin,paint:VEHICLE_PAINTS[paintId]??paintId,paintId};
}
