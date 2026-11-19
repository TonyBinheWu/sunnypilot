import unittest
from tools.training_studio.teacher_adapt import require_optimizer_success


class OptimizerLifecycleTest(unittest.TestCase):
  def test_controlled_stop_after_stdout_eof_is_interrupted_even_with_failure_exit(self):
    for returncode in (0,137,-15):
      with self.subTest(returncode=returncode):
        with self.assertRaises(InterruptedError):require_optimizer_success(returncode,authorized=False)

  def test_real_active_failure_stays_distinct_from_success(self):
    require_optimizer_success(0,authorized=True)
    with self.assertRaises(RuntimeError):require_optimizer_success(137,authorized=True)


if __name__=='__main__':unittest.main()
