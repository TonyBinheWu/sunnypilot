// Recorded SEI only: no live car data or inference from control labels.
export function sampleAt(samples, seconds) {
  if (!Number.isFinite(seconds) || !Array.isArray(samples)) return null;
  let lo=0,hi=samples.length;
  while(lo<hi){const mid=(lo+hi)>>>1;if(samples[mid].time_s<=seconds)lo=mid+1;else hi=mid;}
  const row=samples[lo-1];
  return row&&seconds-row.time_s<=.100001?row:null;
}

export function attachDrivingSei(video, parent, options={}) {
  const doc=parent.ownerDocument,target=doc.defaultView;
  const text=(key,fallback)=>target.getUIText?.(key,fallback)||fallback;
  const el=(tag,cls,value)=>{const n=doc.createElement(tag);n.className=cls;if(value)n.textContent=value;return n;};
  const panel=el('section','driving-sei'),header=el('div','driving-sei__header');
  const status=el('span','driving-sei__status'),toggle=el('button','driving-sei__toggle'),grid=el('div','driving-sei__grid'),retry=el('button','driving-sei__toggle',text('sei_retry','Retry SEI'));
  panel.setAttribute('aria-label',text('sei_title','Embedded driving data (SEI)'));
  toggle.type='button';toggle.setAttribute('aria-expanded','true');
  retry.type='button';retry.hidden=true;retry.onclick=()=>load();
  header.append(status,retry,toggle);panel.append(header,grid);parent.append(panel);parent.classList.add('has-driving-sei');
  const definitions=[['speed','sei_speed','Speed'],['angle','sei_angle','Steering angle'],['gas','sei_gas','Accelerator'],['brake','sei_brake','Brake'],['assist','sei_assist','Driver assistance'],['acc','sei_acc','ACC']];
  const outputs={};
  for(const [id,key,label] of definitions){const cell=el('div','driving-sei__cell'),caption=el('small','',text(key,label)),value=el('b','','—');cell.append(caption,value);grid.append(cell);outputs[id]=value;}
  let rows=[],state='loading',closed=false,frame=null,abort=new AbortController(),collapsed=Boolean(target.matchMedia?.('(orientation: landscape) and (max-height: 500px)').matches),last='',loadId=0;
  toggle.setAttribute('aria-expanded',String(!collapsed));
  const reserve=()=>{if(options.reserveStage)parent.style.setProperty('--replay-sei-height',`${panel.getBoundingClientRect().height}px`);};
  const unknown=text('sei_unknown','Unknown'),on=text('sei_on','On'),off=text('sei_off','Off');
  const flag=x=>typeof x==='boolean'?(x?on:off):unknown;
  const pedal=x=>typeof x==='boolean'?(x?text('sei_pressed','Pressed'):text('sei_released','Released')):unknown;
  const numeric=(x,scale=1,unit='')=>typeof x==='number'&&Number.isFinite(x)?`${(x*scale).toFixed(1)}${unit}`:unknown;
  function render(time=video.currentTime){
    if(closed)return;
    const row=sampleAt(rows,time),ready=state==='ready';
    panel.dataset.frameId=row?.frame_id??'';panel.dataset.mediaTime=row?.time_s??'';
    retry.hidden=!['busy','unavailable'].includes(state);
    panel.dataset.state=ready&&!row?'gap':state;grid.hidden=collapsed||!ready;
    const message=ready?(row?text('sei_embedded','SEI · recorded driving data'):text('sei_gap','No fresh SEI at this time')):text(`sei_${state}`,state==='no_sei'?'This video has no embedded SEI.':state==='loading'?'Reading embedded SEI…':'SEI unavailable; video playback is still available.');
    status.textContent=message;
    toggle.hidden=!ready;toggle.textContent=collapsed?text('sei_expand','Show data'):text('sei_collapse','Collapse');
    const values={speed:numeric(row?.speed_mps,3.6,' km/h'),angle:numeric(row?.steering_angle_deg,1,'°'),
      gas:`${numeric(row?.gas,100,'%')} · ${pedal(row?.gas_pressed)}`,brake:`${numeric(row?.brake,100,'%')} · ${pedal(row?.brake_pressed)}`,
      assist:`${text('sei_lateral','Lat')} ${flag(row?.lateral_active)} · ${text('sei_longitudinal','Long')} ${flag(row?.longitudinal_active)} · ${text('sei_enabled','Enabled')} ${flag(row?.control_enabled)}`,
      acc:flag(row?.cruise_enabled)};
    const signature=JSON.stringify(values);if(signature!==last){last=signature;for(const [k,v]of Object.entries(values))outputs[k].textContent=v;}
    reserve();
  }
  toggle.onclick=()=>{collapsed=!collapsed;toggle.setAttribute('aria-expanded',String(!collapsed));render();};
  function cancelFrame(){if(frame!==null&&video.cancelVideoFrameCallback)video.cancelVideoFrameCallback(frame);frame=null;}
  function tick(_now,meta){frame=null;render(meta?.mediaTime??video.currentTime);schedule();}
  function schedule(){if(!closed&&!video.paused&&!video.ended&&frame===null&&video.requestVideoFrameCallback)frame=video.requestVideoFrameCallback(tick);}
  const time=()=>{render();schedule();},pause=()=>{cancelFrame();render();};
  const events={timeupdate:time,seeking:time,seeked:time,loadedmetadata:time,play:time,playing:time,pause,ended:pause,emptied:()=>render(-1)};
  for(const [name,fn]of Object.entries(events))video.addEventListener(name,fn);
  const resize=target.ResizeObserver?new target.ResizeObserver(reserve):null;resize?.observe(panel);
  async function load(){
    abort.abort();abort=new AbortController();const controller=abort,id=++loadId;
    let timedOut=false;const timer=target.setTimeout(()=>{timedOut=true;controller.abort();},30000);
    rows=[];state='loading';render();
    try{
      let payload;
      for(let attempt=0;attempt<5;attempt++){
        if(closed||id!==loadId||controller.signal.aborted)return;
        const response=await target.fetch(`/api/dashcam/sei/${encodeURIComponent(options.segment)}`,{signal:controller.signal,cache:'no-store'});
        if(!response.ok)throw Error('SEI HTTP');
        payload=await response.json();if(payload.status!=='busy'||attempt===4)break;
        await new Promise(resolve=>target.setTimeout(resolve,500*2**attempt));
      }
      if(closed||id!==loadId)return;
      state=payload.status||'unavailable';
      rows=state==='ready'&&Array.isArray(payload.samples)?payload.samples.filter(r=>r&&Number.isFinite(r.time_s)).slice(0,6000).sort((a,b)=>a.time_s-b.time_s):[];
      render();schedule();
    }catch(error){if(!closed&&id===loadId&&(timedOut||error.name!=='AbortError')){state='unavailable';render();}}
    finally{target.clearTimeout(timer);}
  }
  load();
  return {panel,render,destroy(){closed=true;abort.abort();cancelFrame();resize?.disconnect();for(const [name,fn]of Object.entries(events))video.removeEventListener(name,fn);panel.remove();parent.classList.remove('has-driving-sei');if(options.reserveStage)parent.style.removeProperty('--replay-sei-height');}};
}

if(typeof window==='object')window.CarrotDrivingSei={attach:attachDrivingSei};
