// Per-account, per-device, in-memory edits. A value match is never a write receipt.
export const pendingEdit = row => !!row && ['sending','queued','delivered','uncertain'].includes(row.status);
export const sameValue = (a,b) => Object.is(a,b);
export function sameSettingValue(key,a,b) {
  if(key!=='NavDestination' || sameValue(a,b))return sameValue(a,b);
  try {
    const left=JSON.parse(a),right=JSON.parse(b);
    return ['latitude','longitude','place_name'].every(k=>sameValue(left[k],right[k])) && Object.keys(left).length===3 && Object.keys(right).length===3;
  }catch{return false;}
}
export function controlValue(entry, raw) {
  if(entry.widget==='navigation') {
    if(typeof raw!=='string' || raw.length>512)return undefined;
    try {
      const v=JSON.parse(raw);
      if(Object.keys(v).sort().join(',')!=='latitude,longitude,place_name' || typeof v.place_name!=='string' || !v.place_name.length || v.place_name.length>120 || /[\x00-\x1f]/.test(v.place_name))return undefined;
      if(!['latitude','longitude'].every(k=>typeof v[k]==='number' && Number.isFinite(v[k]) && Math.abs(v[k])<=(k==='latitude'?90:180)))return undefined;
      return raw;
    }catch{return undefined;}
  }
  if (entry.type==='BOOL') return typeof raw==='boolean' ? raw : undefined;
  if (entry.options) {
    const option=entry.options.find(o=>o.enabled && sameValue(o.value,raw));
    return option?.value;
  }
  if (entry.type==='STRING') return typeof raw==='string' && raw.length<=256 && !/[\x00-\x1f]/.test(raw) ? raw : undefined;
  if (!['number','string'].includes(typeof raw)) return undefined;
  if (typeof raw==='string' && !raw.trim()) return undefined;
  const value=Number(raw);
  if (!Number.isFinite(value) || entry.type==='INT' && !Number.isInteger(value)) return undefined;
  if (!(entry.step>0) || value<entry.min || value>entry.max) return undefined;
  const step=(value-entry.min)/entry.step;
  return Math.abs(step-Math.round(step))<=1e-6 ? value : undefined;
}

export class SettingsEdits {
  constructor() { this.owner=null; this.devices=new Map(); }
  reset() { this.owner=null; this.devices.clear(); }
  scope(owner) { if(this.owner!==owner){this.reset();this.owner=owner;} }
  rows(device) {
    if(!this.devices.has(device))this.devices.set(device,new Map());
    return this.devices.get(device);
  }
  get(device,key) { return this.rows(device).get(key); }
  edit(device,key,value,snapshot) {
    let row=this.get(device,key);
    if(pendingEdit(row))return row;
    if(!row || row.status==='applied') {
      row={base:snapshot.values[key],session:snapshot.session,catalog:snapshot.catalog_revision,status:'draft'};
      this.rows(device).set(key,row);
    }
    row.value=value;
    if(row.status!=='conflict'){row.status='draft';row.reason=null;row.command=null;}
    if(sameSettingValue(key,value,row.base) && row.status==='draft')this.rows(device).delete(key);
    return row;
  }
  discard(device,key) {
    if(!pendingEdit(this.get(device,key)))this.rows(device).delete(key);
  }
  rebase(device,key,snapshot) {
    const row=this.get(device,key),entry=snapshot.catalog.find(e=>e.key===key);
    if(!row || pendingEdit(row) || !entry?.enabled)return false;
    row.base=snapshot.values[key];row.session=snapshot.session;row.catalog=snapshot.catalog_revision;
    row.status='draft';row.reason=null;row.command=null;
    if(sameSettingValue(key,row.value,row.base))this.rows(device).delete(key);
    return true; // User still needs to press Save; never resend automatically.
  }
  begin(device,key,snapshot,now=Date.now()) {
    this.reconcile(device,{snapshot,fresh:true,commands:[]},now);
    const row=this.get(device,key);
    if(!row || !['draft','failed'].includes(row.status) || sameSettingValue(key,row.value,row.base))return null;
    const entry=snapshot.catalog.find(e=>e.key===key);
    const value=entry && controlValue(entry,row.value);
    if(!entry?.enabled || value===undefined)return null;
    row.status='sending';row.reason=null;row.started=now;row.command=null;
    return {key,value,expected_revision:snapshot.revision,session:snapshot.session};
  }
  queued(device,key,result) {
    const row=this.get(device,key);
    if(row?.status!=='sending')return;
    if(typeof result?.id!=='string' || result.status!=='queued'){this.failed(device,key,{});return;}
    row.command=result.id;row.status='queued';
  }
  failed(device,key,error) {
    const row=this.get(device,key);if(!row)return;
    row.reason=error.reason||(error.status>=400&&error.status<500?'write_failed':'receipt_missing');
    row.status=error.reason==='conflict' || error.reason==='wrong_session' ? 'conflict' :
      error.status>=400 && error.status<500 ? 'failed' : 'uncertain';
  }
  reconcile(device,state,now=Date.now()) {
    if(!state.snapshot)return;
    const snapshot=state.snapshot;
    for(const [key,row] of this.rows(device)) {
      const command=row.command && state.commands?.find(c=>c.id===row.command);
      if(command) {
        if(command.status==='applied') {
          row.status='applied';row.reason=null;
          // Keep the receipt badge until the device value changes again.
          if(state.fresh && !sameSettingValue(key,snapshot.values[key],row.value))this.rows(device).delete(key);
          continue;
        }
        row.status=['queued','delivered'].includes(command.status) ? command.status :
          command.reason==='conflict' || command.reason==='wrong_session' ? 'conflict' : 'failed';
        row.reason=command.reason || (command.status==='expired'?'expired':'write_failed');
      }
      if(pendingEdit(row)) {
        // Lost HTTP responses and missing receipts never count as applied.
        if(state.fresh && now-row.started>60000 && !state.commands?.some(c=>['queued','delivered'].includes(c.status))) {
          row.status='conflict';row.reason='receipt_missing';row.command=null;
        } else continue;
      }
      if(row.status==='applied') {
        if(state.fresh && !sameSettingValue(key,snapshot.values[key],row.value))this.rows(device).delete(key);
        continue;
      }
      const entry=snapshot.catalog.find(e=>e.key===key);
      if(state.fresh && (!entry || snapshot.session!==row.session || snapshot.catalog_revision!==row.catalog || !sameSettingValue(key,snapshot.values[key],row.base))) {
        row.status='conflict';row.reason=!entry?'setting_unavailable':'conflict';
      }
    }
  }
}
