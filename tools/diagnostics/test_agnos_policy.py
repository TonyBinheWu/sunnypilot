"""Exercise device OS selection and update entry points without flashing hardware."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[2]
LATEST = 'openpilot/common/hardware/comma/agnos.json'
LEGACY = 'openpilot/common/hardware/comma/agnos-19.9.json'


class TestAgnosPolicy(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.model = Path(self.temp.name) / 'model'
    self.env = dict(os.environ)
    self.env.pop('AGNOS_VERSION', None)
    self.env.pop('AGNOS_MANIFEST', None)
    self.env['AGNOS_DEVICE_MODEL_PATH'] = str(self.model)

  def select(self, model, override=None):
    self.model.write_bytes(model)
    env = dict(self.env)
    if override is not None:
      env['AGNOS_VERSION'] = override
    return subprocess.check_output(
      ['bash', '-c', 'source ./launch_env.sh && printf "%s\\n%s\\n" "$AGNOS_VERSION" "$AGNOS_MANIFEST"'],
      cwd=ROOT, env=env, text=True, stderr=subprocess.PIPE,
    ).strip().splitlines()

  def test_device_detection_and_version_manifest_pair(self):
    for model, version, manifest in (
      (b'comma tizi\0', '19.9', LEGACY), (b'tizi\0', '19.9', LEGACY),
      (b'comma mici\0', '20.1', LATEST), (b'comma tici\0', '20.1', LATEST),
      (b'unknown\0', '20.1', LATEST),
    ):
      with self.subTest(model=model):
        self.assertEqual(self.select(model), [version, manifest])

  def test_explicit_version_override_cannot_keep_a_stale_manifest(self):
    self.env['AGNOS_MANIFEST'] = 'stale.json'
    self.assertEqual(self.select(b'comma mici\0', '19.9'), ['19.9', LEGACY])
    self.assertEqual(self.select(b'comma tizi\0', '20.1'), ['20.1', LATEST])
    with self.assertRaises(subprocess.CalledProcessError):
      self.select(b'comma tizi\0', '99.9')

  def test_upstream_manifests_and_inactive_slot_partitions(self):
    for name, blob in ((LATEST, '4e90e7c8d82388f02078fffa8ddd928afebbc784'),
                       (LEGACY, '96803bdb859c53b6ef3130c683f7730164c7daff')):
      with self.subTest(manifest=name):
        raw = (ROOT / name).read_bytes()
        normalized = raw.replace(b'\r\n', b'\n')
        self.assertEqual(hashlib.sha1(b'blob ' + str(len(normalized)).encode() + b'\0' + normalized).hexdigest(), blob)
        images = json.loads(raw)
        self.assertEqual({x['name'] for x in images}, {'xbl', 'xbl_config', 'abl', 'aop', 'devcfg', 'boot', 'system'})
        self.assertTrue(all(x['has_ab'] for x in images))
        for image in images:
          self.assertTrue(image['url'].startswith('https://commadist.azureedge.net/agnosupdate/'))
          for key in ('hash', 'hash_raw', 'ondevice_hash'):
            self.assertEqual(len(image[key]), 64)

  def background_update(self, current):
    path = ROOT / 'openpilot/system/updated/updated.py'
    tree = ast.parse(path.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'handle_agnos_update')
    flash = Mock()
    consistent = Mock()
    calls = Mock()
    calls.attach_mock(consistent, 'consistent')
    calls.attach_mock(flash, 'flash')
    module = SimpleNamespace(flash_agnos_update=flash, get_target_slot_number=lambda: 1)
    def run(command, cwd):
      return subprocess.check_output(command, cwd=cwd, env=self.env, text=True)
    namespace = {'HARDWARE': SimpleNamespace(get_os_version=lambda: current), 'run': run,
                 'OVERLAY_MERGED': str(ROOT), 'os': os, 'cloudlog': Mock(), 'set_consistent_flag': consistent}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), namespace)
    with patch.dict(sys.modules, {'openpilot.common.hardware.comma.agnos': module}):
      namespace['handle_agnos_update']()
    return flash, consistent, calls

  def test_background_c3x_downgrade_uses_19_9_inactive_slot(self):
    self.model.write_bytes(b'comma tizi\0')
    # The current process can still have its old launch environment.
    self.env.update(AGNOS_VERSION='20.1', AGNOS_MANIFEST=LATEST)
    flash, consistent, calls = self.background_update('20.1')
    self.assertEqual(flash.call_args.args[:2], (str(ROOT / LEGACY), 1))
    consistent.assert_called_once_with(False)
    self.assertEqual([c[0] for c in calls.mock_calls], ['consistent', 'flash'])

  def test_background_skips_matching_os_and_keeps_c4_latest(self):
    for model, current in ((b'comma tizi\0', '19.9'), (b'comma mici\0', '20.1')):
      with self.subTest(model=model):
        self.model.write_bytes(model)
        flash, consistent, _ = self.background_update(current)
        flash.assert_not_called()
        consistent.assert_not_called()
    self.model.write_bytes(b'comma mici\0')
    flash, _, _ = self.background_update('19.9')
    self.assertEqual(flash.call_args.args[:2], (str(ROOT / LATEST), 1))

  def test_manual_update_passes_selected_manifest_without_flashing(self):
    self.model.write_bytes(b'comma tizi\0')
    temp = Path(self.temp.name)
    (temp / 'AGNOS').touch()
    (temp / 'VERSION').write_text('20.1')
    source = (ROOT / 'tools/op.sh').read_text()
    function = source[source.index('function op_check_agnos_update()'):source.index('function op_switch()')]
    # Replace only OS identity files; all selection and invocation code is production code.
    function = function.replace('"/AGNOS"', '"$TEST_ROOT/AGNOS"').replace('< /VERSION', '< "$TEST_ROOT/VERSION"')
    command = 'op_run_command() { printf "CALL:%s\\n" "$@"; }\n' + function + '\nop_check_agnos_update'
    env = dict(self.env, TEST_ROOT=str(temp), OPENPILOT_ROOT=str(ROOT))
    output = subprocess.check_output(['bash', '-c', command], env=env, text=True, input='y\nn\n')
    self.assertIn('20.1 → 19.9', output)
    self.assertIn('CALL:--swap', output)
    self.assertIn(f'CALL:{ROOT / LEGACY}', output)

  def test_shell_syntax_and_boot_manifest(self):
    for name in ('launch_env.sh', 'launch_chffrplus.sh', 'tools/op.sh'):
      subprocess.run(['bash', '-n', str(ROOT / name)], check=True)
    launcher = (ROOT / 'launch_chffrplus.sh').read_text()
    self.assertIn('MANIFEST="$DIR/$AGNOS_MANIFEST"', launcher)
    self.assertIn('unset AGNOS_VERSION AGNOS_MANIFEST', launcher)


if __name__ == '__main__':
  unittest.main()
