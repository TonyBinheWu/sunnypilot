"""Owner-authorized, signed road scenes. No raw images or cabin data in this channel."""

import asyncio
from contextlib import contextmanager, suppress
import json
import time
import uuid

from cryptography.exceptions import InvalidSignature
from fastapi import HTTPException, Request
from fastapi.responses import StreamingResponse
from pathlib import Path
import math

from openpilot.sunnypilot.formosalink.protocol import verify
from openpilot.sunnypilot.formosalink.road_scene import (
  SCHEMA,
  check_camera,
  coords,
  exact,
  number,
  paint_code,
  seq,
  valid_frame,
)
from .scene_osm import road_context
from .scene_history import recent_geometry

RETENTION = 30 * 86400
MAX_SAMPLES = 200_000
LIMIT_BYTES = 128 * 1024
NOTICE = {
  "zh-TW": "分享期間會傳送道路位置、行進方向、車道線、道路邊緣和前方目標至你的 FormosaLink，供道路建模研究。含座艙辨識的分類與框，無影像、音訊或車內資料。可使用行動網路，資料最多保留 30 天，可停用並刪除。",
  "en": "Send location, heading, lane and road edges and front target observations to your FormosaLink for road modeling. Includes cockpit classes and boxes, excludes video, audio and cabin data. Cellular data may be used. Retained for up to 30 days. You can stop sharing and erase records.",
  "ja": "位置、方位、車線、道路端、前方物体の分類と枠を道路モデリング研究のため FormosaLink に送信します。映像・音声・車内データは含みません。携帯回線を使用する場合があります。最長30日保存し、停止・削除できます。",
}


def check_scene(s):
  if (
    not exact(s, "frame eof calibrated lines targets fix camera meta")
    or not valid_frame(s)
    or type(s["calibrated"]) is not bool
  ):
    raise ValueError("invalid scene")
  meta = s["meta"]
  if not exact(meta, "clocks rpy camera_height_m paint_clock") or not isinstance(meta["clocks"], dict):
    raise ValueError("invalid source metadata")
  if not set(meta["clocks"]) <= {
    "modelV2",
    "carState",
    "radarState",
    "liveCalibration",
    "gpsLocationExternal",
    "gpsLocation",
  } or not all(type(v) is int and v > 0 and abs(v - s["eof"]) <= 2_000_000_000 for v in meta["clocks"].values()):
    raise ValueError("invalid source clocks")
  if (
    meta["rpy"] is not None
    and not coords(meta["rpy"], [(-1, 1)] * 3)
    or meta["camera_height_m"] is not None
    and not number(meta["camera_height_m"], 0.5, 3)
  ):
    raise ValueError("invalid calibration metadata")
  if meta["paint_clock"] is not None and (
    type(meta["paint_clock"]) is not int or abs(meta["paint_clock"] - s["eof"]) > 200_000_000
  ):
    raise ValueError("invalid paint time")
  if not seq(s["lines"], 6) or not seq(s["targets"], 48) or not seq(s["camera"], 6):
    raise ValueError("scene too large")
  for line in s["lines"]:
    if not exact(line, "kind index std probability oem xyz") or line["kind"] not in ("lane", "edge"):
      raise ValueError("unknown line source")
    lane = line["kind"] == "lane"
    if type(line["index"]) is not int or not 0 <= line["index"] < (4 if lane else 2) or not number(line["std"], 0, 2):
      raise ValueError("invalid line")
    if not number(line["probability"], 0.5, 1) if lane else line["probability"] is not None:
      raise ValueError("invalid probability")
    if line["oem"] is not None and (
      not lane or line["index"] not in (1, 2) or not paint_code(line["oem"]) or meta["paint_clock"] is None
    ):
      raise ValueError("invalid OEM paint")
    points = line["xyz"]
    if not seq(points, 33) or len(points) < 2 or not all(coords(p, [(0, 100), (-30, 30), (-10, 10)]) for p in points):
      raise ValueError("invalid polyline")
    if any(b[0] <= a[0] for a, b in zip(points, points[1:])):
      raise ValueError("unordered polyline")
  if not all(coords(p, [(0.1, 120), (-35, 35)]) for p in s["targets"]):
    raise ValueError("invalid target")
  fix = s["fix"]
  if fix is not None:
    if not exact(fix, "lat lon accuracy heading heading_std dt_ms") or not coords(
      [fix[k] for k in ("lat", "lon", "accuracy", "dt_ms")], [(-85, 85), (-180, 180), (0.01, 15), (-200, 200)]
    ):
      raise ValueError("invalid GPS")
    if (
      fix["heading"] is None
      and fix["heading_std"] is not None
      or fix["heading"] is not None
      and not (number(fix["heading"], 0, 360) and number(fix["heading_std"], 0.01, 15))
    ):
      raise ValueError("invalid bearing")
  for packet in s["camera"]:
    check_camera(packet)
    if (packet["eof"], packet["frame"]) != (s["eof"], s["frame"]):
      raise ValueError("unrelated camera sample")


def geographic_features(scene):
  """Approximate planimetric overlay; keep measured/predicted Z in its original frame."""
  fix = scene["fix"]
  if not fix or fix["heading"] is None or not scene["calibrated"]:
    return []
  yaw = math.radians(fix["heading"])
  cosine, sine = math.cos(yaw), math.sin(yaw)

  def lonlat(x, y):
    return [
      fix["lon"] + (x * sine + y * cosine) / (111320 * math.cos(math.radians(fix["lat"]))),
      fix["lat"] + (x * cosine - y * sine) / 111320,
    ]

  def feature(kind, geometry, coordinates, **props):
    return dict(type="Feature", properties=dict(kind=kind, **props), geometry=dict(type=geometry, coordinates=coordinates))

  features = [
    feature(line["kind"], "LineString", [lonlat(x, y) for x, y, _ in line["xyz"]], index=line["index"], oem=line["oem"])
    for line in scene["lines"]
  ]
  features.extend(feature("unknown", "Point", lonlat(*p), source="radarState") for p in scene["targets"])
  for packet in scene["camera"]:
    if packet["frame"] == scene["frame"] and packet["eof"] == scene["eof"]:
      features.extend(
        feature(o["kind"], "Point", lonlat(*o["xy"]), source=packet["detector"])
        for o in packet["objects"]
        if o["xy"] is not None
      )
  return features


def attach(app, directory, store, owner, rate):
  @contextmanager
  def connection():
    with store.connection() as db:
      db.execute("ATTACH DATABASE ? AS research", (str(directory / "road-research.sqlite3"),))
      yield db

  with connection() as db:
    db.executescript("""
      CREATE TABLE IF NOT EXISTS research.scene_consent(device TEXT PRIMARY KEY, owner TEXT, revision INTEGER, enabled INTEGER);
      CREATE TABLE IF NOT EXISTS research.road_samples(seq INTEGER PRIMARY KEY, device TEXT, owner TEXT, boot TEXT,
        eof INTEGER, received INTEGER, body TEXT, UNIQUE(device,owner,boot,eof));
      CREATE INDEX IF NOT EXISTS research.scene_age ON road_samples(received);
      CREATE INDEX IF NOT EXISTS research.scene_lookup ON road_samples(device,owner,seq);
    """)

  def access(db, device, user=None):
    row = db.execute("SELECT owner_id,public_key FROM devices WHERE id=? AND state='paired'", (device,)).fetchone()
    if row is None or (user is not None and user != row["owner_id"]):
      raise HTTPException(404, "device unavailable")
    grant = db.execute(
      "SELECT revision,enabled FROM scene_consent WHERE device=? AND owner=?", (device, row["owner_id"])
    ).fetchone()
    return row, (int(grant["revision"]), bool(grant["enabled"])) if grant else (0, False)

  def osm_index():
    custom = directory / "scene-osm.sqlite3"
    return custom if custom.is_file() else Path(__file__).with_name("scene-osm.sqlite3")

  @app.get("/api/v1/devices/{device}/road-scenes/download")
  def download(device: str, request: Request):
    user = owner(request)["id"]
    cutoff = int(time.time()) - RETENTION
    with connection() as db:
      access(db, device, user)
      last = db.execute("SELECT MAX(seq) FROM road_samples WHERE device=? AND owner=?", (device, user)).fetchone()[0] or 0

    def stream():
      after = 0
      index = osm_index()
      revision = None
      if index.exists():
        revision = index.stat().st_mtime_ns
      yield (
        json.dumps(
          dict(
            schema=SCHEMA,
            axes="model calibrated FRD metres",
            control_eligible=False,
            ground_truth=False,
            osm_attribution="© OpenStreetMap contributors, ODbL 1.0",
            osm_index_mtime_ns=revision,
          )
        )
        + "\n"
      )
      while after < last:
        with connection() as db:
          access(db, device, user)
          rows = db.execute(
            """SELECT * FROM road_samples WHERE device=? AND owner=? AND seq>? AND seq<=? AND received>=?
                             ORDER BY seq LIMIT 32""",
            (device, user, after, last, cutoff),
          ).fetchall()
        if not rows:
          break
        for r in rows:
          s = json.loads(r["body"])
          roads = road_context(index, s["fix"])
          item = dict(
            seq=r["seq"],
            boot=r["boot"],
            received=r["received"],
            scene=s,
            osm_candidates=[dict(way=o["way"], highway=o["highway"], distance_m=o["distance_m"]) for o in roads],
            geographic_features=geographic_features(s),
          )
          yield json.dumps(item, allow_nan=False, separators=(",", ":")) + "\n"
          after = r["seq"]

    return StreamingResponse(
      stream(),
      media_type="application/x-ndjson",
      headers={"Content-Disposition": 'attachment; filename="road-scenes.ndjson"'},
    )

  @app.get("/api/v1/devices/{device}/road-scenes")
  def status(device: str, request: Request, after: int | None = None):
    user = owner(request)["id"]
    with connection() as db:
      _, (revision, enabled) = access(db, device, user)
      cutoff = int(time.time()) - RETENTION
      args = (device, user, cutoff)
      count = db.execute("SELECT COUNT(*) FROM road_samples WHERE device=? AND owner=? AND received>=?", args).fetchone()[0]
      if after is None:
        rows = db.execute(
          "SELECT * FROM road_samples WHERE device=? AND owner=? AND received>=? ORDER BY seq DESC LIMIT 9", args
        ).fetchall()
      else:
        rows = db.execute(
          "SELECT * FROM road_samples WHERE device=? AND owner=? AND received>=? AND seq>? ORDER BY seq LIMIT 32",
          (*args, after),
        ).fetchall()
    items = [dict(seq=r["seq"], boot=r["boot"], received=r["received"], scene=json.loads(r["body"])) for r in rows]
    history = recent_geometry(items[0], items[1:]) if after is None and items else []
    if after is None:
      items = items[:1]
    index = osm_index()
    # Context belongs to the displayed vehicle fix. No device coordinates leave this host.
    roads = road_context(index, items[-1]["scene"]["fix"]) if items else []
    return dict(
      schema=SCHEMA,
      notice=NOTICE,
      enabled=enabled,
      revision=revision,
      count=count,
      items=items,
      history=history,
      osm=roads,
      osm_index=index.is_file(),
      osm_attribution="© OpenStreetMap contributors",
    )

  @app.post("/api/v1/devices/{device}/road-scenes")
  async def choose(device: str, request: Request):
    user = owner(request)["id"]
    try:
      data = await request.json()
    except ValueError as exc:
      raise HTTPException(400, "invalid JSON") from exc
    if (
      not exact(data, "schema revision action")
      or data["schema"] != SCHEMA
      or data["action"] not in ("enable", "disable", "erase")
      or type(data["revision"]) is not int
    ):
      raise HTTPException(400, "invalid choice")
    with connection() as db:
      db.execute("BEGIN IMMEDIATE")
      _, (revision, _) = access(db, device, user)
      if revision != data["revision"]:
        raise HTTPException(409, "refresh and review the current choice")
      db.execute(
        "INSERT OR REPLACE INTO scene_consent VALUES(?,?,?,?)", (device, user, revision + 1, data["action"] == "enable")
      )
      if data["action"] == "erase":
        db.execute("DELETE FROM road_samples WHERE device=? AND owner=?", (device, user))
    return {"ok": True}

  @app.post("/api/v1/agent/road-scenes")
  async def ingest(request: Request):
    rate(request, "road-scenes", 3000)
    try:
      envelope = await request.json()
      device = envelope["device_id"]
      with connection() as db:
        row, _ = access(db, device)
      data = verify(envelope, row["public_key"], "road-scenes")["payload"]
      store.consume_nonce(device, envelope["nonce"])
      with connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row, (revision, enabled) = access(db, device)
        if data != {"operation": "status"}:
          if (
            not enabled
            or not exact(data, "revision boot samples")
            or type(data["revision"]) is not int
            or data["revision"] != revision
          ):
            raise ValueError("grant changed")
          boot = str(uuid.UUID(data["boot"]))
          if not seq(data["samples"], 8) or not data["samples"]:
            raise ValueError("invalid batch")
          for s in data["samples"]:
            check_scene(s)
            body = json.dumps(s, allow_nan=False, separators=(",", ":"), sort_keys=True)
            cursor = db.execute(
              "INSERT OR IGNORE INTO road_samples(device,owner,boot,eof,received,body) VALUES(?,?,?,?,?,?)",
              (
                device,
                row["owner_id"],
                boot,
                s["eof"],
                int(time.time()),
                body,
              ),
            )
            if cursor.rowcount == 0:
              existing = db.execute(
                "SELECT body FROM road_samples WHERE device=? AND owner=? AND boot=? AND eof=?",
                (device, row["owner_id"], boot, s["eof"]),
              ).fetchone()
              if json.loads(existing["body"]) != s:
                raise ValueError("conflicting capture")
          db.execute(
            """DELETE FROM road_samples WHERE device=? AND owner=? AND seq<=(
            SELECT seq FROM road_samples WHERE device=? AND owner=? ORDER BY seq DESC LIMIT 1 OFFSET ?)""",
            (device, row["owner_id"], device, row["owner_id"], MAX_SAMPLES),
          )
      result = dict(schema=SCHEMA, revision=revision, enabled=enabled)
      if "samples" in data and data["samples"][-1]["fix"]:
        fix = data["samples"][-1]["fix"]
        result["map"] = {"center": [fix["lat"], fix["lon"]], "ways": [r["lonlat"] for r in road_context(osm_index(), fix)]}
      return result
    except (ValueError, TypeError, KeyError, AttributeError, InvalidSignature) as exc:
      raise HTTPException(403, "invalid road scene or expired grant") from exc

  task = None

  def purge():
    with connection() as db:
      db.execute("DELETE FROM road_samples WHERE received<=?", (int(time.time()) - RETENTION,))

  async def cleanup():
    while True:
      await asyncio.to_thread(purge)
      await asyncio.sleep(3600)

  @app.on_event("startup")
  async def start():
    nonlocal task
    task = asyncio.create_task(cleanup())

  @app.on_event("shutdown")
  async def stop():
    if task:
      task.cancel()
      with suppress(asyncio.CancelledError):
        await task
