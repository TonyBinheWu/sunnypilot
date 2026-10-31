from pathlib import Path
import subprocess

import tinygrad

from openpilot.common.basedir import BASEDIR
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.models.tinygrad_ref import get_tinygrad_ref


class TestTinygradRef(OpenpilotTestCase):
  def test_installed_runtime_matches_source_pin(self):
    # Plain artifacts are independent of the compiler's Python class revision.
    # The artifact-loading workflow and CPU contract test verify compatibility.
    pinned = subprocess.check_output(["git", "rev-parse", "HEAD:tinygrad_repo"], cwd=BASEDIR, text=True).strip()
    self.assertEqual(get_tinygrad_ref(), pinned)
    self.assertTrue(Path(tinygrad.__file__).resolve().is_relative_to((Path(BASEDIR) / "tinygrad_repo").resolve()))
