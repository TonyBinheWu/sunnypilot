#!/usr/bin/env python3
import time

from openpilot.cereal import car
from openpilot.common.params import Params
from openpilot.common.realtime import Priority, config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.common.runtime_diagnostics import RuntimeDiagnostics
from openpilot.selfdrive.controls.lib.ldw import LaneDepartureWarning
from openpilot.selfdrive.controls.lib.lateral_planner import LateralPlanner
import openpilot.cereal.messaging as messaging
from openpilot.selfdrive.controls.lib.upstream_planner import LongitudinalPlanner


def main():
  # Keep planning off camera/model cores and away from card's FIFO53 on core5.
  # Planner and radarcan share core4/FIFO51; controlsd/selfdrived use core6.
  config_realtime_process(4, Priority.CTRL_LOW)

  cloudlog.info("plannerd is waiting for CarParams")
  params = Params()
  CP = messaging.log_from_bytes(params.get("CarParams", block=True), car.CarParams)
  cloudlog.info("plannerd got CarParams: %s", CP.brand)

  ldw = LaneDepartureWarning()
  longitudinal_planner = LongitudinalPlanner(CP, sunny=True)
  lateral_planner = LateralPlanner(CP, debug=False)
  pm = messaging.PubMaster(['longitudinalPlan', 'driverAssistance', 'lateralPlan'])
  sm = messaging.SubMaster(
    ['carControl', 'carState', 'controlsState', 'liveParameters', 'radarState',
     'modelV2', 'selfdriveState', 'carrotMan', 'carrotNavi', 'livePose', 'navInstruction'],
    poll='modelV2',
    ignore_avg_freq=['radarState'],
  )
  model_frame = 0
  last_longitudinal_trigger_mono_ns = 0
  diagnostics = RuntimeDiagnostics('plannerd', cloudlog.event)

  while True:
    wait_start = time.monotonic()
    sm.update()
    loop_start, cpu_start = time.monotonic(), time.thread_time()
    timings = {'poll_ms': (loop_start - wait_start) * 1000}

    trigger_mono_ns = sm.logMonoTime['modelV2']
    run_longitudinal = sm.updated['modelV2'] and (
      last_longitudinal_trigger_mono_ns == 0 or trigger_mono_ns - last_longitudinal_trigger_mono_ns >= 25_000_000
    )
    if run_longitudinal:
      last_longitudinal_trigger_mono_ns = trigger_mono_ns
      planner_start = time.monotonic()
      longitudinal_planner.update(sm)
      longitudinal_planner.publish(sm, pm)
      timings['longitudinal_ms'] = (time.monotonic() - planner_start) * 1000

    if sm.updated['modelV2']:
      lateral_start = time.monotonic()
      timings['model_age_at_lateral_ms'] = (lateral_start - sm.logMonoTime['modelV2'] * 1e-9) * 1000
      model_frame += 1
      lateral_planner.update(sm)
      lateral_planner.publish(sm, pm)

      ldw.update(model_frame, sm['modelV2'], sm['carState'], sm['carControl'])
      msg = messaging.new_message('driverAssistance')
      msg.valid = sm.all_checks(['carState', 'carControl', 'modelV2', 'liveParameters'])
      msg.driverAssistance.leftLaneDeparture = ldw.left
      msg.driverAssistance.rightLaneDeparture = ldw.right
      pm.send('driverAssistance', msg)
      timings['lateral_and_assistance_ms'] = (time.monotonic() - lateral_start) * 1000

    diagnostics.record(
      context={'planning_trigger': 'modelV2', 'model_frame_id': int(sm['modelV2'].frameId)},
      work_ms=(time.monotonic() - loop_start) * 1000, thread_cpu_ms=(time.thread_time() - cpu_start) * 1000,
      model_updated=int(sm.updated['modelV2']), longitudinal_run=int(run_longitudinal and sm.seen['modelV2']), **timings,
    )


if __name__ == "__main__":
  main()
