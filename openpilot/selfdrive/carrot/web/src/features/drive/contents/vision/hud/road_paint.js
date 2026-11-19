export function lanePaint(target, now) {
  const car=target.CarrotHudState?.carState;
  const stamps=target.CarrotStateReceivedAtMonotonic||{};
  const eof=target.CarrotOverlayState?.roadCameraState?.timestampEof;
  if (!car?.canValid || car.canTimeout || !Number.isFinite(eof) || !(car.laneLineInfoMonoTime>0)
      || Math.abs(eof-car.laneLineInfoMonoTime)>200e6
      || !['carState','roadCameraState'].every(k=>now-stamps[k]>=0&&now-stamps[k]<=500)) return [];
  return [null,car.leftLaneLine,car.rightLaneLine,null];
}

export function paintStripes(code,index,neutral) {
  const type=Number.isInteger(code)?code%10:-1;
  const family=Math.floor(code/10);
  const known=family>=1&&family<=3&&type>=0&&type<=8;
  // Road edge / barrier are boundary observations, not a painted stripe.
  if(known&&(type===3||type===8))return {color:neutral,offsets:[]};
  const color=known&&family===2?'#ffca36':known&&family===3?'#5ab6ff':neutral;
  return {color,offsets:known&&type>=4&&type<=6?[0,index===1?-.28:.28]:[0]};
}

// DLM encodes only the INNER stripe's style. Do not infer an outer pattern.
export function stripePattern(code,stripe=0){
  if(!Number.isInteger(code)||Math.floor(code/10)<1||Math.floor(code/10)>3||stripe!==0)return 'boundary';
  switch(code%10){
    case 0:case 5:return 'dashed';
    case 7:return 'dots';
    case 1:case 4:return 'solid';
    default:return 'boundary';
  }
}
