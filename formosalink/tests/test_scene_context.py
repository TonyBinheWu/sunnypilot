from collections import deque
from threading import Lock
from types import SimpleNamespace
import asyncio
import json
import time

from formosalink.server.scene_history import recent_geometry
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from openpilot.sunnypilot.formosalink import scene_agent as agent


# The web package registers all features eagerly. Exercise this standalone route
# on IIS/workstation Python without importing unrelated on-device IPC modules.
spec = spec_from_file_location(
  "scene_routes_under_test", Path(__file__).resolve().parents[2] / "openpilot/selfdrive/carrot/server/features/road_scenes.py"
)
local = module_from_spec(spec)
spec.loader.exec_module(local)


def test_live_reference_map_requires_fresh_matching_revision_and_heading():
  fix = {"lat": 25.0, "lon": 121.0, "heading": 0.0}
  pos = {"revision": 3, "eof": 2_000_000_000, "fix": fix}
  cache = {"revision": 3, "expires": 10.0, "map": {"center": [25.0, 121.0], "ways": [[[121.0, 25.0], [121.0, 25.0001]]]}}
  (seg,) = local.map_lines(3, pos, cache, 2.4)
  assert seg[1][0] > 10 and seg[1][1] == 0
  for age, revision in [(3.1, 3), (2.4, 4)]:
    assert not local.map_lines(revision, pos, cache, age)
  fix["heading"] = None
  assert not local.map_lines(3, pos, cache, 2.4)


def test_map_crossing_view_with_both_endpoints_outside():
  assert local.clip_view([-50, 0], [150, 0]) == [[0, 0], [100, 0]]
  assert local.clip_view([50, -100], [50, 100]) == [[50, -32], [50, 32]]
  assert local.clip_view([3, -80], [10, -40]) is None


def test_owner_grant_and_local_camera_endpoint(tmp_path, monkeypatch):
  monkeypatch.setattr(local, "SHARED", tmp_path)
  monkeypatch.setattr(local, "active_lease", lambda: agent.active_lease(tmp_path))
  eof = time.monotonic_ns()
  packet = dict(
    frame=8, eof=eof, detector="road", objects=[dict(kind="crosswalk", score=0.7, xy=None, box=[0.0, 0.1, 0.4, 0.2])]
  )

  class Content:
    async def iter_chunked(self, size):
      yield json.dumps(dict(revision=2, packet=packet)).encode()

  req = SimpleNamespace(content_type="application/json", content=Content())
  agent.publish(tmp_path / "lease", dict(revision=2, until=time.monotonic() + 20))
  assert asyncio.run(local.observation(req)).status == 200
  assert agent.read_small(tmp_path / "road", 8192)["packet"] == packet


def test_outbox_lost_ack_and_revocation(tmp_path, monkeypatch):
  import requests

  monkeypatch.setattr(agent, "SHARED", tmp_path)
  clock = SimpleNamespace(now=100.0)
  monkeypatch.setattr(agent, "time", SimpleNamespace(monotonic=lambda: clock.now))
  pending, grant, calls, saved = deque(maxlen=90), [None, 0.0], [], set()
  stop = SimpleNamespace(is_set=lambda: clock.now >= 163)
  lock = Lock()

  def wait(seconds):
    if grant[0] == 1 and not pending and not saved:
      pending.append({"eof": 810})
    clock.now += seconds

  stop.wait = wait

  def call(data):
    if data == {"operation": "status"}:
      active = 130 <= clock.now < 160
      return dict(enabled=active, revision=1 if active else 2)
    calls.append((clock.now, data["revision"], [s["eof"] for s in data["samples"]]))
    assert grant[0] == 1 and 130 <= clock.now < 160
    saved.update(calls[-1][2])
    if len(calls) == 1:
      raise requests.Timeout("server committed before client received acknowledgement")
    return {"enabled": True, "revision": 1}

  agent.sync_loop(stop, call, pending, lock, grant, "boot", SimpleNamespace(is_alive=lambda: True))
  assert [row[2] for row in calls] == [[810], [810]]
  assert saved == {810} and not pending and grant == [None, 0.0]
  assert not (tmp_path / "lease").exists()


def test_static_history_does_not_ghost_targets_or_cross_a_reboot():
  def frame(eof):
    return dict(
      boot="boot",
      scene=dict(
        eof=eof,
        frame=12,
        calibrated=True,
        fix=dict(lat=25.0, lon=121.0, heading=90.0),
        lines=[dict(kind="edge", xyz=[[2, 0, 1], [5, 0, 1]])],
        targets=[[5, 4]],
      ),
    )

  a, b = frame(3_000_000_000), frame(2_000_000_000)
  curves = recent_geometry(a, [b])
  assert len(curves) == 1 and curves[0]["kind"] == "edge" and curves[0]["xy"] == [[2.0, 0.0], [5.0, 0.0]]
  b["boot"] = "another"
  assert recent_geometry(a, [b]) == []
