import {groundPoint} from './hud/scene_objects.js';

// Conservative paint geometry candidates, NOT a learned slot/occupancy model.
// Metric coordinates use a locally flat, freshly calibrated ROAD camera only.
export function slotsFromPoints(points){
  const lines=[];
  for(let angle=0;angle<180;angle+=10){
    const c=Math.cos(angle*Math.PI/180),s=Math.sin(angle*Math.PI/180),bins=new Map();
    for(const p of points){const key=Math.round((p[0]*c+p[1]*s)/.12),list=bins.get(key)||[];list.push(p);bins.set(key,list);}
    for(const [key,list] of bins){
      if(list.length<20)continue;
      const ts=list.map(p=>-p[0]*s+p[1]*c).sort((a,b)=>a-b);let start=0;
      for(let i=1;i<=ts.length;i++)if(i===ts.length||ts[i]-ts[i-1]>.40){
        const lo=ts[start],hi=ts[i-1];if(i-start>=20&&hi-lo>=1.7)lines.push({angle,c,s,rho:key*.12,lo,hi,count:i-start});start=i;
      }
    }
  }
  lines.sort((a,b)=>b.count-a.count);const limited=lines.slice(0,80),slots=[];
  for(let i=0;i<limited.length;i++)for(let j=i+1;j<limited.length;j++){
    const a=limited[i],b=limited[j],width=Math.abs(a.rho-b.rho),lo=Math.max(a.lo,b.lo),hi=Math.min(a.hi,b.hi);
    if(a.angle!==b.angle||width<2.1||width>3.5||hi-lo<3.7||hi-lo>7)continue;
    const point=(r,t)=>[a.c*r-a.s*t,a.s*r+a.c*t];
    const closes=t=>limited.some(l=>{if(Math.abs(l.angle-a.angle)!==90)return false;
      return [point(a.rho,t),point(b.rho,t)].every(([x,y])=>Math.abs(x*l.c+y*l.s-l.rho)<.3&&-x*l.s+y*l.c>=l.lo-.3&&-x*l.s+y*l.c<=l.hi+.3);});
    if(!closes(lo)&&!closes(hi))continue;
    const corners=[point(a.rho,lo),point(a.rho,hi),point(b.rho,hi),point(b.rho,lo)];
    if(corners.some(([x,y])=>x<1||x>18||Math.abs(y)>8))continue;
    const center=[corners.reduce((n,p)=>n+p[0],0)/4,corners.reduce((n,p)=>n+p[1],0)/4];
    if(slots.some(o=>Math.hypot(o.center[0]-center[0],o.center[1]-center[1])<1))continue;
    slots.push({corners,center,source:'visible_paint_geometry',occupancy:'unknown'});if(slots.length===12)return slots;
  }return slots;
}
export function parkingMarks(rgba,width,height,geometry){
  if(!geometry||!rgba||rgba.length!==width*height*4||width>640||height>640)return [];
  const points=new Map(),bright=(x,y)=>{const i=(y*width+x)*4,r=rgba[i],g=rgba[i+1],b=rgba[i+2];return Math.min(r,g,b)>160&&Math.max(r,g,b)-Math.min(r,g,b)<45;};
  for(let y=Math.floor(height*.5);y<height*.97;y+=2)for(let x=2;x<width-2;x+=2){
    if(!bright(x,y)||bright(x-2,y)&&bright(x+2,y)&&bright(x,y-2)&&bright(x,y+2))continue;
    const p=groundPoint({originX:x-1,originY:y-2,width:2,height:2},geometry,18);
    if(p&&Math.abs(p[1])<=8)points.set(`${Math.round(p[0]*10)},${Math.round(p[1]*10)}`,p);
    if(points.size>=5000)break;
  }
  return slotsFromPoints([...points.values()].slice(0,5000));
}
