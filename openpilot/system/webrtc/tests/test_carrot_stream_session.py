import asyncio
import json
from types import SimpleNamespace

from aiohttp import web
import pytest

from openpilot.system.webrtc import carrot_session, webrtcd


class TestCarrotStreamSession:
  def setup_method(self):
    self.loop = asyncio.new_event_loop()

  def teardown_method(self):
    self.loop.stop()
    self.loop.close()

  def test_stream_identifiers_are_bounded_and_log_safe(self):
    raw = "  device\nwith spaces/" + ("x" * 160)
    normalized = carrot_session.normalize_stream_identifier(raw)

    assert normalized.startswith("device-with-spaces-")
    assert "\n" not in normalized
    assert " " not in normalized
    assert len(normalized) == 128

  @staticmethod
  def _stream_request(
    mocker,
    streams,
    *,
    client_id: str,
    device_id: str | None = None,
    tab_id: str = "",
    attempt_id: str = "",
    takeover: bool = False,
  ):
    request = mocker.Mock()
    request.remote = "192.168.0.2"
    request.app = {
      "streams": streams,
      "debug": False,
      "stream_lock": asyncio.Lock(),
    }
    payload = {
      "sdp": "offer",
      "cameras": ["road"],
      "client_id": client_id,
      "tab_id": tab_id,
      "attempt_id": attempt_id,
      "takeover": takeover,
    }
    if device_id is not None:
      payload["device_id"] = device_id
    request.json = mocker.AsyncMock(return_value=payload)
    return request

  @staticmethod
  def _stream_session(mocker, identifier: str):
    session = mocker.Mock()
    session.identifier = identifier
    session.uses_road_camera = True
    session._carrot_disconnected_monotonic = None
    session.get_answer = mocker.AsyncMock(return_value=SimpleNamespace(sdp="answer", type="answer"))
    session.stop = mocker.AsyncMock()
    return session

  @staticmethod
  def _lifecycle_session(mocker, identifier: str = "session"):
    session = object.__new__(carrot_session.CarrotStreamSession)
    session.logger = mocker.Mock()
    session.identifier = identifier
    session.client_key = "client:viewer"
    session.uses_road_camera = True
    session.carrot_state = False
    session.stream = mocker.Mock()
    session.stream.stop = mocker.AsyncMock()
    session.stream.wait_for_connection = mocker.AsyncMock()
    session.stream.wait_for_disconnection = mocker.AsyncMock()
    session.stream.has_messaging_channel.return_value = False
    session.incoming_bridge = None
    session.outgoing_bridge = None
    session.outgoing_bridge_runner = None
    session.carrot_state_bridge = None
    session.carrot_state_bridge_runner = None
    session._video_tracks = []
    session.run_task = None
    session._carrot_cleanup_lock = asyncio.Lock()
    session._carrot_cleanup_complete = False
    session.stream_dict = {identifier: session}
    return session

  def test_rejects_foreign_road_session_without_takeover(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:owner-device"
    streams = {owner.identifier: owner}
    request = self._stream_request(
      mocker,
      streams,
      client_id="legacy-viewer-tab",
      device_id="viewer-device",
      tab_id="viewer-tab",
      attempt_id="attempt-1",
    )
    session_factory = mocker.patch.object(carrot_session, "CarrotStreamSession")

    with pytest.raises(web.HTTPConflict) as exc_info:
      self.loop.run_until_complete(carrot_session.get_stream(request))

    assert json.loads(exc_info.value.text)["code"] == webrtcd.CARROT_VISION_BUSY_CODE
    owner.stop.assert_not_awaited()
    session_factory.assert_not_called()

  def test_explicit_takeover_replaces_healthy_foreign_owner(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:other-device"
    owner.run_task = SimpleNamespace(done=lambda: False)
    owner.stream.peer_connection.connectionState = "connected"
    replacement = self._stream_session(mocker, "replacement")
    streams = {owner.identifier: owner}
    request = self._stream_request(
      mocker,
      streams,
      client_id="viewer",
      device_id="viewer-device",
      takeover=True,
    )
    mocker.patch.object(carrot_session, "CarrotStreamSession", return_value=replacement)

    response = self.loop.run_until_complete(carrot_session.get_stream(request))

    assert response.status == 200
    owner.stop.assert_awaited_once()
    replacement.start.assert_called_once()
    assert streams == {replacement.identifier: replacement}

  def test_same_device_replaces_previous_tab_and_attempt(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:viewer-device"
    owner.tab_id = "old-tab"
    owner.attempt_id = "old-attempt"
    replacement = self._stream_session(mocker, "replacement")
    streams = {owner.identifier: owner}
    request = self._stream_request(
      mocker,
      streams,
      client_id="legacy-new-tab",
      device_id="viewer-device",
      tab_id="new-tab",
      attempt_id="new-attempt",
    )
    mocker.patch.object(carrot_session, "CarrotStreamSession", return_value=replacement)

    response = self.loop.run_until_complete(carrot_session.get_stream(request))

    assert response.status == 200
    owner.stop.assert_awaited_once()
    replacement.start.assert_called_once()
    assert replacement.device_id == "viewer-device"
    assert replacement.tab_id == "new-tab"
    assert replacement.attempt_id == "new-attempt"
    assert owner.identifier not in streams

  def test_legacy_client_id_still_replaces_same_client(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:legacy-viewer"
    replacement = self._stream_session(mocker, "replacement")
    streams = {owner.identifier: owner}
    request = self._stream_request(mocker, streams, client_id="legacy-viewer")
    mocker.patch.object(carrot_session, "CarrotStreamSession", return_value=replacement)

    response = self.loop.run_until_complete(carrot_session.get_stream(request))

    assert response.status == 200
    owner.stop.assert_awaited_once()
    replacement.start.assert_called_once()
    assert replacement.device_id == "legacy-viewer"
    assert owner.identifier not in streams

  def test_prunes_ended_owner_before_ownership_check(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:owner"
    owner.run_task = SimpleNamespace(done=lambda: True)
    replacement = self._stream_session(mocker, "replacement")
    streams = {owner.identifier: owner}
    request = self._stream_request(mocker, streams, client_id="viewer")
    mocker.patch.object(carrot_session, "CarrotStreamSession", return_value=replacement)

    response = self.loop.run_until_complete(carrot_session.get_stream(request))

    assert response.status == 200
    owner.stop.assert_awaited_once()
    replacement.start.assert_called_once()
    assert owner.identifier not in streams
    assert streams[replacement.identifier] is replacement

  def test_prunes_stalled_negotiation_before_ownership_check(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:owner"
    owner.run_task = SimpleNamespace(done=lambda: False)
    owner.stream.peer_connection.connectionState = "connecting"
    owner._carrot_created_monotonic = 10.0
    replacement = self._stream_session(mocker, "replacement")
    streams = {owner.identifier: owner}
    request = self._stream_request(mocker, streams, client_id="viewer")
    mocker.patch.object(carrot_session.time, "monotonic", return_value=31.0)
    mocker.patch.object(carrot_session, "CarrotStreamSession", return_value=replacement)

    response = self.loop.run_until_complete(carrot_session.get_stream(request))

    assert response.status == 200
    owner.stop.assert_awaited_once()
    replacement.start.assert_called_once()
    assert owner.identifier not in streams

  def test_disconnected_session_is_reclaimed_only_after_grace_period(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.run_task = SimpleNamespace(done=lambda: False)
    owner.stream.peer_connection.connectionState = "disconnected"

    assert carrot_session.stream_session_reclaim_reason(owner, 100.0) is None
    assert carrot_session.stream_session_reclaim_reason(owner, 102.9) is None
    assert carrot_session.stream_session_reclaim_reason(owner, 103.0) == "disconnected-grace-expired"

  def test_recently_disconnected_foreign_owner_remains_protected(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:other-device"
    owner.run_task = SimpleNamespace(done=lambda: False)
    owner.stream.peer_connection.connectionState = "disconnected"
    owner._carrot_disconnected_monotonic = 99.0
    streams = {owner.identifier: owner}
    request = self._stream_request(mocker, streams, client_id="viewer", device_id="viewer-device")
    mocker.patch.object(carrot_session.time, "monotonic", return_value=100.0)
    session_factory = mocker.patch.object(carrot_session, "CarrotStreamSession")

    with pytest.raises(web.HTTPConflict):
      self.loop.run_until_complete(carrot_session.get_stream(request))

    owner.stop.assert_not_awaited()
    session_factory.assert_not_called()

  def test_expired_disconnected_foreign_owner_is_reclaimed_before_busy_check(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.client_key = "client:other-device"
    owner.run_task = SimpleNamespace(done=lambda: False)
    owner.stream.peer_connection.connectionState = "disconnected"
    owner._carrot_disconnected_monotonic = 95.0
    replacement = self._stream_session(mocker, "replacement")
    streams = {owner.identifier: owner}
    request = self._stream_request(mocker, streams, client_id="viewer", device_id="viewer-device")
    mocker.patch.object(carrot_session.time, "monotonic", return_value=100.0)
    mocker.patch.object(carrot_session, "CarrotStreamSession", return_value=replacement)

    response = self.loop.run_until_complete(carrot_session.get_stream(request))

    assert response.status == 200
    owner.stop.assert_awaited_once()
    replacement.start.assert_called_once()
    assert streams == {replacement.identifier: replacement}

  def test_connection_state_observer_records_disconnect_start(self, mocker):
    session = self._lifecycle_session(mocker)
    session._carrot_connected_monotonic = None
    session._carrot_disconnected_monotonic = None
    session.stream.peer_connection.connectionState = "disconnected"
    mocker.patch.object(carrot_session.time, "monotonic", return_value=42.0)

    session._record_carrot_connection_state()

    assert session._carrot_disconnected_monotonic == 42.0

  def test_connected_foreign_session_is_not_reclaimable(self, mocker):
    owner = self._stream_session(mocker, "owner")
    owner.run_task = SimpleNamespace(done=lambda: False)
    owner.stream.peer_connection.connectionState = "connected"
    owner._carrot_created_monotonic = 1.0
    owner._carrot_disconnected_monotonic = 9.0

    assert carrot_session.stream_session_reclaim_reason(owner, 1000.0) is None
    assert owner._carrot_disconnected_monotonic is None
    assert owner._carrot_connected_monotonic == 1000.0

  def test_cleanup_is_idempotent_and_unregisters(self, mocker):
    session = self._lifecycle_session(mocker)
    sync_active = mocker.patch.object(webrtcd, "_sync_carrot_vision_active")

    self.loop.run_until_complete(session.stop())
    self.loop.run_until_complete(session.stop())

    session.stream.stop.assert_awaited_once()
    assert session.identifier not in session.stream_dict
    sync_active.assert_called_once_with(session.stream_dict)

  def test_cleanup_failure_still_releases_all_resources(self, mocker):
    session = self._lifecycle_session(mocker)
    session.stream.stop.side_effect = RuntimeError("stream stop failed")
    session.outgoing_bridge_runner = mocker.Mock()
    session.carrot_state_bridge_runner = mocker.Mock()
    track = mocker.Mock()
    session._video_tracks = [track]
    sync_active = mocker.patch.object(webrtcd, "_sync_carrot_vision_active")

    self.loop.run_until_complete(session.post_run_cleanup())

    session.outgoing_bridge_runner.stop.assert_called_once()
    session.carrot_state_bridge_runner.stop.assert_called_once()
    track.close_sock.assert_called_once()
    assert session.identifier not in session.stream_dict
    sync_active.assert_called_once_with(session.stream_dict)
    assert session._carrot_cleanup_complete is True

  def test_normal_disconnect_cleans_up_once(self, mocker):
    session = self._lifecycle_session(mocker)

    self.loop.run_until_complete(session.run())

    session.stream.wait_for_connection.assert_awaited_once()
    session.stream.wait_for_disconnection.assert_awaited_once()
    session.stream.stop.assert_awaited_once()
    assert session.identifier not in session.stream_dict

  def test_stop_cancels_running_task_and_cleans_up_once(self, mocker):
    session = self._lifecycle_session(mocker)
    connection_wait = asyncio.Event()

    async def wait_for_connection():
      await connection_wait.wait()

    session.stream.wait_for_connection.side_effect = wait_for_connection

    async def start_and_stop():
      session.start()
      await asyncio.sleep(0)
      await session.stop()

    self.loop.run_until_complete(start_and_stop())

    session.stream.stop.assert_awaited_once()
    assert session.run_task is None
    assert session.identifier not in session.stream_dict

  def test_shutdown_continues_after_session_stop_failure(self, mocker):
    failed = self._stream_session(mocker, "failed")
    failed.stop.side_effect = RuntimeError("cleanup failed")
    healthy = self._stream_session(mocker, "healthy")
    app = {"streams": {failed.identifier: failed, healthy.identifier: healthy}}
    set_active = mocker.patch.object(webrtcd, "_set_carrot_vision_active")

    self.loop.run_until_complete(carrot_session.on_shutdown(app))

    failed.stop.assert_awaited_once()
    healthy.stop.assert_awaited_once()
    assert app["streams"] == {}
    set_active.assert_called_once_with(False)


def test_parked_camera_demand_refreshes_active_key_after_offroad_transition(mocker):
  params = mocker.Mock()
  params.get_bool.return_value = False
  mocker.patch.object(webrtcd, '_carrot_vision_mode', True)
  mocker.patch.object(webrtcd, '_carrot_vision_params', params)
  mocker.patch.object(webrtcd, '_carrot_vision_active', True)
  lease = mocker.patch.object(carrot_session, 'update_camera_request')
  carrot_session.sync_camera_request({'viewer': SimpleNamespace(uses_road_camera=True)})
  lease.assert_called_once_with(True)
  params.put_bool_nonblocking.assert_called_once_with('CarrotVisionActive', True)
  carrot_session.sync_camera_request({})
  assert lease.call_args.args == (False,)


def test_carrot_mode_rejects_input_bridge_and_other_cameras(mocker):
  mocker.patch.object(webrtcd, '_carrot_vision_mode', True)

  async def check():
    for patch in ({'cameras': ['driver']}, {'bridge_services_in': ['carControl']}):
      request = mocker.Mock()
      request.app = {'streams': {}, 'debug': False}
      request.json = mocker.AsyncMock(return_value={'sdp': 'offer', 'cameras': ['road'], **patch})
      with pytest.raises(web.HTTPBadRequest):
        await carrot_session.get_stream(request)
  asyncio.run(check())


def test_camera_lease_renews_while_negotiation_holds_registry_lock(mocker):
  mocker.patch.object(carrot_session, 'CARROT_STREAM_PRUNE_INTERVAL_SEC', 0)
  prune = mocker.patch.object(carrot_session, 'prune_ended_stream_sessions', new_callable=mocker.AsyncMock)

  async def check():
    renewed = asyncio.Event()
    sync = mocker.patch.object(carrot_session, 'sync_camera_request', side_effect=lambda _: renewed.set())
    app = {'streams': {}, 'stream_lock': asyncio.Lock()}
    async with app['stream_lock']:
      context = carrot_session.stream_session_cleanup_context(app)
      await anext(context)
      try:
        await asyncio.wait_for(renewed.wait(), timeout=1)
        sync.assert_called_with(app['streams'])
        prune.assert_not_awaited()
      finally:
        await context.aclose()
    assert 'stream_cleanup_task' not in app
  asyncio.run(check())


def test_stalled_answer_times_out_and_releases_session(mocker):
  mocker.patch.object(carrot_session, 'CARROT_STREAM_NEGOTIATION_TIMEOUT_SEC', 0.01)
  mocker.patch.object(carrot_session, 'sync_camera_request')

  async def check():
    session = TestCarrotStreamSession._lifecycle_session(mocker)
    async def pending_answer():
      await asyncio.Future()
    session.get_answer = pending_answer
    mocker.patch.object(carrot_session, 'CarrotStreamSession', return_value=session)
    streams = {}
    request = TestCarrotStreamSession._stream_request(mocker, streams, client_id='viewer')
    with pytest.raises(TimeoutError):
      await carrot_session.get_stream(request)
    assert streams == {}
    session.stream.stop.assert_awaited_once()
  asyncio.run(check())
