// The network predicts the probability that a 1 m optical-Z interval contains the
// first visible surface, plus the probability of seeing through that interval.
export const GRID = Object.freeze({width:64,height:36,bins:43,near:2,cell:1,halfX:.34,halfY:.34*126/224});
export const MIN_HIT=.22, MIN_FREE=.95;
export const OCCUPANCY_TTL_MS=900;

export function surfaceMotion(motion,ageMs){
  if(!Number.isFinite(ageMs)||ageMs<0||ageMs>=OCCUPANCY_TTL_MS||!Number.isFinite(motion?.speed))return null;
  const seconds=ageMs/1000,distance=motion.speed*seconds;
  // Without a measured turn rate, use the straight approximation only over a short translation.
  if(!Number.isFinite(motion.yaw)&&Math.abs(distance)>3)return null;
  const turn=(motion.yaw||0)*seconds;
  return {x:-distance*(turn?Math.sin(turn)/turn:1),y:distance*(turn?(1-Math.cos(turn))/turn:0),angle:-turn};
}

export function opticalCrop(g) {
  if(!g||![g.fx,g.fy,g.width,g.height,g.heightM,...(g.rpy||[])].every(Number.isFinite)||g.rpy?.length!==3||g.fx<=0||g.fy<=0)return null;
  const width=2*GRID.halfX*g.fx,height=2*GRID.halfY*g.fy;
  if(width>g.width||height>g.height)return null;
  return {x:(g.width-width)/2,y:(g.height-height)/2,width,height};
}

export function visibleVoxels(occupied,free,g) {
  const {width,height,bins,near,halfX,halfY}=GRID, rays=width*height;
  if(!opticalCrop(g)||occupied?.length!==rays*bins||free?.length!==rays*bins)throw Error('occupancy dimensions');
  const [r,p,h]=g.rpy,cr=Math.cos(r),sr=Math.sin(r),cp=Math.cos(p),sp=Math.sin(p),ch=Math.cos(h),sh=Math.sin(h);
  const cells=new Map(), ranges=[];
  function project(depth,rayX,rayY){
    const right=depth*rayX,down=depth*rayY;
    // Inverse device-from-calibration, then flip down into the scene's up axis.
    return [ch*cp*depth+sh*cp*right-sp*down,
      (ch*sp*sr-sh*cr)*depth+(sh*sp*sr+ch*cr)*right+cp*sr*down,
      g.heightM-((ch*sp*cr+sh*sr)*depth+(sh*sp*cr-ch*sr)*right+cp*cr*down)];
  }
  const inside=([x,y,z])=>x>=2&&x<=45&&Math.abs(y)<=17&&z>=-.65&&z<=6;
  let supportedRays=0,visibleEmpty=0;
  for(let i=0;i<rays;i++){
    let peak=-1,best=0;
    for(let b=0;b<bins;b++){
      const value=occupied[b*rays+i];
      if(value>best&&value<=1){best=value;peak=b;}
    }
    if(peak<0)continue;
    const col=i%width,row=Math.floor(i/width),rayX=((col+.5)/width*2-1)*halfX,rayY=((row+.5)/height*2-1)*halfY;
    const point=project(near+peak+.5,rayX,rayY);
    if(!inside(point))continue;
    if(best<MIN_HIT){
      // Display a sparse distance interval, never an occupied cube, for an ambiguous raised surface.
      if(best<.065||point[2]<.5||col%4!==2||row%4!==2||free[i]<.75)continue;
      let first=-1,last=-1;
      for(let b=0;b<bins;b++){
        const remaining=free[b*rays+i];
        if(!Number.isFinite(remaining)||remaining<0||remaining>1)break;
        if(first<0&&remaining<=.75)first=b;
        if(remaining<=.25){last=b;break;}
      }
      if(first<0||last<first||last-first+1>8)continue;
      const start=project(near+first,rayX,rayY),end=project(near+last+1,rayX,rayY);
      if(inside(start)&&inside(end))ranges.push(...start,...end);
      continue;
    }
    const [forward,lateral,up]=point;
    supportedRays++;
    for(let b=0;b<peak;b++) if(free[b*rays+i]>=MIN_FREE && free[b*rays+i]<=1)visibleEmpty++;
    const x=Math.floor(forward),y=Math.floor(lateral),z=Math.round(up);
    const key=(x*40+y+20)*10+z+1;
    if(!cells.has(key))cells.set(key,[x+.5,y+.5,z]);
  }
  const unique=[...cells.values()];
  return {positions:Float32Array.from(unique.flat()),raisedCells:unique.filter(point=>point[2]>0).length,ranges:Float32Array.from(ranges),supportedRays,visibleEmpty};
}
