import copy
import json
import sqlite3
import uuid
from types import SimpleNamespace as NS

import numpy as np
from fastapi.testclient import TestClient

from formosalink.server.app import create_app
from formosalink.server.config import initialize
from formosalink.server.road_scenes import check_scene, geographic_features
from formosalink.tests.test_platform import ORIGIN, PASSWORD, pair
from openpilot.sunnypilot.formosalink.protocol import sign
from openpilot.sunnypilot.formosalink.road_scene import SCHEMA, model_scene
from openpilot.sunnypilot.formosalink.scene_agent import SERVICES, SceneBuffer
from tools.carrot_mapping.depth_surface import distance_band, surface_voxels


def inputs():
  class SM(dict):
    pass

  eof = 5_000_000_000
  curve = NS(x=[1.0, 4.0, 12.0], y=[1.0, 1.0, 1.0], z=[1.0, 1.0, 1.0])
  model = NS(
    frameId=42,
    timestampEof=eof,
    laneLines=[curve] * 4,
    laneLineStds=[0.2] * 4,
    laneLineProbs=[0.9] * 4,
    roadEdges=[curve] * 2,
    roadEdgeStds=[0.4] * 2,
  )
  lead = NS(status=True, dRel=12.5, yRel=2.5)
  radar = NS(
    leadOne=lead, leadTwo=lead, leadsLeft=[lead], leadsRight=[], leadsCenter=[], leadsLeft2=[], leadsRight2=[], leadsCutIn=[]
  )
  gps = NS(
    hasFix=True, latitude=25.0, longitude=121.0, horizontalAccuracy=2.0, speed=10.0, bearingDeg=0.0, bearingAccuracyDeg=2.0
  )
  sm = SM(
    modelV2=model,
    carState=NS(canValid=True, canTimeout=False, laneLineInfoMonoTime=eof, leftLaneLine=24, rightLaneLine=11),
    radarState=radar,
    liveCalibration=NS(calStatus="calibrated", rpyCalib=[0.0, 0.0, 0.0], height=[1.24]),
    gpsLocationExternal=gps,
    gpsLocation=gps,
  )
  sm.valid = dict.fromkeys(SERVICES, True)
  sm.updated = sm.valid.copy()
  sm.logMonoTime = dict.fromkeys(SERVICES, eof)
  return sm, eof


def camera(frame, eof):
  return dict(
    frame=frame,
    eof=eof,
    detector="efficientdet",
    objects=[
      dict(kind="person", score=0.9, xy=[12.0, -2.0], box=None),
      dict(kind="traffic light", score=0.9, xy=None, box=[0.1, 0.1, 0.2, 0.2]),
    ],
  )


def test_exact_capture_and_uncertainty():
  sm, t = inputs()
  ring = SceneBuffer()
  ring.add(sm, t)
  ring.camera(camera(42, t + 1))
  ring.camera(camera(43, t))
  ring.camera(camera(42, t))
  ring.camera(camera(42, t))
  (s,) = ring.ready(t + 3_000_000_000)
  check_scene(s)
  assert len(s["camera"]) == 1 and s["targets"] == [[12.5, -2.5]]
  assert [line["oem"] for line in s["lines"][:4]] == [None, 24, 11, None]
  f = geographic_features(s)
  assert len(f) == 8 and f[-1]["properties"]["kind"] == "person"
  assert f[-1]["geometry"]["coordinates"][0] < 121 and f[-1]["geometry"]["coordinates"][1] > 25
  sm["carState"].laneLineInfoMonoTime = t - 1_000_000_000
  sm["gpsLocation"].speed = 0.0
  s = model_scene(sm, t)
  assert s["lines"][1]["oem"] is None and s["fix"]["heading"] is None
  assert not geographic_features(s)
  sm.valid["gpsLocation"] = sm.valid["gpsLocationExternal"] = False
  assert model_scene(sm, t)["fix"] is None


def test_signed_consent_delivery_export_and_erase(tmp_path):
  initialize(tmp_path, ORIGIN, PASSWORD)
  with sqlite3.connect(tmp_path / "scene-osm.sqlite3") as db:
    db.execute("CREATE TABLE roads(id INTEGER PRIMARY KEY,way INTEGER,kind TEXT,nodes TEXT)")
    db.execute("CREATE VIRTUAL TABLE bounds USING rtree(id,west,east,south,north)")
    db.execute("INSERT INTO roads VALUES(1,477,'primary','[[121,24.999],[121,25.001]]')")
    db.execute("INSERT INTO bounds VALUES(1,121,121,24.999,25.001)")
  sm, t = inputs()
  s = model_scene(sm, t)
  s["camera"] = [camera(42, t)]
  with TestClient(create_app(tmp_path), base_url=ORIGIN) as c:
    device, key, _ = pair(c)
    path = f"/api/v1/devices/{device}/road-scenes"
    payload = dict(revision=1, boot=str(uuid.uuid4()), samples=[s])

    def upload(body):
      return c.post("/api/v1/agent/road-scenes", json=sign(key, device, "road-scenes", body))

    def action(which, rev):
      return c.post(path, json=dict(schema=SCHEMA, revision=rev, action=which), headers={"Origin": ORIGIN})

    assert not c.get(path).json()["enabled"]
    assert upload(payload).status_code == 403
    assert action("enable", 0).is_success
    assert upload({"operation": "status"}).json()["revision"] == 1
    assert upload(payload).is_success and upload(payload).is_success
    value = c.get(path).json()
    assert value["count"] == 1 and value["osm"][0]["way"] == 477
    header, row = map(json.loads, c.get(path + "/download").text.splitlines())
    assert header["control_eligible"] is False and len(row["geographic_features"]) == 8
    assert row["osm_candidates"][0]["way"] == 477
    dirty = copy.deepcopy(payload)
    dirty["samples"][0]["targets"] = []
    assert upload(dirty).status_code == 403
    dirty["samples"][0]["video"] = "x"
    assert upload(dirty).status_code == 403
    assert action("disable", 1).is_success and upload(payload).status_code == 403
    assert action("erase", 1).status_code == 409 and action("erase", 2).is_success
    assert c.get(path).json()["count"] == 0
    c.cookies.clear()
    assert c.get(path + "/download").status_code == 401


def test_surface_only_unknown_and_scale():
  d = np.full((9, 9), 10.0)
  camera = dict(width=9, height=9, fx=5, fy=5, cx=4, cy=4, rectified=True)
  cells, count = surface_voxels(d, camera, stride=1)
  assert set(cells[:, 2]) == {50} and count.sum() == 81
  band, dist = distance_band(d, camera, cells)
  assert np.min(dist) < 0 < np.max(dist) and np.max(np.abs(dist)) <= 0.4
  assert np.allclose(dist, 10.0 - (band[:, 2] + 0.5) * 0.2)
  d[:] = np.nan
  assert not surface_voxels(d, camera)[0].size
