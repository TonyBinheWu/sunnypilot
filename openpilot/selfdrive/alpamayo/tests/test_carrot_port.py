from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.cereal import car, log
from openpilot.common import sunny_models
from openpilot.selfdrive.alpamayo import install
from openpilot.selfdrive.alpamayo.capture import state_value
from openpilot.selfdrive.alpamayo.carrot import strictly_parked
from openpilot.selfdrive.alpamayo.planner import MAX_LATENCY, PlanSelector
from openpilot.selfdrive.alpamayo.selected.frozen import manifest, verify_assets
from openpilot.selfdrive.controls.lib.near_radar import ClosingLead, occupied_side


class Subscribers(dict):
  def all_checks(self, keys):
    return self.valid


def observations():
  sm = Subscribers(carState=car.CarState.new_message(canValid=True, vEgo=3., gearShifter='drive'),
                   radarState=log.RadarState.new_message())
  sm.valid = True
  sm.logMonoTime = {}
  sm['radarState'].leadOne = dict(status=True, radar=True, radarTrackId=4, dRel=2.5, yRel=.1, vRel=-2.)
  return sm


def advance(sm, stamp):
  sm.logMonoTime.update(carState=stamp, radarState=stamp)
  sm['radarState'].carStateMonoTime = sm['radarState'].mdMonoTime = stamp
  return stamp


def confirmed(sm):
  guard = ClosingLead()
  for i in range(3):
    now = advance(sm, 1_000_000_000+50_000_000*i)
    assert guard.update(sm, now) == (i == 2)
  return guard, now


@pytest.mark.parametrize('reason', ['timestamp', 'future', 'can', 'fault', 'temporary', 'gear', 'speed', 'vision', 'identity', 'opening', 'far', 'nan', 'service'])
def test_front_radar_veto_releases(reason):
  sm = observations()
  guard, now = confirmed(sm)
  r, cs = sm['radarState'], sm['carState']
  now = advance(sm, now+50_000_000)
  if reason == 'timestamp': r.mdMonoTime -= 200_000_001
  elif reason == 'future': r.carStateMonoTime += 1
  elif reason == 'can': cs.canValid = False
  elif reason == 'fault': r.radarErrors.radarFault = True
  elif reason == 'temporary': r.radarErrors.radarUnavailableTemporary = True
  elif reason == 'gear': cs.gearShifter = 'reverse'
  elif reason == 'speed': cs.vEgo = 5.
  elif reason == 'vision': r.leadOne.radar = False
  elif reason == 'identity': r.leadOne.radarTrackId += 1
  elif reason == 'opening': r.leadOne.vRel = 1.
  elif reason == 'far': r.leadOne.dRel = 12.
  elif reason == 'nan': r.leadOne.yRel = float('nan')
  elif reason == 'service': sm.valid = False
  assert not guard.update(sm, now)


def test_duplicate_radar_samples_never_qualify():
  sm = observations()
  guard = ClosingLead()
  now = advance(sm, 1_000_000_000)
  assert not any(guard.update(sm, now+i) for i in range(10))


@pytest.mark.parametrize('side', ['left', 'right'])
def test_side_range_validity_and_oem_lamp(side):
  sm = observations()
  now = advance(sm, 3_000_000_000)
  field = 'leads'+side.title()
  other = 'left' if side == 'right' else 'right'
  lead = sm['radarState'].leadOne.to_dict()
  setattr(sm['radarState'], field, [dict(lead, radar=False)])
  assert occupied_side(sm, side, now) is False
  setattr(sm['radarState'], field, [lead])
  assert occupied_side(sm, side, now) is True
  assert occupied_side(sm, other, now) is False
  setattr(sm['radarState'], field, [])
  setattr(sm['carState'], side+'Blindspot', True)
  assert occupied_side(sm, side, now) is True
  assert occupied_side(sm, side, now+300_000_000) is None


def test_packet_handoff_and_local_action_schema():
  q = 2_000_000_000
  msg = log.Event.new_message()
  plan = msg.init('alpamayoPlan')
  plan.queryMonoTime, plan.readyMonoTime = q, q+200_000_000
  plan.x, plan.y, plan.yaw = np.arange(1, 65, dtype=float).tolist(), [0.]*64, [0.]*64
  selector = PlanSelector()
  selector.receive(plan, q+max(MAX_LATENCY, 900_000_000), q+200_000_000)
  assert selector.path is None
  selector.receive(plan, q+210_000_000, q+200_000_000)
  assert selector.query == q
  model = log.Event.new_message().init('modelV2')
  model.localAction = log.ModelDataV2.Action.new_message(desiredCurvature=.01)
  model.action = dict(desiredCurvature=-.01, desiredAcceleration=-.1, desiredVelocity=2., shouldStop=False)
  assert model.action.desiredCurvature < 0 < model.localAction.desiredCurvature


def test_catalog_and_pinned_assets():
  assert (True, 'lat2v', 'lat2v (Nvidia)') in sunny_models.model_items()
  assert not any(not big and key == 'lat2v' for big, key, _ in sunny_models.model_items())
  assert len(install.identity()) == 64
  verify_assets()
  assert len(manifest()['objects']) == 48


@pytest.mark.parametrize('on', ['IsOnroad', 'IsEngaged', 'ForceOffroad', 'ForceOffroadActive', None])
def test_parked_gate(on):
  flags = {'IsOffroad', on}
  assert strictly_parked(SimpleNamespace(get_bool=flags.__contains__)) is (on is None)
  flags.discard('IsOffroad')
  assert not strictly_parked(SimpleNamespace(get_bool=flags.__contains__))


def test_carrot_capture_wire_names():
  cs = car.CarState.new_message(canValid=True, vEgo=4.)
  assert state_value('carState', cs)[0]['vEgo'] == 4.
  cs.canValid = False
  assert not state_value('carState', cs)[1]


def test_first_selection_and_failed_validation_never_change_saved_choice(monkeypatch, tmp_path):
  from openpilot.selfdrive.alpamayo import carrot
  monkeypatch.setenv('CARROT_BIG_MODEL_DIR', str(tmp_path))
  sunny_models.save('big', None)
  def reject(*args):
    raise ValueError('recording did not qualify')
  monkeypatch.setattr(carrot, 'prepare_selection', reject)
  with pytest.raises(ValueError, match='did not qualify'):
    sunny_models.choose_model(True, 'lat2v', lambda: True)
  assert sunny_models.key_for(True) is None
  monkeypatch.setattr(carrot, 'prepare_selection', lambda *args: None)
  sunny_models.choose_model(True, 'lat2v', lambda: True)
  assert sunny_models.key_for(True) == 'lat2v'
  assert sunny_models.key_for(True, True) is None


def test_qualified_config_is_device_and_content_bound(tmp_path, monkeypatch):
  import hashlib
  monkeypatch.setattr(install, 'ROOT', tmp_path)
  config = tmp_path/'config.json'
  monkeypatch.setattr(install, 'CONFIG', config)
  config.write_text('{}')
  (tmp_path/'installed').write_text(hashlib.sha256(config.read_bytes()+install.identity().encode()).hexdigest())
  monkeypatch.setattr(install, 'qualification_id', lambda: 'device-a')
  assert install.complete() and not install.ready()
  (tmp_path/'qualified').write_text('device-b')
  assert not install.ready()
  (tmp_path/'qualified').write_text('device-a')
  assert install.ready()
  config.write_text('{"changed":true}')
  assert not install.complete() and not install.ready()
