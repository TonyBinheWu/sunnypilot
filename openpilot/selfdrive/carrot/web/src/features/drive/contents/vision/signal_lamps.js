import {shadeColor,locallyLit} from './signal_contrast.js';
import {arrowShape} from './signal_glyph.js';

const SIGNAL_COLORS=['green','yellow','red'];
function pixelColor(r,g,b){
  const max=Math.max(r,g,b),min=Math.min(r,g,b);
  if(max<86||max-min<42||max-min<max*.36)return -1;
  if(g>r*1.35&&g>b*.88)return 0;
  if(r>=g*.92&&g>=r*.55&&b<g*.64)return 1;
  if(r>g*3.1&&r>b*1.55)return 2;
  return -1;
}

// Segment lamps in the original aspect ratio. The neighborhood bridges small gaps
// between LED dots. Only lit pixels (never the bridged area) vote on the glyph.
export function observedLamps(rgba,width,height){
  const pixels=width*height;
  if(width<8||height<8||rgba.length!==pixels*4)return [];
  const mask=new Int8Array(pixels);
  let dark=0;
  for(let i=0;i<pixels;i++){
    const j=i*4,r=rgba[j],g=rgba[j+1],b=rgba[j+2];
    mask[i]=pixelColor(r,g,b);
    if(Math.max(r,g,b)<102)dark++;
  }
  const smallGap=Math.min(3,Math.max(1,Math.round(Math.min(width,height)/19)));
  const lamps=dark>=pixels*.20?components(mask,rgba,width,height,smallGap):[];
  const wideGap=Math.min(7,Math.round(Math.min(width,height)/9));
  if(dark>=pixels*.20&&wideGap>smallGap&&(!lamps.length||lamps.some(l=>l.shape==='color'))){
    for(const glyph of components(mask,rgba,width,height,wideGap)){
      if(glyph.shape==='color')continue;
      const nearby=lamps.filter(l=>l.color===glyph.color&&Math.abs(l.minX+l.w/2-glyph.minX-glyph.w/2)<(l.w+glyph.w)*.5&&
        Math.abs(l.minY+l.h/2-glyph.minY-glyph.h/2)<(l.h+glyph.h)*.5);
      if(nearby.some(l=>l.shape!=='color')||nearby.length>1)continue;
      if(nearby.length)Object.assign(nearby[0],glyph);else lamps.push(glyph);
    }
  }
  if(lamps.length){
    const strict=resolveColors(lamps,width>=height);
    if(!strict.length||strict.every(l=>l.shape!=='color'))return strict;
    // A lower-contrast shaft may complete a bright arrowhead. Only upgrade the
    // original lamp when a second mask corroborates the same place and color.
    const local=localCandidates();
    for(const lamp of lamps){
      const hits=local.filter(g=>g.color===lamp.color&&g.shape!=='color'&&
        Math.abs(g.minX+g.w/2-lamp.minX-lamp.w/2)<Math.min(g.w,lamp.w)*.55&&
        Math.abs(g.minY+g.h/2-lamp.minY-lamp.h/2)<Math.min(g.h,lamp.h)*.55);
      if(!lamp.drop&&lamp.shape==='color'&&hits.length===1)lamp.shape=hits[0].shape;
    }
    return resolveColors(lamps,width>=height);
  }
  return resolveColors(localCandidates(),width>=height);

  function localCandidates(){
    for(let i=0;i<pixels;i++)mask[i]=shadeColor(rgba[i*4],rgba[i*4+1],rgba[i*4+2]);
    const broad=components(mask,rgba,width,height,smallGap,true);
    if(broad.length)return broad;
    // Isolate the colored core if the weaker halo has merged with scenery or
    // reached an edge. The new core must still pass the surrounding-ring test.
    const peaks=[0,0,0],contrast=new Uint8Array(pixels);
    for(let i=0;i<pixels;i++){
      const c=mask[i];if(c<0)continue;
      const r=rgba[i*4],g=rgba[i*4+1],b=rgba[i*4+2];
      contrast[i]=c===0?g-r:c===1?Math.min(r,g)-b:r-Math.max(g,b);
      peaks[c]=Math.max(peaks[c],contrast[i]);
    }
    for(let i=0;i<pixels;i++)if(mask[i]>=0&&contrast[i]<peaks[mask[i]]*.62)mask[i]=-1;
    return components(mask,rgba,width,height,smallGap,true);
  }
}

function components(mask,rgba,width,height,gap,local=false){
  const pixels=width*height,visited=new Uint8Array(pixels),stack=new Int32Array(pixels),lamps=[];
  for(let i=0;i<pixels;i++){
    const code=mask[i];
    if(code<0||visited[i])continue;
    let n=0,len=1,minX=width,minY=height,maxX=0,maxY=0,peak=0;
    visited[i]=1;stack[0]=i;
    while(len){
      const k=stack[--len],x=k%width,y=Math.floor(k/width);
      n++;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);
      peak=Math.max(peak,rgba[k*4],rgba[k*4+1],rgba[k*4+2]);
      const left=Math.max(0,x-gap),right=Math.min(width-1,x+gap),bottom=Math.min(height-1,y+gap);
      for(let yy=Math.max(0,y-gap);yy<=bottom;yy++){
        for(let xx=left;xx<=right;xx++){
          const p=yy*width+xx;
          if(!visited[p]&&mask[p]===code){stack[len++]=p;visited[p]=1;}
        }
      }
    }
    const w=maxX-minX+1,h=maxY-minY+1;
    if(minX===0||minY===0||maxX===width-1||maxY===height-1||Math.min(w,h)<3||Math.max(w,h)>Math.min(w,h)*2.1||
        n<Math.max(local?8:6,pixels*.0015)||n>pixels*.31||peak<(local?60:128)||n/(w*h)<.17)continue;
    if(local&&code===2&&Math.min(w,h)<4)continue;
    if(local&&!locallyLit(rgba,width,height,{minX,minY,w,h,code},mask))continue;
    const shape=(!local||Math.min(w,h)>=12)&&arrowShape(mask,width,{minX,minY,w,h,code})||'color';
    if(shape==='color'&&n/(w*h)<.40)continue;
    lamps.push({color:SIGNAL_COLORS[code],shape,minX,minY,w,h,n});
  }
  return lamps;
}

function resolveColors(lamps,horizontal){
  // An amber lamp often has an orange/red halo. Conflicting overlapping
  // chromatic regions cannot count as two independent illuminated bulbs.
  for(let i=0;i<lamps.length;i++)for(const b of lamps.slice(i+1)){
    const a=lamps[i];
    if(a.color!==b.color&&Math.abs(a.minX+a.w/2-b.minX-b.w/2)<(a.w+b.w)*.42&&
      Math.abs(a.minY+a.h/2-b.minY-b.h/2)<(a.h+b.h)*.42){
      if([a.color,b.color].includes('yellow')&&[a.color,b.color].includes('red')){
        const amber=a.color==='yellow'?a:b,red=a.color==='red'?a:b;
        if(amber.n>=red.n*.45){red.drop=true;continue;}
      }
      return [];
    }
  }
  const largest=Math.max(0,...lamps.filter(l=>!l.drop).map(l=>l.n));
  const unique=lamps.filter(l=>!l.drop&&(l.shape!=='color'||l.n>=largest*.15)).sort((a,b)=>horizontal?a.minX-b.minX:a.minY-b.minY)
    .map(({color,shape})=>({color,shape}));
  const circles=new Set(unique.filter(l=>l.shape==='color').map(l=>l.color));
  if(circles.size>1)return [];
  if(unique.length>4||new Set(unique.map(l=>l.color)).size===3)return [];
  return unique.filter((l,i)=>unique.findIndex(o=>o.color===l.color&&o.shape===l.shape)===i);
}
