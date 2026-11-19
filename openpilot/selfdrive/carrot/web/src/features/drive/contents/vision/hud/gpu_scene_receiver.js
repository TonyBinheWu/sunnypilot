// One outstanding read per viewer. Freshness includes the fetch and image decode.
export function createGpuSceneReceiver(target, canvas) {
  let active = false, generation = 0, controller, poll, expiry, latest = '', painted = 0;
  canvas.style.objectFit = 'contain';
  let status = 'paused', cells = 0, raised = 0;
  let parking = false, desiredView = '', sentView = '', retryViewAt = 0;
  function setView(width,height,{night=false,view={}}={}) {
    const v = view || {};
    if(parking !== (v.parking===true)){parking=v.parking===true;if(active)clear('waiting');}
    desiredView = JSON.stringify({w:width,h:height,night:!!night,yaw:v.yaw||0,pitch:v.pitch||25,
      parking:v.parking===true,distance:Math.max(5,Math.min(26,v.distance||9)),bottomFraction:v.bottomFraction||0});
  }
  const time = () => target.performance.now();
  function clear(state) {
    status = state;
    cells = raised = 0;
    canvas.getContext('2d')?.clearRect(0, 0, canvas.width, canvas.height);
  }
  async function read(epoch) {
    if (!active || epoch !== generation) return;
    const requestController = new AbortController();
    controller = requestController;
    const start = time();
    let bitmap;
    const deadline = target.setTimeout(() => requestController.abort(), 850);
    try {
      if (desiredView && desiredView !== sentView && time() >= retryViewAt) {
        const view = desiredView;
        const result = await target.fetch('/api/vision/gpu-scene/view',{method:'POST',headers:{'Content-Type':'application/json'},body:view,signal:requestController.signal});
        if (epoch !== generation || !active) return;
        if (result.ok) sentView = view;
        retryViewAt = time() + (result.ok ? 100 : 1000);
      }
      const suffix = status === 'ready' && latest ? '?after='+encodeURIComponent(latest) : '';
      const response = await target.fetch('/api/vision/gpu-scene/frame'+suffix, {signal:requestController.signal, cache:'no-store'});
      if (epoch !== generation) return;
      if (response.status === 304) return;
      if (!response.ok || response.status === 204) { clear('waiting'); return; }
      const frameIsParked=response.headers.get('X-Scene-Parking')==='1';
      if(frameIsParked!==parking){clear('waiting');return;}
      const seq = response.headers.get('X-Scene-Frame');
      const age = Number(response.headers.get('X-Scene-Age-Ms') ?? NaN);
      if (!seq || !Number.isFinite(age) || age < 0 || age >= 900) { clear('stale'); return; }
      if (seq === latest && status === 'ready') return;
      const size = Number(response.headers.get('Content-Length'));
      if (response.headers.get('Content-Type') !== 'image/jpeg' || !Number.isSafeInteger(size) || size < 1 || size > 1048576) throw Error('invalid image');
      const image = await response.blob();
      if (image.size !== size) throw Error('invalid size');
      bitmap = await target.createImageBitmap(image);
      if (epoch !== generation || !active || frameIsParked!==parking) return;
      const remaining = 900 - age - (time() - start);
      if (remaining <= 0) { clear('stale'); return; }
      if (canvas.width !== bitmap.width) canvas.width = bitmap.width;
      if (canvas.height !== bitmap.height) canvas.height = bitmap.height;
      canvas.getContext('2d').drawImage(bitmap, 0, 0);
      target.clearTimeout(expiry);
      expiry = target.setTimeout(() => { if (epoch === generation) clear('stale'); }, remaining);
      latest = seq;
      cells = Number(response.headers.get('X-Scene-Cells')) || 0;
      raised = Number(response.headers.get('X-Scene-Raised')) || 0;
      status = 'ready';
      painted++;
    } catch { if (epoch === generation) clear('waiting'); }
    finally {
      bitmap?.close();
      target.clearTimeout(deadline);
      if (active && epoch === generation) poll = target.setTimeout(() => read(epoch), 45);
    }
  }
  function update(next) {
    if (active === next) return;
    active = next;
    generation++;
    controller?.abort();
    target.clearTimeout(poll);
    target.clearTimeout(expiry);
    latest = sentView = '';
    retryViewAt = 0;
    if (active) { status = 'waiting'; void read(generation); }
    else clear('paused');
  }
  return {update,setView, snapshot:()=>({status,backend:'external-gpu',painted,frame:latest,cells,raised}),destroy:()=>update(false)};
}
