// Display actual lamp state only. Deceleration alone is not a brake-light signal.
export function vehicleLamps(data,stale=false,at=0){
  if(stale)return {brake:false,left:false,right:false};
  const flash=Number.isFinite(at)&&((at%1000)+1000)%1000<500;
  return {...(data?.lightingStateValid===true?{lowBeam:data.lowBeamOn===true,highBeam:data.highBeamOn===true}:{}),brake:data?.brakeLights===true,left:data?.leftBlinker===true&&flash,right:data?.rightBlinker===true&&flash};
}
