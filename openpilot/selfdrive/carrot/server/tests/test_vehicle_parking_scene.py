from types import SimpleNamespace as S

import numpy as np

from openpilot.selfdrive.carrot.server.services.parking_scene import (
  FORWARD,
  RIGHT,
  Confirm,
  DisplayReceipts,
  ground_paint,
  parked,
  primary_target,
  slot_candidates,
)


def grid(end_bars, side=True):
  x, y = FORWARD[:, None], RIGHT[None, :]
  bright = (np.abs(np.abs(y) - 1.35) < 0.09) & (x >= 5) & (x <= 10) & side
  for bar in end_bars:
    bright |= (np.abs(x - bar) < 0.08) & (np.abs(y) <= 1.35)
  intensity = np.where(bright, 210, 70)
  return np.where(bright, intensity, 0), intensity


def model():
  return S(laneLines=[S(x=[0, 20], y=[v, v]) for v in (-1.35, 1.35)], laneLineProbs=[0.9, 0.9])


def test_gate_rejects_motion_invalid_can_stale_or_nonpark():
  class Bus(dict):
    valid = {"carState": True}
    seen = {"carState": True}
    logMonoTime = {"carState": 10_000_000_000}

  car = S(canValid=True, gearShifter="park", standstill=True, vEgo=0)
  sm = Bus(carState=car)
  assert parked(sm, 10.03)
  assert not parked(sm, 10.5) and not parked(sm, 9.9)
  for key, bad in (("gearShifter", "reverse"), ("canValid", False), ("standstill", False), ("vEgo", 0.2)):
    good = getattr(car, key)
    setattr(car, key, bad)
    assert not parked(sm, 10.02)
    setattr(car, key, good)
  sm.valid["carState"] = False
  assert not parked(sm, 10.02)


def test_gpu_lines_require_real_paint_and_two_ends():
  observed = slot_candidates(model(), *grid([5, 10]))
  assert len(observed) == 1 and np.allclose(observed[0]["center"], [7.5, 0])
  for ends in ([], [5], [5, 6, 7, 8, 9, 10]):
    assert not slot_candidates(model(), *grid(ends))
  assert not slot_candidates(model(), *grid([5, 10], False))
  dark = np.zeros((len(FORWARD), len(RIGHT)))
  assert not slot_candidates(model(), dark, dark)
  weak = model()
  weak.laneLineProbs[0] = 0.3
  assert not slot_candidates(weak, *grid([5, 10]))


def test_confirmation_requires_distinct_timely_frames_and_consistent_corners():
  h = Confirm()
  slot = slot_candidates(model(), *grid([5, 10]))
  assert h.update(10, 1, [6, 1], slot) == (None, [])
  assert h.update(10, 1, [6, 1], slot) == (None, [])
  assert h.update(11, 1.05, [6, 1], slot) == ([6, 1], slot)
  assert h.update(11, 1.05, [6, 1], slot) == ([6, 1], slot)
  assert h.update(30, 2.5, [6, 1], slot) == (None, [])
  assert h.update(31, 2.6, [11, 0], []) == (None, [])


def test_gpu_lead_uses_only_present_hypothesis():
  m = S(leadsV3=[S(x=[5, 50], y=[1, 10], prob=0.9), S(x=[1.8], y=[0], prob=1)])
  assert primary_target(m) == [5, 1]
  for v in (float("nan"), 0, 16):
    m.leadsV3[0].x[0] = v
    assert primary_target(m) is None
  m.leadsV3[0].x[0] = 4
  m.leadsV3[0].prob = 0.65
  assert primary_target(m) is None


def test_display_receipts_require_recent_offered_frame_and_consistent_geometry():
  receipts = DisplayReceipts()
  apk = "WebView CarrotWebAndroid/0.1"
  body = {"frameId": 12, "target": None, "slots": []}
  receipts.offered(body, 30)
  receipts.acknowledge("12,0,0", "browser", 30.1, 90)
  receipts.acknowledge("12,1,0", apk, 30.1, 90)
  receipts.acknowledge("12,0,1", apk, 30.1, 90)
  assert receipts.summary["drawnFrames"] == 0
  receipts.acknowledge("12,0,0", apk, 30.4, 90)
  receipts.acknowledge("12,0,0", apk, 30.5, 90)
  assert receipts.summary == {"drawnFrames": 1, "frontRangeFrames": 0, "paintFrames": 0, "lastDrawUnix": 90}
  receipts.offered({"frameId": 13, "target": [5, 0], "slots": [{}]}, 31)
  receipts.acknowledge("13,1,1", apk, 33, 92)
  assert receipts.summary["drawnFrames"] == 1
  receipts.offered({"frameId": 14, "target": [5, 0], "slots": [{}]}, 33)
  receipts.acknowledge("14,1,1", apk, 33.2, 93)
  assert receipts.summary == {"drawnFrames": 2, "frontRangeFrames": 1, "paintFrames": 1, "lastDrawUnix": 93}


def test_padded_nv12_excludes_chroma_and_nonvisible_ground():
  stride, w, h = 80, 64, 48
  uv_offset = stride * 64
  buf = np.full(uv_offset + stride * h // 2, 220, dtype=np.uint8)
  buf[uv_offset:] = 128
  f = S(width=w, height=h, stride=stride, data=buf, uv_offset=uv_offset)
  proj = np.array([[32, 45, 0, 0], [24, 0, 0, 60], [1, 0, 0, 0]])
  white, bg = ground_paint(f, proj)
  assert (white == 220).any() and (bg == -1).any()
  central, _ = ground_paint(f, proj, center_radius=12)
  assert 0 < np.count_nonzero(central) < np.count_nonzero(white)
  buf[uv_offset::2] = 190
  assert not ground_paint(f, proj)[0].any()


def test_idle_parked_cameras_released_on_sample_worker_and_reopened(monkeypatch):
  import asyncio
  import json
  import threading
  from aiohttp import web
  from aiohttp.test_utils import TestClient, TestServer
  from openpilot.selfdrive.carrot.server.features import parking_scene

  async def run():
    released = asyncio.Event()
    loop = asyncio.get_running_loop()
    sequence = []
    class Source:
      def sample(self):
        sequence.append(("sample", self, threading.get_ident()))
        return {"status": "ready"}

      def close(self):
        sequence.append(("close", self, threading.get_ident()))
        loop.call_soon_threadsafe(released.set)

    monkeypatch.setattr(parking_scene, "ParkingSource", Source)
    monkeypatch.setattr(parking_scene, "PARKING_IDLE_SECONDS", 0.05)
    enabled = {"vision_parking_assist": True}
    monkeypatch.setattr(parking_scene, "read_web_settings", lambda: enabled)
    app = web.Application()
    parking_scene.register(app)
    async with TestClient(TestServer(app)) as client:
      async def request():
        response = await client.get("/api/vision/parking-scene")
        return json.loads(await response.text())["status"]

      assert await request() == "ready"
      await asyncio.wait_for(released.wait(), 2)
      assert [v[0] for v in sequence] == ["sample", "close"]
      assert sequence[0][1:] == sequence[1][1:]
      released.clear()
      assert await request() == "ready"
      enabled["vision_parking_assist"] = False
      assert await request() == "off"
      await asyncio.wait_for(released.wait(), 2)
      assert sequence[2][1] is not sequence[0][1]
      assert sequence[2][1:] == sequence[3][1:]

  asyncio.run(run())
