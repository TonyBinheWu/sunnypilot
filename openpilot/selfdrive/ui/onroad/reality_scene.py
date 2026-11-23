"""Read-only perspective display of current model, lead and navigation messages."""

from itertools import chain, islice
from math import isfinite
import time

import pyray as rl


def fresh(state, service, seconds, now):
  sm = state.sm
  return sm.valid[service] and sm.recv_frame[service] >= state.started_frame and 0 <= now - sm.logMonoTime[service] * 1e-9 < seconds


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


class RealityScene:
  def __init__(self, style):
    self.style = style
    self.map_input = self.texture = None
    self.next_demand = self.image_time = 0
    self.key = None
    self.faces = []

  def draw(self, rect, state):
    now = time.monotonic()
    model_ok = fresh(state, "modelV2", 0.5, now)
    radar_ok = fresh(state, "radarState", 0.5, now)
    sm = state.sm
    car_ok = fresh(state, "carState", 0.5, now)
    key = (
      car_ok,
      sm.recv_frame["modelV2"] if model_ok else -1,
      sm.recv_frame["radarState"] if radar_ok else -1,
      rect.x,
      rect.y,
      rect.width,
      rect.height,
    )
    if key != self.key:
      self.faces = self.geometry(rect, sm["modelV2"] if model_ok else None, sm["radarState"] if radar_ok else None, car_ok)
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
    self.draw_map(rect, state, now)
    if car_ok:
      car = sm["carState"]
      for active, side in ((car.leftBlindspot, 0.012), (car.rightBlindspot, 0.975)):
        if active:
          rl.draw_rectangle_rec(
            rl.Rectangle(rect.x + rect.width * side, rect.y + rect.height * 0.42, rect.width * 0.012, rect.height * 0.13), tint(0xFFB54E)
          )

  def geometry(self, rect, model, radar, car_ok=False):
    v = self.style
    faces = []

    def face(layer, points, color):
      vertices = []
      for x, z, y in points:
        scale = 740 / (z + 8)
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
      ribbon("path", model.position, 1.65, 132)
      for line, prob in zip(model.laneLines, model.laneLineProbs):
        if prob > 0.5:
          ribbon("lane", line, 0.12, int(255 * min(prob, 1)))
    vehicles = vehicle_points(model, radar)
    if car_ok:
      vehicles.append((1.3, 0))  # viewport anchor for the reporting vehicle
    for z, x in vehicles:
      size = v["vehicle_size"] / 100

      def panel(vertices, color):
        face("vehicle", [(x + a * size, z + b * size, y * size) for a, b, y in vertices], color)

      body = v["vehicle_color"]
      panel([(-0.93, 0, 0.16), (0.93, 0, 0.16), (0.94, 0, 0.82), (-0.94, 0, 0.82)], tint(body, 0.75))
      panel([(-0.94, 0, 0.82), (0.94, 0, 0.82), (0.88, 4, 0.76), (-0.88, 4, 0.76)], tint(body))
      side = 1 if x < 0 else -1
      panel([(side * 0.93, 0, 0.16), (side * 0.9, 4, 0.16), (side * 0.88, 4, 0.76), (side * 0.94, 0, 0.82)], tint(body, 0.62))
      panel([(-0.84, 0.4, 0.83), (0.84, 0.4, 0.83), (0.69, 1.3, 1.45), (-0.69, 1.3, 1.45)], tint(0x304451))
      panel([(-0.69, 1.3, 1.45), (0.69, 1.3, 1.45), (0.67, 2.7, 1.45), (-0.67, 2.7, 1.45)], tint(body, 0.94))
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
