"""Read-only perspective display of current model, lead and navigation messages."""

from itertools import chain, islice
from math import isfinite
import json
from pathlib import Path
import time

from openpilot.selfdrive.carrot.server.config import CARROT_WEB_SETTINGS_PATH, WEB_DIR

import numpy as np
import pyray as rl


def fresh(state, service, seconds, now):
  sm = state.sm
  return sm.valid[service] and sm.recv_frame[service] >= state.started_frame and 0 <= now - sm.logMonoTime[service] * 1e-9 < seconds


def road_opening(model):
  """Bracket a possible crossroads using observed widening on both sides of the driving path."""
  if len(model.roadEdges) != 2 or len(model.roadEdgeStds) != 2 or not all(0 <= s < .5 for s in model.roadEdgeStds):
    return None
  grid = np.arange(4., 58., 2.)
  samples = []
  for line in (model.position, model.roadEdges[0], model.roadEdges[1]):
    x, y = np.asarray(line.x), np.asarray(line.y)
    if len(x) != len(y) or len(x) < 5 or not np.isfinite(x).all() or not np.isfinite(y).all() or not (np.diff(x) > 0).all():
      return None
    values = np.interp(grid, x, y, left=np.nan, right=np.nan)
    idx = np.clip(np.searchsorted(x, grid), 1, len(x)-1)
    values[x[idx] - x[idx-1] > 8.] = np.nan
    samples.append(values)
  path, left, right = samples
  margins = np.column_stack((path - left, right - path))
  for i in range(2, len(grid) - 4):
    before = margins[i-2:i]
    if not ((before >= 1.3) & (before <= 10.)).all() or np.max(np.ptp(before, axis=0)) > 1.:
      continue
    base = before.mean(axis=0)
    wide = (margins[i:] - base >= 2.).all(axis=1)
    if not wide[:2].all():
      continue
    ends = np.flatnonzero(~wide)
    if ends.size and 2 <= ends[0] <= 10:
      end = i + ends[0]
      after = margins[end:end+2]
      if len(after) == 2 and (np.abs(after - base) < 1.5).all():
        return float(grid[i]), float(grid[end])
  return None


def vehicle_points(model, radar):
  found = []
  if radar is not None and not any(
    getattr(radar.radarErrors, key) for key in ("canError", "radarFault", "wrongConfig", "radarUnavailableTemporary")
  ):
    for lead in chain(
      (radar.leadOne, radar.leadTwo), islice(radar.leadsCenter, 24), islice(radar.leadsLeft, 24), islice(radar.leadsRight, 24)
    ):
      if lead.status:
        found.append((lead.dRel, -lead.yRel))
  if model is not None:
    for lead in model.leadsV3:
      if lead.prob > 0.5 and len(lead.x) and len(lead.y):
        found.append((lead.x[0], lead.y[0]))
  points = []
  for z, x in found:
    if 1 <= z <= 110 and abs(x) <= 18 and not any(abs(z - a) < 2 and abs(x - b) < 1.2 for a, b in points):
      points.append((z, x))
  return sorted(points, reverse=True)


def tint(rgb, shade=1.0, alpha=255):
  return rl.Color(*(min(255, int(((rgb >> shift) & 255) * shade)) for shift in (16, 8, 0)), alpha)


def rear_points(car, radar):
  points = []
  if car is None or not car.canValid:
    return ()
  for prefix, sign in (("displayRearLeft", -1), ("displayRearRight", 1)):
    d, y = getattr(car, prefix + "Distance", 0), getattr(car, prefix + "Lateral", 0)
    if 0 < d <= 26 and 0 < y <= 13:
      points.append((-d, sign * y))
  if radar is not None and not any(getattr(radar.radarErrors, k) for k in ("canError", "radarFault", "wrongConfig", "radarUnavailableTemporary")):
    for lead in chain((radar.leadOne, radar.leadTwo), radar.leadsCenter, radar.leadsLeft, radar.leadsRight):
      d, y = lead.dRel, -lead.yRel
      if lead.status and d < 0 and lead.radar and -26 <= d < 0 and abs(y) <= 13 and not any(abs(d-a)<2 and abs(y-b)<1.2 for a,b in points):
        points.append((d, y))
  return tuple(points)


def ego_lamps(car, now):
  if car is None or not car.canValid:
    return False, False, False
  phase = getattr(car, "turnLampState", "unknown")
  if phase == "unknown":
    blink = now % 1.0 < 0.5
    return car.brakeLights, car.leftBlinker and blink, car.rightBlinker and blink
  return car.brakeLights, phase in ("left", "both"), phase in ("right", "both")


class RealityScene:
  def __init__(self, style):
    self.style = style
    self.map_input = self.texture = None
    self.next_demand = self.image_time = 0
    self.key = None
    self.faces = []
    self.objects = ()
    self.next_objects = 0.
    self.opening = None
    self.next_style_check = 0
    self.settings_stamp = None
    self.ego_scale = (1, 1, 1)
    try:
      self.vehicle_scales = json.loads((Path(WEB_DIR) / "src/features/cockpit/vehicle_scales.json").read_bytes())
    except (OSError, ValueError):
      self.vehicle_scales = {}

  def update_appearance(self, now):
    if now < self.next_style_check:
      return
    self.next_style_check = now + 2
    path = Path(CARROT_WEB_SETTINGS_PATH)
    try:
      stamp = path.stat().st_mtime_ns
      if stamp != self.settings_stamp:
        settings = json.loads(path.read_bytes())
        self.ego_scale = self.vehicle_scales.get(settings.get("vision_vehicle_model"), (1, 1, 1))
        self.settings_stamp = stamp
    except (OSError, ValueError, AttributeError, TypeError):
      self.ego_scale = (1, 1, 1)
      self.settings_stamp = None

  def draw(self, rect, state, model_only=False):
    now = time.monotonic()
    model_ok = fresh(state, "modelV2", 0.5, now)
    radar_ok = not model_only and fresh(state, "radarState", 0.5, now)
    sm = state.sm
    car_ok = not model_only and fresh(state, "carState", 0.5, now)
    lamps = ego_lamps(sm["carState"] if car_ok else None, now)
    rear = rear_points(sm["carState"] if car_ok else None, sm["radarState"] if radar_ok else None)
    if model_only and model_ok and now >= self.next_objects:
      from openpilot.selfdrive.ui.onroad.scene_objects import read_objects
      self.objects = read_objects(now)
      self.next_objects = now + .1
    elif not model_only or not model_ok:
      self.objects = ()
      self.next_objects = 0.
    self.update_appearance(now)
    key = (
      model_only, self.objects, car_ok, lamps, rear, self.ego_scale,
      sm.recv_frame["modelV2"] if model_ok else -1,
      sm.recv_frame["radarState"] if radar_ok else -1,
      rect.x,
      rect.y,
      rect.width,
      rect.height,
    )
    if key != self.key:
      self.faces = self.geometry(rect, sm["modelV2"] if model_ok else None, sm["radarState"] if radar_ok else None, car_ok, lamps, rear, self.objects, model_only)
      self.key = key
    night = self.style["scene_style"] == 1
    rl.draw_rectangle_gradient_v(
      int(rect.x),
      int(rect.y),
      int(rect.width),
      int(rect.height),
      tint(0x18232F if night else 0xDAE6EB),
      tint(0x34414D if night else 0x788894),
    )
    for vertices, color in self.faces:
      rl.draw_triangle_fan(vertices, len(vertices), color)
    if model_only:
      if self.objects:
        font = max(10, int(rect.height * .025))
        occupied = []
        for kind, z, x in sorted(self.objects, key=lambda obj: obj[1]):
          scale = 740 / (z + 8)
          px = rect.x + rect.width * ((435 + x * scale) / 1000 + self.style["vehicle_x"] / 100)
          py = rect.y + rect.height * ((118 + 2.2 * scale) / 450 + self.style["vehicle_y"] / 100) - font * 1.4
          width = rl.measure_text(kind, font)
          if (rect.x <= px - width/2 and px + width/2 <= rect.x + rect.width and rect.y <= py < rect.y + rect.height - font
              and all(abs(px - ox) > (width + ow)/2 + 2 or abs(py - oy) > font + 2 for ox, oy, ow in occupied)):
            rl.draw_rectangle(int(px - width/2 - 2), int(py - 1), width + 4, font + 2, tint(0x18232F, alpha=210))
            rl.draw_text(kind, int(px - width/2), int(py), font, rl.WHITE)
            occupied.append((px, py, width))
        rl.draw_text("ROAD detector", int(rect.x + rect.width * .03), int(rect.y + rect.height * .79),
                     max(10, int(rect.height * .03)), rl.SKYBLUE)
      if self.opening:
        rl.draw_text(f"Possible junction  {self.opening[0]:.0f} m", int(rect.x + rect.width * .03),
                     int(rect.y + rect.height * .12), max(11, int(rect.height * .033)), rl.SKYBLUE)
      if not model_ok:
        rl.draw_text("modelV2 unavailable", int(rect.x + rect.width * .32), int(rect.y + rect.height * .46),
                     max(13, int(rect.height * .045)), rl.LIGHTGRAY)
      return
    self.draw_map(rect, state, now)
    if fresh(state, "navInstructionCarrot", 2, now):
      instruction = sm["navInstructionCarrot"]
      distance = instruction.maneuverDistance
      direction = {"left": "LEFT", "right": "RIGHT", "slight left": "KEEP LEFT", "slight right": "KEEP RIGHT",
                   "sharp left": "SHARP LEFT", "sharp right": "SHARP RIGHT", "uturn": "U-TURN"}.get(instruction.maneuverModifier)
      if direction and 0 <= distance < 100000:
        label = f"{direction}  {distance:.0f} m" if distance < 1000 else f"{direction}  {distance/1000:.1f} km"
        rl.draw_text(label, int(rect.x + rect.width * .58), int(rect.y + rect.height * .04), max(12, int(rect.height * .042)), rl.SKYBLUE)
    if car_ok:
      car = sm["carState"]
      for active, side in ((car.leftBlindspot, 0.012), (car.rightBlindspot, 0.975)):
        if active:
          rl.draw_rectangle_rec(
            rl.Rectangle(rect.x + rect.width * side, rect.y + rect.height * 0.42, rect.width * 0.012, rect.height * 0.13), tint(0xFFB54E)
          )

  def geometry(self, rect, model, radar, car_ok=False, lamps=(False, False, False), rear=(), objects=(), model_only=False):
    v = self.style
    self.opening = road_opening(model) if model_only and model is not None else None
    faces = []

    # Pull behind the furthest measured rear target, including room for its body.
    setback = max((max(10, abs(x) * 2) - z for z, x in rear), default=0)
    def face(layer, points, color):
      vertices = []
      for x, z, y in points:
        scale = 740 / (z + 8 + setback)
        vertices.append(
          rl.Vector2(
            rect.x + rect.width * ((435 + x * scale) / 1000 + v[layer + "_x"] / 100),
            rect.y + rect.height * ((118 + (4 - y) * scale) / 450 + v[layer + "_y"] / 100),
          )
        )
      a, b, c = vertices[:3]
      if (b.x - a.x) * (c.y - a.y) > (b.y - a.y) * (c.x - a.x):
        vertices.reverse()
      faces.append((vertices, color))

    def ribbon(layer, line, width, alpha):
      previous = None
      width *= v[layer + "_size"] / 100
      color = tint(v[layer + "_color"], alpha=alpha)
      for z, x in zip(line.x, line.y):
        if not (0 <= z <= 110 and abs(x) <= 30):
          previous = None
          continue
        pair = [(x - width / 2, z, 0), (x + width / 2, z, 0)]
        if previous and z > previous[0][1]:
          face(layer, previous + pair[::-1], color)
        previous = pair

    if model is not None:
      if model_only and len(model.roadEdges) == len(model.roadEdgeStds) == 2 and all(0 <= s < .5 for s in model.roadEdgeStds):
        left, right = model.roadEdges
        previous = None
        for zl, xl, zr, xr in zip(left.x, left.y, right.x, right.y):
          if not (0 <= zl <= 110 and 0 <= zr <= 110 and -30 <= xl < xr <= 30):
            previous = None
            continue
          pair = [(xl, zl, 0), (xr, zr, 0)]
          if previous and zl > previous[0][1] and zr > previous[1][1]:
            in_opening = self.opening and self.opening[0] <= (zl + zr) / 2 <= self.opening[1]
            face("lane", previous + pair[::-1], tint(0x466D72 if in_opening else 0x425563))
          previous = pair
      for edge, std in zip(getattr(model, "roadEdges", ()), getattr(model, "roadEdgeStds", ())):
        if 0 <= std < 0.5:
          ribbon("lane", edge, 0.09, 85)
      ribbon("path", model.position, 1.65, 132)
      for line, prob in zip(model.laneLines, model.laneLineProbs):
        if prob > 0.5:
          ribbon("lane", line, 0.12, int(255 * min(prob, 1)))
    vehicles = vehicle_points(model, radar)
    if objects:
      vehicles = [(d, y) for d, y in vehicles if not any(abs(d - od) < 2 and abs(y - oy) < 1.2 for _, od, oy in objects)]
    # Ground positions come from calibrated image detections. Icon dimensions
    # identify the class and are independent of the estimated object distance.
    for kind, z, x in sorted(objects, key=lambda obj: -obj[1]):
      if kind == 'person':
        face('vehicle', [(x-.24,z,0),(x+.24,z,0),(x+.22,z,1.3),(x-.22,z,1.3)], tint(0xFCB971))
        face('vehicle', [(x-.18,z,1.35),(x+.18,z,1.35),(x+.16,z,1.72),(x-.16,z,1.72)], tint(0xFCB971))
      else:
        narrow = kind in ('bicycle', 'motorcycle')
        width, height, length = (.36, 1.3, 1.8) if narrow else (1.2, 2.6, 5.5) if kind in ('bus','truck') else (.88, 1.35, 3.8)
        color = 0xCF9DF6 if narrow else 0x59C5DB
        face('vehicle', [(x-width,z,0),(x+width,z,0),(x+width,z,height),(x-width,z,height)], tint(color,.78))
        face('vehicle', [(x-width,z,height),(x+width,z,height),(x+width,z+length,height),(x-width,z+length,height)], tint(color))
    if car_ok:
      vehicles.append((1.3, 0))  # viewport anchor for the reporting vehicle
    vehicles.extend(sorted(rear, reverse=True))
    ego_index = len(vehicles) - len(rear) - 1
    for index, (z, x) in enumerate(vehicles):
      size = v["vehicle_size"] / 100

      length, width, height = self.ego_scale if car_ok and index == ego_index else (1, 1, 1)

      def panel(vertices, color):
        face("vehicle", [(x + a * size * width, z + b * size * length, y * size * height) for a, b, y in vertices], color)

      body = v["vehicle_color"]
      panel([(-0.93, 0, 0.16), (0.93, 0, 0.16), (0.94, 0, 0.82), (-0.94, 0, 0.82)], tint(body, 0.75))
      panel([(-0.94, 0, 0.82), (0.94, 0, 0.82), (0.88, 4, 0.76), (-0.88, 4, 0.76)], tint(body))
      side = 1 if x < 0 else -1
      panel([(side * 0.93, 0, 0.16), (side * 0.9, 4, 0.16), (side * 0.88, 4, 0.76), (side * 0.94, 0, 0.82)], tint(body, 0.62))
      panel([(-0.84, 0.4, 0.83), (0.84, 0.4, 0.83), (0.69, 1.3, 1.45), (-0.69, 1.3, 1.45)], tint(0x304451))
      panel([(-0.69, 1.3, 1.45), (0.69, 1.3, 1.45), (0.67, 2.7, 1.45), (-0.67, 2.7, 1.45)], tint(body, 0.94))
      if car_ok and index == ego_index:
        brake, left, right = lamps
        for sign, indicator in ((-1, left), (1, right)):
          if brake:
            panel([(sign * a, 0, h) for a, h in ((0.34, 0.52), (0.71, 0.52), (0.71, 0.69), (0.34, 0.69))], tint(0xFF3434))
          if indicator:
            panel([(sign * a, 0, h) for a, h in ((0.73, 0.52), (0.92, 0.52), (0.92, 0.69), (0.73, 0.69))], tint(0xFFB020))
    return faces

  def draw_map(self, rect, state, now):
    sm = state.sm
    if not fresh(state, "navInstructionCarrot", 2, now) or not sm.valid["navRoute"] or not sm["navRoute"].carrotRouteId:
      return
    from openpilot.selfdrive.navigation.preview import WEB_DEMAND_PATH

    if now >= self.next_demand:
      self.next_demand = now + 1
      try:
        WEB_DEMAND_PATH.touch()
      except OSError:
        return
    if self.map_input is None:
      from openpilot.selfdrive.navigation.map_client import MapInput

      self.map_input = MapInput()
    source = self.map_input
    source.receive(now)
    if source.image is None or source.route_time != sm["navRoute"].carrotRouteId or not 0 <= now - source.image_time < 0.5:
      return
    if self.image_time != source.image_time:
      import numpy as np
      from openpilot.selfdrive.navigation.renderer import ROUTE_INTENSITY

      if self.texture is None:
        image = rl.gen_image_color(256, 256, rl.BLACK)
        self.texture = rl.load_texture_from_image(image)
        rl.unload_image(image)
      pixels = np.empty((256, 256, 4), dtype=np.uint8)
      pixels[:, :, :3] = source.image[:, :, None]
      pixels[:, :, 3] = 255
      rgb = self.style["map_color"]
      pixels[source.image == ROUTE_INTENSITY, :3] = [(rgb >> 16) & 255, (rgb >> 8) & 255, rgb & 255]
      rl.update_texture(self.texture, rl.ffi.cast("void *", rl.ffi.from_buffer(pixels)))
      self.image_time = source.image_time
    v = self.style
    side = min(rect.width * 0.31, rect.height * 0.48) * v["map_size"] / 100
    x = rect.x + rect.width * (0.805 + v["map_x"] / 100) - side / 2
    y = rect.y + rect.height * (128 / 450 + v["map_y"] / 100) - side / 2
    rl.draw_texture_pro(self.texture, rl.Rectangle(0, 0, 256, 256), rl.Rectangle(x, y, side, side), rl.Vector2(0, 0), 0, rl.WHITE)
    rl.draw_text("© OpenStreetMap", int(x), int(y + side), max(9, int(rect.height * 0.028)), rl.WHITE)


def draw_minimal_hud(rect, state, hud, v):
  now = time.monotonic()
  if not fresh(state, "carState", 0.5, now) or not isfinite(hud.speed):
    return
  small = rect.width < 1000
  unit = "km/h" if state.is_metric else "mph"

  def reading(part, text, label, anchor):
    x = rect.x + rect.width * anchor + v["hud_x"] + v[part + "_x"]
    y = rect.y + rect.height * 0.045 + v["hud_y"] + v[part + "_y"]
    size = v[part + "_font"] * 0.66
    x = max(rect.x + 3, min(x, rect.x + rect.width - size * 2))
    y = max(rect.y + 2, min(y, rect.y + rect.height - size * 2))
    ink = tint(0xEFF5F8 if v["scene_style"] == 1 else 0x142735)
    rl.draw_text_ex(hud._font_display, text, rl.Vector2(x, y), size, 0, ink)
    rl.draw_text_ex(hud._font_display, label, rl.Vector2(x, y + size), max(10, size * 0.36), 0, ink)

  reading("speed", str(round(hud.speed)), unit, 0.035)
  if fresh(state, "selfdriveState", 0.5, now) and hud._engaged and hud.is_cruise_set and isfinite(hud.set_speed):
    reading("cruise", str(round(hud.set_speed * (1 if state.is_metric else 0.621371))), "MAX", 0.24 if small else 0.17)
