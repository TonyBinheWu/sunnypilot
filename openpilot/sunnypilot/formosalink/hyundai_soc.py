"""Passive Hyundai/Kia SOC observation; never publishes CAN or changes carState.

Only BAT11's documented 12V signal is enabled. Traction candidates are not
interchangeable with this signal and remain unsupported until verified.
"""
import threading
import time


def profile(brand,model,canfd,dbc_aux_verified=False):
  return {"model":model,"family":"canfd" if canfd else "can",
          "aux_supported":brand=="hyundai" and not canfd and dbc_aux_verified,
          "traction_supported":False}


class SocTracker:
  def __init__(self):
    self.configuration=None
    self.last=None
    self.count=0
    self.soc=None
    self.voltage=None

  def configure(self,configuration):
    if configuration!=self.configuration:
      self.configuration=configuration;self.last=None;self.count=0;self.soc=None;self.voltage=None

  def feed(self,address,bus,data,producer_time,now):
    if not self.configuration or not self.configuration["aux_supported"] or address!=0x549 or bus!=0 or len(data)!=8:
      return
    if not 0<=now-producer_time<=2 or self.last is not None and producer_time<=self.last:
      return
    if data==bytes(8) or data==b"\xff"*8:
      self.last=None;self.count=0;return
    raw=int.from_bytes(data,"little")
    soc=(raw>>16)&255;voltage=((raw>>24)&0x3fff)*.001+6
    if soc>100 or not 6<=voltage<=18:
      self.last=None;self.count=0;return
    self.count=self.count+1 if self.last is not None and producer_time-self.last<=2 else 1
    self.last=producer_time;self.soc=soc;self.voltage=round(voltage,3)

  def snapshot(self,now):
    supported=bool(self.configuration and self.configuration["aux_supported"])
    valid=supported and self.count>=2 and self.last is not None and 0<=now-self.last<=2
    return {"aux_soc_status":"available" if valid else "waiting" if supported and self.last is None else "stale" if supported else "unsupported",
            "aux_soc_percent":self.soc if valid else None,"aux_battery_voltage":self.voltage if valid else None,
            "aux_soc_source":"BAT11.BAT_SOC (12V)" if supported else "",
            "soc_detection":"hyundai_canfd_no_verified_traction_signal" if self.configuration and self.configuration["family"]=="canfd" else "no_verified_traction_signal" if self.configuration else "",
            "vehicle_powertrain":self.configuration.get("powertrain","unknown") if self.configuration else "unknown",
            "soc_vehicle_model":self.configuration["model"] if self.configuration else ""}


def verify_aux_dbc(dbc):
  message=dbc.name_to_msg.get("BAT11")
  if not message or message.address!=0x549 or message.size!=8:
    return False
  signal=message.sigs.get("BAT_SOC");voltage=message.sigs.get("BAT_SNSR_V")
  return bool(signal and voltage and signal.start_bit==16 and signal.size==8 and signal.factor==1 and signal.offset==0 and signal.is_little_endian
              and voltage.start_bit==24 and voltage.size==14 and voltage.factor==.001 and voltage.offset==6 and voltage.is_little_endian)


class NativeSocObserver:
  def __init__(self,params):
    self.params=params;self.tracker=SocTracker();self.lock=threading.Lock();self.cp_bytes=None;self.started=False

  def capture(self):
    from openpilot.cereal import messaging
    from opendbc.car.structs import car
    from opendbc.car import Bus
    from opendbc.car.hyundai.values import HyundaiFlags,DBC
    from opendbc.can.dbc import DBC as Database
    raw=self.params.get("CarParamsPersistent")
    if raw!=self.cp_bytes:
      configuration=None
      if raw:
        try:
          cp=messaging.log_from_bytes(raw,car.CarParams)
          if cp.brand=="hyundai" and cp.carFingerprint in DBC:
            canfd=bool(cp.flags&HyundaiFlags.CANFD)
            verified=not canfd and verify_aux_dbc(Database(DBC[cp.carFingerprint][Bus.pt]))
            configuration=profile(cp.brand,cp.carFingerprint,canfd,verified)
            configuration["powertrain"]="EV" if cp.flags&HyundaiFlags.EV else "HEV/PHEV" if cp.flags&HyundaiFlags.HYBRID else "FCEV" if cp.flags&getattr(HyundaiFlags,"FCEV",0) else "ICE"
        except Exception:
          configuration=None
      with self.lock:
        self.tracker.configure(configuration)
      self.cp_bytes=raw
      if configuration and configuration["aux_supported"] and not self.started:
        self.started=True
        threading.Thread(target=self._receive,name="formosalink-soc",daemon=True).start()
    with self.lock:
      return self.tracker.snapshot(time.monotonic())

  def _receive(self):
    from openpilot.cereal import messaging
    sock=messaging.sub_sock("can",conflate=False,timeout=0)
    try:
      while True:
        for _ in range(256):
          event=messaging.recv_one_or_none(sock)
          if event is None:
            break
          if not event.valid:
            continue
          now=time.monotonic();stamp=event.logMonoTime/1e9
          with self.lock:
            for frame in event.can:
              self.tracker.feed(frame.address,frame.src,bytes(frame.dat),stamp,now)
        time.sleep(.05)
    finally:
      del sock
