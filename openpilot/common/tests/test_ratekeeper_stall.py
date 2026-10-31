"""Deterministic scheduling regression; no real sleep, scheduler, GPU or CAN access."""
import unittest
from unittest import mock

from openpilot.common import realtime


# Include the C3X/C4 UI rates and the control, hardware and touch loop rates.
RATES = (2, 20, 60, 100, 140)


class FakeClock:
  def __init__(self):
    self.now = 100.0
    self.sleeps: list[float] = []

  def monotonic(self):
    return self.now

  def sleep(self, duration):
    if duration <= 0:
      raise AssertionError("Ratekeeper must only sleep for a positive duration")
    self.sleeps.append(duration)
    self.now += duration


class TestRatekeeperStall(unittest.TestCase):
  def setUp(self):
    self.clock = FakeClock()
    # Patch this module's clock only, not the process-wide time module.
    self.clock_patch = mock.patch.object(realtime, "time", self.clock)
    self.clock_patch.start()
    self.addCleanup(self.clock_patch.stop)

  def prime(self, rate, threshold=None):
    rk = realtime.Ratekeeper(rate, print_delay_threshold=threshold)
    rk.keep_time()
    self.clock.sleeps.clear()
    return rk

  def test_normal_cadence_is_unchanged(self):
    for rate in RATES:
      with self.subTest(rate=rate):
        rk = self.prime(rate)
        start = self.clock.now
        for _ in range(20):
          self.clock.now += 0.25 / rate
          self.assertFalse(rk.keep_time())
          self.assertAlmostEqual(rk.remaining, 0.75 / rate)
        self.assertAlmostEqual(self.clock.now - start, 20 / rate)
        self.assertEqual(rk.frame, 21)
        self.assertFalse(rk.lagging)

  def test_long_stall_resynchronizes_deadline(self):
    for rate in RATES:
      for stall in (2.0, 30.0):
        with self.subTest(rate=rate, stall=stall):
          rk = self.prime(rate)
          self.clock.now += stall
          old_deadline = rk._next_frame_time
          rk.keep_time()
          self.assertAlmostEqual(rk.remaining, old_deadline - self.clock.now)
          self.assertLess(rk.remaining, -1 / rate)
          self.assertEqual(self.clock.sleeps, [])
          self.assertAlmostEqual(rk._next_frame_time, self.clock.now + 1 / rate)

  def test_next_cycle_sleeps_instead_of_catching_up(self):
    for rate in RATES:
      with self.subTest(rate=rate):
        rk = self.prime(rate)
        self.clock.now += 30.0
        rk.keep_time()
        self.clock.now += 0.25 / rate
        rk.keep_time()
        self.assertEqual(len(self.clock.sleeps), 1)
        self.assertAlmostEqual(self.clock.sleeps[0], 0.75 / rate)
        self.assertEqual(rk.frame, 3)

  def test_short_overrun_preserves_phase(self):
    for rate in RATES:
      with self.subTest(rate=rate):
        rk = self.prime(rate)
        deadline = rk._next_frame_time
        self.clock.now = deadline + 0.5 / rate
        rk.keep_time()
        self.assertEqual(self.clock.sleeps, [])
        self.assertAlmostEqual(rk._next_frame_time, deadline + 1 / rate)
        rk.keep_time()
        self.assertAlmostEqual(self.clock.sleeps[-1], 0.5 / rate)

  def test_exact_interval_boundary_does_not_resynchronize(self):
    # Binary-exact interval avoids testing floating-point rounding by accident.
    rk = self.prime(8)
    deadline = rk._next_frame_time
    self.clock.now = deadline + 0.125
    rk.keep_time()
    self.assertEqual(rk.remaining, -0.125)
    self.assertEqual(rk._next_frame_time, deadline + 0.125)
    self.assertEqual(self.clock.sleeps, [])

  def test_lag_reporting_is_not_hidden(self):
    rk = self.prime(20, threshold=0.001)
    self.clock.now += 30.0
    with mock.patch("builtins.print") as warning:
      self.assertTrue(rk.keep_time())
    warning.assert_called_once()
    self.assertTrue("lagging by" in warning.call_args.args[0])
    self.assertTrue(rk.lagging)
    self.assertLess(rk.remaining, 0.0)

  def test_monitor_time_remains_nonblocking(self):
    rk = self.prime(20)
    self.clock.now += 30.0
    rk.monitor_time()
    rk.monitor_time()
    self.assertGreater(rk.remaining, 0.0)
    self.assertEqual(self.clock.sleeps, [])

  def test_repeated_stalls_recover_without_synthetic_frames(self):
    for rate in RATES:
      with self.subTest(rate=rate):
        rk = self.prime(rate)
        for _ in range(10):
          self.clock.now += 5.0
          rk.keep_time()
          rk.keep_time()
        self.assertEqual(rk.frame, 21)
        self.assertEqual(len(self.clock.sleeps), 10)
        for duration in self.clock.sleeps:
          self.assertAlmostEqual(duration, 1 / rate)


if __name__ == "__main__":
  unittest.main()
