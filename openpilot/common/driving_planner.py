"""Persistent DrivingPlannerMode values, sampled at onroad startup."""
CAMERA_ONLY = 2
CAMERA_ONLY_AUTO = 3
SUNNY_BLENDED = 4


def automatic_longitudinal(mode):
  return mode in (CAMERA_ONLY_AUTO, SUNNY_BLENDED)


def camera_only(mode):
  return mode in (CAMERA_ONLY, CAMERA_ONLY_AUTO)


def active_planner_mode(cp, params):
  # Historical CarParams and saved settings can contain retired planner profiles.
  return SUNNY_BLENDED


def auto_alpha_candidate(cp, *, recognized, release, stock_requested):
  return (recognized and not release and not stock_requested and not cp.dashcamOnly
          and cp.brand != "mock" and cp.alphaLongitudinalAvailable and not cp.openpilotLongitudinalControl)
