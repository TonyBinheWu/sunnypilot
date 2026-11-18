import pytest

from openpilot.cereal import log
from openpilot.selfdrive.carrot.realtime.compact_state import encode_carrot_state_frame
from openpilot.selfdrive.carrot.realtime.compact_state_pyx import encode_frame


@pytest.mark.parametrize('phase', ['off', 'preLaneChange', 'laneChangeStarting', 'laneChangeFinishing'])
@pytest.mark.parametrize('direction', ['none', 'left', 'right'])
@pytest.mark.parametrize('source', ['', 'forecast_desire', 'forecast_path', 'navigation_exit', 'lane_completed', 'lane_cancelled', 'lane_unverified'])
def test_real_native_encoder_matches_python_for_app_maneuver_metadata(phase, direction, source):
  event = log.Event.new_message()
  md = event.init('modelV2')
  md.frameId = 41
  md.position.x, md.position.y = [0., 12.], [0., -.5]
  md.meta.laneChangeState = phase
  md.meta.laneChangeDirection = direction
  md.meta.indicatorPrepareDirection = direction
  md.meta.indicatorPrepareSource = source
  assert encode_frame('modelV2', event.to_bytes(), 17) == encode_carrot_state_frame('modelV2', md, 17)


@pytest.mark.parametrize('can_valid', [False, True])
@pytest.mark.parametrize('timeout', [False, True])
@pytest.mark.parametrize('pressed', [False, True])
def test_real_native_encoder_preserves_notice_health_and_takeover_gates(can_valid, timeout, pressed):
  event = log.Event.new_message()
  cs = event.init('carState')
  cs.canValid, cs.canTimeout, cs.steeringPressed = can_valid, timeout, pressed
  cs.gearShifter, cs.vEgo = 'drive', 30.
  cs.laneLineInfoMonoTime = 123456789012 if can_valid else 0
  assert encode_frame('carState', event.to_bytes(), 17) == encode_carrot_state_frame('carState', cs, 17)
