import importlib.util
from pathlib import Path
from types import SimpleNamespace

spec=importlib.util.spec_from_file_location('display_lighting',Path(__file__).parents[1]/'lighting.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_actual_lamps_release_and_stale_values_become_unknown():
  cp=SimpleNamespace(vl={'CGW1':{'CF_Gway_HeadLampLow':1,'CF_Gway_HeadLampHigh':0}},
    ts_nanos={'CGW1':{'CF_Gway_HeadLampLow':1_000_000_000,'CF_Gway_HeadLampHigh':1_000_000_000}},
    dat={1345:bytes(8)},bus_timeout=False,_last_update_nanos=1_010_000_000)
  assert module.classic_lighting_state(cp)==(True,True,False)
  cp.vl['CGW1']['CF_Gway_HeadLampLow']=0
  assert module.classic_lighting_state(cp)==(True,False,False)
  cp._last_update_nanos=1_500_000_001
  assert module.classic_lighting_state(cp)==(False,False,False)
  cp._last_update_nanos=1_010_000_000;cp.bus_timeout=True
  assert module.classic_lighting_state(cp)==(False,False,False)
  cp.bus_timeout=False;cp.dat[1345]=bytes(7)
  assert module.classic_lighting_state(cp)==(False,False,False)
