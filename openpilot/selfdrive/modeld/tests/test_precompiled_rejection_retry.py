"""Boot boundary and integrity checks for persisted numerical failures."""
import json
from types import SimpleNamespace

import pytest

from openpilot.selfdrive.modeld import egpu_worker_progress, precompiled_model as pm
from openpilot.selfdrive.modeld.tests.test_precompiled_model import Response, catalog
from openpilot.selfdrive.modeld import egpu_rejection as rejection
from openpilot.selfdrive.modeld.egpu_usb_wait import RUNTIME_SHA, VERIFIED_USB_RUNTIMES


BRIDGE_SETUP_ERROR = '''Traceback (most recent call last):
  File "/runtime/tinygrad/runtime/support/system.py", line 142, in pci_setup_usb_bars
    usb.pcie_cfg_req(pci.PCI_PRIMARY_BUS, bus=bus, dev=0, fn=0, value=buses, size=4)
  File "/runtime/tinygrad/runtime/support/usb.py", line 133, in pcie_request
    raise RuntimeError(message)
RuntimeError: TLP completion status: Unsupported Request: 0x1000018
'''


@pytest.mark.parametrize('phase', ['load', 'boot_validation'])
def test_bridge_setup_failure_requires_new_boot(tmp_path, monkeypatch, phase):
  from openpilot.selfdrive.modeld.egpu_recovery import retryable_preparation
  value = {'pickle': {'sha256': 'a' * 64}, 'runtime': {'sha256': RUNTIME_SHA}}
  (tmp_path / 'installed.json').write_text(json.dumps(value))
  receipt = tmp_path / 'boot_validation.json'
  receipt.write_text('{}')
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'first')
  assert pm.record_failure(tmp_path / 'model.pkl', BRIDGE_SETUP_ERROR, phase)
  saved = tmp_path / 'last_failure.json'
  failure = json.loads(saved.read_text())
  assert failure['classification'] == 'device_restart_required'
  assert not receipt.exists() and (tmp_path / 'rejected').exists()
  assert not retryable_preparation(RuntimeError(BRIDGE_SETUP_ERROR), value)
  # A report saved by the previous release must follow the same boot boundary.
  saved.write_text(json.dumps(failure | {'classification': 'artifact_blocked'}))
  original = saved.read_bytes()
  assert rejection.rejection_status(tmp_path)['reason'] == 'device_restart_required'
  assert not pm.retry_usb_rejection(tmp_path, 'a' * 64)
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'second')
  assert pm.retry_usb_rejection(tmp_path, 'a' * 64)
  assert not pm.retry_usb_rejection(tmp_path, 'b' * 64)
  assert saved.read_bytes() == original and (tmp_path / 'rejected').exists()


@pytest.mark.parametrize('detail,phase,runtime', [
  (BRIDGE_SETUP_ERROR, 'inference', RUNTIME_SHA),
  (BRIDGE_SETUP_ERROR, 'load', 'unknown'),
  (BRIDGE_SETUP_ERROR.replace('0x1000018', '0x1000020'), 'load', RUNTIME_SHA),
  (BRIDGE_SETUP_ERROR.replace('pci_setup_usb_bars', 'do_inference'), 'load', RUNTIME_SHA),
  (BRIDGE_SETUP_ERROR.splitlines()[-1], 'load', RUNTIME_SHA),
  (BRIDGE_SETUP_ERROR + 'ValueError: checksum mismatch', 'load', RUNTIME_SHA),
  (BRIDGE_SETUP_ERROR + 'Traceback (most recent call last):\nRuntimeError: TLP completion status: Unsupported Request: 0x1000018', 'load', RUNTIME_SHA),
])
def test_unrelated_failures_remain_blocked(tmp_path, detail, phase, runtime):
  value = {'pickle': {'sha256': 'a' * 64}, 'runtime': {'sha256': runtime}}
  (tmp_path / 'installed.json').write_text(json.dumps(value))
  assert pm.record_failure(tmp_path / 'model.pkl', detail, phase)
  assert json.loads((tmp_path / 'last_failure.json').read_text())['classification'] == 'artifact_blocked'


def test_n16_disconnected_during_output_readback(tmp_path, monkeypatch):
  error = 'Traceback (most recent call last):\n  result = self.copy_outputs().numpy()\nRuntimeError: AMD failed with -4\n'
  manifest = {'pickle': {'sha256': 'a' * 64}, 'runtime': {'sha256': RUNTIME_SHA}}
  (tmp_path / 'installed.json').write_text(json.dumps(manifest))
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'first')
  assert pm.record_failure(tmp_path / 'model.pkl', error, 'inference')
  report = tmp_path / 'last_failure.json'
  failure = json.loads(report.read_text())
  assert failure['classification'] == 'device_restart_required'
  report.write_text(json.dumps(failure | {'classification': 'artifact_blocked'}))
  assert rejection.rejection_status(tmp_path)['reason'] == 'device_restart_required'
  assert not pm.retry_usb_rejection(tmp_path, 'a' * 64)
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'second')
  assert pm.retry_usb_rejection(tmp_path, 'a' * 64)
  assert not pm.retry_usb_rejection(tmp_path, 'b' * 64)
  assert not pm.gpu_restart_failure(error + 'ValueError: checksum mismatch', manifest)
  assert not pm.gpu_restart_failure(error, {'runtime': {'sha256': 'unknown'}})


@pytest.mark.parametrize('runtime', sorted(VERIFIED_USB_RUNTIMES))
@pytest.mark.parametrize('phase', ['load', 'boot_validation', 'inference'])
@pytest.mark.parametrize('error', ['RuntimeError: AMD failed with -7', 'RuntimeError: AMD:0 failed with -7',
                                 'RuntimeError: AMD failed with -7\nDuring handling of the above exception:\nRuntimeError: Device hang detected'])
def test_device_hang_keeps_this_boot_blocked_and_retries_next_boot(tmp_path, monkeypatch, runtime, phase, error):
  from openpilot.selfdrive.modeld.egpu_recovery import retryable
  value = {'pickle': {'sha256': 'a' * 64}, 'runtime': {'sha256': runtime}}
  assert not retryable(RuntimeError(error), value)
  (tmp_path / 'installed.json').write_text(json.dumps(value))
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'first')
  assert pm.record_failure(tmp_path / 'model.pkl', error, phase)
  failure = json.loads((tmp_path / 'last_failure.json').read_text())
  assert failure['classification'] == 'device_restart_required'
  assert not pm.retry_usb_rejection(tmp_path, 'a' * 64)
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'second')
  assert pm.retry_usb_rejection(tmp_path, 'a' * 64)
  # Old reports had no classification; migration must work for those too.
  failure.pop('classification')
  (tmp_path / 'last_failure.json').write_text(json.dumps(failure))
  assert pm.retry_usb_rejection(tmp_path, 'a' * 64)
  # A second failure stops the new boot as well, never a tight retry loop.
  pm.record_failure(tmp_path / 'model.pkl', error, phase)
  assert not pm.retry_usb_rejection(tmp_path, 'a' * 64)


@pytest.mark.parametrize('error', ['ValueError: Device hang detected', 'RuntimeError: AMD failed with -70',
                                 'RuntimeError: Device hang detected\nValueError: checksum mismatch',
                                 'ValueError: quoted RuntimeError: AMD failed with -7'])
def test_hang_classifier_does_not_release_artifact_failures(error):
  manifest = {'runtime': {'sha256': next(iter(VERIFIED_USB_RUNTIMES))}}
  assert not pm.gpu_restart_failure(error, manifest)
  assert not pm.gpu_restart_failure('RuntimeError: Device hang detected', {'runtime': {'sha256': 'unknown'}})


def test_manual_request_is_next_boot_one_shot_and_bound_to_exact_failure(tmp_path, monkeypatch):
  value = {'pickle': {'sha256': 'a' * 64}, 'runtime': {'sha256': 'b' * 64}}
  (tmp_path / 'installed.json').write_text(json.dumps(value))
  monkeypatch.setattr(rejection, 'boot_identity', lambda: 'first')
  pm.record_failure(tmp_path / 'model.pkl', 'ValueError: checkpoint mismatch', 'load')
  evidence = (tmp_path / 'last_failure.json').read_bytes()
  rejection.request_retry(tmp_path)
  assert rejection.rejection_status(tmp_path)['retry_pending']
  assert not rejection.consume_retry_request(tmp_path, value)
  assert (tmp_path / 'rejected').exists()
  monkeypatch.setattr(rejection, 'boot_identity', lambda: 'second')
  assert not rejection.consume_retry_request(tmp_path, value | {'runtime': {'sha256': 'c' * 64}})
  assert rejection.consume_retry_request(tmp_path, value)
  assert not rejection.consume_retry_request(tmp_path, value)
  assert (tmp_path / 'last_failure.json').read_bytes() == evidence
  assert (tmp_path / 'rejected').exists()  # only verified installer can clear it
  rejection.request_retry(tmp_path)
  (tmp_path / 'last_failure.json').write_bytes(evidence + b' ')
  monkeypatch.setattr(rejection, 'boot_identity', lambda: 'third')
  assert not rejection.consume_retry_request(tmp_path, value)


@pytest.mark.parametrize('missing', ['installed.json', 'last_failure.json', 'rejected'])
def test_missing_evidence_cannot_schedule_release(tmp_path, missing):
  (tmp_path / 'rejected').write_text('a' * 64)
  (tmp_path / 'installed.json').write_text('{}')
  (tmp_path / 'last_failure.json').write_text('{}')
  (tmp_path / missing).unlink()
  assert not rejection.rejection_status(tmp_path).get('can_request')
  assert not rejection.consume_retry_request(tmp_path, {})


@pytest.mark.parametrize('corrupt_download', [False, True])
def test_requested_retry_runs_installer_checks_before_removing_marker(tmp_path, monkeypatch, corrupt_download):
  value, data = catalog()
  model = SimpleNamespace(sha256='a' * 64, url='https://nas.example/model.onnx')
  def fetch(request, **kwargs):
    name = request.full_url.rsplit('/', 1)[-1]
    return Response(json.dumps(value).encode() if name == 'precompiled.json' else data[name])
  monkeypatch.setattr(pm, 'urlopen', fetch)
  monkeypatch.setattr(rejection, 'boot_identity', lambda: 'first')
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'first')
  path = pm.ensure_precompiled(model, tmp_path)
  pm.record_failure(path, 'ValueError: checkpoint mismatch', 'boot_validation')
  rejection.request_retry(path.parent)
  path.write_bytes(b'corrupt')
  receipt = path.parent / 'boot_validation.json'
  receipt.write_text('{"key":"old"}')
  assert pm.ensure_precompiled(model, tmp_path) is None  # same boot cannot bypass
  monkeypatch.setattr(rejection, 'boot_identity', lambda: 'second')
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'second')
  if corrupt_download:
    data['pickle'] = b'x' * len(data['pickle'])
    with pytest.raises(ValueError, match='hash mismatch'):
      pm.ensure_precompiled(model, tmp_path)
    assert (path.parent / 'rejected').exists()
    assert not rejection.consume_retry_request(path.parent, value)
  else:
    assert pm.ensure_precompiled(model, tmp_path) == path
    assert path.read_bytes() == data['pickle']
    assert not (path.parent / 'rejected').exists()
    # File recovery is not inference acceptance: boot receipt stays invalid.
  assert not receipt.exists()


@pytest.mark.parametrize('error,phase,old_boot,allowed', [
  ('ValueError: invalid precompiled model output', 'inference', True, True),
  ('non-finite model output', 'inference', True, True),
  ('NonFiniteModelOutput: invalid numbers', 'inference', True, True),
  ('RepeatedInvalidModelOutput: two consecutive invalid eGPU outputs', 'inference', True, True),
  ('ValueError: invalid precompiled model output', 'inference', False, False),
  ('ValueError: invalid precompiled model output', 'boot_validation', True, False),
  ('ValueError: invalid precompiled model output: count=1, expected=2', 'inference', True, False),
  ('ValueError: checkpoint mismatch', 'inference', True, False),
  ('TimeoutError: flush_tlb timeout. Timed out after 10000 ms, condition not met: 0 != 1', 'load', True, True),
  ('TimeoutError: flush_tlb timeout. Timed out after 10000 ms, condition not met: 0 != 1', 'load', False, False),
  ('TimeoutError: flush_tlb timeout. Timed out after 10000 ms, condition not met: 0 != 1', 'inference', True, False),
  ('NonFiniteModelOutput: invalid\nValueError: checksum mismatch', 'inference', True, False),
])
def test_reboot_retry_rehashes_artifacts_and_requires_new_smoke_test(tmp_path, monkeypatch, capsys, error, phase, old_boot, allowed):
  value, data = catalog()
  model = SimpleNamespace(sha256='a' * 64, url='https://nas.example/models/v2/model.onnx')
  def fetch(request, **kwargs):
    name = request.full_url.rsplit('/', 1)[-1]
    return Response(json.dumps(value).encode() if name == 'precompiled.json' else data[name])
  monkeypatch.setattr(pm, 'urlopen', fetch)
  monkeypatch.setattr(egpu_worker_progress, 'boot_identity', lambda: 'this-boot')
  path = pm.ensure_precompiled(model, tmp_path)
  failure = {'rejected': True, 'pickle_sha256': value['pickle']['sha256'], 'phase': phase,
             'boot_id': 'previous-boot' if old_boot else 'this-boot', 'error': error}
  (path.parent / 'last_failure.json').write_text(json.dumps(failure))
  pm.reject(path)
  receipt = path.parent / 'boot_validation.json'
  receipt.write_text('{"key":"old"}')
  path.write_bytes(b'corrupt')
  (path.parent / 'runtime.tar.gz').write_bytes(b'corrupt')
  result = pm.ensure_precompiled(model, tmp_path)
  events = [json.loads(line.removeprefix('[eGPU] ')) for line in capsys.readouterr().err.splitlines()]
  assert events[-1]['event'] == ('artifact_retry' if allowed else 'artifact_blocked')
  if not allowed:
    assert events[-1]['retry'] is False and events[-1]['error'] == error.splitlines()[-1]
  assert (result == path) == allowed
  assert (path.parent / 'rejected').exists() == (not allowed)
  assert json.loads((path.parent / 'last_failure.json').read_text()) == failure
  if allowed:
    assert path.read_bytes() == data['pickle']
    assert (path.parent / 'runtime.tar.gz').read_bytes() == data['runtime']
    assert not receipt.exists()
  else:
    assert pm.installed(model, tmp_path) is None
