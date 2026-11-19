// Local evidence for a shaded or backlit housing. Work on native crop samples;
// never create color/shape information by upscaling an unresolved lamp.
export function shadeColor(r,g,b){
  const hi=Math.max(r,g,b),spread=hi-Math.min(r,g,b);
  if(hi<40||spread<19||spread<hi*.16)return -1;
  if(g-r>=Math.max(16,g*.18)&&g>=b*.90)return 0;
  if(r-b<19||r<g*.95)return -1;
  const hue=(g-b)/(r-b);
  if(hue>=.44&&hue<1.1)return 1;
  if(hue<.23&&r-g>=16)return 2;
  return -1;
}

function median(values){
  values.sort((a,b)=>a-b);
  return values[Math.floor(values.length/2)];
}

// Compare a component to the surrounding lens/housing in all three channels.
// A rectangular crop may include sky even when the housing itself is dark.
export function locallyLit(rgba,width,height,{minX,minY,w,h,code},mask){
  const cx=minX+(w-1)/2,cy=minY+(h-1)/2;
  const rx=Math.max(2,w/2),ry=Math.max(2,h/2),ring=[[],[],[]],core=[[],[],[]];
  const step=Math.max(1,Math.floor(Math.min(rx,ry)/5));
  for(let y=Math.max(0,Math.floor(cy-ry*2.1));y<=Math.min(height-1,cy+ry*2.1);y+=step){
    for(let x=Math.max(0,Math.floor(cx-rx*2.1));x<=Math.min(width-1,cx+rx*2.1);x+=step){
      const d=((x-cx)/rx)**2+((y-cy)/ry)**2,i=y*width+x;
      const sample=d>=1.65&&d<=4.25?ring:d<=1&&mask[i]===code?core:null;
      if(sample)for(let c=0;c<3;c++)sample[c].push(rgba[4*i+c]);
    }
  }
  if(core[0].length<5||ring[0].length<12)return false;
  const [r,g,b]=core.map(median),background=ring.map(median);
  const dr=r-background[0],dg=g-background[1],db=b-background[2];
  if(code===0)return dg>=18&&dg-dr>=22&&(g>=b*.97||dg>=db*.85)&&g-r>=g*.25;
  if(code===2)return dr>=22&&dr-dg>=18&&dg-db<.27*(dr-db)&&dr-db>=20;
  return dr>=20&&dg>=13&&dg-db>=.43*(dr-db)&&dr-db>=20&&r-b>=.40*r&&g-b>=.25*g;
}
