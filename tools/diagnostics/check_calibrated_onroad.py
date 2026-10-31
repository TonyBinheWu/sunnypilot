"""Host-only calibrated onroad regression; no camera, CAN or control process starts."""
import importlib
import os
import time
import unittest
from unittest import mock

import numpy as np
import pyray as rl

from openpilot.cereal import messaging
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.ui_state import UIStatus, ui_state
from openpilot.system.ui.lib.application import gui_app


class TestCalibratedOnroad(OpenpilotTestCase):
  def test_calibration_transition_and_overlays(self):
    big = os.environ["EXPECTED_DEVICE"] == "tizi"
    self.assertEqual(gui_app.big_ui(), big)
    package = "openpilot.selfdrive.ui.onroad" if big else "openpilot.selfdrive.ui.mici.onroad"
    road = importlib.import_module(package + ".augmented_road_view")
    gui_app.init_window("Calibrated onroad regression")
    view = None
    try:
      # Production refreshes persisted settings before a calibrated onroad session.
      # Do not confuse an uninitialized test fixture with a post-calibration fault.
      ui_state.update_params()
      sm = ui_state.sm
      ui_state.started = True
      ui_state.ignition = True
      ui_state.started_frame = 1
      ui_state.started_time = time.monotonic() - 10
      ui_state.is_metric = True
      ui_state.chevron_metrics = 4
      ui_state.navigation_enabled = False
      ui_state.nav_destination_set = False
      ui_state.active_bundle = None
      ui_state.always_on_dm = False

      def message(service, values):
        event = messaging.new_message(service)
        setattr(event, service, values)
        sm.data[service] = getattr(event, service)
        sm.valid[service] = sm.alive[service] = sm.seen[service] = sm.updated[service] = True
        sm.recv_frame[service] = 10
        sm.recv_time[service] = time.monotonic()
        return sm.data[service]

      x = np.linspace(0, 100, 33).tolist()
      t = np.linspace(0, 10, 33).tolist()
      def line(y):
        return {"x": x, "y": [y] * 33, "z": [0.0] * 33, "t": t}
      message("modelV2", {"position": line(0.0),
                         "velocity": {"x": [10.0] * 15 + [0.0] * 18, "t": t},
                         "acceleration": {"x": [-0.5] * 33},
                         "laneLines": [line(y) for y in (-3.6, -1.8, 1.8, 3.6)],
                         "roadEdges": [line(-4.5), line(4.5)],
                         "laneLineProbs": [0.9] * 4, "roadEdgeStds": [0.1, 0.1],
                         "action": {"shouldStop": True}})
      message("deviceState", {"deviceType": "tizi" if big else "mici", "started": True})
      message("narrowRoadCameraState", {"sensor": "ox03c10"})
      message("carState", {"vEgo": 10.0, "aEgo": -0.5})
      cp = message("carParams", {"openpilotLongitudinalControl": True})
      ui_state.CP = cp
      message("longitudinalPlan", {"allowThrottle": True})
      message("carOutput", {})
      message("selfdriveStateSP", {"mads": {"available": False}})
      message("driverStateV2", {"leftDriverData": {"faceOrientation": [0.05, -0.08, 0.01]},
                                "rightDriverData": {"faceOrientation": [-0.03, 0.06, -0.01]}})
      message("driverMonitoringState", {})
      view = road.AugmentedRoadView()
      rect = rl.Rectangle(0, 0, gui_app.width, gui_app.height)
      renderer = view.model_renderer if big else view._model_renderer

      # Preserve all overlay code; replace only the unavailable host camera transport.
      def render_camera(camera, content_rect):
        matrix = camera._calc_frame_matrix(content_rect)
        self.assertTrue(np.isfinite(matrix).all())
        rl.draw_rectangle_rec(content_rect, rl.BLACK)

      with mock.patch.object(road.CameraView, "_render", render_camera):
        for calibrated in (False, True):
          message("extrinsicsCalibration", {"calStatus": "calibrated" if calibrated else "uncalibrated",
                                            "rpyCalib": [0.01, -0.02, 0.01], "wideFromDeviceEuler": [0.0, 0.0, 0.0],
                                            "height": [1.22]})
          for status in UIStatus:
            for style in ("normal", "experimental", "rainbow", "blue"):
              with self.subTest(calibrated=calibrated, status=status.name, style=style):
                print(f"CASE device={os.environ['EXPECTED_DEVICE']} calibrated={calibrated} status={status.name} style={style}", flush=True)
                ui_state.status = status
                ui_state.rainbow_path = style in ("rainbow", "blue")
                ui_state.rainbow_mode_style = 1 if style == "blue" else 0
                ui_state.predicted_stop_marker = True
                message("selfdriveState", {"experimentalMode": style == "experimental", "enabled": status == UIStatus.ENGAGED})
                message("radarState", {"leadOne": {"present": True, "dRel": 30.0, "vRel": -1.0, "yRel": 0.0}})
                for service in ("modelV2", "carState"):
                  sm.recv_time[service] = time.monotonic()
                for _ in range(2):
                  rl.begin_drawing()
                  try:
                    view.render(rect)
                  finally:
                    rl.end_drawing()
                self.assertGreater(len(renderer._path.projected_points), 0, "Fixture did not exercise projected path")
                self.assertTrue(np.isfinite(renderer._path.projected_points).all())
    finally:
      if view is not None:
        view.close()
      rl.close_window()


if __name__ == "__main__":
  unittest.main(verbosity=2)
