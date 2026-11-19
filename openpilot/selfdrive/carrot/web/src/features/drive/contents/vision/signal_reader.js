import {observedLamps} from './signal_lamps.js';

// EfficientDet supplies the housing ROI. Read pixels from this exact frame in
// its native aspect ratio; enlarging a distant arrow cannot add evidence.
export function createSignalReader(){
  const crop=new OffscreenCanvas(1,1),ctx=crop.getContext('2d',{willReadFrequently:true});
  function read(bitmap,b){
    if(!b||![b.originX,b.originY,b.width,b.height].every(Number.isFinite))return [];
    const x=Math.round(b.originX),y=Math.round(b.originY);
    const w=Math.round(b.width),h=Math.round(b.height);
    if(x<0||y<0||x+w>bitmap.width+1||y+h>bitmap.height+1||Math.min(w,h)<8)return [];
    const scale=Math.min(1,256/Math.max(w,h)),cw=Math.round(w*scale),ch=Math.round(h*scale);
    if(Math.min(cw,ch)<8)return [];
    if(crop.width!==cw)crop.width=cw;
    if(crop.height!==ch)crop.height=ch;
    ctx.drawImage(bitmap,x,y,w,h,0,0,cw,ch);
    return observedLamps(ctx.getImageData(0,0,cw,ch).data,cw,ch);
  }
  return read;
}
