import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.cereal import log
from openpilot.selfdrive.alpamayo.capture import state_value
from openpilot.selfdrive.alpamayo.frontend import CAMERAS, OFFSETS_NS, Frame, Preparer, State, Store, navigation
from openpilot.selfdrive.alpamayo.runtime import validate_input
from openpilot.selfdrive.carrot import carrot_serv

HUD = 'navInstructionCarrot'
NOW = 5_000_000_000
DEFAULT = 'Continue straight.'


@pytest.fixture
def sources(monkeypatch):
  monkeypatch.setattr(carrot_serv, 'Params', lambda *args: None)
  monkeypatch.setattr(carrot_serv.CarrotServ, 'update_params', lambda self: None)
  serv = carrot_serv.CarrotServ()
  class Native(dict):
    alive = valid = {'navInstruction': True}
  sm = Native(navInstruction=log.NavInstruction.new_message(maneuverType='turn', maneuverModifier='left', maneuverDistance=80))
  sm.logMonoTime = {'navInstruction': NOW-10}
  sent = {}
  def publish(stamp):
    def message(name, valid):
      event = log.Event.new_message(logMonoTime=stamp, valid=valid)
      event.init(name)
      return event
    monkeypatch.setattr(carrot_serv.messaging, 'new_message', message, raising=False)
    serv.send_nav_instruction(sm, SimpleNamespace(send=lambda name, event: sent.update({name: event.to_bytes()})))
    with log.Event.from_bytes(sent[HUD]) as event:
      value, valid = state_value(event.which(), event.navInstructionCarrot)
      return State(stamp, stamp, value if event.valid else None, valid and event.valid)
  return serv, sm, publish


def external(serv):
  serv.active_count, serv.active_carrot = 80, 2
  serv.nTBTTurnType, serv.nTBTDist = 13, 180
  serv._update_tbt()
  serv.xDistToTurn -= 87  # Dead-reckoned HUD distance since the external packet.


def test_hud_to_model_input(sources):
  serv, _, publish = sources
  external(serv)
  row = publish(NOW)
  assert (row.value['maneuverModifier'], row.value['maneuverDistance']) == ('right', int(serv.xDistToTurn))
  store = Store()
  assert HUD in store.states and 'navInstruction' not in store.states
  store.add_state(HUD, row.stamp, row.received, row.value)
  store.add_state('carParams', NOW-2_100_000_000, NOW-2_100_000_000,
                  dict(mass=1800., rotationalInertia=3000., wheelbase=2.9, centerToFront=1.3, steerRatioRear=0.,
                       tireStiffnessFront=100000., tireStiffnessRear=100000., steerRatio=15.))
  for stamp in range(NOW-2_100_000_000, NOW+1, 50_000_000):
    store.add_state('extrinsicsCalibration', stamp, stamp, dict(rpyCalib=[0.]*3, wideFromDeviceEuler=[0.]*3))
    store.add_state('carState', stamp, stamp, dict(vEgo=6., steeringAngleDeg=0., aEgo=0.))
    store.add_state('vehicleParameters', stamp, stamp, dict(centerToFrontRatio=.45, stiffnessFactor=1., steerRatio=15., angleOffsetDeg=0., roll=0.))
    store.add_state('deviceMotion', stamp, stamp, [[0.]*3, [6., 0., 0.]])
  pixels = np.zeros((3, 432, 768), dtype=np.uint8)
  pixels.flags.writeable = False
  for camera in CAMERAS:
    for fid, offset in enumerate(OFFSETS_NS):
      t = NOW+offset
      store.add_frame(Frame(camera, fid, t, t+1, t+2, t+2, pixels))
  cfg = json.loads((Path(__file__).parents[1]/'release.json').read_text())['config']
  prep = Preparer(cfg['geometry'], sampler=lambda image, *_: image,
                  default_navigation=cfg['default_navigation'], navigation_within_m=cfg['navigation_within_m'])
  arrays, meta = prep.prepare(store.select(NOW+3))
  validate_input(arrays, meta)
  assert arrays['nav_text'] == ['Turn right in 93m']
  assert meta['navigation']['instruction']['carrotSource'] == 'external'


def test_source_switch_and_cancellation(sources):
  serv, sm, publish = sources
  native = publish(NOW)
  external(serv)
  turn = publish(NOW+1)
  assert navigation([native, turn], NOW, DEFAULT, 150)[0] == DEFAULT
  assert navigation([native, turn], NOW+1, DEFAULT, 150)[0] == 'Turn right in 93m'
  serv.active_carrot = 1  # Connected without usable external guidance.
  assert not publish(NOW+2).valid
  serv.active_count = serv.active_carrot = 0
  assert not publish(NOW+3).valid  # Native message predates the external session.
  sm.logMonoTime['navInstruction'] = NOW+4
  resumed = publish(NOW+5)
  assert resumed.value['carrotSource'] == 'native'
  assert navigation([resumed], NOW+5, DEFAULT, 150)[0] == 'Turn left in 80m'
  assert navigation([resumed], NOW+2_000_000_004, DEFAULT, 150)[0] == DEFAULT
  assert not publish(NOW+2_000_000_004).valid


@pytest.mark.parametrize('distance,expected', [(150, 'Turn right in 150m'), (151, DEFAULT), (-.1, DEFAULT)])
def test_distance_boundary_and_passed_turn(sources, distance, expected):
  serv, _, publish = sources
  external(serv)
  serv.xDistToTurn = distance
  row = publish(NOW)
  assert navigation([row], NOW, DEFAULT, 150)[0] == expected
