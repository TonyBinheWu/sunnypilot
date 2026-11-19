// Display geometry in vehicle metres (forward, right, up).
// Both renderers sample only between consecutive observations.
export const roadColors = night => night
  ? {sky:'#17202a',road:'#222b35',verge:'#34404a',edge:'#61707d',lane:'#b6c3cd',path:'#3077b4',near:'#3b87c8',chevron:'#64aeeb'}
  : {sky:'#f5f5f7',road:'#f4f4f6',verge:'#d4d4d7',edge:'#c2c3c7',lane:'#a9acb0',path:'#bfd5ed',near:'#7fb4eb',chevron:'#438cda'};

const segmentCache=new WeakMap();
function segments(path) {
  if(!path||typeof path!=='object')return [];
  const cached=segmentCache.get(path);
  if(cached)return cached;
  const result=[];
  let lastEnd=-Infinity;
  for(let i=1;i<Math.min(path?.x?.length||0,path?.y?.length||0,256);i++){
    const a=path.x[i-1], b=path.x[i], y=path.y[i-1], z=path.y[i];
    if([a,b,y,z].every(Number.isFinite)&&a>=0&&a>=lastEnd&&b>a&&b<=100&&Math.abs(y)<=30&&Math.abs(z)<=30){
      result.push([a,b,y,z]);
      lastEnd=b;
    }
  }
  segmentCache.set(path,result);
  return result;
}

export function pathLateral(path,x) {
  for(const [a,b,y,z] of segments(path))if(x>=a&&x<=b)return y+(z-y)*(x-a)/(b-a);
  return null;
}

export function nearPathCar(object,path) {
  if(object.kind!=='car'||(object.state && object.state!=='confirmed'))return false;
  const lateral=pathLateral(path,object.x);
  return lateral!==null&&Math.abs(lateral-object.y)<=1.25;
}

export function pathChevrons(path) {
  const triangles=[];
  for(let tip=3;tip<=24;tip+=3.5){
    const base=tip+1.0,tipY=pathLateral(path,tip),baseY=pathLateral(path,base);
    if(tipY===null||baseY===null)continue;
    // Reject a missing sample inside the glyph as well as at its endpoints.
    const contiguous=segments(path).filter(([a,b])=>a<base&&b>tip);
    if(!contiguous.length||contiguous.some((s,i)=>i&&s[0]!==contiguous[i-1][1]))continue;
    const z=.045, mid=[tip,tipY,z], back=[tip+.64,tipY,z];
    for(const side of [-1,1]){
      const end=[base,baseY+side*.76,z], inner=[base,baseY+side*.42,z];
      triangles.push(...mid,...end,...inner,...mid,...inner,...back);
    }
  }
  return triangles;
}

export function nearPathSurface(path) {
  const out=[];
  for(const [a,b,y,z] of segments(path)){
    if(a>=13)break;
    const end=Math.min(b,13), ey=y+(z-y)*(end-a)/(b-a);
    const p=[a,y-.83,.034], q=[a,y+.83,.034], r=[end,ey+.83,.034], s=[end,ey-.83,.034];
    out.push(...p,...q,...r,...p,...r,...s);
  }
  return out;
}

export function dashedRibbon(path,left,right) {
  const points=[];
  for(const [a,b,y,z] of segments(path)){
    const lateral=x=>y+(z-y)*(x-a)/(b-a);
    for(let start=Math.floor(a/6)*6;start<b;start+=6){
      const s=Math.max(a,start),e=Math.min(b,start+2.75);
      if(e<=s)continue;
      const sl=[s,lateral(s)+left,.03],sr=[s,lateral(s)+right,.03],el=[e,lateral(e)+left,.03],er=[e,lateral(e)+right,.03];
      points.push(...sl,...sr,...er,...sl,...er,...el);
    }
  }
  return points;
}

export function isDashed(code){return Number.isInteger(code)&&code>=10&&code<=38&&code%10===0;}
