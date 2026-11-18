// The displayed RTP frame clock is independent from browser receipt time.
export function captureIdentity(target, replay) {
  const frame = target.DriveVisionPresentedFrames?.status?.().last;
  if (replay || !frame || frame.source !== 'live' || frame.imageMapping !== 'rtp' || frame.clockMappingConfidence !== 'exact-frame'
      || !Number.isSafeInteger(frame.frameId) || !Number.isSafeInteger(frame.cameraTimestampEof) || frame.cameraTimestampEof <= 0) return null;
  return {frame:frame.frameId, eof:frame.cameraTimestampEof};
}

export function sceneContributor(target, detector) {
  let revision=null, checkAt=0, sendAt=0, busy=false;
  return async function contribute(identity, state, now) {
    if (!identity || !target.fetch || busy || now<sendAt) return;
    busy=true;
    try {
      if (now>=checkAt) {
        revision=null;
        checkAt=now+30000;
        const res=await target.fetch('/api/research/road-scenes',{cache:'no-store'});
        if (res.ok) revision=(await res.json()).revision;
      }
      if (!Number.isInteger(revision) || revision<1) return;
      const objects=[
        ...state.objects.map(o=>({kind:o.kind,score:o.probability,xy:[o.x,o.y],box:null})),
        ...state.imageObjects.map(o=>({kind:o.kind,score:o.probability,xy:null,box:o.box})),
      ].slice(0,32);
      if (!objects.length) return;
      sendAt=now+950;
      const res=await target.fetch('/api/research/road-scenes',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({revision,packet:{...identity,detector,objects}})});
      if (res.status===403) revision=null;
    } catch { /* Perception stays local when the research channel is unavailable. */ }
    finally {busy=false;}
  };
}
