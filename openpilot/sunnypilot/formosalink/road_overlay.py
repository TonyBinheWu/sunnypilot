"""Frame-aligned, read-only HUD for the owner's wide-road stream."""
import math

import numpy as np


def projected_lines(sm, current, width, height):
  from openpilot.common.transformations.camera import DEVICE_CAMERAS, view_frame_from_device_frame
  from openpilot.common.transformations.orientation import rot_from_euler

  if not all(current(name, age) for name, age in (("deviceState", 5), ("wideRoadCameraState", 1), ("extrinsicsCalibration", 5), ("modelV2", .35))):
    return []
  calib, model = sm["extrinsicsCalibration"], sm["modelV2"]
  camera = DEVICE_CAMERAS.get((str(sm["deviceState"].deviceType), str(sm["wideRoadCameraState"].sensor)))
  if not camera or str(calib.calStatus) != "calibrated" or len(calib.rpyCalib) != 3 or len(calib.wideFromDeviceEuler) != 3:
    return []
  wide = camera.wide_road
  if not wide.width or not wide.height:
    return []
  transform = wide.intrinsics @ view_frame_from_device_frame @ rot_from_euler(calib.wideFromDeviceEuler) @ rot_from_euler(calib.rpyCalib)
  lines = []

  def project(points):
    pixels = np.asarray(points) @ transform.T
    front = np.isfinite(pixels).all(axis=1) & (pixels[:, 2] > 1)
    xy = np.full((len(points), 2), np.nan)
    xy[front] = pixels[front, :2] / pixels[front, 2:3] * (width / wide.width, height / wide.height)
    return xy

  def curve(line, z_offset, color):
    if not len(line.x) or len(line.x) != len(line.y) or len(line.y) != len(line.z):
      return
    xyz = np.column_stack((line.x, line.y, line.z))
    xyz = xyz[(xyz[:, 0] >= 2) & (xyz[:, 0] <= 100)]
    if len(xyz) >= 2:
      xyz[:, 2] += z_offset
      lines.append((project(xyz), color))

  for lane, probability in zip(model.laneLines, model.laneLineProbs, strict=False):
    if probability >= .5:
      curve(lane, 0, (230, 128, 128))
  for edge, deviation in zip(model.roadEdges, model.roadEdgeStds, strict=False):
    if 0 <= deviation < .6:
      curve(edge, 0, (170, 48, 190))
  height_offset = calib.height[0] if len(calib.height) and .1 < calib.height[0] < 4 else None
  if height_offset is not None:
    curve(model.position, height_offset, (170, 76, 68))
    if current("radarState", .35) and len(model.position.x) == len(model.position.z) and len(model.position.x):
      for lead in (sm["radarState"].leadOne, sm["radarState"].leadTwo):
        if lead.present and 1 < lead.dRel < 120:
          z = float(np.interp(lead.dRel, model.position.x, model.position.z)) + height_offset
          x, y = project([[lead.dRel, -lead.yRel, z]])[0]
          radius = max(8, min(width / 24, width / lead.dRel))
          lines.append((np.array([[x-radius, y-radius], [x, y], [x+radius, y-radius]]), (134, 72, 215)))
  return lines


def paint(y_plane, uv_plane, lines):
  """Draw into private NV12 planes. Work in 2×2 chroma cells to keep edges colored."""
  h, w = y_plane.shape
  radius = max(1, w // 800)
  for xy, (luma, u, v) in lines:
    pixels = []
    for a, b in zip(xy[:-1], xy[1:], strict=True):
      if not np.isfinite([a, b]).all() or not all(-w < p[0] < 2*w and -h < p[1] < 2*h for p in (a, b)):
        continue
      count = max(2, int(np.max(np.abs(b-a)) / 2) + 1)
      pixels.append(np.linspace(a / 2, b / 2, count).astype(int))
    if not pixels:
      continue
    points = np.concatenate(pixels)
    for dy in range(-radius, radius+1):
      for dx in range(-radius, radius+1):
        col, row = points[:, 0] + dx, points[:, 1] + dy
        inside = (col >= 0) & (row >= 0) & (col < w//2) & (row < h//2)
        x, r = col[inside]*2, row[inside]
        uv_plane[r, x], uv_plane[r, x+1] = u, v
        for offset in (0, 1):
          y_plane[r*2+offset, x] = y_plane[r*2+offset, x+1] = luma


class RoadOverlay:
  def __init__(self):
    from openpilot.cereal import messaging
    self.sm = messaging.SubMaster(["carState", "selfdriveState", "deviceState", "wideRoadCameraState",
                                   "modelV2", "radarState", "extrinsicsCalibration"])

  def sample(self, captured, width, height):
    sm = self.sm
    sm.update(0)

    def current(name, age):
      return sm.seen[name] and sm.valid[name] and abs(sm.logMonoTime[name]/1e9 - captured) <= age

    speed = sm["carState"].vEgo * 3.6 if current("carState", .5) and sm["carState"].canValid else None
    hud = {"speed_kph": round(speed, 1) if speed is not None and math.isfinite(speed) and 0 <= speed <= 500 else None,
           "engaged": bool(sm["selfdriveState"].active) if current("selfdriveState", .5) else None}
    if abs(sm["modelV2"].timestampEof / 1e9 - captured) > .35:
      return hud, []
    return hud, projected_lines(sm, current, width, height)
