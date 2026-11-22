"""Verify normal UI scheduling before applying onroad/offroad display placement."""
import os
import sys

from openpilot.common.realtime import drop_realtime
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware import PC

_VERIFY_ATTEMPTS = 2  # bounded 재시도 — 무한/매 프레임 syscall 폭주 금지


def ensure_ui_sched_other() -> None:
  """UI 메인 스레드를 SCHED_OTHER로 명시 강등하고 readback으로 검증한다.

  검증 실패는 fail-stop — RT policy UI가 센서·위치 추정을 굶기며 계속
  실행되는 것보다 manager 재시작(restart_if_crash)이 낫다 (fail-closed).
  readback이 SCHED_OTHER가 아니면 성공 로그를 내지 않는다 (false success 금지)."""
  if sys.platform != "linux" or PC:
    return  # RT 스케줄링이 없는 환경 — 계약 자체가 불필요
  policy = None
  for _ in range(_VERIFY_ATTEMPTS):
    try:
      drop_realtime()
      policy = os.sched_getscheduler(0)
    except OSError:
      continue
    if policy == os.SCHED_OTHER:
      cloudlog.info("UISCHED: UI SCHED_OTHER verified (core0 bootstrap)")
      return
  cloudlog.critical(f"UISCHED: UI could not be verified SCHED_OTHER (policy={policy}); fail-stop")
  raise RuntimeError("UI must run SCHED_OTHER (realtime preemption contract)")


class C4DisplayRate:
  """Give modeld its 50 ms cycle before using spare time for display frames."""
  def __init__(self):
    self.healthy_since = None

  def target(self, started, sm, now):
    if not started:
      self.healthy_since = None
      return 60
    model = sm["modelV2"]
    healthy = (sm.valid["modelV2"] and sm.alive["modelV2"] and 0 <= now - sm.recv_time["modelV2"] < 0.15
               and 0 < model.modelExecutionTime <= 0.045 and 0 <= model.frameDropPerc < 1)
    if not healthy:
      self.healthy_since = None
      return 20
    if self.healthy_since is None:
      self.healthy_since = now
    return 60 if now - self.healthy_since >= 2.0 else 20
