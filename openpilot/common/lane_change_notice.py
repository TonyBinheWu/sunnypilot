"""Presentation of model/FSM notices. Never an admission or signal command."""
import math


def direction_name(value):
  text = str(value)
  return text if text in ('left', 'right') else {'1': 'left', '2': 'right'}.get(text, '')


def notice_state(meta):
  direction = direction_name(getattr(meta, 'laneChangeDirection', 'none'))
  phase = str(getattr(meta, 'laneChangeState', 'off'))
  phase = {'1': 'preLaneChange', '2': 'laneChangeStarting', '3': 'laneChangeFinishing'}.get(phase, phase)
  if direction and phase in ('laneChangeStarting', 'laneChangeFinishing'):
    return 'changing', direction
  prepared_direction = direction_name(getattr(meta, 'indicatorPrepareDirection', 'none'))
  source = str(getattr(meta, 'indicatorPrepareSource', ''))
  kind = {'forecast_desire': 'forecast', 'forecast_path': 'forecast', 'model_desire': 'forecast',
          'model_path': 'forecast', 'navigation_exit': 'exit', 'lane_completed': 'completed',
          'lane_cancelled': 'cancelled', 'lane_unverified': 'unverified'}.get(source)
  if kind in ('completed', 'cancelled', 'unverified') and prepared_direction:
    return kind, prepared_direction
  if phase == 'preLaneChange' and source == 'lane_waiting_driver':
    return None
  if direction and phase == 'preLaneChange':
    return 'prepare', direction
  return (kind, prepared_direction) if kind and prepared_direction else None


def fresh_notice(sm, now):
  try:
    if not all(sm.valid[s] and sm.alive[s] and 0 <= now - sm.recv_time[s] < .5
               for s in ('modelV2', 'carState', 'carControl', 'selfdriveState')):
      return None
    cs = sm['carState']
    if (not sm['carControl'].latActive or not cs.canValid or cs.canTimeout or str(cs.gearShifter) != 'drive' or
        not math.isfinite(cs.vEgo) or cs.vEgo < 30 / 3.6 or str(sm['selfdriveState'].alertSize) != 'none'):
      return None
    value = notice_state(sm['modelV2'].meta)
    if value and value[0] in ('forecast', 'exit') and cs.steeringPressed:
      return None
    return value
  except (AttributeError, KeyError, TypeError, ValueError):
    return None


TITLES = {
  ('forecast', 'left'): 'Model anticipates a left lane change',
  ('forecast', 'right'): 'Model anticipates a right lane change',
  ('prepare', 'left'): 'Prepare to change left', ('prepare', 'right'): 'Prepare to change right',
  ('changing', 'left'): 'Left lane-change procedure active', ('changing', 'right'): 'Right lane-change procedure active',
  ('exit', 'left'): 'Left exit ahead', ('exit', 'right'): 'Right exit ahead',
  ('completed', 'left'): 'Left lane change completed', ('completed', 'right'): 'Right lane change completed',
  ('cancelled', 'left'): 'Left lane change cancelled', ('cancelled', 'right'): 'Right lane change cancelled',
  ('unverified', 'left'): 'Left lane change ended; completion unconfirmed',
  ('unverified', 'right'): 'Right lane change ended; completion unconfirmed',
}
