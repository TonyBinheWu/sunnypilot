// Phase 1: same-origin HTTPS preview and browser-local clips. No driving controls.
export const clipLimit=60;
export function recordingMime(recorder){
 return ['video/webm;codecs=vp8','video/webm','video/mp4'].find(type=>recorder?.isTypeSupported?.(type))||null;
}
export function mediaCursor(frame){return frame.stream+':'+frame.sequence;}
export function validPreview(frame){return frame&&['demo','road-preview'].includes(frame.source)&&Number.isSafeInteger(frame.sequence)&&frame.sequence>=0&&Number.isInteger(frame.width)&&frame.width>0&&frame.width<=1280&&Number.isInteger(frame.height)&&frame.height>0&&frame.height<=720&&typeof frame.jpeg==='string'&&frame.jpeg.length<=240004;}

export function mediaViewer({api,t,el}){
 const translated=(tag,key,cls)=>{const node=el(tag,t(key),cls);node.dataset.mediaI18n=key;return node;};
 function say(key){if(status){status.dataset.mediaI18n=key;status.textContent=t(key);}}
 let device=null,root=null,generation=0,timer=null,freshness=null,active=false,recording=null,recordStream=null,recordTimer=null,urls=[],pip=null,last=0,cursor='',canvas=null,ctx=null,status=null,recButton=null,clips=null;
 function clearPicture(){if(ctx){ctx.fillStyle='#10151d';ctx.fillRect(0,0,canvas.width,canvas.height);}}
 function stopRecording(){if(recording&&recording.state!=='inactive')recording.stop();clearTimeout(recordTimer);recordTimer=null;}
 function stop(){active=false;generation++;clearTimeout(timer);stopRecording();if(pip){pip.srcObject?.getTracks().forEach(track=>track.stop());pip.srcObject=null;if(document.pictureInPictureElement===pip)document.exitPictureInPicture().catch(()=>{});}cursor='';last=0;clearPicture();if(status)say('mediaStopped');}
 function close(){clearInterval(freshness);freshness=null;stop();root?.querySelectorAll('video').forEach(video=>{video.pause();video.removeAttribute('src');video.load();});urls.forEach(url=>URL.revokeObjectURL(url));urls=[];root?.remove();root=null;device=null;}
 function open(parent,id){
  if(device===id&&root?.isConnected)return;
  close();device=id;root=el('section',undefined,'workspace-card media-panel');parent.replaceChildren(root);
  root.append(translated('h2','mediaTitle'),translated('p','mediaPhase','workspace-muted'));
  status=translated('p','mediaStopped','media-status');status.setAttribute('role','status');root.append(status);
  canvas=el('canvas');canvas.width=640;canvas.height=360;canvas.setAttribute('aria-label',t('mediaTitle'));ctx=canvas.getContext('2d',{alpha:false});clearPicture();root.append(canvas);
  const actions=el('div',undefined,'media-actions');root.append(actions);
  const button=(name,callback)=>{const node=translated('button',name);node.type='button';node.addEventListener('click',callback);actions.append(node);return node;};
  button('mediaStart',()=>{if(active)return;active=true;const mine=++generation;say('waiting');poll(mine);});
  button('mediaStop',stop);
  recButton=button('mediaRecord',()=>{
   if(recording?.state==='recording'){stopRecording();return;}
   if(!active||!last||performance.now()-last>3000)return;
   const mime=recordingMime(globalThis.MediaRecorder);if(!mime||!canvas.captureStream)return;
   try{
    const chunks=[],ownedRoot=root,ownedClips=clips;let size=0;
    recordStream=canvas.captureStream(2);const stream=recordStream;
    const recorder=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:700000});recording=recorder;
    recorder.ondataavailable=event=>{if(event.data.size){chunks.push(event.data);size+=event.data.size;if(size>=16*1024*1024)stopRecording();}};
    recorder.onstop=()=>{
     stream.getTracks().forEach(track=>track.stop());if(recording===recorder){recording=null;recButton.dataset.mediaI18n='mediaRecord';recButton.textContent=t('mediaRecord');}
     if(!ownedRoot.isConnected||!chunks.length)return;
     const blob=new Blob(chunks,{type:recorder.mimeType}),url=URL.createObjectURL(blob);urls.push(url);
     if(urls.length>3){URL.revokeObjectURL(urls.shift());ownedClips.firstElementChild?.remove();}
     const item=el('article'),player=el('video');player.controls=true;player.src=url;player.playsInline=true;
     const download=translated('a','mediaDownload','workspace-save');download.href=url;download.download='FormosaLink-'+new Date().toISOString().replace(/[:.]/g,'-')+(recorder.mimeType.includes('mp4')?'.mp4':'.webm');item.append(player,download);ownedClips.append(item);
    };
    recorder.onerror=()=>{say('mediaUnsupported');stopRecording();};
    recorder.start(1000);recButton.dataset.mediaI18n='mediaFinish';recButton.textContent=t('mediaFinish');recordTimer=setTimeout(stopRecording,clipLimit*1000);
   }catch{recordStream?.getTracks().forEach(track=>track.stop());say('mediaUnsupported');}
  });
  recButton.disabled=!recordingMime(globalThis.MediaRecorder)||!canvas.captureStream;
  const fullButton=button('mediaFullscreen',()=>canvas.requestFullscreen?.().catch(()=>{say('mediaUnsupported');}));fullButton.disabled=!canvas.requestFullscreen;
  pip=el('video');pip.setAttribute('aria-hidden','true');pip.tabIndex=-1;pip.muted=true;pip.playsInline=true;pip.className='media-pip';root.append(pip);
  const pipButton=button('mediaPip',async()=>{const video=pip,mine=generation;try{if(!active||!last||performance.now()-last>3000)return;video.srcObject?.getTracks().forEach(track=>track.stop());video.srcObject=canvas.captureStream(2);await video.play();if(generation===mine&&active)await video.requestPictureInPicture();}catch{video.srcObject?.getTracks().forEach(track=>track.stop());video.srcObject=null;if(generation===mine&&active)say('mediaUnsupported');}});
  pipButton.disabled=!document.pictureInPictureEnabled||!canvas.captureStream;
  root.append(translated('p','mediaRecordingNote','settings-edit-note'));clips=el('div',undefined,'media-clips');root.append(clips);
  root.append(translated('h3','mediaNextTitle'),translated('p','mediaNext','workspace-muted'));
  freshness=setInterval(()=>{if(active&&last&&performance.now()-last>3000){last=0;clearPicture();stopRecording();say('stale');}},250);
 }
 async function poll(mine){
  if(!active||generation!==mine||!root?.isConnected)return;
  try{
   if(document.hidden){stopRecording();clearPicture();say('mediaPaused');}
   else{
    const requested=performance.now();const data=await api('/devices/'+encodeURIComponent(device)+'/media?after='+encodeURIComponent(cursor));
    if(generation!==mine)return;
    if(performance.now()-requested>3000){last=0;clearPicture();stopRecording();say('stale');}
    else if(!data.available){last=0;cursor='';clearPicture();stopRecording();say('mediaWaiting');}
    else if(data.frame){
     const frame=data.frame;if(!validPreview(frame))throw Error();
     const image=new Image();image.src='data:image/jpeg;base64,'+frame.jpeg;await image.decode();if(generation!==mine)return;
     canvas.width=frame.width;canvas.height=frame.height;ctx.drawImage(image,0,0);ctx.fillStyle='#000a';ctx.fillRect(0,0,canvas.width,48);ctx.font='20px sans-serif';ctx.fillStyle='#fff';
     ctx.fillText(frame.source==='demo'?'DEMO · '+t('mediaDemo'):t('mediaRoad'),14,30);
     if(typeof frame.hud?.speed_kph==='number')ctx.fillText(Math.round(frame.hud.speed_kph)+' km/h',14,canvas.height-18);
     last=performance.now();cursor=mediaCursor(frame);say(frame.source==='demo'?'mediaDemo':'mediaRoad');
    }else if(performance.now()-last>3000){clearPicture();stopRecording();say('stale');}
   }
  }catch(e){if(generation!==mine)return;clearPicture();stopRecording();say(e.status===404?'mediaUpgrade':'networkError');if([401,403,404].includes(e.status)){stop();say(e.status===404?'mediaUpgrade':'expired');return;}}
  if(generation===mine&&active)timer=setTimeout(()=>poll(mine),750);
 }
 return {open,close,translate(){root?.querySelectorAll('[data-media-i18n]').forEach(n=>n.textContent=t(n.dataset.mediaI18n));if(canvas)canvas.setAttribute('aria-label',t('mediaTitle'));}};
}
