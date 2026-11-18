const clamp=(n,lo,hi)=>Math.max(lo,Math.min(hi,n));
const wrap=n=>((n+180)%360+360)%360-180;
export function orbitCamera(camera,pose,zoom=1){
  const yaw=Number.isFinite(pose?.yaw)?wrap(pose.yaw):0;
  const pitch=Number.isFinite(pose?.pitch)?clamp(pose.pitch,18,60):25;
  return {...camera,yaw,pitch,distance:camera.distance/clamp(Number.isFinite(zoom)?zoom:1,.6,1.6),anchorY:camera.anchorY};
}
export function createViewOrbit(){
  let pose={yaw:0,pitch:25},drag=null,zoom=1;
  return {
    get pose(){return {...pose};},
    get zoom(){return zoom;},
    setZoom(value){if(!Number.isFinite(value))return false;const next=clamp(value,.6,1.6),changed=next!==zoom;zoom=next;return changed;},
    zoomBy(factor){return Number.isFinite(factor)&&factor>0?this.setZoom(zoom*factor):false;},
    begin(id,x,y,width,height){
      if(drag||![x,y,width,height].every(Number.isFinite)||width<=0||height<=0)return false;
      drag={id,x,y,width,height,start:{...pose},moved:false};return true;
    },
    move(id,x,y){
      if(!drag||drag.id!==id||![x,y].every(Number.isFinite))return false;
      const dx=x-drag.x,dy=y-drag.y;if(!drag.moved&&Math.hypot(dx,dy)<4)return false;
      drag.moved=true;pose={yaw:wrap(drag.start.yaw+dx/drag.width*360),pitch:clamp(drag.start.pitch-dy/drag.height*90,18,60)};return true;
    },
    end(id){if(!drag||drag.id!==id)return false;const moved=drag.moved;drag=null;return moved;},
    cancel(){drag=null;},
    reset(){drag=null;pose={yaw:0,pitch:25};zoom=1;},
    key(key){
      if(key==='Home'){this.reset();return true;}
      if(key==='+'||key==='=')return this.zoomBy(1.1);
      if(key==='-'||key==='_')return this.zoomBy(1/1.1);
      if(key==='ArrowLeft'||key==='ArrowRight')pose.yaw=wrap(pose.yaw+(key==='ArrowRight'?10:-10));
      else if(key==='ArrowUp'||key==='ArrowDown')pose.pitch=clamp(pose.pitch+(key==='ArrowUp'?5:-5),18,60);
      else return false;
      return true;
    },
  };
}
