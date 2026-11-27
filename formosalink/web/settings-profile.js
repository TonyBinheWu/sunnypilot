import {controlValue} from './settings-edits.js?v=0.9.2';

const format = 'FormosaLink.settings';
const limit = 128 * 1024;
const scalar = v => ['boolean','string','number'].includes(typeof v) && (typeof v !== 'number' || Number.isFinite(v));
const modelSlot = key => key.replace(/^(DrivingModel(?:Small|Big))Page\d+$/, '$1');
const isModel = key => /^DrivingModel(?:Small|Big)$/.test(key);

function portable(entry) {
  return entry.widget !== 'info' && entry.widget !== 'navigation' && entry.key !== 'DrivingModelAction' &&
    !['NavDestination','FormosaLinkEnabled','FormosaLinkRemoteSettings','FormosaLinkTripConsent'].includes(entry.key);
}
export function exportProfile(snapshot) {
  const values = Object.create(null);
  for (const entry of snapshot.catalog || []) {
    if (!portable(entry)) continue;
    const key = modelSlot(entry.key), value = snapshot.values[entry.key];
    if (scalar(value) && (!Object.hasOwn(values,key) || isModel(key) && value !== '')) values[key] = value;
  }
  return JSON.stringify({format,version:1,values}, null, 2);
}
export function readProfile(text) {
  if (typeof text !== 'string' || new TextEncoder().encode(text).length > limit) throw Error('profileInvalid');
  let data;
  try { data = JSON.parse(text); } catch { throw Error('profileInvalid'); }
  if (data?.format !== format || data.version !== 1 || !data.values || typeof data.values !== 'object' || Array.isArray(data.values)) throw Error('profileInvalid');
  const entries = Object.entries(data.values);
  if (entries.length > 256 || entries.some(([k,v]) => !/^[A-Z][A-Za-z0-9_]{0,95}$/.test(k) || !scalar(v) || typeof v === 'string' && v.length > 4096)) throw Error('profileInvalid');
  return data.values;
}
export function profilePlan(values, snapshot) {
  return Object.entries(values).map(([key,value]) => {
    const entries = snapshot.catalog.filter(e => portable(e) && modelSlot(e.key) === key);
    const entry = entries.find(e => controlValue(e,value) === value);
    const current = entries.map(e => snapshot.values[e.key]).find(v => isModel(key) ? !!v : v !== undefined) ?? snapshot.values[entries[0]?.key];
    let status = 'different';
    if (!entries.length) status = 'unsupported';
    else if (current === value) status = 'same';
    else if (!entry) status = 'unsupported';
    else if (!entry.enabled) status = 'locked';
    return {key,value,current,status,entry:entry || entries[0]};
  });
}
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

export async function restoreProfile(values, {read,write,active,update,pause=delay}) {
  const applied = new Set();
  const initial = await read();
  const session = initial.snapshot?.session;
  let waitingForModel = false, modelWaitStart = 0;
  while (active()) {
    const state = await read(), snap = state.snapshot;
    if (!active()) break;
    if (!state.fresh || !snap?.offroad || !snap.remote_enabled || snap.session !== session) throw Error('profileStopped');
    const plan = profilePlan(values,snap);
    if (waitingForModel) {
      const result = JSON.parse(snap.info?.model_manager || '{}');
      if (['failed','cancelled','refresh_failed'].includes(result.status)) throw Error('profileStopped');
      const lastModel = [...applied].filter(isModel).at(-1);
      if (plan.find(row=>row.key===lastModel)?.status !== 'same') {
        if (Date.now()-modelWaitStart > 15*60*1000) throw Error('profileStopped');
        await pause(1500); continue;
      }
      waitingForModel = false;
    }
    const next = plan.filter(r=>r.status==='different' && !applied.has(r.key)).sort((a,b)=>Number(isModel(a.key))-Number(isModel(b.key)))[0];
    const blocked = plan.filter(r=>!applied.has(r.key) && ['unsupported','locked'].includes(r.status));
    if (!next) return {applied:applied.size,skipped:blocked.length};
    if (state.commands?.some(c=>['queued','delivered'].includes(c.status))) throw Error('profileBusy');
    const posted = await write({key:next.entry.key,value:next.value,session,expected_revision:snap.revision});
    if (!posted?.id) throw Error('profileStopped');
    let receipt = posted;
    for (let n=0; ['queued','delivered'].includes(receipt?.status) && n<40 && active(); n++) {
      await pause(800);
      const refreshed = await read();
      receipt = refreshed.commands?.find(c=>c.id===posted.id) || receipt;
    }
    if (receipt.status !== 'applied') throw Error('profileStopped');
    applied.add(next.key);
    update(applied.size,next);
    if (isModel(next.key)) { waitingForModel=true; modelWaitStart=Date.now(); }
  }
  throw Error('profileStopped');
}

export function profileView(parent, {getState,api,path,active,model,t,el,label}) {
  const snapshot = getState()?.snapshot;
  if (!snapshot) return;
  const card = el('section',undefined,'workspace-card profile-card');
  const out = el('button',t('profileExport')), pick = el('button',t('profileImport'));
  for (const button of [out,pick]) button.type='button';
  const file = el('input'); file.type='file'; file.accept='.json,application/json'; file.hidden=true;
  const status = el('p',model.message || '', 'profile-message'); status.setAttribute('role','status');
  const actions = el('div',undefined,'profile-actions'); actions.append(out,pick,file);
  const preview = el('div'); card.setAttribute('aria-label',t('section_profiles'));
  card.append(el('p',t('profileHelp')),actions,preview,status); parent.append(card);
  function show(text) { model.message=text; status.textContent=text; }
  function render() {
    pick.disabled = model.running;
    preview.replaceChildren();
    if (!model.values) return;
    const state=getState(), plan=profilePlan(model.values,state.snapshot);
    const list=el('dl',undefined,'profile-diff');
    for (const r of plan.filter(r=>r.status!=='same')) {
      const showValue=v=>{
        if (typeof v==='boolean') return t(v?'profileOn':'profileOff');
        const option=r.entry?.options?.find(o=>o.value===v);
        return option?label(option.label):String(v??'—');
      };
      list.append(el('dt',r.entry?label(r.entry.title):r.key),el('dd',r.status==='different'?showValue(r.current)+' → '+showValue(r.value):t('profile_'+r.status)));
    }
    const changed=plan.filter(r=>r.status==='different').length;
    const apply=el('button',t('profileApply')+' ('+changed+')','primary');
    apply.type='button'; apply.disabled=!changed || !state.fresh || !state.snapshot.offroad || !state.snapshot.remote_enabled || model.running;
    apply.onclick=async()=>{
      if(model.running || !active()) return;
      model.running=true;
      show(t('profileWorking')); render();
      try {
        const result=await restoreProfile(model.values,{read:()=>api(path),write:c=>api(path,c),active,update:(n,r)=>show(t('profileWorking')+' '+n+' · '+label(r.entry.title))});
        show(t('profileApplied')+' '+result.applied+' · '+t('profileSkipped')+' '+result.skipped);
        model.values=null;
      } catch(e){show(t(e.message==='profileBusy'?'profileBusy':'profileStopped'));}
      finally {model.running=false;if(active())model.redraw?.();}
    };
    preview.append(el('p',changed?t('profileReview'):t('profileNoChanges')),list,apply);
  }
  out.onclick=()=>{
    const data=exportProfile(getState().snapshot);
    if (window.CcncFiles) {window.CcncFiles.save(data);return;}
    const url=URL.createObjectURL(new Blob([data],{type:'application/json'}));
    const link=el('a'); link.href=url;link.download='FormosaLink-settings.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1500);
  };
  pick.onclick=()=>{
    if (!window.CcncFiles) {file.click();return;}
    window.ccncImport=text=>{
      if (!active()) return;
      try {model.values=readProfile(text);show('');} catch {model.values=null;show(t('profileInvalid'));}
      model.redraw?.();
    };
    window.CcncFiles.open();
  };
  file.onchange=async()=>{
    const source=file.files[0]; if(!source) return;
    try { if(source.size>limit) throw Error(); model.values=readProfile(await source.text()); show(''); }
    catch {model.values=null;show(t('profileInvalid'));}
    file.value=''; if(active()) model.redraw?.();
  };
  render();
}
