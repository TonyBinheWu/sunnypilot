import {parkingMarks} from './parking_marks.js';
self.onmessage=({data})=>{
  const bitmap=data?.bitmap;
  try{
    if(data.type!=='frame'||!bitmap)return;
    const canvas=new OffscreenCanvas(bitmap.width,bitmap.height),ctx=canvas.getContext('2d',{willReadFrequently:true});
    ctx.drawImage(bitmap,0,0);const image=ctx.getImageData(0,0,canvas.width,canvas.height);
    self.postMessage({id:data.id,slots:parkingMarks(image.data,canvas.width,canvas.height,data.geometry)});
  }catch{self.postMessage({id:data?.id,error:true});}finally{bitmap?.close();}
};
