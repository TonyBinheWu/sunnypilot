import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.cereal import car, log
from openpilot.common.runtime_diagnostics import RuntimeDiagnostics


class EndOfInputs(Exception):
  pass


def run_planner_events(mocker, brand, configured_mode, radar_period_ms, *, stopping=False, gas_pressed=False, upstream=False):
  model_times = list(range(0, 1000, 50))
  radar_times = list(range(20, 1000, radar_period_ms))
  events = iter(sorted(set(model_times + radar_times)))
  services = ('modelV2', 'radarState', 'liveTracks', 'carState')
  radar_state = log.RadarState.new_message()
  radar_state.leadOne.status = radar_state.leadOne.radar = True
  radar_state.leadOne.radarTrackId = 35
  radar_state.leadOne.dRel = 5.5
  radar_state.leadOne.vLead = radar_state.leadOne.vLeadK = 0.217
  radar_state.leadOne.vRel = 0.17

  class SubMaster:
    def __init__(self):
      self.now = 10.0
      self.seen = dict.fromkeys(services, False)
      self.updated = dict.fromkeys(services, False)
      self.valid = dict.fromkeys(services, True)
      self.alive = dict.fromkeys(services, True)
      self.recv_time = dict.fromkeys(services, 0.0)
      self.logMonoTime = dict.fromkeys(services, 0)

    def update(self):
      try:
        offset_ms = next(events)
      except StopIteration:
        raise EndOfInputs from None
      self.now = 10.0 + offset_ms / 1000.0
      for service in services:
        updated = offset_ms in (radar_times if service == 'liveTracks' else model_times)
        self.updated[service] = updated
        if updated:
          self.seen[service] = True
          self.recv_time[service] = self.now
          self.logMonoTime[service] = 10_000_000_000 + offset_ms * 1_000_000

    def __getitem__(self, service):
      return {
        'selfdriveState': SimpleNamespace(experimentalMode=False),
        'carState': SimpleNamespace(vEgo=0.05 if stopping else 10.0, gasPressed=gas_pressed),
        'controlsState': SimpleNamespace(longControlState=(
          car.CarControl.Actuators.LongControlState.stopping if stopping else car.CarControl.Actuators.LongControlState.pid)),
        'radarState': radar_state,
        'modelV2': SimpleNamespace(frameId=round((self.now - 10.0) * 20)),
      }.get(service, SimpleNamespace())

    def all_checks(self, _services):
      return True

  sm = SubMaster()
  sub_master_factory = mocker.Mock(return_value=sm)
  cp = SimpleNamespace(brand=brand, flags=0, radarUnavailable=False, radarDelay=0.8, openpilotLongitudinalControl=True)
  params = mocker.Mock()
  params.get_int.side_effect = lambda key: int(upstream) if key == "DrivingPlannerMode" else configured_mode
  planner = mocker.Mock()
  calls = []
  planner.publish.side_effect = lambda *args, **kwargs: calls.append((sm.now, kwargs))
  namespace = {
    'time': SimpleNamespace(monotonic=lambda: sm.now, thread_time=lambda: sm.now),
    'car': car,
    'Params': lambda: params,
    'Priority': SimpleNamespace(CTRL_LOW=0),
    'config_realtime_process': mocker.Mock(),
    'cloudlog': mocker.Mock(),
    'RuntimeDiagnostics': RuntimeDiagnostics,
    'LongitudinalPlanner': mocker.Mock(return_value=planner),
    'LateralPlanner': mocker.Mock(),
    'LaneDepartureWarning': mocker.Mock(),
    'messaging': SimpleNamespace(
      log_from_bytes=lambda value, schema: cp,
      PubMaster=mocker.Mock(),
      SubMaster=sub_master_factory,
      new_message=lambda service: SimpleNamespace(driverAssistance=SimpleNamespace()),
    ),
  }
  # Exercise the production event loop without loading hardware, messaging or
  # the native MPC solver. Only imports and the __main__ invocation are omitted.
  path = Path(__file__).parents[1] / 'plannerd.py'
  tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
  tree.body = [node for node in tree.body if isinstance(node, (ast.Assign, ast.FunctionDef))]
  exec(compile(tree, str(path), 'exec'), namespace)
  with pytest.raises(EndOfInputs):
    namespace['main']()
  namespace['LongitudinalPlanner'].assert_called_once_with(cp, sunny=True)
  assert planner.update.call_count == len(calls)
  return calls, sub_master_factory.call_args.kwargs['poll'], planner


@pytest.mark.parametrize('brand', ['hyundai', 'volkswagen', 'toyota', 'honda'])
@pytest.mark.parametrize('radar_period_ms', [20, 40, 50])
@pytest.mark.parametrize('saved_mode', [0, 1, 2, 3, 4])
def test_all_profiles_plan_at_model_rate_using_unmodified_leads(mocker, brand, radar_period_ms, saved_mode):
  calls, poll, planner = run_planner_events(mocker, brand, 1, radar_period_ms, upstream=saved_mode)
  assert poll == 'modelV2'
  assert [timestamp for timestamp, _ in calls] == pytest.approx([10.0 + n * 0.05 for n in range(20)])
  for call in planner.update.call_args_list:
    sm, = call.args
    assert sm['radarState'].leadOne.vLead == pytest.approx(.217)
