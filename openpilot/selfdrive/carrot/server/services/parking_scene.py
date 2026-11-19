"""Display-only parking observations from the driving GPU's published outputs and ROAD paint."""

import math
import numpy as np

# Forward/right offsets from the camera in metres, sampled on the calibrated ground plane.
FORWARD = np.arange(1.0, 18.01, 0.10)
RIGHT = np.arange(-8.0, 8.01, 0.075)


def fresh(sm, key, clock, limit):
  return sm.valid[key] and sm.seen[key] and 0 <= clock - sm.logMonoTime[key] * 1e-9 < limit


def parked(sm, clock):
  car = sm["carState"]
  return fresh(sm, "carState", clock, 0.35) and car.canValid and str(car.gearShifter) == "park" and car.standstill and abs(car.vEgo) < 0.1


def ground_paint(frame, projection, center_radius=None):
  """Sample visible neutral, bright paint. Out-of-frame grid cells stay unknown."""
  w, h, stride = frame.width, frame.height, frame.stride
  if w <= 0 or h <= 0 or w % 2 or h % 2 or stride < w:
    raise ValueError("camera layout")
  y = np.ndarray((h, stride), dtype=np.uint8, buffer=frame.data)
  uv = np.ndarray((h // 2, stride), dtype=np.uint8, buffer=frame.data, offset=frame.uv_offset)
  x, r = FORWARD[:, None], RIGHT[None, :]
  grid = [row[0] * x + row[1] * r + row[3] for row in projection]
  z = grid[2]
  u = np.rint(grid[0] / np.maximum(z, 0.01)).astype(int)
  v = np.rint(grid[1] / np.maximum(z, 0.01)).astype(int)
  visible = (z > 0.1) & (u >= 0) & (u < w) & (v >= 0) & (v < h * 0.985)
  if center_radius is not None:
    # Use the central calibrated portion of the wide image; peripheral distortion is not modelled here.
    visible &= (u - w / 2) ** 2 + (v - h / 2) ** 2 <= center_radius**2
  u, v = np.clip(u, 0, w - 1), np.clip(v, 0, h - 1)
  ui = u // 2 * 2
  intensity = y[v, u]
  neutral = (np.abs(uv[v // 2, ui].astype(int) - 128) <= 22) & (np.abs(uv[v // 2, ui + 1].astype(int) - 128) <= 22)
  return np.where(visible & neutral & (intensity >= 155), intensity, 0), np.where(visible, intensity.astype(int), -1)


def slot_candidates(model, paint, background):
  """Model boundaries seed the search. Require contrasting side paint and two distinct end bars."""
  lines = []
  for line, prob in zip(model.laneLines, model.laneLineProbs):
    lx, ly = np.asarray(list(line.x)), np.asarray(list(line.y))
    if (
      not 0.65 <= prob <= 1
      or len(lx) < 2
      or lx.shape != ly.shape
      or not np.isfinite(lx).all()
      or not np.isfinite(ly).all()
      or not (np.diff(lx) > 0).all()
    ):
      lines.append(None)
      continue
    lines.append(np.interp(FORWARD, lx, ly, left=np.nan, right=np.nan))
  result = []
  rows = np.arange(len(FORWARD))

  def index(y):
    return np.clip(np.rint((y - RIGHT[0]) / 0.075).astype(int), 0, len(RIGHT) - 1)

  def painted_side(y):
    col = index(y)
    # Sample narrow offsets around the model estimate. A featureless bright area is not paint.
    left, right = background[rows, col - 5], background[rows, col + 5]
    bright = np.maximum.reduce([paint[rows, col + i] for i in (-2, -1, 0, 1, 2)]).astype(int)
    return (left >= 0) & (right >= 0) & (bright >= np.maximum(left, right) + 28)

  for a, b in zip(lines, lines[1:]):
    if a is None or b is None:
      continue
    valid = np.isfinite(a) & np.isfinite(b) & (np.abs(a) < 7.4) & (np.abs(b) < 7.4) & (b - a >= 2.1) & (b - a <= 3.5)
    if not valid.any():
      continue
    a, b = np.where(valid, a, -1.3), np.where(valid, b, 1.3)
    sides = valid & painted_side(a) & painted_side(b)
    col = index(a[:, None] + (b - a)[:, None] * np.linspace(0.10, 0.90, 15))
    front = background[np.maximum(rows - 3, 0)[:, None], col]
    rear = background[np.minimum(rows + 3, len(rows) - 1)[:, None], col]
    contrast = (paint[rows[:, None], col].astype(int) > np.maximum(front, rear) + 28) & (front >= 0) & (rear >= 0)
    bars = np.flatnonzero(valid & (contrast.mean(axis=1) >= 0.80))
    groups = np.split(bars, np.flatnonzero(np.diff(bars) > 1) + 1)
    ends = [int(g[len(g) // 2]) for g in groups if 0 < len(g) <= 5]
    for lo, hi in zip(ends, ends[1:]):
      if not (3.7 <= FORWARD[hi] - FORWARD[lo] <= 7 and valid[lo : hi + 1].all() and sides[lo : hi + 1].mean() >= 0.75):
        continue
      corners = [[FORWARD[lo], a[lo]], [FORWARD[hi], a[hi]], [FORWARD[hi], b[hi]], [FORWARD[lo], b[lo]]]
      result.append({"corners": np.round(corners, 2).tolist(), "center": np.round(np.mean(corners, axis=0), 2).tolist()})
  return result[:12]


def primary_target(model):
  if not model.leadsV3:
    return None
  lead = model.leadsV3[0]
  if not lead.x or not lead.y or not 0.8 <= lead.prob <= 1:
    return None
  x, y = float(lead.x[0]), float(lead.y[0])
  if not (1.52 < x <= 12 and math.hypot(x, y) <= 12):
    return None
  return [x, y]


class DisplayReceipts:
  """Volatile self-reported render counts. No images, coordinates or device identifiers."""

  def __init__(self):
    self.sent = {}
    self.summary = {"drawnFrames": 0, "frontRangeFrames": 0, "paintFrames": 0, "lastDrawUnix": None}

  def offered(self, body, now):
    self.sent = {k: v for k, v in self.sent.items() if 0 <= now - v[0] <= 1.5}
    if "frameId" in body:
      self.sent.setdefault(body["frameId"], (now, bool(body.get("target")), len(body.get("slots", [])), False))

  def acknowledge(self, raw, ua, now, wall):
    if not raw or len(raw) > 32 or "CarrotWebAndroid/" not in ua:
      return
    try:
      frame, cue, slots = map(int, raw.split(","))
    except ValueError:
      return
    row = self.sent.get(frame)
    if row is None or row[3] or not 0 <= now - row[0] <= 1.5 or cue not in (0, 1) or (cue and not row[1]) or slots != row[2]:
      return
    self.sent[frame] = (*row[:3], True)
    self.summary["drawnFrames"] += 1
    self.summary["frontRangeFrames"] += cue
    self.summary["paintFrames"] += int(slots > 0)
    self.summary["lastDrawUnix"] = int(wall)


class Confirm:
  def __init__(self):
    self.last = None
    self.confirmed = (None, [])

  def update(self, frame, stamp, target, slots):
    previous = self.last
    if previous and frame == previous[0] and stamp == previous[1]:
      return self.confirmed
    self.last = frame, stamp, target, slots
    if previous is None or frame <= previous[0] or not 0 < stamp - previous[1] < 0.8:
      self.confirmed = (None, [])
      return self.confirmed
    lead = target if target and previous[2] and math.dist(target, previous[2]) < 1.5 else None
    confirmed = [s for s in slots if any(max(math.dist(a, b) for a, b in zip(s["corners"], p["corners"])) < 0.65 for p in previous[3])]
    self.confirmed = lead, confirmed
    return self.confirmed
