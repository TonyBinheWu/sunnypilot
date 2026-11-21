import time
from types import SimpleNamespace

import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car import Bus, gen_empty_fingerprint, interfaces, structs
from opendbc.car.hyundai import carstate, hyundaicanfd, interface
from opendbc.car.hyundai.fingerprints import FW_VERSIONS
from opendbc.car.hyundai.values import CAR, HyundaiExtFlags, HyundaiFlags, HyundaiSafetyFlags


@pytest.mark.parametrize('longitudinal,hda2,camera,bosch,expects_scc', [
  (True, True, False, False, False),
  (False, True, False, False, True),
  (True, True, True, False, True),
  (True, True, False, True, True),
  (True, False, False, False, True),
])
def test_startup_scc_frame_and_required_brake_feedback(monkeypatch, longitudinal, hda2, camera, bosch, expects_scc):
  monkeypatch.setattr(carstate, 'Params', lambda: SimpleNamespace(get_bool=lambda key: True))
  flags = HyundaiFlags.CANFD | (HyundaiFlags.CANFD_HDA2 if hda2 else 0) | (HyundaiFlags.CANFD_CAMERA_SCC if camera else 0)
  cp = structs.CarParams(carFingerprint=str(CAR.KIA_EV6), flags=int(flags), openpilotLongitudinalControl=longitudinal,
                         extFlags=int(HyundaiExtFlags.BOSCH_RADAR) if bosch else 0)
  state = SimpleNamespace(CP=cp, controls_ready_count=119, scc_control=None,
                          _update_camera_scc_hint=lambda *_: None, _discover_canfd_camera_tx_messages=lambda *_: None)
  dbc = 'hyundai_canfd_generated'
  pt = CANParser(dbc, [], 1)
  cam = CANParser(dbc, [], 2)
  pt.controls_ready = cam.controls_ready = True
  parser = cam if camera else pt
  packer = CANPacker(dbc)
  started = time.monotonic_ns()
  parsers = {Bus.pt: pt, Bus.cam: cam}
  startup = [(started, [packer.make_can_msg('SCC_CONTROL', parser.bus, {}), packer.make_can_msg('TCS', pt.bus, {})])]
  for stream in parsers.values():
    stream.update(startup)
  for _ in range(2):
    carstate.CarState.monitor_fingerprint(state, parsers, True)
  assert ('SCC_CONTROL' in parser.vl) == expects_scc
  assert 'TCS' in pt.vl
  for tick in range(320):
    now = started + tick * 20_000_000
    packets = [packer.make_can_msg('TCS', pt.bus, {})] if tick < 260 else []
    # Host echoes cannot satisfy OEM input checks.
    packets.append(packer.make_can_msg('SCC_CONTROL', parser.bus + 128, {}))
    for stream in parsers.values():
      stream.update([(now, packets)])
    valid = pt.can_valid and (cam.can_valid if camera else True)
    if tick == 250:
      assert valid == (not expects_scc)
  assert not pt.can_valid


def configure_params(monkeypatch, settings):
  class Params:
    def get_int(self, key): return int(settings.get(key, 0))
    def get_bool(self, key): return bool(settings.get(key, False))
    def get(self, key): return settings.get(key, '')
    def put_bool(self, key, value): pass

  for module in (interface, interfaces, hyundaicanfd):
    monkeypatch.setattr(module, 'Params', Params)


@pytest.mark.parametrize('addr,dlc,adas,manual,alpha,hda2,host_long', [
  (0x50, 16, True, False, True, True, True), (0x110, 32, True, False, False, True, False),
  (0x50, 8, True, False, False, False, False), (0x50, 16, False, True, True, True, False),
])
def test_ev6_harness_and_longitudinal_owner(monkeypatch, addr, dlc, adas, manual, alpha, hda2, host_long):
  fingerprint = gen_empty_fingerprint()
  fingerprint[2][addr] = dlc
  settings = {'CanfdHDA2': int(manual), 'FingerPrints': repr(fingerprint)}

  configure_params(monkeypatch, settings)
  fw = [structs.CarParams.CarFw(ecu='adas')] if adas else []
  cp = interface.CarInterface.get_params(CAR.KIA_EV6, fingerprint, fw, alpha, False, False)
  assert bool(cp.flags & HyundaiFlags.CANFD_HDA2) == hda2
  assert cp.openpilotLongitudinalControl == host_long
  assert cp.pcmCruise != host_long
  assert bool(cp.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.LONG) == host_long


@pytest.mark.parametrize('platform,alpha,camera,tracks,eligible,active', [
  (CAR.HYUNDAI_KONA_2022, False, 0, 0, True, False),
  (CAR.HYUNDAI_KONA_2022, True, 0, 0, True, True),
  (CAR.KIA_SORENTO_2024, True, 3, 1, False, False),
  (CAR.HYUNDAI_IONIQ_6, True, 0, 1, False, False),
])
def test_longitudinal_owner_requires_supported_platform_and_configuration(monkeypatch, platform, alpha, camera, tracks, eligible, active):
  fingerprint = gen_empty_fingerprint()
  configure_params(monkeypatch, {'FingerPrints': repr(fingerprint), 'EnableRadarTracks': tracks, 'HyundaiCameraSCC': camera})
  cp = interface.CarInterface.get_params(platform, fingerprint, [], alpha, False, False)
  assert cp.alphaLongitudinalAvailable == eligible
  assert cp.openpilotLongitudinalControl == active
  assert cp.pcmCruise != active
  assert bool(cp.safetyConfigs[-1].safetyParam & HyundaiSafetyFlags.LONG) == active


def test_kona_2022_donor_firmware_requires_matching_powertrain():
  from opendbc.car.fw_versions import match_fw_to_car_exact
  platform = CAR.HYUNDAI_KONA_2022
  live = {addr[1:]: {versions[0]} for addr, versions in FW_VERSIONS[platform].items()}
  assert match_fw_to_car_exact(live, 'hyundai', log=False) == {platform}
  electric = FW_VERSIONS[CAR.HYUNDAI_KONA_EV_2022]
  live[(0x7d0, None)] = {electric[(structs.CarParams.Ecu.fwdRadar, 0x7d0, None)][0]}
  assert platform not in match_fw_to_car_exact(live, 'hyundai', log=False)
