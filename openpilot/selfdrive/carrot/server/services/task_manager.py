"""On-demand Linux hardware and process snapshots. One sample shared by all viewers."""
import json
import math
import shutil
import threading
import time
from pathlib import Path

import psutil

from openpilot.selfdrive.modeld.gpu_workload import ROOT, WATCH


def numeric(path, divisor=1):
  try:
    value = float(path.read_text().strip()) / divisor
    return value if math.isfinite(value) else None
  except (OSError, ValueError):
    return None


class TaskManager:
  def __init__(self):
    self.lock = threading.Lock()
    self.at, self.last, self.prev, self.cpu = 0., {}, {}, []
    self.io = None
    self.sock = self.chestnut_sock = None
    self.chestnut_at, self.chestnut_temps = 0., []

  def snapshot(self):
    with self.lock:
      now = time.monotonic()
      if self.last and now - self.at < 1.:
        return self.last
      try:
        WATCH.touch()
      except OSError:
        pass
      memory = psutil.virtual_memory()
      disk = shutil.disk_usage("/data" if Path("/data").exists() else "/")
      rows, latest = [], {}
      for process in psutil.process_iter(["name", "cpu_times", "memory_info", "create_time"], ad_value=None):
        try:
          info = process.info
          if info["cpu_times"] is None or info["memory_info"] is None:
            continue
          key = process.pid, info["create_time"]
          times = info["cpu_times"].user + info["cpu_times"].system
          latest[key] = times
          pct = round(max(0., times-self.prev[key])*100/(now-self.at), 1) if key in self.prev else None
          rows.append(dict(pid=process.pid, name=info["name"] or "?", cpu=pct, rss=info["memory_info"].rss))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
          continue
      cores = []
      ticks = psutil.cpu_times(percpu=True)
      for a, b in zip(self.cpu, ticks):
        total = sum(b)-sum(a)-(getattr(b,"guest",0)-getattr(a,"guest",0))-(getattr(b,"guest_nice",0)-getattr(a,"guest_nice",0))
        idle = b.idle-a.idle + getattr(b,"iowait",0)-getattr(a,"iowait",0)
        cores.append(round(max(0., min(100., 100*(1-idle/total))), 1) if total > 0 else None)
      sensors = []
      for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        temp = numeric(zone / "temp", 1000)
        if temp is not None and -40 < temp < 180:
          try:
            sensors.append([zone.joinpath("type").read_text().strip(), round(temp,1)])
          except OSError:
            pass
      gpu = self.device_gpu(now)
      rows.sort(key=lambda row: (row['cpu'] or 0, row['rss']), reverse=True)
      net, storage_io = psutil.net_io_counters(), psutil.disk_io_counters()
      io = {"rx":net.bytes_recv, "tx":net.bytes_sent} if net else {}
      if storage_io:
        io.update(read=storage_io.read_bytes, write=storage_io.write_bytes)
      rates = {k:(v-self.io[k])/(now-self.at) for k,v in io.items() if self.io and k in self.io and v >= self.io[k]}
      self.io = io
      egpu = external_gpu(now)
      egpu["temps"] = self.chestnut_temps if 0 <= now-self.chestnut_at <= 3 else []
      self.last = dict(cores=cores, io=rates, memory=dict(total=memory.total, free=memory.available),
                       disk=dict(total=disk.total, free=disk.free), temps=sensors, gpu=gpu,
                       egpu=egpu, processes=rows[:256], process_count=len(rows))
      self.at, self.prev, self.cpu = now, latest, ticks
      return self.last

  def device_gpu(self, now):
    # Read hardwared's existing sample; never reset its KGSL interval by reading gpubusy again.
    try:
      import openpilot.cereal.messaging as messaging
      if self.sock is None:
        self.sock = messaging.sub_sock("deviceState", conflate=True)
        self.gpu_at, self.gpu = 0., None
        from openpilot.cereal.services import SERVICE_LIST
        if "chestnutGpuState" in SERVICE_LIST:
          self.chestnut_sock = messaging.sub_sock("chestnutGpuState", conflate=True)
      if self.chestnut_sock is not None:
        chestnut = messaging.recv_one_or_none(self.chestnut_sock)
        if chestnut is not None:
          self.chestnut_at = chestnut.logMonoTime/1e9
          self.chestnut_temps = [(name, value) for name, value in
                                 (("GPU", chestnut.chestnutGpuState.tempC), ("VRAM", chestnut.chestnutGpuState.memoryTempC))
                                 if chestnut.valid and math.isfinite(value) and 0 < value < 160]
      event = messaging.recv_one_or_none(self.sock)
      if event is not None:
        self.gpu_at = event.logMonoTime/1e9
        self.gpu = int(event.deviceState.gpuUsagePercent) if event.valid else None
      if 0 <= now-self.gpu_at < 4:
        return self.gpu
    except (ImportError, OSError, RuntimeError):
      pass
    return None


def external_gpu(now):
  from openpilot.common.hardware.usb import get_usb_state, is_chestnut_usb_id
  bridge = next((r for r in get_usb_state() if is_chestnut_usb_id(r["vendorId"], r["productId"])), None)
  workers = []
  for path in ROOT.glob("carrot-gpu-work-*.json"):
    try:
      row = json.loads(path.read_bytes()[:2048])
      if 0 <= now-row["at"] < 3 and psutil.pid_exists(row["pid"]):
        workers.append(row)
    except (OSError, ValueError, KeyError, TypeError):
      continue
  cards = []
  for card in Path("/sys/class/drm").glob("card[0-9]*"):
    if not card.name.removeprefix("card").isdigit():
      continue
    dev = card / "device"
    if numeric_hex(dev / "vendor") != 0x1002:
      continue
    total, used = numeric(dev / "mem_info_vram_total"), numeric(dev / "mem_info_vram_used")
    cards.append(dict(name=card.name, busy=numeric(dev / "gpu_busy_percent"), total_bytes=total,
                      free_bytes=total-used if total is not None and used is not None else None,
                      temps=[[f.name,numeric(f,1000)] for f in sorted(dev.glob("hwmon/hwmon*/temp*_input"))]))
  return dict(bridge=bridge["product"] if bridge else None, usb_mbps=bridge["speedMbps"] if bridge else None,
              cards=cards, workers=workers)


def numeric_hex(path):
  try:
    return int(path.read_text().strip(), 16)
  except (OSError, ValueError):
    return None
