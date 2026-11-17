// Display subscriptions only. Camera sessions and vehicle control are separate.
export function createCockpitSceneActivity(){
  let lease=null,owner=null;
  function release(){lease?.release?.();lease=null;owner=null;}
  return {sync(frame,active){
    const replay=frame?.CarrotVisionReplay?.isActive?.()||frame?.CarrotVisionReplay?.status?.()?.active===true;
    if(!active||!frame||replay){release();return;}
    if(owner===frame&&lease?.active)return;
    release();
    if(frame.CarrotDriveDataActivity?.acquire){
      try{owner=frame;lease=frame.CarrotDriveDataActivity.acquire({owner:'cockpit_scene',hud:true,overlay:true});}
      catch{owner=null;lease=null;} // A frame can be unloading; retry after it is ready.
    }
  },release};
}
