// The native host opts in only after verifying its current device origin.
// No JavascriptInterface, permissions, driving commands or extra media session.
export function installAndroidVision(target = globalThis) {
  let host = false, dismissed = false, focused = false, manual = false;
  let framing = 'fit';
  const listeners = ['carrot:pagechange', 'carrot:visionchange', 'carrot:visioncontentchange',
    'drive:workspacecontentchange', 'drive:workspacelayoutchange', 'carrot:websettingschange'];
  function sync(nativeHost) {
    if (typeof nativeHost === 'boolean') host = nativeHost;
    const active = target.document?.body?.dataset?.page === 'carrot'
      && target.CarrotVisionContentRuntime?.isActive?.() === true
      && !target.CarrotVisionReplay?.isActive?.() && !target.CarrotMiniHudMode?.isActive?.();
    if (!active) { dismissed = false; manual = false; }
    const setting = target.CarrotWebSettingsState?.vision_fullscreen_default;
    const enabled = setting !== false && setting !== 0 && setting !== '0' && setting !== 'false';
    const next = Boolean(host && active && (enabled || manual) && !dismissed);
    if (next !== focused) {
      if (next) framing = 'fit';
      focused = next;
      target.document.body.classList.toggle('carrot-android-vision', focused);
      target.dispatchEvent?.(new target.CustomEvent('carrot:androidvisionchange'));
      target.dispatchEvent?.(new target.Event('resize'));
    }
    return focused;
  }
  function exit() { dismissed = true; manual = false; sync(); return true; }
  function toggle() { if (focused) exit(); else { dismissed = false; manual = true; sync(); } return true; }
  listeners.forEach(name => target.addEventListener?.(name, () => sync()));
  function setDisplayMode(value) {
    if (!focused || !['fit','normal','crop'].includes(value)) return false;
    framing = value;
    target.dispatchEvent?.(new target.CustomEvent('carrot:androidvisionchange'));
    return true;
  }
  const api = { sync, exit, toggle, isImmersive: () => focused, isHost: () => host,
    displayMode: () => focused ? framing : null, setDisplayMode };
  target.CarrotAndroidVision = api;
  return api;
}
