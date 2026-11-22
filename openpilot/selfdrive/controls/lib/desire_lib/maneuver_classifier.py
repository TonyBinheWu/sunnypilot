from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL
from .constants import BLINKER_LEFT, BLINKER_RIGHT

def signalled_turn_probability(model, direction):
  values = getattr(getattr(model, "meta", None), "desireState", ())
  if direction not in (BLINKER_LEFT, BLINKER_RIGHT) or len(values) <= BLINKER_RIGHT:
    return 0.
  selected, opposite = values[direction], values[3 - direction]
  return selected if 0 <= opposite < selected <= 1 else 0.


def driver_started_turn(car, side, direction, probability):
  """Driver and model agree on a slow turn even if the far curb is occluded."""
  sign = 1 if direction == BLINKER_LEFT else -1
  return (direction in (BLINKER_LEFT, BLINKER_RIGHT) and 0 < car.vEgo < 30 * CV.KPH_TO_MS
          and str(getattr(car, 'gearShifter', '')) == 'drive' and car.canValid and not car.trailerConnected
          and car.steeringPressed and sign * car.steeringTorque > 0 and sign * car.steeringAngleDeg >= 20
          and probability >= .5 and not side.lane_available and not side.side_object_detected
          and side.bsd_hold_counter == 0
          and not (car.leftBlindspot if direction == BLINKER_LEFT else car.rightBlindspot))


def classify_maneuver_type(blinker_state: int,
                           carstate,
                           side,                 # SideState
                           turn_desire_state: bool,
                           atc_type: str,
                           old_type: str):
  if blinker_state == 0:
    return "none"

  v_kph = carstate.vEgo * CV.MS_TO_KPH
  accel = carstate.aEgo

  score_turn = 0
  if v_kph < 30.0:
    score_turn += 1
  elif v_kph < 40.0 and accel < -1.0:
    score_turn += 1

  # 차로 없고 edge 여유도 없으면 turn 가산
  if v_kph < 40.0 and (not side.lane_available) and (not side.edge_available):
    score_turn += 1

  # 차선이 잘 안 보이면(교차로 등)
  if v_kph < 40.0 and side.lane_exist_count.counter < int(0.5 / DT_MDL):
    score_turn += 1

  if turn_desire_state:
    score_turn += 1

  if atc_type in ("turn left", "turn right"):
    score_turn += 2
  elif atc_type in ("fork left", "fork right", "atc left", "atc right"):
    score_turn -= 2

  edge_far = side.dist_to_edge_far > 4.0

  if score_turn >= 2:
    if edge_far:
      return "turn"
    return old_type
  return "lane_change"
