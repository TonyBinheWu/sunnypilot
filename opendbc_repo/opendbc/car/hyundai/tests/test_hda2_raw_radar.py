import time

import pytest

from opendbc.can import CANPacker
from opendbc.car import structs
from opendbc.car.hyundai import hyundaicanfd, radar_interface
from opendbc.car.hyundai.values import CAR, HyundaiExtFlags, HyundaiFlags


def make_radar(monkeypatch, *, longitudinal=True, camera=False, mode=1):
  class Settings:
    def get_int(self, key):
      return {'EnableRadarTracks': mode, 'HyundaiCameraSCC': int(camera)}.get(key, 0)

  monkeypatch.setattr(radar_interface, 'Params', Settings)
  monkeypatch.setattr(hyundaicanfd, 'Params', Settings)
  cp = structs.CarParams(carFingerprint=str(CAR.KIA_EV6),
    flags=int(HyundaiFlags.CANFD | HyundaiFlags.CANFD_HDA2 | (HyundaiFlags.CAMERA_SCC if camera else 0)),
    extFlags=int(HyundaiExtFlags.RADAR_GROUP1), radarUnavailable=False,
    openpilotLongitudinalControl=longitudinal, safetyConfigs=[{}])
  return radar_interface.RadarInterface(cp)


@pytest.mark.parametrize('mode', [1, 2, 3])
def test_disabled_hda2_scc_does_not_invalidate_healthy_raw_radar(monkeypatch, mode):
  radar = make_radar(monkeypatch, mode=mode)
  packer = CANPacker('hyundai_canfd_radar_generated')
  reports = []
  started = time.monotonic_ns()
  for tick in range(200):
    packets = [packer.make_can_msg(f'RADAR_TRACK_{address:x}', 0, {}) for address in range(0x210, 0x220)]
    result = radar.update([(started + tick * 50_000_000, packets)])
    if result is not None:
      reports.append(result)
  assert reports and not any(item.errors.canError for item in reports)
  assert radar.rcp_scc is None
  assert radar.rcp_tracks.can_valid
  assert not any(point.radarSource == 'scc' for item in reports for point in item.points)


def test_missing_raw_slot_still_invalidates_even_with_own_scc_echo(monkeypatch):
  radar = make_radar(monkeypatch)
  packer = CANPacker('hyundai_canfd_radar_generated')
  reports = []
  started = time.monotonic_ns()
  for tick in range(100):
    packets = [packer.make_can_msg(f'RADAR_TRACK_{address:x}', 0, {}) for address in range(0x211, 0x220)]
    packets.append((0x1a0, bytes(32), 129))
    result = radar.update([(started + tick * 50_000_000, packets)])
    if result is not None:
      reports.append(result)
  assert reports and reports[-1].errors.canError


@pytest.mark.parametrize('longitudinal,camera', [(False, False), (False, True), (True, True)])
def test_native_scc_remains_required_without_hda2_knockout(monkeypatch, longitudinal, camera):
  radar = make_radar(monkeypatch, longitudinal=longitudinal, camera=camera)
  assert radar.rcp_scc is not None
