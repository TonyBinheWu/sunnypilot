"""Exercise pre-build UI imports without retained vehicle dependencies."""
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.skipif(sys.platform != "linux", reason="vehicle hardware imports require Linux")
@pytest.mark.parametrize("device", ["mici", "tici"])
def test_os_updater_imports_before_runtime_dependencies_and_native_build(device):
  script = r'''
import importlib
import importlib.abc
import os
import sys
from unittest.mock import patch

class FreshInstall(importlib.abc.MetaPathFinder):
  def find_spec(self, fullname, path=None, target=None):
    if fullname.split('.')[0] == 'serial' or fullname in (
      'openpilot.common.params', 'openpilot.common.params_pyx',
    ):
      raise ModuleNotFoundError('Not installed before AGNOS update: ' + fullname, name=fullname)

sys.meta_path.insert(0, FreshInstall())
isfile = os.path.isfile
with patch('os.path.isfile', side_effect=lambda name: str(name) in ('/TICI', '/AGNOS') or isfile(name)):
  from openpilot.system.hardware import HARDWARE
  with patch.object(HARDWARE, 'get_device_type', return_value=sys.argv[1]), \
       patch.object(HARDWARE, 'get_os_version', return_value='fresh-agnos'):
    importlib.import_module('openpilot.system.ui.updater')
    importlib.import_module('openpilot.system.ui.' + ('mici_updater' if sys.argv[1] == 'mici' else 'tici_updater'))
    importlib.import_module('openpilot.system.ui.spinner')
    importlib.import_module('openpilot.system.ui.text')
assert 'serial' not in sys.modules
assert 'openpilot.system.hardware.tici.lpa' not in sys.modules
print('Fresh ' + sys.argv[1] + ' updater, spinner and failure display imports passed')
'''
  result = subprocess.run([sys.executable, "-c", script, device], cwd=ROOT,
                          env={**os.environ, "PYTHONPATH": f"{ROOT}:{ROOT / 'opendbc_repo'}", "SCALE": "1"},
                          capture_output=True, text=True, timeout=60)
  assert result.returncode == 0, result.stdout + result.stderr
