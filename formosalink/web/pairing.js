// Pairing credentials stay in the URL fragment and this tab's session storage.
// Never put them in query parameters, cookies, localStorage, analytics or logs.
const KEY = 'formosalink-pending-pair-v1';

export function validatePairing(value, now = Date.now()/1000) {
  if(!value || typeof value!=='object' || Array.isArray(value))return null;
  if(Object.keys(value).sort().join(',')!=='code,expires_at,fingerprint,version')return null;
  if(value.version!==1 || typeof value.code!=='string' || typeof value.fingerprint!=='string' || !/^[A-F0-9]{12}$/.test(value.code) || !/^[a-f0-9]{24}$/.test(value.fingerprint))return null;
  if(typeof value.expires_at!=='number' || !Number.isFinite(value.expires_at) || value.expires_at<=now || value.expires_at>now+900)return null;
  return {version:1,code:value.code,fingerprint:value.fingerprint,expires_at:value.expires_at};
}

export function parsePairingFragment(fragment, now = Date.now()/1000) {
  if(typeof fragment!=='string' || fragment.length>256)return null;
  const params = new URLSearchParams(fragment.replace(/^#/,''));
  if([...params.keys()].sort().join(',')!=='expires,fp,pair')return null;
  return validatePairing({version:1,code:params.get('pair'),fingerprint:params.get('fp'),expires_at:Number(params.get('expires'))},now);
}

export function readPending(storage, now = Date.now()/1000) {
  try{
    const raw=storage.getItem(KEY);
    const value=raw && raw.length<=1024 ? validatePairing(JSON.parse(raw),now) : null;
    if(!value)storage.removeItem(KEY);
    return value;
  }catch{return null;}
}

export function savePending(storage, value) {
  try{storage.setItem(KEY,JSON.stringify(value));return true;}catch{return false;}
}

export function clearPending(storage) {try{storage.removeItem(KEY);}catch{}}
