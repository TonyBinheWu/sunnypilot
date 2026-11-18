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
  if (!Number.isInteger(code)||code<10||code>38) return {color:neutral,offsets:[0]};
  const color=Math.floor(code/10)===2?'#ffca36':Math.floor(code/10)===3?'#5ab6ff':neutral;
  // OEM DLM inner solid. Width/separation are illustrative, not survey values.
  return {color,offsets:code%10===4?[0,index===1?-.28:.28]:[0]};
}
