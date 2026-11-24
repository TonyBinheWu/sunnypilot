from types import SimpleNamespace as NS
import time

import numpy as np
import pytest

from openpilot.common import sunny_models as sunny
from openpilot.selfdrive.modeld.auxiliary_inference import AuxiliaryInference, refine


def test_choices_keep_named_aliases_and_freeze_boot(tmp_path, monkeypatch):
  monkeypatch.setenv('CARROT_BIG_MODEL_DIR', str(tmp_path))
  small = [k for k,v in sunny.catalog().items() if not v['big']]
  big = [k for k,v in sunny.catalog().items() if v['big']]
  assert (len(small), len(big)) == (79,25)
  assert len({v['sha256'] for v in sunny.catalog().values()}) == 101
  sunny.save('small', small[0])
  sunny.save('big', big[-1])
  sunny.freeze_boot()
  sunny.save('small', small[-1])
  sunny.save('assistant', True)
  sunny.freeze_boot()
  assert sunny.key_for(False, True) == small[0] and sunny.key_for(True, True) == big[-1]
  assert sunny.key_for(False) == small[-1] and not sunny.prefs(True).get('assistant')
  with pytest.raises(ValueError):
    sunny.select(False, small[-1], lambda:False)


def test_bad_download_does_not_replace_cache(tmp_path):
  import hashlib
  src, dst = tmp_path/'payload', tmp_path/'cache'
  src.write_bytes(b'new')
  dst.write_bytes(b'old')
  sha = hashlib.sha256(b'new').hexdigest()
  with pytest.raises(ValueError):
    sunny.download(src.as_uri(), '0'*64, dst, lambda:True, 3)
  assert dst.read_bytes() == b'old'
  with pytest.raises(ValueError):
    sunny.download(src.as_uri(), sha, dst, lambda:False, 3)
  sunny.download(src.as_uri(), sha, dst, lambda:True, 3)
  assert dst.read_bytes() == b'new'


@pytest.mark.parametrize('current,other', [(.5,-.8),(-.1,-.5),(-1,-.8),(-1,-3),(-1,float('nan'))])
def test_auxiliary_does_not_start_braking_or_relax_primary(current,other):
  assert refine(current,(current,0,0,12),(other,0,0,12)) == current


def test_auxiliary_requires_agreement_on_speed_and_path():
  p = (-1.,0,0,12)
  assert refine(-1.,p,(-1.8,0,0,12)) == pytest.approx(-1.15)
  assert refine(-1.,p,(-1.5,0,1.5,12)) == -1.
  assert refine(-1.,p,(-1.5,0,0,9)) == -1.


def test_auxiliary_expires_and_consumes_each_agreement_once():
  aux = AuxiliaryInference.__new__(AuxiliaryInference)
  aux.last_used = -1
  aux.result = (50, 1., (-1.6,0,0,10))
  plan = np.zeros((1,33,15))
  plan[:,:,3] = 10
  output = {'plan':plan,'action':np.array([[0,-1.]])}
  action = NS(shouldStop=False,desiredAcceleration=-1.)
  def result(frame, now, enabled=True):
    return aux.acceleration(output,action,frame,1.05,now,enabled,.2)
  assert result(51,1.06,False) == -1.
  assert result(52,1.06) == -1.
  assert result(51,1.06) == pytest.approx(-1.15)
  assert result(51,1.07) == -1.
  aux.last_used = -1
  assert result(51,1.13) == -1.


def test_submit_owns_buffers_and_drops_work_while_busy():
  import threading
  aux = AuxiliaryInference.__new__(AuxiliaryInference)
  aux.runner, aux.gate, aux.wake = object(), threading.Lock(), threading.Event()
  data = bytearray(b'abcd')
  buf = NS(data=data,width=2,height=2,stride=2,uv_offset=2)
  matrix = np.eye(3)
  aux.submit({'img':buf},{'img':matrix},{'action_t':np.zeros(2)},1,time.monotonic())
  data[0] = 0
  matrix[0,0] = 0
  aux.submit({}, {}, {}, 2, time.monotonic())
  assert aux.job[0]['img'].data == b'abcd' and aux.job[1]['img'][0,0] == 1 and aux.job[3] == 1


def test_second_model_must_warm_again_after_a_gap(monkeypatch):
  import threading
  from openpilot.selfdrive.modeld import auxiliary_inference as mod
  aux = AuxiliaryInference.__new__(AuxiliaryInference)
  aux.result = None
  current = [0.]
  seen = {}
  plan = np.zeros((1,33,15))
  runner = NS(run=lambda *args: {'plan':plan}, close=lambda:None)
  frames = iter([*range(1,101), *range(102,203)])
  class End(BaseException):
    pass
  class Wake:
    def wait(self):
      if aux.result:
        seen[aux.result[0]] = True
      frame = next(frames,None)
      if frame is None:
        raise End
      eof = frame*.05
      current[0] = eof+.03 if frame < 202 else eof+.13
      aux.job = {},{},dict(action_t=[0,.2]),frame,eof
      aux.gate.acquire()
    def clear(self):
      pass
  aux.gate, aux.wake = threading.Lock(), Wake()
  monkeypatch.setattr(mod.time, 'monotonic', lambda:current[0])
  monkeypatch.setattr(mod, 'publish_status', lambda *args:None)
  monkeypatch.delattr(mod.os, 'sched_setscheduler', raising=False)
  with pytest.raises(End):
    aux.work(lambda:runner)
  assert set(seen) == {100,201}
  assert aux.runner is aux.result is None


def test_legacy_pedal_and_disengagement_layouts_are_distinct():
  from openpilot.selfdrive.modeld.fill_model_msg import LegacyMeta, Meta
  a=np.arange(55)
  assert a[LegacyMeta.HARD_BRAKE_5].tolist() == [6,13,20,27,34]
  assert a[LegacyMeta.GAS_PRESS].tolist() == [7,14,21,28,35]
  assert not hasattr(LegacyMeta, 'BRAKE_PRESS')
  assert a[Meta.HARD_BRAKE_5].tolist() == [6,12,18,24,30]
