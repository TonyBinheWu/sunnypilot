const FLAGS = [
  ['selfdriveState', 'enabled', 'replay_event_control_engaged'],
  ['carControl', 'latActive', 'replay_event_lateral_control_on'],
  ['carControl', 'longActive', 'replay_event_longitudinal_control_on'],
  ['carState', 'gasPressed', 'replay_event_accelerator_pressed'],
  ['carState', 'brakePressed', 'replay_event_brake_pressed'],
  ['carState', 'steeringPressed', 'replay_event_steering_override_start'],
  ['carState', 'leftBlinker', 'replay_event_left_blinker'],
  ['carState', 'rightBlinker', 'replay_event_right_blinker'],
  ['carState', 'brakeHoldActive', 'replay_event_brake_hold_on'],
  ['carState', 'parkingBrake', 'replay_event_parking_brake_on'],
  ['carState', 'leftBlindspot', 'replay_event_left_blindspot'],
  ['carState', 'rightBlindspot', 'replay_event_right_blindspot'],
];

export function currentVisionEvents(state = {}, fresh = () => true) {
  const rows = [];
  const sd = state.selfdriveState;
  if (fresh('selfdriveState') && sd && sd.alertSize !== 'none' && sd.alertSize !== 0 && sd.alertSize != null) {
    const text = [sd.alertText1, sd.alertText2].filter(v => typeof v === 'string' && v.trim()).join(' · ').slice(0, 512);
    if (text) rows.push({key:'vision_live_event_alert', text, warning:true});
  }
  for (const [service, field, key] of FLAGS) {
    if (fresh(service) && state[service]?.[field] === true) rows.push({key, text:'', warning:key.includes('blindspot')});
  }
  return rows;
}

export function visionEventSnapshot(target, replay, now, wallNow) {
  const parked = !replay && target.CarrotDeviceRuntimeState?.isOffroad === true && target.CarrotDeviceRuntimeState?.isOnroad !== true;
  const state = parked ? {} : target.CarrotHudState || {};
  const fresh = service => {
    if (!state[service]) return false;
    if (replay) return true;
    const mono = target.CarrotStateReceivedAtMonotonic?.[service];
    const stamp = Number.isFinite(mono) ? mono : target.CarrotStateUpdatedAt?.[service];
    const age = (Number.isFinite(mono) ? now : wallNow) - stamp;
    return Number.isFinite(age) && age >= 0 && age <= 1500;
  };
  return {rows:currentVisionEvents(state, fresh), available:['carState','carControl','selfdriveState'].some(fresh)};
}
