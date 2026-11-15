import {diagnosticText} from './messages.js';
import {classifyDiagnosticText,createDiagnosticErrors} from './state.js';

const API='/api/device/diagnostics';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function createSelfDiagnostics(target=globalThis) {
  const text=key=>diagnosticText(key,target), errors=createDiagnosticErrors();
  let report=null, received=0, flight=null, timer=null, lastAuto=-Infinity, root=null;
  let visionTimer=null, latestVision=null, visionWaiting=false;
  let busy=false, confirmation=null, message='', input='', guess=null, reportText='', closed=false;
  const document=target.document;
  function notice(){
    const button=document?.getElementById('btnSelfDiagnostics');
    if(button)button.textContent=text('title')+(errors.list().length?` (${errors.list().length})`:'');
    const note=document?.getElementById('selfDiagnosticsNotice');
    if(note){note.hidden=!errors.list().length;note.textContent=text('recent');}
  }
  async function check() {
    if(flight)return flight;
    reportText='';
    const controller=new AbortController(), timeout=target.setTimeout(()=>controller.abort(),7000);
    flight=(async()=>{
      try{
        const response=await target.fetch(API,{cache:'no-store',credentials:'same-origin',signal:controller.signal});
        const value=await response.json();
        if(!response.ok||value.ok!==true||value.version!==1||!Array.isArray(value.checks)||!Array.isArray(value.actions))throw new Error('unavailable');
        report=value;received=Date.now();
      }catch{report=null;received=Date.now();}
      finally{target.clearTimeout(timeout);flight=null;if(root?.isConnected&&!closed)draw();}
      return report;
    })();
    if(root?.isConnected&&!closed)draw();
    return flight;
  }
  function record(value){
    if(!errors.record(value))return;
    notice();
    if(target.document?.hidden||timer||Date.now()-lastAuto<30000)return;
    timer=target.setTimeout(()=>{
      timer=null;if(document?.hidden)return;lastAuto=Date.now();void check();
    },1000);
  }
  function card(code,level='info',evidence){
    const details=evidence&&Object.keys(evidence).length?`<pre>${esc(JSON.stringify(evidence,null,2))}</pre>`:'';
    return `<section class="self-diag__card" data-level="${esc(level)}"><h3>${esc(text(code))}</h3><small>${esc(text('level_'+level))}</small><p>${esc(text(code+'_help'))}</p>${details}</section>`;
  }
  function draw(){
    if(!root?.isConnected||closed)return;
    const list=[...(report?.checks||[])];
    if(visionWaiting)list.unshift({code:'vision_waiting',level:'unknown',evidence:{phase:latestVision?.phase}});
    const button=(key,action=key,disabled=busy)=>`<button class="btn" type="button" data-action="${action}"${disabled?' disabled':''}>${esc(text(key))}</button>`;
    const repairButtons=(report?.actions||[]).filter(action=>['enable_vision','reboot'].includes(action))
      .map(action=>button(action,action,busy||report.repairAllowed!==true)).join('');
    root.innerHTML=`<p>${esc(text('intro'))}</p>
      <div class="self-diag__actions">${button(flight?'checking':'check','check')}${button('refresh')}${button('download')}</div>
      <p class="self-diag__status" role="status" tabindex="-1">${esc(message)}</p>
      ${confirmation?`<div class="self-diag__confirm" role="group"><p>${esc(text(confirmation==='refresh'?'refreshConfirm':'confirm_'+confirmation))}</p>${button('confirm','execute')}${button('cancel','cancel_action')}</div>`:''}
      <p>${esc(text('stamp'))}: ${received?esc(new Date(typeof report?.collectedAt==='number'?report.collectedAt*1000:received).toLocaleTimeString()):'—'}</p>
      ${report?list.map(row=>card(row.code,row.level,row.evidence)).join(''):`<p role="status">${esc(flight?text('checking'):text('offline'))}</p>`}
      ${repairButtons?`<div class="self-diag__actions">${repairButtons}</div><p>${esc(text('park'))}</p>`:''}
      <details><summary>${esc(text('errors'))} (${errors.list().length})</summary><pre>${esc(errors.list().length?JSON.stringify(errors.list(),null,2):text('none'))}</pre></details>
      <label>${esc(text('paste'))}<textarea rows="3" maxlength="800" data-error-text></textarea></label>
      ${button('analyze')}<div data-guess>${guess?`<p>${esc(text('guess'))}</p>${card(guess,'unknown')}`:''}</div>
      <p>${esc(text('setupHelp'))}</p><p>${esc(text('note'))}</p>
      ${reportText?`<label>${esc(text('report'))}<textarea rows="6" readonly data-report-text>${esc(reportText)}</textarea></label>`:''}`;
    const textarea=root.querySelector('[data-error-text]');textarea.value=input;textarea.oninput=()=>{input=textarea.value.slice(0,800);};
    root.querySelectorAll('[data-action]').forEach(button=>{button.onclick=()=>act(button.dataset.action);});
  }
  function reveal(selector){
    const element=root?.querySelector(selector);if(!element)return;
    element.scrollIntoView?.({block:'nearest'});
    (element.querySelector?.('button')||element).focus?.({preventScroll:true});
  }
  async function act(action){
    if(busy||closed)return;
    if(action==='check'){confirmation=null;message='';await check();return;}
    if(action==='cancel_action'){confirmation=null;draw();return;}
    if(action==='analyze'){guess=classifyDiagnosticText(input);message=guess?'':text('unknown');draw();reveal(guess?'[data-guess]':'.self-diag__status');return;}
    if(action==='download'){
      const bundle={format:'carrot-self-diagnostics/v1',time:new Date().toISOString(),report:report?{...report,ticket:undefined}:null,errors:errors.list()};
      if(visionWaiting)bundle.viewer={waiting:true,phase:latestVision?.phase};
      // No pasted text, credentials, raw logs or upload endpoint in this report.
      reportText=JSON.stringify(bundle,null,2);
      try{
        const blob=new Blob([reportText],{type:'application/json'});
        const url=target.URL.createObjectURL(blob), link=document.createElement('a');link.href=url;link.download='carrot-diagnostics.json';link.click();
        target.setTimeout(()=>target.URL.revokeObjectURL(url),30000);
      }catch{}
      message=text('downloaded');draw();reveal('[data-report-text]');return;
    }
    if(['enable_vision','reboot','refresh'].includes(action)){confirmation=action;draw();reveal('.self-diag__confirm');return;}
    if(action!=='execute'||!confirmation)return;
    const chosen=confirmation;confirmation=null;
    if(chosen==='refresh'){target.location.reload();return;}
    if(!report?.ticket||Date.now()-received>60000){message=text('report_expired');draw();reveal('.self-diag__status');return;}
    busy=true;message=text('checking');draw();
    let refreshAfterSuccess=false;
    const controller=new AbortController(), timeout=target.setTimeout(()=>controller.abort(),8000);
    try{
      const response=await target.fetch(API+'/repair',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({ticket:report.ticket,action:chosen}),signal:controller.signal});
      const value=await response.json();
      if(!response.ok||value.ok!==true){message=text(value.error==='report_expired'?'report_expired':['park_required','moving','controls_active','controls_unavailable','vehicle_unavailable'].includes(value.error)?'park':'repair_unconfirmed');}
      else if(['vision_enabled','reboot_requested'].includes(value.result)){message=text(value.result);refreshAfterSuccess=value.result==='vision_enabled';}
      else message=text('repair_unconfirmed');
      // A POST is never retried automatically, even after a lost response.
    }catch{message=text('repair_unconfirmed');}
    finally{target.clearTimeout(timeout);busy=false;if(report)report={...report,ticket:null,actions:[]};if(refreshAfterSuccess)await check();draw();reveal('.self-diag__status');}
  }
  async function open(){
    if(root?.isConnected)return;
    closed=false;confirmation=null;message='';
    const done=target.appAlert('',{title:text('title'),html:true,confirmLabel:text('close'),messageHtml:'<div class="self-diag" data-self-diagnostics></div>'});
    root=document.querySelector('[data-self-diagnostics]');if(!root)return done;
    draw();void check();
    try{await done;}finally{closed=true;root=null;input='';guess=null;reportText='';confirmation=null;}
  }
  function install(){
    target.addEventListener('carrot:languagechange',()=>{notice();draw();});
    target.addEventListener('carrot:diagnosticerror',event=>record(event.detail));
    target.addEventListener('error',()=>record({kind:'script',code:'SCRIPT_ERROR'}));
    target.addEventListener('unhandledrejection',()=>record({kind:'script',code:'UNHANDLED_REJECTION'}));
    target.addEventListener('carrot:visionstatechange',event=>{
      const state=event.detail?.state, wasWaiting=visionWaiting;latestVision=state;
      const waiting=state?.active&&['recovering','first-frame-waiting','track-waiting','rtc-connecting'].includes(state.phase);
      if(!waiting){target.clearTimeout(visionTimer);visionTimer=null;visionWaiting=false;}
      if(state?.active&&state.phase==='failed'){visionWaiting=true;record({kind:'vision',code:'VISION_FAILED'});}
      else if(waiting&&!visionTimer){
        visionTimer=target.setTimeout(()=>{
          visionTimer=null;
          if(!document?.hidden&&latestVision?.active&&['recovering','first-frame-waiting','track-waiting','rtc-connecting'].includes(latestVision.phase)){
            visionWaiting=true;record({kind:'vision',code:'VISION_WAITING'});draw();
          }
        },10000);
      }
      if(wasWaiting!==visionWaiting)draw();
    });
    notice();
  }
  return {open,record,install,check,errors:()=>errors.list()};
}

export function installSelfDiagnostics(target=globalThis){
  if(target.CarrotSelfDiagnostics)return target.CarrotSelfDiagnostics;
  const api=createSelfDiagnostics(target);target.CarrotSelfDiagnostics=api;api.install();return api;
}
