// Cockpit is a presentation override in its dedicated frame, never a saved
// preference. Preserve explicit BEV; regular web/CarrotAssist use their setting.
export function visionPresentation(target){
  const saved=target.CarrotWebSettingsState?.vision_presentation;
  return target.document?.body?.dataset?.cockpitPanel==='vision'
    ? saved==='bev'?'bev':'tesla'
    : saved;
}
export function cockpitTelemetryStale(target) {
  const source=target?.document?.body?.dataset;
  return source?.cockpitPanel==='vision'&&source.cockpitTelemetryFresh==='false'
    && !target.CarrotVisionReplay?.isActive?.() && target.CarrotVisionReplay?.status?.()?.active!==true;
}
