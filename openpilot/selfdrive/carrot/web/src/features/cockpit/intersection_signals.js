import * as T from 'three';
import {observedLamps} from '../drive/contents/vision/signal_lamps.js';
import {createSignalHistory,SIGNAL_GLYPHS} from '../drive/contents/vision/signal_history.js';

const colors={red:'#ff151a',yellow:'#ffd229',green:'#00df72'};
const labels={red:'紅',yellow:'黃',green:'綠'};
const approaches=[
  ['北',31,3.7,0],['東',24,7.4,Math.PI/2],['南',14,-3.8,Math.PI],['西',21,-7.4,-Math.PI/2],
];
// Four virtual cameras can see their own signal face. Only recognized pixels
// feed the displayed lenses. Placement and headings belong to this simulator.
function sample(ctx,color,arrow,obscured){
  ctx.fillStyle='#20262a';ctx.fillRect(0,0,96,32);
  if(!obscured){
    const x={red:16,yellow:48,green:80}[color];ctx.fillStyle=colors[color];ctx.strokeStyle=colors[color];
    ctx.beginPath();
    if(arrow){
      ctx.lineWidth=4;ctx.moveTo(x-10,16);ctx.lineTo(x+10,16);ctx.lineTo(x+1,7);
      ctx.moveTo(x+10,16);ctx.lineTo(x+1,25);ctx.stroke();
    }else{ctx.arc(x,16,9,0,2*Math.PI);ctx.fill();}
  }
  return observedLamps(ctx.getImageData(0,0,96,32).data,96,32);
}

export function intersectionSignals(doc){
  const group=new T.Group(),meshTypes=new Map(),surfaces=new Map();
  function mesh(parent,shape,material,x,y,z){
    const m=new T.Mesh(shape,material);m.position.set(x,y,z);parent.add(m);return m;
  }
  function box(w,h,d){
    const key=[w,h,d].join('/');
    if(!meshTypes.has(key))meshTypes.set(key,new T.BoxGeometry(w,h,d));
    return meshTypes.get(key);
  }
  function paint(color){
    if(!surfaces.has(color))surfaces.set(color,new T.MeshStandardMaterial({color,roughness:.7}));
    return surfaces.get(color);
  }
  const disk=new T.CylinderGeometry(.155,.155,.05,16).rotateZ(Math.PI/2);
  // A rectangular shaft and triangular tip on the front face retain their
  // orientation when the observer rotates around the intersection.
  const pointer=new T.Shape();
  pointer.moveTo(-.13,-.034);pointer.lineTo(.028,-.034);pointer.lineTo(.028,-.10);
  pointer.lineTo(.14,0);pointer.lineTo(.028,.10);pointer.lineTo(.028,.034);pointer.lineTo(-.13,.034);
  pointer.closePath();
  const arrowGeometry=new T.ShapeGeometry(pointer);
  const arrowPaint=new T.MeshBasicMaterial({color:colors.green,side:T.DoubleSide});
  const ctx=doc.createElement('canvas');ctx.width=96;ctx.height=32;
  const camera=ctx.getContext('2d',{willReadFrequently:true});
  const heads=approaches.map(([name,x,y,yaw])=>{
    const post=new T.Group();post.position.set(x,y,0);post.rotation.z=yaw;group.add(post);
    mesh(post,box(.12,.12,3.35),paint('#737e86'),0,0,1.675);
    mesh(post,box(.32,1.28,.5),paint('#242a30'),0,0,3.48);
    const lenses={};
    for(const [i,color] of Object.keys(colors).entries()){
      const m=new T.MeshBasicMaterial({color:'#454b50'});lenses[color]=mesh(post,disk,m,-.17,(i-1)*.40,3.48);
    }
    const arrow=mesh(post,arrowGeometry,arrowPaint,-.205,.40,3.48);
    arrow.rotation.order='ZYX';arrow.rotation.set(Math.PI/2,0,Math.PI/2);arrow.visible=false;
    const readout=doc.createElement('span');doc.getElementById('directions').appendChild(readout);
    return {history:createSignalHistory(),lenses,arrow,readout,name};
  });
  let last=-Infinity;
  function update(time){
    if(time-last<.20&&time>=last)return;
    if(time<last||time-last>1)for(const h of heads)h.history.clear();
    last=time;
    for(const [i,{history,lenses,arrow,readout,name}] of heads.entries()){
      const sec=(time+(i%2)*8)%16;
      const color=sec<5?'green':sec<7?'yellow':'red';
      const lamps=sample(camera,color,i===1&&color==='green',i===3&&sec>=9&&sec<12);
      const found=history.confirm([{box:[0,0,96,32],lamps}],time*1000)[0]||[];
      for(const [color,lens] of Object.entries(lenses))lens.material.color.set(found.some(v=>v.color===color&&v.shape==='color')?colors[color]:'#454b50');
      arrow.visible=found.some(v=>v.color==='green'&&v.shape==='right');
      const text=found.map(v=>labels[v.color]+SIGNAL_GLYPHS[v.shape]).join(' ');
      readout.textContent=name+'向　'+(text||'未確認');readout.dataset.signal=found[0]?.color||'unknown';
    }
  }
  return {group,update,dispose(){disk.dispose();arrowGeometry.dispose();arrowPaint.dispose();for(const g of meshTypes.values())g.dispose();for(const m of surfaces.values())m.dispose();for(const h of heads)for(const lens of Object.values(h.lenses))lens.material.dispose();}};
}
