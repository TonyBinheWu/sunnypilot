export const VEHICLE_PAINTS=Object.freeze({white:'#e7edf4',silver:'#aab5c3',gray:'#616b78',black:'#242932',red:'#a72d39',blue:'#355d8b',green:'#526b61',beige:'#c9bda7',orange:'#c47a3d'});
export const vehiclePaint=value=>Object.hasOwn(VEHICLE_PAINTS,value)?value:'white';
export const paintedVehicle=(skin,value)=>({...skin,paint:VEHICLE_PAINTS[vehiclePaint(value)],paintId:vehiclePaint(value)});
