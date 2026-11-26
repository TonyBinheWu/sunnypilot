import json
import os
import time
from types import SimpleNamespace as NS

from openpilot.selfdrive.modeld import gpu_workload as work
from openpilot.selfdrive.carrot.server.services import task_manager as monitor


def test_workload_idle_expiry_and_headroom(monkeypatch,tmp_path):
  monkeypatch.setattr(work,"ROOT",tmp_path)
  monkeypatch.setattr(work,"WATCH",tmp_path/"watch")
  monkeypatch.setattr(monitor,"ROOT",tmp_path)
  from openpilot.common.hardware import usb
  monkeypatch.setattr(usb,"get_usb_state",lambda:[])
  dev=NS(arch="gfx1200",iface=NS(dev_impl=NS(vram_size=1000,mm=NS(pa_allocator=NS(blocks={0:(200,None,None,True),1:(700,None,None,False)})))))
  task=work.GpuWorkload(dev,"test GPU")
  t=time.monotonic()
  task.start=t-2
  task.completed(t-.5,t)
  assert not task.path.exists()
  work.WATCH.touch()
  task.completed(t+1,t+2)
  row=json.loads(task.path.read_text())
  assert row["pid"]==os.getpid() and row["worker_busy"]==50 and row["free_bytes"]==200
  assert monitor.external_gpu(t+2)["workers"]==[row]
  assert not monitor.external_gpu(t+5)["workers"]


def test_process_samples_shared_and_bounded(monkeypatch,tmp_path):
  monkeypatch.setattr(monitor,"WATCH",tmp_path/"watch")
  monkeypatch.setattr(monitor,"external_gpu",lambda now: {})
  obj=monitor.TaskManager()
  monkeypatch.setattr(obj,"device_gpu",lambda now: None)
  a=obj.snapshot()
  assert obj.snapshot() is a and a["memory"]["total"]>=a["memory"]["free"]>0 and a["gpu"] is None
  assert 0<len(a["processes"])<=256
  obj.at-=2
  b=obj.snapshot()
  assert b is not a and len(b["cores"])>0 and any(p["cpu"] is not None for p in b["processes"])
