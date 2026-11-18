"""Short, same-boot accumulation of static geometry only, in the latest ego frame."""

import math


def recent_geometry(current, history):
  now = current["scene"]
  origin = now["fix"]
  if not now["calibrated"] or not origin or origin["heading"] is None:
    return []
  yaw = math.radians(origin["heading"])
  c, s = math.cos(yaw), math.sin(yaw)
  observed = []
  last = now["eof"]
  for item in history:
    scene = item["scene"]
    fix = scene["fix"]
    age = (now["eof"] - scene["eof"]) / 1e9
    if item["boot"] != current["boot"] or not 0 < age <= 6 or not 0 < last - scene["eof"] <= 2_000_000_000:
      break
    last = scene["eof"]
    if not scene["calibrated"] or not fix or fix["heading"] is None:
      break
    de = (fix["lon"] - origin["lon"]) * 111320 * math.cos(math.radians(origin["lat"]))
    dn = (fix["lat"] - origin["lat"]) * 111320
    if math.hypot(de, dn) > 120:
      break
    dyaw = math.radians(fix["heading"] - origin["heading"])
    cd, sd = math.cos(dyaw), math.sin(dyaw)
    for line in scene["lines"]:
      points = []
      for x, y, _ in line["xyz"]:
        forward = dn * c + de * s + x * cd - y * sd
        right = de * c - dn * s + x * sd + y * cd
        if -30 <= forward <= 80 and abs(right) <= 30:
          points.append([round(forward, 2), round(right, 2)])
      if len(points) >= 2:
        observed.append(dict(source_frame=scene["frame"], age_s=round(age, 2), kind=line["kind"], xy=points))
  return observed
