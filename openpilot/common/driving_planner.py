"""Persistent DrivingPlannerMode values, sampled at onroad startup."""
CAMERA_ONLY = 2
CAMERA_ONLY_AUTO = 3
SUNNY_BLENDED = 4
SUNNY_RELEASE = 5
SUNNY_RELEASE_VISION = 6
SUNNY_PROFILES = {SUNNY_BLENDED: 'sunny', SUNNY_RELEASE: 'sunnyRelease', SUNNY_RELEASE_VISION: 'sunnyVision'}


def selected_sunny_mode(cp, selection):
  if cp.openpilotLongitudinalControl and not cp.passive and not cp.dashcamOnly:
    if selection == 1:
      return SUNNY_RELEASE_VISION if cp.radarUnavailable else SUNNY_RELEASE
    if selection == 2:
      return SUNNY_RELEASE_VISION
  return SUNNY_BLENDED


def automatic_longitudinal(mode):
  return mode in (CAMERA_ONLY_AUTO, SUNNY_BLENDED)


def camera_only(mode):
  return mode in (CAMERA_ONLY, CAMERA_ONLY_AUTO)


def active_planner_mode(cp, params):
  # Historical CarParams and saved settings can contain retired planner profiles.
  mode = getattr(cp, 'drivingPlannerMode', 0)
  if mode in (SUNNY_RELEASE, SUNNY_RELEASE_VISION):
    return mode
  return SUNNY_BLENDED


def auto_alpha_candidate(cp, *, recognized, release, stock_requested):
  return (recognized and not release and not stock_requested and not cp.dashcamOnly
          and cp.brand != "mock" and cp.alphaLongitudinalAvailable and not cp.openpilotLongitudinalControl)
