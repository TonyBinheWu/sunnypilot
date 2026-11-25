#!/usr/bin/env python3
"""Carrot's shared CPU map renderer; model, Web and USB reuse the same image."""
import os
import time

import numpy as np

from openpilot.selfdrive.navigation.helpers import ParkedPosition, approach_maneuver
from openpilot.selfdrive.navigation.jetlink_demand import jetlink_map_demand
from openpilot.selfdrive.navigation.pmtiles import PMTiles
from openpilot.selfdrive.navigation.preview import write_preview, write_navigation_view, preview_fresh, WEB_DEMAND_PATH
from openpilot.selfdrive.navigation.renderer import SIZE, MapRenderer, Position
from openpilot.selfdrive.navigation.route import RouteTracker, route_coordinates


def render_interval(cpu_seconds):
  # At most 10 Hz / approximately 10% of one CPU. A >40 ms render can cause
  # the model's unchanged 500 ms freshness gate to reject the map.
  return max(.1, cpu_seconds * 10)


def main():
  from openpilot.selfdrive.navigation.shortbread import ShortbreadTiles, local_source
  from openpilot.selfdrive.navigation.tiles import RemoteTiles
  from openpilot.selfdrive.navigation.mapbox_tiles import MapboxTiles
  import openpilot.cereal.messaging as messaging
  from openpilot.common.params import Params
  from msgq.visionipc import VisionIpcServer, VisionStreamType
  from openpilot.common.realtime import Ratekeeper
  from openpilot.common.runtime_diagnostics import RuntimeDiagnostics
  from openpilot.common.swaglog import cloudlog

  # Auxiliary work shares only the little cores. Never compete at FIFO priority
  # with camera/control, radar, driving model or DM on cores 4..7.
  if hasattr(os, 'sched_setaffinity'):
    os.sched_setscheduler(0, os.SCHED_OTHER, os.sched_param(0))
    allowed = os.sched_getaffinity(0) & {0, 1, 2, 3}
    if allowed:
      os.sched_setaffinity(0, allowed)
    os.nice(15)
  sm = messaging.SubMaster(['carrotMan', 'gpsLocation', 'gpsLocationExternal', 'navRoute', 'navInstructionCarrot', 'carState'])
  pm = messaging.PubMaster(['mapRenderState'])
  position = ParkedPosition()
  server = VisionIpcServer('mapsd')
  server.create_buffers_with_sizes(VisionStreamType.VISION_STREAM_MAP, 4, SIZE, SIZE, SIZE * SIZE, SIZE, SIZE * SIZE)
  server.start_listener()
  params = Params()
  demand_checked, demand = 0., False
  offline_source = None
  mapbox_token = ''
  archive_created = 0.
  diagnostics = RuntimeDiagnostics('mapsd', cloudlog.event, interval=5.)
  rk = Ratekeeper(10., print_delay_threshold=None)
  route, tracker, archive, renderer = np.empty((0, 2)), None, None, None
  retry_at = next_render = render_budget_at = next_preview = next_view = 0.
  last_match = None
  matched_since = 0
  last_matched_fix = None
  next_report = 0.
  route_id = 0
  image = np.zeros((SIZE, SIZE), np.uint8)
  try:
    while True:
      sm.update(0)
      now = time.monotonic()
      now_ns = int(now * 1e9)
      active_route = sm['navRoute'].carrotRouteId if sm.valid['navRoute'] else 0
      if sm.updated['navRoute'] and active_route != route_id:
        route_id = active_route
        route = route_coordinates(sm['navRoute']) if sm.valid['navRoute'] else np.empty((0, 2))
        tracker = RouteTracker(route) if route_id and 2 <= len(route) <= 4096 and np.isfinite(route).all() else None
        last_matched_fix = None
        next_render = 0.
      gps = position.update(sm)
      tbt_stamp = sm.logMonoTime['navInstructionCarrot']
      tbt_age = (now_ns - tbt_stamp) * 1e-9
      fresh_tbt = sm.valid['navInstructionCarrot'] and tbt_stamp >= route_id and 0 <= tbt_age < 2.
      fresh_route = sm.valid['navRoute'] and 0 <= now_ns - sm.logMonoTime['navRoute'] < 5_000_000_000
      if demand and now >= next_view:
        # A separate UI-only route copy; route/model rendering below is intact.
        try:
          write_navigation_view(route, gps, route_id if tracker is not None else 0,
                                instruction=sm['navInstructionCarrot'] if fresh_tbt else None)
        except (OSError, ValueError, TypeError):
          pass
        next_view = now + 1.
      # Navigation without usable position/instruction immediately publishes black.
      if now >= demand_checked:
        demand = (params.get_bool('UsbGpuActive') or jetlink_map_demand(now=now) or
                  params.get_int('ClusterHudScreenMode') == 7 or preview_fresh(WEB_DEMAND_PATH))
        token = os.environ.get('MAPBOX_TOKEN') or params.get('MapboxPublicKey') or ''
        if isinstance(token, bytes):
          token = token.decode('utf-8')
        installed = local_source(gps) if demand else None
        if installed != offline_source or token != mapbox_token or (archive is not None and now - archive_created >= 3600):
          if archive is not None:
            archive.close()
          archive = renderer = None
          retry_at = next_render = 0.
          mapbox_token, offline_source = token, installed
        demand_checked = now + 1.
      match, pose, approach = 'unavailable', None, ''
      if fresh_route and fresh_tbt and tracker is not None and gps is not None:
        advance = gps.speed * (now - gps.time)
        if last_matched_fix is not None and gps.fix_time - last_matched_fix > 2.:
          # After a GNSS gap the car can be beyond the previous segment window (e.g. a tunnel).
          tracker.progress = -np.inf
          last_matched_fix = None
        previous_progress = tracker.progress
        match, pose = tracker.match_pose(gps.longitude, gps.latitude, advance, course=gps.course)
        if pose is not None:
          step = approach_maneuver(sm['navInstructionCarrot'].allManeuvers, gps.speed, tbt_age)
          if step is not None:
            approach, distance = step
            if tracker.contradicts_turn(approach, advance + distance):
              tracker.progress = previous_progress
              match, pose = 'instructionConflict', None
          if pose is not None:
            last_matched_fix = gps.fix_time
      state = (route_id, match, approach, demand)
      changed = state != last_match
      if last_match is None or state[:2] != last_match[:2]:
        matched_since = now_ns if match == 'matched' else 0
      # Publish independently of tile requests. Control consumers check the original fix and report ages.
      if changed or now >= next_report:
        msg = messaging.new_message('mapRenderState', valid=True)
        report = msg.mapRenderState
        report.carrotRouteId, report.routeMatch = route_id, match
        report.approachManeuver = approach
        report.locationMonoTime = int(gps.fix_time * 1e9) if gps is not None else 0
        report.matchedSinceMonoTime = matched_since
        report.frameId = rk.frame
        pm.send('mapRenderState', msg)
        next_report = now + .5
      last_match = state
      want_tiles = demand and pose is not None
      if changed:
        next_render = render_budget_at if want_tiles else 0.
      if now >= next_render and (not want_tiles or now >= render_budget_at):
        started, cpu_started = time.monotonic(), time.process_time()
        image.fill(0)
        valid = False
        reason = ('idle' if not demand else 'route' if tracker is None or not fresh_route else 'position' if gps is None else
                  'instruction' if not fresh_tbt else 'route_position' if match == 'offRoute' else match if pose is None else 'tiles')
        try:
          if want_tiles and now >= retry_at:
            if renderer is None:
              if offline_source:
                archive = ShortbreadTiles(*offline_source)
              else:
                archive = MapboxTiles(mapbox_token) if mapbox_token else PMTiles(RemoteTiles())
              archive_created = now
              renderer = MapRenderer(archive)
            # Fetch only the current view; do not prefetch a whole country/route.
            lon, lat, bearing = pose
            result = renderer.render(Position(lat, lon, bearing), route)
            valid = result.valid
            reason = 'ready' if valid else 'tiles'
            if valid:
              image = result.image
        except (OSError, ValueError, RuntimeError):
          cloudlog.warning('mapsd: map unavailable; retry in 30 seconds')
          if archive is not None:
            archive.close()
          archive = renderer = None
          retry_at = time.monotonic() + 30.
        finished = time.monotonic()
        if finished - started >= .5:
          image.fill(0)
          valid = False
          reason = 'slow'
        cpu = time.process_time() - cpu_started
        interval = render_interval(cpu)
        if want_tiles:
          render_budget_at = finished + interval
        next_render = finished + (interval if valid else max(1., interval))
        # Timestamp at render START prevents a slow tile request looking fresh.
        server.send(VisionStreamType.VISION_STREAM_MAP, image.tobytes(), rk.frame,
                    route_id if valid else 0, int(started * 1e9))
        if finished >= next_preview:
          write_preview(image, reason=reason)
          next_preview = finished + .5
        diagnostics.record(render_ms=(finished - started) * 1000, cpu_ms=cpu * 1000,
                           context={'map_valid': valid, 'route_points': len(route), 'interval': interval,
                                    'parked_position_hold': position.held})
      rk.keep_time()
  finally:
    if archive is not None:
      archive.close()


if __name__ == '__main__':
  main()
