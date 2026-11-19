// Playback on the workstation uses the same projection and Three.js geometry as the cockpit.
import {GRID, opticalCrop, visibleVoxels} from '/src/features/drive/contents/vision/occupancy_grid.js';
import {cameraTargets} from '/src/features/drive/contents/vision/hud/scene_objects.js';
import {createObjectTracker, inCameraView} from '/src/features/drive/contents/vision/hud/object_tracker.js';
import {createDrivingScene3D} from '/src/features/drive/contents/vision/hud/scene_3d.js';

const base = '/api/vision/gpu-scene/';
const video = document.querySelector('video');
const status = document.getElementById('status');
const scene = createDrivingScene3D(document, window);
document.body.append(scene.canvas);
const input = document.createElement('canvas');
input.width = 224;
input.height = 126;
const pixels = input.getContext('2d', {willReadFrequently:true});
let running = false, generation=0, config=null, refreshed=-Infinity;
const tracker=createObjectTracker();
const detector=document.createElement('canvas');detector.width=detector.height=416;
const rgb=detector.getContext('2d',{willReadFrequently:true});
function resetTracks(){generation++;tracker.reset();}
for(const event of ['pause','seeking','emptied'])video.addEventListener(event,resetTracks);

async function occupancy(geometry,captured) {
  const crop = opticalCrop(geometry);
  if (!crop) throw Error('影片尺寸與校正不符');
  const x = geometry.cx - crop.width / 2, y = geometry.cy - crop.height / 2;
  if (x < 0 || y < 0 || x + crop.width > geometry.width || y + crop.height > geometry.height) throw Error('影片未涵蓋校正視野');
  if (performance.now() - captured >= 900 || video.paused) return;
  pixels.drawImage(video, x, y, crop.width, crop.height, 0, 0, 224, 126);
  const response = await fetch(base+'infer', {method:'POST', body:pixels.getImageData(0,0,224,126).data});
  const n = GRID.width * GRID.height * GRID.bins;
  if (!response.ok || Number(response.headers.get('Content-Length')) !== n*8) throw Error('工作站 GPU 推論未就緒');
  const data = new Float32Array(await response.arrayBuffer());
  if (video.paused || performance.now() - captured >= 900) return;
  return visibleVoxels(data.subarray(0,n), data.subarray(n), geometry);
}

async function detectObjects(geometry,lenses,captured,epoch) {
  const inputs=Object.entries(lenses||{road:{...geometry,left:0,top:0}}).map(([name,g])=>{
    if(g.left+g.width>video.videoWidth || g.top+g.height>video.videoHeight)throw Error('雙鏡頭裁切超出影片');
    const scale=Math.min(416/g.width,416/g.height);
    const width=Math.max(1,Math.floor(g.width*scale)),height=Math.max(1,Math.floor(g.height*scale));
    rgb.fillStyle='rgb(114,114,114)';rgb.fillRect(0,0,416,416);
    rgb.drawImage(video,g.left,g.top,g.width,g.height,0,0,width,height);
    return {name,g,width,height,rgba:rgb.getImageData(0,0,416,416).data};
  });
  const observations=[];
  for(const {name,g,width,height,rgba} of inputs){
    if(epoch!==generation||performance.now()-captured>=900)return;
    const response=await fetch(base+'infer',{method:'POST',body:rgba});
    if(!response.ok)throw Error('工作站物件模型未就緒');
    const hits=await response.json();
    for(const hit of hits){
      const [left,top,right,bottom]=hit.box;
      if(bottom>=height||right<=0||left>=width||bottom<=0)continue;
      const x=Math.max(0,left),y=Math.max(0,top);
      const box={originX:x*g.width/width,originY:y*g.height/height,width:(Math.min(width,right)-x)*g.width/width,
        height:(bottom-y)*g.height/height};
      const [item]=cameraTargets([{categories:[{categoryName:hit.kind,score:hit.score}],boundingBox:box}],g);
      if(!item || (name==='wide'&&lenses?.road&&inCameraView(lenses.road,item.x,item.y)))continue;
      observations.push({...item,source:'workstation.yolox_nano.'+name});
    }
  }
  if(epoch!==generation||performance.now()-captured>=900)return;
  tracker.ingest('objects',{stamp:captured,objects:observations},performance.now());
  return {tracks:tracker.sample(performance.now()),positions:[],ranges:[],raisedCells:0};
}


async function next(now, metadata) {
  if (running) return;
  running = true;
  try {
    const epoch=generation;
    const captured = Number.isFinite(metadata.expectedDisplayTime) ? Math.min(now, metadata.expectedDisplayTime) : now;
    // Fetch outside the capture. Binding new video pixels to an older callback
    // after an asynchronous request would misdate the observations.
    if(!config || now-refreshed>=500){
      config=await (await fetch('/replay/config',{cache:'no-store'})).json();
      refreshed=performance.now();
      return;
    }
    const geometry = {...config, width:video.videoWidth, height:video.videoHeight};
    const result = config.objects ? await detectObjects(geometry, config.lenses, captured, epoch) : await occupancy(geometry,captured);
    if (!result || epoch!==generation || video.paused || performance.now()-captured>=900) return;
    const v = config.view, scale = Math.min(1, 1280/Math.max(v.w,v.h));
    const ok = scene.render(Math.round(v.w*scale), Math.round(v.h*scale),
      {tracks:result.tracks, environment:result.positions, environmentRanges:result.ranges}, {night:v.night, view:v});
    if (!ok || scene.snapshot().backend !== 'webgl2') throw Error('工作站缺少 WebGL 2');
    const jpeg = await new Promise(resolve=>scene.canvas.toBlob(resolve,'image/jpeg',.84));
    if (!jpeg || video.paused || epoch!==generation || performance.now()-captured>=900) return;
    const sent = await fetch(base+'publish',{method:'POST',body:jpeg,headers:{
      'X-Age':String(performance.now()-captured), 'X-Cells':String(result.positions.length/3), 'X-Raised':String(result.raisedCells)}});
    const detail=config.objects?'物件追蹤 '+result.tracks.length+' 個':'體素 '+(result.positions.length/3)+' 格';
    status.textContent=sent.ok?'GPU 回放中 · '+detail:'略過過期影格';
  } catch (error) {
    status.textContent = error.message;
  } finally {
    running = false;
    video.requestVideoFrameCallback(next);
  }
}
video.requestVideoFrameCallback(next);
video.addEventListener('pause',()=>{scene.pause();status.textContent='影片已暫停';});
window.addEventListener('pagehide',()=>scene.destroy(),{once:true});
