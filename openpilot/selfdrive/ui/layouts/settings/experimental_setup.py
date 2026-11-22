from opendbc.car.hyundai.values import HyundaiFlags
from opendbc.car.selected_car import detected_ev6_for_verification
from openpilot.system.ui.lib.multilang import tr


def auto_setup_status(cp, params, is_release):
  """Return the stored request, whether a new request is possible, and a UI explanation."""
  requested = params.get("AutoExperimentalPlatform")
  if is_release:
    return False, False, tr("Requires a development branch")
  if cp is None or cp.brand == "mock":
    if requested and params.get("AutoExperimentalIssue") == "wiring":
      return True, False, tr("CAN wiring mismatch")
    if requested and params.get("AutoExperimentalIssue") == "identity":
      return True, False, tr("Vehicle match unconfirmed")
    detected = detected_ev6_for_verification(cp, params)
    if detected and not requested:
      return False, True, tr("Verify at next vehicle start")
    return bool(requested), False, tr("Vehicle identification needed")
  if cp.dashcamOnly or cp.passive:
    return bool(requested), False, tr("Vehicle controls unavailable")
  if requested and requested != cp.carFingerprint:
    return True, False, tr("Set for a different vehicle")
  if cp.brand == "hyundai" and params.get_int("HyundaiCameraSCC") == 3:
    return bool(requested), bool(cp.flags & HyundaiFlags.CANFD), tr("Stock cruise selected")
  if cp.openpilotLongitudinalControl:
    return bool(requested), True, tr("Experimental mode available")
  # A manually selected Hyundai CAN-FD car can lack its ADAS firmware
  # because manual identification normally skips the firmware query.
  needs_query = (cp.brand == "hyundai" and cp.flags & HyundaiFlags.CANFD and
                 cp.fingerprintSource == "fixed" and not cp.carFw)
  if cp.alphaLongitudinalAvailable or needs_query or detected_ev6_for_verification(cp, params):
    return bool(requested), True, tr("Verify at next vehicle start")
  return bool(requested), False, tr("Experimental longitudinal unavailable")


def set_auto_setup(enabled, ui):
  requested, available, _ = auto_setup_status(ui.CP, ui.params, ui.is_release)
  if not ui.is_offroad() or ui.is_release:
    return
  if enabled and available:
    ui.params.put("AutoExperimentalPlatform", detected_ev6_for_verification(ui.CP, ui.params) or ui.CP.carFingerprint)
  elif not enabled and requested:
    ui.params.remove("AutoExperimentalPlatform")
