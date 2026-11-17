// Cockpit is a presentation override in its dedicated frame, never a saved
// preference. Preserve explicit BEV; regular web/CarrotAssist use their setting.
export function visionPresentation(target){
  const saved=target.CarrotWebSettingsState?.vision_presentation;
  return target.document?.body?.dataset?.cockpitPanel==='vision'
    ? saved==='bev'?'bev':'tesla'
    : saved;
}
