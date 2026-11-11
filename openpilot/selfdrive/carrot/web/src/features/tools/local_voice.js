import { driveAccessEnabled, executeDriveCommand } from './assistant_drive.js';
import { assignSpokenSetting } from './spoken_setting.js';

// The Android wrapper calls this on the verified, visible device page. No relay/account is involved.
export function createLocalVoice(openSetting, driveEnabled, drive, now = Date.now, assign = assignSpokenSetting, wait = ms => new Promise(resolve => setTimeout(resolve, ms))) {
  let current = null, lastDrive = -Infinity;
  const recent = new Map();
  function start(id, expires, run) {
    if (document.hidden || !/^[A-Za-z0-9_-]{43}$/.test(id) || !Number.isFinite(expires) ||
        expires <= now() || expires - now() > 5000) return false;
    for (const [key, prior] of recent) if (prior.expires <= now()) recent.delete(key);
    if (recent.has(id)) return true;
    if (current && !current.status) return false;
    const request = { id, expires, status: '' };
    current = request;
    recent.set(id, request);
    run().then(status => { request.status = status; }, () => { request.status = 'unverified'; });
    return true;
  }
  return Object.freeze({
    findSettings(query, id, expires) {
      if (typeof query !== 'string' || !query.trim() || query.length > 80) return false;
      return start(id, expires, async () => await globalThis.findPhoneSettings(query, id) || 'unavailable');
    },
    setResultValue(searchId, position, value, language, id, expires) {
      if (!/^[A-Za-z0-9_-]{43}$/.test(searchId) || !Number.isInteger(position) || position < 1 ||
          !Number.isSafeInteger(value)) return false;
      return start(id, expires, async () => {
        const selected = () => globalThis.phoneSearchResultName(searchId, position);
        const name = selected();
        if (!name) return { status: 'no_result' };
        return assign(name, value, id, expires, { selected, language });
      });
    },
    setValue(name, value, id, expires) {
      if (typeof name !== 'string' || !name.trim() || name.length > 100 || !Number.isSafeInteger(value)) return false;
      return start(id, expires, () => assign(name, value, id, expires));
    },
    cruise(action, value, id, expires) {
      if (!['speed_up', 'speed_down', 'speed_set'].includes(action)) return false;
      if (action === 'speed_up' ? value !== null : !Number.isSafeInteger(value) || value < 1 || value > 199) return false;
      return start(id, expires, async () => {
        const result = (status, extra = {}) => ({ kind: 'cruise', status, ...extra });
        const usable = () => !document.hidden && driveEnabled() && now() < expires;
        if (!driveEnabled()) return result('permission');
        if (!usable()) return result('unverified');
        if (now() - lastDrive < 10000) return result('duplicate');
        lastDrive = now();
        // Exactly one execution. Subsequent calls only read that same request's status.
        let reply = await drive({ id, action, ...(value === null ? {} : { value }), expires_at: expires, operation: 'execute' });
        for (let attempt = 0; attempt < 6 && ['waiting', 'running'].includes(reply?.result?.status); attempt++) {
          await wait(120);
          if (!usable()) return result('unverified');
          reply = await drive({ id, expires_at: expires, operation: 'status' });
        }
        if (!usable()) return result('unverified');
        const feedback = reply?.result;
        if (!feedback || feedback.id !== id) return result('unverified');
        if (['applied', 'unchanged'].includes(feedback.status)) {
          if (!Number.isFinite(feedback.current) || feedback.current < 1 || feedback.current > 199) return result('unverified');
          return result(feedback.status, { current: feedback.current });
        }
        const status = ['waiting', 'running', 'rejected', 'expired', 'cancelled', 'interrupted'].includes(feedback.status) ? feedback.status : 'unverified';
        return result(status);
      });
    },
    start(action, id, expires) {
      if (!['lane_left', 'lane_right', 'blinker_settings'].includes(action)) return false;
      return start(id, expires, async () => {
        if (action === 'blinker_settings') return await openSetting('AutoBlinkerControl') === 'opened' ? 'opened' : 'unavailable';
        if (!driveEnabled()) return 'permission';
        if (now() - lastDrive < 10000) return 'duplicate';
        lastDrive = now();
        const reply = await drive({ id, action, expires_at: expires, operation: 'execute' });
        return reply?.result?.status || 'unverified';
      });
    },
    result(id) { return (recent.get(id) || (current?.id === id ? current : null))?.status ?? 'unverified'; },
  });
}

export const localVoice = createLocalVoice(name => globalThis.openAssistantSetting(name), driveAccessEnabled, executeDriveCommand);
