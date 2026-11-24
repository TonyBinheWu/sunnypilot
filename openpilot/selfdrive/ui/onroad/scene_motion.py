"""Display-only ground-plane velocity from consecutive camera observations and measured ego motion."""
from dataclasses import dataclass
import math


@dataclass
class Track:
  kind: str
  forward: float
  right: float
  vf: float = 0.
  vr: float = 0.
  count: int = 0


class SceneMotion:
  def __init__(self):
    self.tracks = []
    self.stamp = self.ego = None

  def update(self, detections, stamp, ego):
    tracks = [Track(*obs) for obs in detections]
    dt = stamp - self.stamp if self.stamp is not None else 0.
    valid = ego is not None and all(math.isfinite(v) for v in ego) and 0 <= ego[0] < 65 and abs(ego[1]) < 1.5
    if valid and self.ego is not None and .08 <= dt <= .65:
      speed, rate = [(a+b)*.5 for a,b in zip(self.ego, ego, strict=True)]
      yaw, travel = rate*dt, speed*dt
      c, s = math.cos(yaw), math.sin(yaw)
      df, dr = (s/rate*speed, (1-c)/rate*speed) if abs(rate) > .0001 else (travel, 0.)
      predictions = []
      candidates = []
      for i, old in enumerate(self.tracks):
        f, r = old.forward-df, old.right-dr
        f, r = c*f+s*r, -s*f+c*r
        vf, vr = c*old.vf+s*old.vr, -s*old.vf+c*old.vr
        predictions.append((f, r, vf, vr))
        for j, new in enumerate(tracks):
          if new.kind != old.kind:
            continue
          lateral = abs(new.right-r-vr*dt)
          distance = math.hypot(new.forward-f-vf*dt, lateral)
          limit = (8 if old.count else 32) * dt + .5 + .015 * new.forward
          if distance <= limit and lateral <= min(limit, 18*dt+1):
            candidates.append((distance, i, j))
      # A crowded or crossing pair with two equally plausible matches gets no heading.
      assigned, consumed = set(), set()
      for distance, i, j in sorted(candidates):
        if i in assigned or j in consumed or any((a == i or b == j) and (a,b) != (i,j) and d < distance+1.
                                                  for d,a,b in candidates):
          continue
        assigned.add(i)
        consumed.add(j)
        old, new = self.tracks[i], tracks[j]
        f, r, vf, vr = predictions[i]
        measured = ((new.forward-f)/dt, (new.right-r)/dt)
        consistent = math.hypot(measured[0]-vf, measured[1]-vr) < 2.5 + .04 * new.forward
        new.count = old.count+1 if consistent else 1
        new.vf, new.vr = ((.5*v+.5*m) if consistent else m for v,m in zip((vf,vr), measured, strict=True))
    self.tracks, self.stamp, self.ego = tracks, stamp, ego if valid else None
    return [(t.kind, t.forward, t.right,
             math.atan2(t.vr, t.vf) if t.count >= 3 and math.hypot(t.vf,t.vr) > 1.2 + .055*t.forward else None)
            for t in tracks]
