// Physical measurements use metres and the same monotonic observation clock as the track.
const bodies = new Set(['sedan','suv','mpv','pickup','truck','bus']);
const vehicles = new Set(['car','vehicle','truck','bus']);
const reliableMethods = new Set(['stereo_3d','lidar_3d','radar_3d']);
const named = new Map([['motorcycle','motorcycle'],['bicycle','bicycle'],['person','person'],
  ['traffic cone','cone'],['road barrier','barrier'],['traffic drum','drum']]);

function reliable(sample,track) {
  return sample && reliableMethods.has(sample.method) && Number.isFinite(track.measurementAt)
    && Number.isFinite(sample.measuredAt) && Math.abs(sample.measuredAt-track.measurementAt)<=150
    && Number.isFinite(sample.confidence) && sample.confidence>=.8 && sample.confidence<=1;
}

export function metricSize(track) {
  const d=track.dimensions;
  if(!reliable(d,track) || d.unit!=='m')return null;
  if(![d.length,d.width,d.height].every(Number.isFinite))return null;
  return d.length>=1.4 && d.length<=20 && d.width>=.75 && d.width<=3.3 && d.height>=.7 && d.height<=4.6 ? d : null;
}

export function roadModelKind(track) {
  if(named.has(track.kind))return named.get(track.kind);
  const c=track.vehicleClass;
  const classified=reliable(c,track) && (bodies.has(c.type) || c.type==='vehicle');
  if(!vehicles.has(track.kind) && !bodies.has(track.kind) && !(track.kind==='unknown' && classified))return null;
  if(!metricSize(track))return 'sedan';
  if(classified && bodies.has(c.type))return c.type;
  if(bodies.has(track.kind) && track.probability>=.8 && track.probability<=1)return track.kind;
  return 'sedan';
}

export function roadModelLod(distance,low,previous) {
  const close=18,far=42,margin=3;
  let level=previous;
  if(level==null)level=distance<=close?0:distance<=far?1:2;
  else if(distance>far+margin)level=2;
  else if(distance<close-margin)level=0;
  else if((level===2 && distance<far-margin)||(level===0 && distance>close+margin))level=1;
  return low ? Math.max(1,level) : level;
}
