from types import SimpleNamespace

from openpilot.sunnypilot.formosalink import camera_status as status


def test_status_only_reports_safe_codes_and_acknowledged_frames(monkeypatch):
  monkeypatch.setattr(status, 'states', {})
  now = [100.]
  monkeypatch.setattr(status.time, 'monotonic', lambda: now[0])
  status.update('watch', 'requested')
  status.update('driver', 'encoding')
  status.update('driver', None, error=RuntimeError('private identity or image'))
  value = status.snapshot()
  assert value['camera_driver_state'] == 'encoding'
  assert value['camera_driver_error'] == 'RuntimeError'
  assert value['camera_driver_frames'] == 0
  assert 'private' not in str(value)
  status.update('driver', 'streaming', sent=True)
  now[0] += .5
  assert status.snapshot()['camera_driver_frames'] == 1
  assert status.snapshot()['camera_driver_frame_age_s'] == .5
  assert status.snapshot()['camera_driver_error'] is None
  now[0] += 16
  assert status.snapshot()['camera_driver_state'] == 'unavailable'
  assert status.snapshot()['camera_watch_state'] == 'unavailable'


def test_http_failure_code_does_not_publish_server_body(monkeypatch):
  monkeypatch.setattr(status, 'states', {})
  error = RuntimeError('server body with private material')
  error.response = SimpleNamespace(status_code=403)
  status.update('watch', 'polling', error=error)
  assert status.snapshot()['camera_watch_error'] == 'HTTP 403'
