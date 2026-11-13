"""Park-only, session-scoped offroad requests and their runtime interlock."""
import math
import threading
import time

REQUEST_KEY = "ForceOffroad"
ACTIVE_KEY = "ForceOffroadActive"
OBSERVER_KEY = "ForceOffroadObserver"
MAX_CAR_AGE = 0.5
MAX_SPEED = 0.05  # m/s; standstill and a confirmed Park gear are also required
SERVICES = ("carState", "carControl", "selfdriveState", "deviceState")


def fresh(sm, service, age, now):
  try:
    elapsed = now - sm.logMonoTime[service] / 1e9
    return bool(sm.seen[service] and sm.valid[service] and 0 <= elapsed <= age)
  except (AttributeError, KeyError, TypeError, ValueError):
    return False


def parked_reason(sm, now=None):
  now = time.monotonic() if now is None else now
  if not fresh(sm, "carState", MAX_CAR_AGE, now):
    return "vehicle_unavailable"
  try:
    state = sm["carState"]
    if not state.canValid:
      return "vehicle_unavailable"
    if str(state.gearShifter) != "park":
      return "park_required"
    speeds = (float(state.vEgo), float(state.vEgoRaw))
    if not state.standstill or any(not math.isfinite(v) or abs(v) > MAX_SPEED for v in speeds):
      return "moving"
  except (AttributeError, KeyError, TypeError, ValueError):
    return "vehicle_unavailable"
  return ""


def toggle_reason(sm, active=False, now=None):
  now = time.monotonic() if now is None else now
  reason = parked_reason(sm, now)
  if reason:
    return reason
  # These publishers stop offroad. A confirmed active session may be released
  # using fresh read-only carState plus hardwared's offroad deviceState.
  if active and fresh(sm, "deviceState", 1.5, now) and not sm["deviceState"].started:
    return ""
  if not all(fresh(sm, name, 0.5, now) for name in ("carControl", "selfdriveState")):
    return "controls_unavailable"
  try:
    control = sm["carControl"]
    if sm["selfdriveState"].enabled or control.enabled or control.latActive or control.longActive:
      return "controls_active"
  except (AttributeError, KeyError, TypeError):
    return "controls_unavailable"
  return ""


class OffroadPolicy:
  """hardwared owns activation; invalid/non-P state always releases the request."""
  def __init__(self):
    self.active = False
    self.reason = ""

  def update(self, requested, sm, ignition=True, now=None):
    self.reason = ""
    if requested and ignition:
      # Once activated, controls are stopped; only the live Park/zero-speed
      # observation is needed to retain it. Never latch an old Park snapshot.
      self.reason = parked_reason(sm, now) if self.active else toggle_reason(sm, now=now)
      self.active = not self.reason
    else:
      self.active = False
    return self.active


def release_observer(params, process):
  """Restart the read-only car process before reusing onroad initialization.

  CarParams and ControlsReady clear on the onroad transition. A retained car
  process cannot safely reuse that previous session's CI/Panda initialization.
  The explicit observer flag also catches a request cancelled between manager
  ticks, after card already stopped its control path.
  """
  if params.get_bool(REQUEST_KEY) or params.get_bool(ACTIVE_KEY):
    # Manager also records the retained process, even if card is temporarily
    # stalled and misses the entire request/activation interval.
    if not params.get_bool(OBSERVER_KEY):
      params.put_bool(OBSERVER_KEY, True)
    return False
  if params.get_bool(OBSERVER_KEY):
    process.stop()
    params.put_bool(OBSERVER_KEY, False)
    return True
  return False


def observer_failed(params, process):
  """Cancel rather than fingerprint/reinitialize a crashed observer offroad."""
  if (params.get_bool(REQUEST_KEY) or params.get_bool(ACTIVE_KEY)) and (process.proc is None or not process.proc.is_alive()):
    params.put_bool(REQUEST_KEY, False)
    return True
  return False


class OffroadService:
  """Same guarded write boundary for the native UI and HTTP API."""
  def __init__(self, params=None, sm=None):
    if params is None:
      from openpilot.common.params import Params
      params = Params()
    if sm is None:
      from openpilot.cereal import messaging
      sm = messaging.SubMaster(list(SERVICES))
    self.params, self.sm = params, sm
    self.lock = threading.RLock()

  def status(self):
    with self.lock:
      self.sm.update(0)
      requested = self.params.get_bool(REQUEST_KEY)
      active = self.params.get_bool(ACTIVE_KEY)
      reason = toggle_reason(self.sm, active)
      pending = requested != active
      return {"requested": requested, "active": active, "pending": pending,
              "can_toggle": not reason and not pending, "reason": reason or ("pending" if pending else "")}

  def request(self, enabled):
    if type(enabled) is not bool:
      raise ValueError("boolean_required")
    with self.lock:
      status = self.status()  # Re-read at the actual write, not just when rendering.
      if not status["can_toggle"]:
        raise PermissionError(status["reason"])
      self.params.put_bool(REQUEST_KEY, enabled)
      return self.status()


_service = None


def get_service():
  global _service
  if _service is None:
    _service = OffroadService()
  return _service
