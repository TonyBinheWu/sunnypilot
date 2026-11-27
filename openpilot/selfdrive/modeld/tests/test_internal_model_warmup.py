from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.selfdrive.modeld.internal_model_warmup import warm_internal_model


@pytest.mark.parametrize('device,available,format_name,overlap', [
  ('mici', 2**31, 'comma-generic-onnx', True), ('mici', 1024**3, 'comma-generic-onnx', False),
  ('mici', 2**31, 'other', False), ('tizi', 2**31, 'comma-generic-onnx', False),
  ('tici', 2**31, 'comma-generic-onnx', False),
])
def test_only_independent_gpu_warmups_overlap(tmp_path, monkeypatch, device, available, format_name, overlap):
  import json
  from openpilot.selfdrive.modeld import internal_model_warmup as warm
  model = object()
  camera = SimpleNamespace(width=1344, height=760)
  pkl = tmp_path / 'model.pkl'
  pkl.write_bytes(b'weights')
  (tmp_path / 'installed.json').write_text(json.dumps({'format': format_name}))
  monkeypatch.setattr(warm, 'vehicle_device_type', lambda: device)
  monkeypatch.setattr(warm.psutil, 'virtual_memory', lambda: SimpleNamespace(available=available))
  calls = []
  def construct(w, h, external, *, enable_shadow):
    assert (w, h, external, enable_shadow) == (1344, 760, False, False)
    return model
  monkeypatch.setattr(warm, 'warm_internal_model_from_camera', lambda selected, cam: calls.append((selected, cam)))
  assert warm.prepare_c4_stock_standby(camera, pkl, construct) is (model if overlap else None)
  assert calls == ([(model, camera)] if overlap else [])


@pytest.mark.parametrize('available,expected,tried', [
  ({'CUDA', 'QCOM'}, 'CUDA', ['CUDA']), ({'QCOM'}, 'QCOM', ['CUDA', 'QCOM']), (set(), 'CPU', ['CUDA', 'QCOM']),
])
def test_compiler_probes_only_selectable_backends(available, expected, tried):
  from openpilot.selfdrive.modeld.build_backend import preferred_backend
  calls = []
  class Devices:
    def __getitem__(self, key):
      calls.append(key)
      if key not in available:
        raise RuntimeError('unavailable')
      return SimpleNamespace(device=key)
  assert preferred_backend(Devices()) == expected
  assert calls == tried


def test_warmup_uses_one_allocated_buffer_without_waiting_for_extra_camera_backlog(monkeypatch):
  from openpilot.selfdrive.modeld import internal_model_warmup as warm
  frame = object()
  buffers = iter([None, None, frame])
  model = SimpleNamespace(vision_input_names=['img', 'big_img'])
  calls = []
  monkeypatch.setattr(warm, 'warm_internal_model', lambda *args: calls.append(args))
  warm.warm_internal_model_from_camera(model, SimpleNamespace(recv=lambda: next(buffers)))
  assert calls == [(model, {'img': frame, 'big_img': frame})]


def test_missing_startup_camera_has_bounded_wait(monkeypatch):
  from openpilot.selfdrive.modeld import internal_model_warmup as warm
  clock = [0.]
  def receive():
    clock[0] += .1
    return None
  monkeypatch.setattr(warm.time, 'monotonic', lambda: clock[0])
  with pytest.raises(RuntimeError, match='camera buffer unavailable'):
    warm.warm_internal_model_from_camera(object(), SimpleNamespace(recv=receive))
  assert 2 <= clock[0] < 2.2


@pytest.mark.parametrize('failure', [False, True])
def test_warmup_executes_full_inference_then_discards_synthetic_history(failure):
  original_shadow, image = object(), object()
  calls, resets = [], []
  def run(bufs, transforms, inputs, prepare_only):
    assert model.signal_shadow is None and not prepare_only
    assert bufs == {'img': image, 'big_img': image}
    np.testing.assert_array_equal(transforms['img'], np.eye(3))
    assert not inputs['desire_pulse'].any()
    calls.append(True)
    model.history = 99
    if failure:
      raise RuntimeError('warmup failure')
    return {'output': True}
  def reset():
    model.history = 0
    resets.append(True)
  model = SimpleNamespace(run=run, reset=reset, history=0, signal_shadow=original_shadow)
  if failure:
    with pytest.raises(RuntimeError, match='warmup failure'):
      warm_internal_model(model, {'img': image, 'big_img': image})
  else:
    warm_internal_model(model, {'img': image, 'big_img': image})
  assert len(calls) == (1 if failure else 3)
  assert resets == [True] and model.history == 0 and model.signal_shadow is original_shadow
