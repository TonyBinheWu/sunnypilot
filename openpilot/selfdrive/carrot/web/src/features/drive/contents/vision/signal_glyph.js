// Compare an illuminated component with outlined and filled road-signal arrows.
// An arrow needs both a shaft and a head; blobs and partial chevrons abstain.
const SIDE=17;
const directions=['up','up_right','right','down_right','down','down_left','left','up_left'];
function segmentDistance(x,y,x1,y1,x2,y2){
  const dx=x2-x1,dy=y2-y1;
  const t=Math.max(0,Math.min(1,((x-x1)*dx+(y-y1)*dy)/(dx*dx+dy*dy)));
  return Math.hypot(x-x1-t*dx,y-y1-t*dy);
}
function template(angle,thickness,filled){
  const hits=[];
  for(let i=0;i<SIDE*SIDE;i++){
    const u=2*((i%SIDE+.5)/SIDE)-1,v=2*((Math.floor(i/SIDE)+.5)/SIDE)-1;
    // In the reference orientation the tip points straight up.
    const x=u*Math.cos(angle)+v*Math.sin(angle),y=-u*Math.sin(angle)+v*Math.cos(angle);
    const shaft=segmentDistance(x,y,0,.92,0,-.84);
    const head=Math.min(segmentDistance(x,y,0,-.86,-.85,-.02),segmentDistance(x,y,0,-.86,.85,-.02));
    if(Math.min(shaft,head)<thickness||(filled&&y>=-.9&&y<.05&&Math.abs(x)<y+.92))hits.push(i);
  }
  return hits;
}
const templates=directions.map((_,index)=>[.12,.21,.30].flatMap(thickness=>
  [false,true].map(filled=>template(index*Math.PI/4,thickness,filled))));

export function arrowShape(mask,width,blob){
  const {minX,minY,w,h,code}=blob;
  if(Math.min(w,h)<9||Math.max(w,h)>Math.min(w,h)*1.85)return null;
  const bits=new Uint8Array(SIDE*SIDE);
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
    if(mask[(minY+y)*width+minX+x]!==code)continue;
    // Each source pixel covers its full footprint. This also handles <17px glyphs.
    const left=Math.floor(x*SIDE/w),right=Math.ceil((x+1)*SIDE/w);
    const top=Math.floor(y*SIDE/h),bottom=Math.ceil((y+1)*SIDE/h);
    for(let j=top;j<bottom;j++)bits.fill(1,j*SIDE+left,j*SIDE+right);
  }
  const count=bits.reduce((a,b)=>a+b,0);
  if(count<35||count>SIDE*SIDE*.78)return null;
  const ranked=templates.map((variants,index)=>{
    let best=0;
    for(const hit of variants){
      let common=0;for(const i of hit)common+=bits[i];
      best=Math.max(best,common/(hit.length+count-common));
    }
    return {direction:directions[index],score:best};
  }).sort((a,b)=>b.score-a.score);
  const [first,second]=ranked;
  const margin=Math.max(.065,.14-.40*(first.score-.60));
  return first.score>=.60&&first.score-second.score>=margin?first.direction:null;
}
