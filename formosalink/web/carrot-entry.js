// Navigation only: the device's existing local web consent remains authoritative.
export function isCarrotDevice(device) {
  return ['carrot-wip', 'origin/carrot-wip'].includes(device?.snapshot?.metrics?.branch);
}

export function carrotUrl(deviceId, settings = false) {
  return '/api/v1/devices/' + encodeURIComponent(deviceId) + '/carrot/' + (settings ? '?formosa_page=setting' : '');
}

export function settingsStatus(device, snapshot, fresh) {
  if (!snapshot) return 'settingsWaiting';
  if (!fresh) return 'settingsOffline';
  if (!snapshot.offroad) return 'settingsDriving';
  if (isCarrotDevice(device)) return 'carrotSettingsHelp';
  return snapshot.remote_enabled ? 'settingsReady' : 'settingsLocalDisabled';
}
