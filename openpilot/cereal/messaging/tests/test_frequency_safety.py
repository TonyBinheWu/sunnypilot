"""Regression for the photographed UI ZeroDivisionError in messaging.

Use real capnp/msgq dependencies. No vehicle, model or GPU process is started.
"""
import ast
import os
from pathlib import Path
import random
import unittest
from unittest.mock import patch

from openpilot.cereal import messaging
from openpilot.cereal.services import SERVICE_LIST
from openpilot.common.test import OpenpilotTestCase


def legacy_valid(tracker):
  """Previous calculation, used only for positive-interval equivalence tests."""
  if tracker.avg_dt.count == 0:
    return False
  freq = 1.0 / tracker.avg_dt.get_average()
  if tracker.min_freq <= freq <= tracker.max_freq:
    return True
  recent = 1.0 / tracker.recent_avg_dt.get_average()
  return tracker.min_freq <= recent <= tracker.max_freq


class TestFrequencySafety(unittest.TestCase):
  def test_no_samples_are_not_healthy(self):
    self.assertFalse(messaging.FrequencyTracker(20, 20, True).valid)

  def test_equal_timestamps_fail_closed_instead_of_crashing(self):
    tracker = messaging.FrequencyTracker(10, 20, False)
    tracker.record_recv_time(100.0)
    tracker.record_recv_time(100.0)
    with self.assertRaises(ZeroDivisionError):
      legacy_valid(tracker)
    self.assertFalse(tracker.valid)

  def test_zero_recent_window_does_not_crash(self):
    tracker = messaging.FrequencyTracker(20, 20, True)
    tracker.avg_dt.add_value(1.0)
    tracker.recent_avg_dt.add_value(0.0)
    with self.assertRaises(ZeroDivisionError):
      legacy_valid(tracker)
    self.assertFalse(tracker.valid)

  def test_invalid_windows_are_not_healthy(self):
    for dt in (0.0, -0.0, -1.0, float('nan'), float('inf'), -float('inf')):
      with self.subTest(interval=dt):
        tracker = messaging.FrequencyTracker(20, 20, True)
        tracker.avg_dt.add_value(dt)
        tracker.recent_avg_dt.add_value(dt)
        self.assertFalse(tracker.valid)

  def test_recent_window_recovery_is_preserved(self):
    tracker = messaging.FrequencyTracker(20, 20, True)
    tracker.avg_dt.add_value(1.0)
    tracker.recent_avg_dt.add_value(0.05)
    self.assertTrue(tracker.valid)
    self.assertEqual(tracker.valid, legacy_valid(tracker))

  def test_recovery_after_repeated_timestamps(self):
    tracker = messaging.FrequencyTracker(10, 20, False)
    for _ in range(250):
      tracker.record_recv_time(100.0)
      self.assertFalse(tracker.valid)
    for i in range(1, 201):
      tracker.record_recv_time(100.0 + i / 10)
    self.assertTrue(tracker.valid)

  def test_c3x_and_c4_positive_interval_decisions_unchanged(self):
    rng = random.Random(20261031)
    comparisons = 0
    for rate in (1, 4, 10, 20, 60, 100):
      for update_rate in (20, 60):
        for is_poll in (False, True):
          tracker = messaging.FrequencyTracker(rate, update_rate, is_poll)
          now = 1000.0
          for _ in range(3000):
            now += rng.uniform(0.1, 4.0) / min(rate, update_rate)
            tracker.record_recv_time(now)
            self.assertEqual(tracker.valid, legacy_valid(tracker))
            comparisons += 1
    self.assertEqual(comparisons, 72000)


class TestSubMasterFrequencySafety(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    self.enterContext(patch.dict(os.environ, {'SIMULATION': '0'}))

  def test_duplicate_services_create_one_socket_each(self):
    services = ['gpsLocation', 'modelV2', 'gpsLocation', 'modelV2']
    with patch.object(messaging, 'sub_sock', wraps=messaging.sub_sock) as subscribe:
      sm = messaging.SubMaster(services)
    self.assertEqual(sm.services, ['gpsLocation', 'modelV2'])
    self.assertEqual(services, ['gpsLocation', 'modelV2', 'gpsLocation', 'modelV2'])
    self.assertEqual([call.args[0] for call in subscribe.call_args_list], ['gpsLocation', 'modelV2'])

  def test_polled_and_nonpolled_services_still_work(self):
    sm = messaging.SubMaster(['modelV2', 'gpsLocation', 'gpsLocation'], poll='modelV2')
    self.assertEqual(sm.services, ['modelV2', 'gpsLocation'])
    self.assertEqual(sm.non_polled_services, {'gpsLocation'})
    self.assertEqual(sm.update_freq, SERVICE_LIST['modelV2'].frequency)

  def test_duplicate_gps_batch_does_not_crash_or_claim_healthy(self):
    sm = messaging.SubMaster(['gpsLocation'])
    gps = messaging.new_message('gpsLocation', valid=True).as_reader()
    sm.update_msgs(100.0, [gps, gps])
    self.assertFalse(sm.freq_ok['gpsLocation'])
    self.assertFalse(sm.all_checks())
    frequency = SERVICE_LIST['gpsLocation'].frequency
    for i in range(1, int(frequency * 12) + 1):
      sm.update_msgs(100.0 + i / frequency, [gps])
    self.assertTrue(sm.all_checks())

  def test_real_gps_pubsub_has_only_one_initial_receive(self):
    pm = messaging.PubMaster(['gpsLocation'])
    sm = messaging.SubMaster(['gpsLocation', 'gpsLocation'])
    pm.send('gpsLocation', messaging.new_message('gpsLocation', valid=True))
    sm.update(1000)
    self.assertTrue(sm.updated['gpsLocation'])
    self.assertEqual(sm.freq_tracker['gpsLocation'].avg_dt.count, 0)
    self.assertFalse(sm.freq_ok['gpsLocation'])

  def test_model_messages_use_the_same_safe_frequency_check(self):
    sm = messaging.SubMaster(['modelV2'])
    model = messaging.new_message('modelV2', valid=True).as_reader()
    sm.update_msgs(100.0, [model, model])
    self.assertFalse(sm.freq_ok['modelV2'])
    self.assertFalse(sm.all_checks())

  def test_on_demand_semantics_unchanged(self):
    sm = messaging.SubMaster(['userBookmark', 'userBookmark'])
    sm.update_msgs(100.0, [])
    self.assertTrue(sm.all_checks())
    self.assertEqual(sm.services, ['userBookmark'])

  def test_invalid_and_stale_data_checks_are_not_disabled(self):
    sm = messaging.SubMaster(['modelV2'])
    freq = SERVICE_LIST['modelV2'].frequency
    invalid = messaging.new_message('modelV2', valid=False).as_reader()
    for i in range(25):
      sm.update_msgs(100.0 + i / freq, [invalid])
    self.assertTrue(sm.freq_ok['modelV2'])
    self.assertFalse(sm.all_valid())
    self.assertFalse(sm.all_checks())
    sm.update_msgs(200.0, [])
    self.assertFalse(sm.all_alive())

  def test_actual_ui_base_and_extension_lists_are_deduplicated(self):
    root = Path(__file__).resolve().parents[3]
    base = ast.parse((root / 'selfdrive/ui/ui_state.py').read_text())
    ext = ast.parse((root / 'selfdrive/ui/sunnypilot/ui_state.py').read_text())
    ui_class = next(n for n in base.body if isinstance(n, ast.ClassDef) and n.name == 'UIState')
    call = next(n for n in ast.walk(ui_class) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == 'SubMaster')
    services = ast.literal_eval(call.args[0].left)
    extra = next(n.value for n in ast.walk(ext) if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Attribute) and t.attr == 'sm_services_ext' for t in n.targets))
    services += ast.literal_eval(extra)
    with patch.object(messaging, 'sub_sock', wraps=messaging.sub_sock) as subscribe:
      sm = messaging.SubMaster(services)
    self.assertEqual(len(sm.services), len(set(services)))
    self.assertEqual(sm.services.count('gpsLocation'), 1)
    self.assertEqual(subscribe.call_count, len(sm.services))
    gps = messaging.new_message('gpsLocation', valid=True).as_reader()
    sm.update_msgs(100.0, [gps])
    self.assertTrue(sm.seen['gpsLocation'])
    self.assertEqual(sm.freq_tracker['gpsLocation'].avg_dt.count, 0)


if __name__ == '__main__':
  unittest.main(verbosity=2)
