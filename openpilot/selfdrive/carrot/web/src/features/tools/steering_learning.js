const API = '/api/device/steering_learning';
const FALLBACK = {
  title: 'Steering learning progress', delay: 'Steering delay learning', torque: 'Steering torque learning',
  progress: 'Data progress', live: 'Live data', stale: 'Data expired (last received)',
  cached: 'Last saved record (not live)', unavailable: 'No learning data available',
  valid: 'Verified', learning: 'Collecting data', invalid: 'Estimate not verified',
  unsupported: 'Live torque tuning is not used', applied: 'Selected delay', estimate: 'Candidate delay',
  blocks: 'Valid data blocks', factor: 'Selected acceleration factor', friction: 'Selected friction compensation',
  samples: 'Collected samples', custom: 'Custom tuning is active; learned values do not override it.',
  help: 'Progress measures data coverage, not driving time. Similar straight-road samples may not advance it. This view does not reset or change tuning.',
  connection: 'Connection interrupted; showing previous data.',
};
const text = key => globalThis.getUIText?.(`steering_learning_${key}`, FALLBACK[key]) || FALLBACK[key] || key;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = (value, digits=0) => typeof value === 'number' && Number.isFinite(value) ? value.toFixed(digits) : '—';

export function expireSnapshot(snapshot) {
  return Object.fromEntries(['delay','torque'].map(key => {
    const state = snapshot?.[key] || {source:'unavailable',status:'unavailable',progress:null};
    return [key,{...state,source:state.source==='live' ? 'stale' : state.source}];
  }));
}

export function learningHtml(snapshot, disconnected=false) {
  const parts = [];
  if (disconnected) parts.push(`<p role="status">${esc(text('connection'))}</p>`);
  for (const key of ['delay','torque']) {
    const state = snapshot?.[key] || {source:'unavailable',status:'unavailable',progress:null};
    const progress = typeof state.progress === 'number' && Number.isFinite(state.progress) && state.progress>=0 && state.progress<=100
      ? state.progress : null;
    const row = (label,value) => `<div class="steering-learning__row"><dt>${esc(text(label))}</dt><dd>${esc(value)}</dd></div>`;
    parts.push(`<section class="steering-learning__section" data-source="${esc(state.source)}"><h3>${esc(text(key))}</h3>
      <p class="steering-learning__source">${esc(text(state.source))}</p>
      <p>${esc(text('progress'))}: <strong>${progress===null?'—':`${number(progress)}%`}</strong> · ${esc(text(state.status))}</p>
      ${progress===null?'':`<progress max="100" value="${progress}" aria-label="${esc(text(key)+' · '+text('progress'))}"></progress>`}`);
    if (state.custom) parts.push(`<p>${esc(text('custom'))}</p>`);
    if (state.source !== 'unavailable') {
      parts.push('<dl>');
      if (key==='delay') parts.push(row('applied',number(state.applied,3)+' s'),row('estimate',number(state.estimate,3)+' s'),row('blocks',number(state.blocks)));
      else parts.push(row('factor',number(state.factor,3)),row('friction',number(state.friction,4)),row('samples',number(state.samples)));
      parts.push('</dl>');
    }
    parts.push('</section>');
  }
  parts.push(`<p class="steering-learning__help">${esc(text('help'))}</p>`);
  return parts.join('');
}

export async function openSteeringLearning() {
  let stopped=false, inFlight=false, timer=null, expiry=null, controller=null, last=null;
  const done=globalThis.appAlert('',{title:text('title'),html:true,
    messageHtml:`<div class="steering-learning" data-steering-learning>${learningHtml(null)}</div>`});
  const root=document.querySelector('[data-steering-learning]');
  if (!root) return done;
  async function refresh() {
    clearTimeout(timer);
    if (stopped || inFlight || !root.isConnected || document.hidden) return;
    inFlight=true;
    const started=performance.now();
    const requestController=new AbortController();
    controller=requestController;
    const timeout=setTimeout(()=>requestController.abort(),5000);
    try {
      const response=await fetch(API,{cache:'no-store',credentials:'same-origin',signal:controller.signal});
      if (!response.ok) throw new Error('status unavailable');
      const snapshot=await response.json();
      if (snapshot.ok!==true) throw new Error('status unavailable');
      const transit=(performance.now()-started)/1000;
      for (const key of ['delay','torque']) {
        const state=snapshot[key];
        if (state?.source==='live' && typeof state.ageSeconds==='number' && state.ageSeconds+transit>=2)
          state.source='stale';
      }
      last=snapshot;
      if (!stopped && root.isConnected) root.innerHTML=learningHtml(snapshot);
      clearTimeout(expiry);
      const remaining=['delay','torque'].filter(key=>snapshot[key]?.source==='live')
        .map(key=>Math.max(0,2000-(snapshot[key].ageSeconds||0)*1000-transit*1000));
      if (remaining.length) expiry=setTimeout(()=>{
        if (!stopped && root.isConnected) {last=expireSnapshot(last);root.innerHTML=learningHtml(last,true);}
      },Math.min(...remaining));
    } catch (_) {
      if (!stopped && root.isConnected) {last=expireSnapshot(last);root.innerHTML=learningHtml(last,true);}
    } finally {
      clearTimeout(timeout);
      controller=null;
      inFlight=false;
      if (!stopped && root.isConnected && !document.hidden) timer=setTimeout(refresh,1000);
    }
  }
  const visible=()=>{if(!document.hidden) refresh();else {clearTimeout(timer);controller?.abort();}};
  document.addEventListener('visibilitychange',visible);
  const language=()=>{if(root.isConnected)root.innerHTML=learningHtml(last);};
  window.addEventListener('carrot:languagechange',language);
  refresh();
  try {await done;} finally {
    stopped=true;clearTimeout(timer);clearTimeout(expiry);controller?.abort();
    document.removeEventListener('visibilitychange',visible);
    window.removeEventListener('carrot:languagechange',language);
  }
}
