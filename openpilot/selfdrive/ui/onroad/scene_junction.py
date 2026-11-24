"""Project connected, ground-level roads from the selected offline OSM map for display only."""
from collections import defaultdict
from functools import lru_cache
import math

import numpy as np

from openpilot.selfdrive.navigation.helpers import latest_gps_source
from openpilot.selfdrive.navigation.renderer import MapRenderer, Position, SIZE, METERS_PER_PIXEL, FORWARD_OFFSET, project
from openpilot.selfdrive.navigation.shortbread import ShortbreadTiles, local_source


@lru_cache(maxsize=1)
def renderer_for(source):
  return MapRenderer(ShortbreadTiles(*source))


def junction_arms(segments):
  # Only shared vector vertices form a junction. A visual crossing of two lines does not.
  graph = defaultdict(set)
  for start, end in segments:
    a, b = (tuple(round(float(v), 2) for v in p) for p in (start, end))
    if a == b:
      continue
    graph[a].add(b)
    graph[b].add(a)
  for node in sorted((p for p in graph if abs(p[0]) <= 9 and 5 <= p[1] <= 65 and len(graph[p]) >= 3),
                     key=lambda p: math.hypot(*p)):
    branches, directions = [], []
    for nxt in sorted(graph[node]):
      line = [node]
      prev, cur, length = node, nxt, 0.
      while cur not in line and len(line) < 16:
        delta = (cur[0]-prev[0], cur[1]-prev[1])
        dist = math.hypot(*delta)
        scale = min(1., (32-length)/dist)
        line.append((prev[0]+scale*delta[0], prev[1]+scale*delta[1]))
        length += scale*dist
        if length >= 31.99 or len(graph[cur]) != 2:
          break
        prev, cur = cur, next(p for p in graph[cur] if p != prev)
      if length >= 3:
        dx, dz = line[-1][0]-node[0], line[-1][1]-node[1]
        directions.append(math.atan2(dx, dz))
        branches.append(line)
    # Require a distinct approach arm pointing toward ego, plus two other arms.
    distinct = []
    for angle in directions:
      if all(math.cos(angle-a) < .94 for a in distinct):
        distinct.append(angle)
    if len(distinct) >= 3 and any(math.cos(a) < -.75 for a in distinct):
      return branches[:8]
  return []


class JunctionView:
  def __init__(self):
    self.bearing = self.parked_at = self.last_position = None

  def update(self, sm, eof):
    service = latest_gps_source(sm)
    if service is None or abs(sm.logMonoTime[service]*1e-9-eof) > .4:
      return []
    gps = sm[service]
    if not 0 < gps.horizontalAccuracy <= 5:
      return []
    if gps.speed >= 1.5 and 0 < gps.bearingAccuracyDeg <= 12:
      self.bearing, self.parked_at = gps.bearingDeg, eof
      self.last_position = gps.latitude, gps.longitude
    elif (self.bearing is None or not 0 <= eof-self.parked_at < 90 or not sm.valid['carState'] or not sm.alive['carState']
          or not sm['carState'].canValid or sm['carState'].gearShifter != 'drive' or not sm['carState'].standstill or gps.speed > 1.
          or math.hypot((gps.latitude-self.last_position[0])*111320,
                        (gps.longitude-self.last_position[1])*111320*math.cos(math.radians(gps.latitude))) > 5):
      return []
    return map_arms(gps, self.bearing)


def map_arms(gps, bearing):
  source = local_source(gps)
  if not source:
    return []
  renderer = renderer_for(source)
  position = Position(gps.latitude, gps.longitude, bearing)
  tiles, complete = renderer.view_tiles(position.longitude, position.latitude)
  if not complete:
    return []
  segments = []
  for x,y in tiles:
    roads = renderer.roads(x,y)
    if roads is None:
      continue
    start, end, _, levels, _ = roads
    def local(points):
      pix = project(points[levels == 0], position) - SIZE/2
      return pix * (METERS_PER_PIXEL, -METERS_PER_PIXEL) + (0, FORWARD_OFFSET)
    a,b = local(start), local(end)
    keep = (np.minimum(a[:,1], b[:,1]) < 110) & (np.maximum(a[:,1],b[:,1]) > -35)
    keep &= (np.minimum(a[:,0], b[:,0]) < 55) & (np.maximum(a[:,0],b[:,0]) > -55)
    segments.extend(zip(a[keep], b[keep], strict=True))
  return junction_arms(segments)
