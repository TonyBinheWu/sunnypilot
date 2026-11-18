from types import SimpleNamespace as NS

import pytest

from openpilot.common.lane_change_notice import fresh_notice, notice_state


@pytest.mark.parametrize('source,kind', [('forecast_desire', 'forecast'), ('forecast_path', 'forecast'),
  ('navigation_exit', 'exit'), ('lane_completed', 'completed'), ('lane_cancelled', 'cancelled'), ('lane_unverified', 'unverified')])
@pytest.mark.parametrize('direction', ['left', 'right'])
def test_display_metadata_distinguishes_prediction_execution_and_confirmation(source, kind, direction):
  assert notice_state(NS(indicatorPrepareDirection=direction, indicatorPrepareSource=source)) == (kind, direction)
  assert notice_state(NS(indicatorPrepareDirection=direction, indicatorPrepareSource='unknown')) is None


class SM(dict):
  pass


def test_completed_notice_is_not_replaced_by_a_held_lamp_waiting_for_new_driver_intent():
  meta = NS(laneChangeState='preLaneChange', laneChangeDirection='left', indicatorPrepareDirection='left', indicatorPrepareSource='lane_completed')
  assert notice_state(meta) == ('completed', 'left')
  meta.indicatorPrepareSource = 'lane_waiting_driver'
  assert notice_state(meta) is None


@pytest.mark.parametrize('blocked', ['stale', 'critical', 'park', 'off', 'can', 'invalid'])
def test_notice_never_outlives_live_driving_or_covers_a_native_alert(blocked):
  sm = SM(modelV2=NS(meta=NS(indicatorPrepareDirection='left', indicatorPrepareSource='forecast_desire')),
          carState=NS(canValid=blocked != 'can', canTimeout=False, vEgo=30., gearShifter='park' if blocked == 'park' else 'drive', steeringPressed=False),
          carControl=NS(latActive=blocked != 'off'), selfdriveState=NS(alertSize='full' if blocked == 'critical' else 'none'))
  sm.valid, sm.alive, sm.recv_time = dict.fromkeys(sm, True), dict.fromkeys(sm, True), dict.fromkeys(sm, 10.)
  if blocked == 'invalid':
    sm.valid['modelV2'] = False
  assert fresh_notice(sm, 10.6 if blocked == 'stale' else 10.1) is None
