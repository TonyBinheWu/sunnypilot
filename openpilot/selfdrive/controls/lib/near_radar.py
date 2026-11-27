"""Low-speed vetoes from fresh, radar-associated Carrot leads in drive gear."""
import math
import time

MAX_SPEED = 15 / 3.6
FRESH_NS = 200_000_000


def boot_time_ns():
  return time.clock_gettime_ns(getattr(time, 'CLOCK_BOOTTIME', time.CLOCK_MONOTONIC))


def healthy(sm, now):
  radar = sm['radarState']
  err = radar.radarErrors
  return (sm.all_checks(['radarState', 'carState']) and sm['carState'].canValid and
          str(sm['carState'].gearShifter) == 'drive' and 0 < sm['carState'].vEgo <= MAX_SPEED and
          all(0 < t <= now and now-t <= FRESH_NS for t in
              (sm.logMonoTime['radarState'], sm.logMonoTime['carState'], radar.mdMonoTime, radar.carStateMonoTime)) and
          not (err.canError or err.radarFault or err.wrongConfig or err.radarUnavailableTemporary))


def near_track(lead, max_distance):
  return (lead.status and lead.radar and lead.radarTrackId >= 0 and
          math.isfinite(lead.yRel) and math.isfinite(lead.vRel) and .1 < lead.dRel <= max_distance)


def occupied_side(sm, side, now):
  """Evaluate the side selected by radard. Missing range never establishes clearance."""
  if side not in ('left', 'right') or not healthy(sm, now):
    return None
  cs, radar = sm['carState'], sm['radarState']
  leads = radar.leadsLeft if side == 'left' else radar.leadsRight
  return bool(getattr(cs, side+'Blindspot') or any(near_track(p, 6.) and abs(p.yRel) <= 3. for p in leads))


class ClosingLead:
  """Three distinct radar publications with the same closing lead inside 2 s."""
  def __init__(self):
    self.reset()

  def reset(self):
    self.stamp, self.track, self.count = 0, -1, 0

  def update(self, sm, now):
    if not healthy(sm, now):
      self.reset()
      return False
    stamp = sm.logMonoTime['radarState']
    lead = sm['radarState'].leadOne
    if not near_track(lead, 7.) or lead.vRel >= -.5 or lead.dRel > -2.*lead.vRel:
      self.reset()
      return False
    if stamp < self.stamp:
      self.reset()
      return False
    if stamp != self.stamp:
      if self.track != lead.radarTrackId or stamp-self.stamp > FRESH_NS:
        self.count = 0
      self.track, self.stamp = lead.radarTrackId, stamp
      self.count = min(3, self.count+1)
    return self.count >= 3
