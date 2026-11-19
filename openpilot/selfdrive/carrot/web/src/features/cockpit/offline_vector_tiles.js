import {VectorTile} from '@mapbox/vector-tile';
import Pbf from 'pbf';

const base='/api/navigation/offline/tiles/';
const land={wood:'#b8d8ae',forest:'#b8d8ae',park:'#c7e1ba',grass:'#d9e9c8',farmland:'#e3e8cd',industrial:'#dfdce1'};
const roads={motorway:'#efa15c',trunk:'#f4b370',primary:'#f8ce81',secondary:'#f7dea3',tertiary:'#fff3d6'};
const drawOrder=['land','ocean','water_polygons','water_lines','buildings','street_polygons','streets','street_labels','place_labels'];
function prepare(bytes){
  const tile=new VectorTile(new Pbf(bytes)),items=[];
  for(const name of drawOrder){
    const source=tile.layers[name];if(!source)continue;
    for(let i=0;i<source.length;i++){
      const f=source.feature(i),kind=f.properties.kind;
      if(name==='land'&&!land[kind])continue;
      const label=name.endsWith('_labels')?String(f.properties.name||f.properties.ref||''):'';
      if(name.endsWith('_labels')&&!label)continue;
      const shape=f.loadGeometry();
      let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
      for(const ring of shape)for(const p of ring){p.x/=source.extent;p.y/=source.extent;x0=Math.min(x0,p.x);x1=Math.max(x1,p.x);y0=Math.min(y0,p.y);y1=Math.max(y1,p.y);}
      items.push({name,kind,label,shape,x0,x1,y0,y1,polygon:f.type===3});
    }
  }
  return items;
}

function draw(ctx,items,z,over,offsetX,offsetY){
  const scale=256*over,used=[];
  ctx.fillStyle='#eeece6';ctx.fillRect(0,0,256,256);ctx.lineJoin=ctx.lineCap='round';
  for(const f of items){
    if(f.x1*over<offsetX||f.y1*over<offsetY||f.x0*over>offsetX+1||f.y0*over>offsetY+1)continue;
    if(f.label){
      const line=f.shape[0];if(!line?.length)continue;
      const mid=line[Math.floor(line.length/2)],x=mid.x*scale-offsetX*256,y=mid.y*scale-offsetY*256;
      if(x<8||x>248||y<8||y>244)continue;
      ctx.font=(f.name==='place_labels'?'bold 15px':'12px')+' system-ui,sans-serif';ctx.textAlign='center';
      const width=ctx.measureText(f.label).width/2;
      if(x-width<0||x+width>256||used.some(p=>Math.abs(x-p.x)<width+p.width+4&&Math.abs(y-p.y)<16))continue;
      used.push({x,y,width});ctx.lineWidth=3;ctx.strokeStyle='#fffffa';ctx.strokeText(f.label,x,y);ctx.fillStyle='#44505b';ctx.fillText(f.label,x,y);continue;
    }
    ctx.beginPath();
    for(const line of f.shape){
      for(const [j,p] of line.entries()){const x=p.x*scale-offsetX*256,y=p.y*scale-offsetY*256;if(j)ctx.lineTo(x,y);else ctx.moveTo(x,y);}
      if(f.polygon)ctx.closePath();
    }
    if(f.polygon){
      ctx.fillStyle=f.name==='land'?land[f.kind]:f.name==='buildings'?'#d8d5d0':f.name==='street_polygons'?'#fff':'#aad4e3';
      ctx.fill('evenodd');
    }else{
      ctx.strokeStyle=f.name==='water_lines'?'#9bcddd':roads[f.kind]||'#fff';
      ctx.lineWidth=f.name==='water_lines'?1.5:roads[f.kind]?Math.min(6,2+Math.max(0,z-12)*.65):Math.min(4,1+Math.max(0,z-12)*.45);
      ctx.stroke();
    }
  }
}

// Parent vectors are decoded once for neighbouring overzoomed tiles. Abandon
// late paints after layer removal and keep only a bounded working set.
export function vectorLayer(L,info){
  const cache=new Map(),requests=new Map();
  const Layer=L.GridLayer.extend({
    createTile(coords,done){
      const canvas=document.createElement('canvas'),dpr=Math.min(2,window.devicePixelRatio||1);
      canvas.width=canvas.height=256*dpr;
      const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);
      const z=Math.min(coords.z,info.maxZoom),over=2**(coords.z-z),x=Math.floor(coords.x/over),y=Math.floor(coords.y/over);
      const key=[z,x,y].join('/'),signal=this.controller.signal;
      let work=cache.has(key)?Promise.resolve(cache.get(key)):requests.get(key);
      if(!work){
        work=fetch(base+key+'.pbf?v='+encodeURIComponent(info.version),{signal}).then(async response=>{
          if(!response.ok)throw Error('offline tile');
          const items=response.status===204?[]:prepare(new Uint8Array(await response.arrayBuffer()));
          if(!signal.aborted){cache.set(key,items);if(cache.size>8)cache.delete(cache.keys().next().value);}
          return items;
        }).finally(()=>{if(requests.get(key)===work)requests.delete(key);});requests.set(key,work);
      }
      work.then(items=>{
        if(signal.aborted)return;
        draw(ctx,items,coords.z,over,coords.x-x*over,coords.y-y*over);
        canvas.dataset.offlinePainted='true';
      }).then(()=>done(null,canvas),error=>done(error,canvas));
      return canvas;
    },
    onAdd(map){this.controller=new AbortController();return L.GridLayer.prototype.onAdd.call(this,map);},
    onRemove(map){this.controller.abort();requests.clear();cache.clear();return L.GridLayer.prototype.onRemove.call(this,map);},
  });
  return new Layer({maxZoom:19,keepBuffer:0,updateWhenIdle:true});
}
