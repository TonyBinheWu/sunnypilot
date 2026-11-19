// Playback on the workstation uses the same projection and Three.js geometry as the cockpit.
import {GRID, opticalCrop, visibleVoxels} from '/src/features/drive/contents/vision/occupancy_grid.js';
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
let running = false;

async function next(now, metadata) {
  if (running) return;
  running = true;
  try {
    const captured = Number.isFinite(metadata.expectedDisplayTime) ? Math.min(now, metadata.expectedDisplayTime) : now;
    const config = await (await fetch('/replay/config', {cache:'no-store'})).json();
    const geometry = {...config, width:video.videoWidth, height:video.videoHeight};
    const crop = opticalCrop(geometry);
    if (!crop) throw Error('影片尺寸與校正不符');
    const x = config.cx - crop.width / 2, y = config.cy - crop.height / 2;
    if (x < 0 || y < 0 || x + crop.width > geometry.width || y + crop.height > geometry.height) throw Error('影片未涵蓋校正視野');
    if (performance.now() - captured >= 900 || video.paused) return;
    pixels.drawImage(video, x, y, crop.width, crop.height, 0, 0, 224, 126);
    const response = await fetch(base+'infer', {method:'POST', body:pixels.getImageData(0,0,224,126).data});
    const n = GRID.width * GRID.height * GRID.bins;
    if (!response.ok || Number(response.headers.get('Content-Length')) !== n*8) throw Error('工作站 GPU 推論未就緒');
    const data = new Float32Array(await response.arrayBuffer());
    if (video.paused || performance.now() - captured >= 900) return;
    const result = visibleVoxels(data.subarray(0,n), data.subarray(n), geometry);
    const v = config.view, scale = Math.min(1, 1280/Math.max(v.w,v.h));
    const ok = scene.render(Math.round(v.w*scale), Math.round(v.h*scale),
      {environment:result.positions, environmentRanges:result.ranges}, {night:v.night, view:v});
    if (!ok || scene.snapshot().backend !== 'webgl2') throw Error('工作站缺少 WebGL 2');
    const jpeg = await new Promise(resolve=>scene.canvas.toBlob(resolve,'image/jpeg',.84));
    if (!jpeg || video.paused) return;
    const sent = await fetch(base+'publish',{method:'POST',body:jpeg,headers:{
      'X-Age':String(performance.now()-captured), 'X-Cells':String(result.positions.length/3), 'X-Raised':String(result.raisedCells)}});
    status.textContent = sent.ok ? 'GPU 回放中 · '+(result.positions.length/3)+' 個體素' : '略過過期影格';
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
