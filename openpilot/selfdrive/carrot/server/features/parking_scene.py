"""On-demand vehicle parking observations. Never acquire the eGPU or request driving work."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import math
import os
import threading
import time

import numpy as np

from aiohttp import web

from ..services.parking_scene import Confirm, DisplayReceipts, fresh, parked, ground_paint, primary_target, slot_candidates
from ..services.web_settings import read_web_settings
from openpilot.sunnypilot.formosalink.cameras import camera_clock


# A connected cockpit polls several times per second. Release both camera
# mappings and model subscriptions once that client leaves the parking view.
PARKING_IDLE_SECONDS = 5.0


class ParkingSource:
  def __init__(self):
    self.sm = None
    self.cameras = {}
    self.history = Confirm()

  def unavailable(self, status):
    self.history = Confirm()
    self.cameras.clear()
    return {"status": status, "slots": [], "target": None}

  def close(self):
    self.cameras.clear()
    self.sm = None
    self.history = Confirm()

  def observe_paint(self, lens, model, frame_id, stamp):
    from msgq.visionipc import VisionIpcClient, VisionStreamType
    from openpilot.common.transformations.camera import DEVICE_CAMERAS, view_frame_from_device_frame
    from openpilot.common.transformations.orientation import rot_from_euler

    wide = lens == "wide"
    state = "wideRoadCameraState" if wide else "roadCameraState"
    if lens not in self.cameras:
      stream = VisionStreamType.VISION_STREAM_WIDE_ROAD if wide else VisionStreamType.VISION_STREAM_ROAD
      self.cameras[lens] = VisionIpcClient("camerad", stream, True)
    camera = self.cameras[lens]
    if not camera.is_connected() and not camera.connect(False):
      return [], "waiting_camera"
    frame = camera.recv(12)
    sm = self.sm
    sm.update(0)
    road, cal = sm[state], sm["liveCalibration"]
    # EOF timestamps share camerad's boottime clock, including time spent suspended.
    if (
      frame is None
      or not sm.seen[state]
      or not sm.valid[state]
      or abs(camera.timestamp_eof * 1e-9 - stamp) > 0.12
      or abs(int(camera.frame_id) - frame_id) > 2
      or abs(int(road.frameId) - int(camera.frame_id)) > 2
      or abs((road.timestampEof - camera.timestamp_eof) * 1e-9) > 0.12
    ):
      return [], "waiting_camera"
    config = DEVICE_CAMERAS.get((str(sm["deviceState"].deviceType), str(road.sensor)))
    angles = cal.wideFromDeviceEuler if wide else [0, 0, 0]
    if (
      not config
      or not fresh(sm, "liveCalibration", time.monotonic(), 1.5)
      or str(cal.calStatus) != "calibrated"
      or not cal.height
      or not 0.5 <= cal.height[0] <= 3
      or len(cal.rpyCalib) != 3
      or len(angles) != 3
      or not all(math.isfinite(v) and abs(v) < 1 for v in [*cal.rpyCalib, *angles])
    ):
      return [], "waiting_calibration"
    camera_config = config.ecam if wide else config.fcam
    if camera_config.size != (frame.width, frame.height):
      return [], "waiting_calibration"
    camera_rotation = view_frame_from_device_frame @ rot_from_euler(angles)
    rotation = camera_rotation @ rot_from_euler(cal.rpyCalib)
    translation = camera_rotation @ np.array([0, 0, cal.height[0]])
    projection = camera_config.intrinsics @ np.column_stack((rotation, translation))
    radius = camera_config.focal_length * 0.6 if wide else None
    return slot_candidates(model, *ground_paint(frame, projection, center_radius=radius)), "ready"

  def sample(self):
    from openpilot.cereal import messaging

    if self.sm is None:
      if hasattr(os, "setpriority"):
        os.setpriority(os.PRIO_PROCESS, threading.get_native_id(), 10)
      self.sm = messaging.SubMaster(["carState", "modelV2", "roadCameraState", "wideRoadCameraState", "liveCalibration", "deviceState"])
    sm = self.sm
    sm.update(0)
    now = time.monotonic()
    if not parked(sm, now):
      return self.unavailable("waiting_park")
    model = sm["modelV2"]
    if not fresh(sm, "modelV2", now, 0.35) or str(model.visionCompute) != "usbGpu":
      return self.unavailable("waiting_usb_model")
    frame_id, stamp = int(model.frameId), model.timestampEof * 1e-9
    if not 0 <= camera_clock() - stamp < 0.35:
      return self.unavailable("stale")
    slots, cameras, status = [], [], "waiting_camera"
    inputs = str(model.visionCameraInputs)
    for lens in {"road": ("road",), "wide": ("wide",), "roadWide": ("road", "wide")}.get(inputs, ()):
      try:
        found, lens_status = self.observe_paint(lens, model, frame_id, stamp)
      except (BufferError, ValueError, OSError, RuntimeError):
        self.cameras.pop(lens, None)
        continue
      if lens_status == "ready":
        cameras.append(lens)
        for candidate in found:
          if all(math.dist(candidate["center"], previous["center"]) > 0.85 for previous in slots):
            slots.append(candidate)
      elif lens_status == "waiting_calibration":
        status = lens_status
    if cameras:
      status = "ready"
    sm.update(0)
    if not parked(sm, time.monotonic()) or not fresh(sm, "modelV2", time.monotonic(), 0.35) or str(sm["modelV2"].visionCompute) != "usbGpu":
      return self.unavailable("stale")
    age = camera_clock() - stamp
    if not 0 <= age < 0.55:
      return self.unavailable("stale")
    target, slots = self.history.update(frame_id, stamp, primary_target(model), slots)
    return {
      "status": status,
      "backend": "drivingModelUsbGpu",
      "paintBackend": "vehicleCpu",
      "paintCameras": cameras,
      "frameId": frame_id,
      "captureTime": stamp,
      "target": target,
      "slots": slots,
    }


def register(app):
  source = None
  idle_timer = None
  receipts = DisplayReceipts()
  executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="parking-display")
  pending = result = None
  last = -math.inf

  def release():
    nonlocal source, idle_timer, pending, result, last
    if idle_timer is not None:
      idle_timer.cancel()
      idle_timer = None
    if source is not None:
      # The same worker owns sample() and cleanup, including in-flight samples.
      executor.submit(source.close)
      source = pending = result = None
      last = -math.inf

  async def snapshot(request):
    nonlocal source, idle_timer, pending, result, last
    receipts.acknowledge(request.headers.get("X-Carrot-Parking-Draw"), request.headers.get("User-Agent", ""), time.monotonic(), time.time())
    if read_web_settings().get("vision_parking_assist") is not True:
      release()
      return web.json_response({"status": "off"}, headers={"Cache-Control": "no-store"})
    loop = asyncio.get_running_loop()
    if idle_timer is not None:
      idle_timer.cancel()
    idle_timer = loop.call_later(PARKING_IDLE_SECONDS, release)
    if source is None:
      source = ParkingSource()
    if pending is None and loop.time() - last >= 0.16:
      pending = loop.run_in_executor(executor, source.sample)
    if pending is not None:
      session, work = source, pending
      try:
        sample = await asyncio.shield(work)
        if source is not session:
          return web.json_response({"status": "stale"}, headers={"Cache-Control": "no-store"})
        result = sample
      except Exception:
        logging.getLogger(__name__).debug("Parking source unavailable", exc_info=True)
        if source is not session:
          return web.json_response({"status": "stale"}, headers={"Cache-Control": "no-store"})
        result = {"status": "unavailable"}
      finally:
        if work.done() and pending is work:
          pending, last = None, loop.time()
    body = dict(result or {"status": "waiting"})
    if "captureTime" in body:
      age = camera_clock() - body.pop("captureTime")
      if not 0 <= age < 0.65:
        body = {"status": "stale"}
      else:
        body["ageMs"] = round(age * 1000)
    receipts.offered(body, time.monotonic())
    return web.json_response(body, headers={"Cache-Control": "no-store"})

  async def last_display(_request):
    return web.json_response(receipts.summary, headers={"Cache-Control": "no-store"})

  async def close(_app):
    release()
    await asyncio.to_thread(executor.shutdown, wait=True)

  app.on_cleanup.append(close)
  app.router.add_get("/api/vision/parking-scene", snapshot)
  app.router.add_get("/api/vision/parking-scene/last-display", last_display)
