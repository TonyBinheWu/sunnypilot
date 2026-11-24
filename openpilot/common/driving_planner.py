"""Persistent DrivingPlannerMode values, sampled at onroad startup."""
CAMERA_ONLY = 2
CAMERA_ONLY_AUTO = 3


def camera_only(mode):
  return mode in (CAMERA_ONLY, CAMERA_ONLY_AUTO)


def active_planner_mode(cp, params):
  mode = getattr(cp, "drivingPlannerMode", -1)
  return params.get_int("DrivingPlannerMode") if mode == -1 else mode


def auto_alpha_candidate(cp, *, recognized, release, stock_requested):
  return (recognized and not release and not stock_requested and not cp.dashcamOnly
          and cp.brand != "mock" and cp.alphaLongitudinalAvailable and not cp.openpilotLongitudinalControl)
