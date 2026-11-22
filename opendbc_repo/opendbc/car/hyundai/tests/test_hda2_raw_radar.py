import time

import pytest

from opendbc.can import CANPacker
from opendbc.car import structs
from opendbc.car.hyundai import hyundaicanfd, radar_interface
from opendbc.car.hyundai.values import CAR, HyundaiExtFlags, HyundaiFlags


def make_radar(monkeypatch, *, longitudinal=True, camera=False, mode=1, hda2=True, corners=False):
  class Settings:
    def get_int(self, key):
      return {'EnableRadarTracks': mode, 'HyundaiCameraSCC': int(camera), 'EnableCornerRadar': int(corners)}.get(key, 0)

  monkeypatch.setattr(radar_interface, 'Params', Settings)
  monkeypatch.setattr(hyundaicanfd, 'Params', Settings)
  cp = structs.CarParams(carFingerprint=str(CAR.KIA_EV6),
    flags=int(HyundaiFlags.CANFD | (HyundaiFlags.CANFD_HDA2 if hda2 else 0) | (HyundaiFlags.CAMERA_SCC if camera else 0)),
    extFlags=int(HyundaiExtFlags.RADAR_GROUP1 | (HyundaiExtFlags.CORNER_RADAR_OBJECTS_235 if corners else 0)), radarUnavailable=False,
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


@pytest.mark.parametrize('hda2', [False, True])
@pytest.mark.parametrize('mode', [0, 1])
def test_disabled_native_scc_never_supplies_leads(monkeypatch, hda2, mode):
  radar = make_radar(monkeypatch, hda2=hda2, mode=mode)
  assert radar.rcp_scc is None
  assert (radar.rcp_tracks is not None) == bool(mode)


def test_corner_only_keeps_its_clock_and_expires_observations(monkeypatch):
  radar = make_radar(monkeypatch, mode=0, corners=True)
  assert radar.rcp_scc is None and radar.rcp_tracks is None
  packer = CANPacker('hyundai_canfd_corner_radar_235_generated')
  now = time.monotonic_ns()
  reports = []
  for tick in range(160):
    packets = []
    if tick < 120:
      for addr in range(radar_interface.CORNER_OBJECT_235_START_ADDR, radar.trigger_msg_corner_objects + 1):
        if tick >= 50 and addr == radar.trigger_msg_corner_objects:
          continue  # Other slots continue; the tracked object's slot stops.
        values = {'OBJ_REL_POS_X': 15, 'OBJ_REL_POS_Y': 2, 'OBJ_REL_VEL_X': 0, 'OBJ_QUAL_LEVEL': 3,
                  'OBJ_OBJECT_ID': 2, 'OBJ_AGE': 10} if addr == radar.trigger_msg_corner_objects else {}
        packets.append(packer.make_can_msg(f'CORNER_RADAR_235_OBJECTS_{addr:x}', radar.rcp_corner_objects.bus, values))
    report = radar.update([(now + tick * 10_000_000, packets)])
    if report is not None:
      reports.append((tick, report))
  assert any(report.points for tick, report in reports if tick < 50)
  assert all(b[0] - a[0] == 5 for a, b in zip(reports, reports[1:]))
  assert any(report.errors.canError and not report.points for tick, report in reports if 100 <= tick < 120)
  assert reports[-1][0] >= 150 and not reports[-1][1].points
