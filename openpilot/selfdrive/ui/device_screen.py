import io
import time
from concurrent.futures import ThreadPoolExecutor

import pyray as rl

from openpilot.common.remote_screen import MAX_FRAME, ScreenSession
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, MouseEvent, MousePos
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.label import gui_label

MAX_TOUCH_FRAME_AGE = 1.4


def parked():
  sm = ui_state.sm
  now = time.monotonic()
  def fresh(service, age):
    return sm.valid[service] and 0 <= now-sm.logMonoTime[service]/1e9 <= age
  if ui_state.started or not fresh("deviceState", 2.5) or sm["deviceState"].started:
    return False
  if not ui_state.params.get_bool("IsOffroad") or any(ui_state.params.get_bool(k) for k in ("IsOnroad","ForceOffroad","ForceOffroadActive","IsEngaged")):
    return False
  if fresh("pandaStates", 1) and any(p.ignitionLine or p.ignitionCan for p in sm["pandaStates"]):
    return False
  if fresh("carState", .5) and sm["carState"].canValid:
    car = sm["carState"]
    if str(car.gearShifter) != "park" or not car.standstill or not abs(car.vEgo) <= .05:
      return False
  return True


def compress_frame(width, height, rgba):
  from PIL import Image
  image = Image.frombytes("RGBA", (width, height), rgba).convert("RGB")
  if image.getbbox() is None:
    return b""
  stream = io.BytesIO()
  image.save(stream, format="PNG", compress_level=1)
  if stream.tell() > MAX_FRAME - 4:
    # High-entropy camera frames can exceed the socket limit at the parked C3X resolution.
    stream.seek(0)
    stream.truncate()
    image.reduce(2).save(stream, format="PNG", compress_level=1)
  return stream.getvalue()


class DeviceScreen(ScreenSession):
  def __init__(self):
    super().__init__(parked, continue_paired=lambda: True)
    self.mode = "waiting"
    self.touch_active = False
    self.notice_until = 0.
    self.encoder = None
    self.encoding = None
    self.session_id = 0
    self.visible_at = None

  def invalidate_frame(self):
    if self.visible_at is not None:
      self.epoch += 4
    self.visible_at = None
    self.down = False

  def close_peer(self):
    super().close_peer()
    self.invalidate_frame()

  def arm(self):
    if not self.listener:
      self.session_id += 1
    super().arm()
    if not self.listener:
      self.notice_until = time.monotonic()+3

  def input_mode(self):
    sm = ui_state.sm
    now = time.monotonic()
    def fresh(service, max_age):
      age = now - sm.logMonoTime[service] / 1e9
      return sm.valid[service] and 0 <= age <= max_age

    if not fresh("deviceState", 2.5):
      return "waiting"
    if ui_state.started and sm["deviceState"].started:
      if not fresh("selfdriveState", 0.5) or str(sm["selfdriveState"].alertSize) not in ("none", "small"):
        return "waiting"
      return "road"
    return "park" if parked() else "waiting"

  def inputs(self, physical):
    if not self.listener and not self.cancel and not self.touch_active:
      return physical

    mode = self.input_mode()
    changed = mode != self.mode
    now = time.monotonic()
    if changed:
      # Inputs from the previous screen state cannot finish a gesture in the new one.
      self.epoch = (self.epoch // 4 + 1) * 4 + {"park": 0, "road": 1, "waiting": 2}[mode]
      self.down = False
      self.visible_at = None
      self.mode = mode
    elif self.visible_at is not None and now - self.visible_at > MAX_TOUCH_FRAME_AGE:
      self.invalidate_frame()

    local_press = any(event.left_pressed for event in physical)
    pairing_overlay = bool(self.pin)
    remote = self.tick(local_press)
    now = time.monotonic()
    events = []
    if self.touch_active and (self.visible_at is None or not self.auth or local_press):
      events.append(MouseEvent(MousePos(-1, -1), 0, False, True, False, now))
      self.touch_active = False

    # The first physical tap dismisses the PIN screen. Once paired, local input takes priority.
    if not pairing_overlay:
      events.extend(physical)
    if self.visible_at is None or not self.auth or mode == "waiting" or local_press:
      self.down = False
      return events

    for action, x, y in remote:
      if action != "down" and not self.touch_active:
        continue
      pressed = action == "down"
      released = action in ("up", "cancel")
      self.touch_active = not released
      pos = MousePos(-1, -1) if action == "cancel" else MousePos(x * (gui_app.width - 1), y * (gui_app.height - 1))
      events.append(MouseEvent(pos, 0, pressed, released, self.touch_active, now))
    return events

  def shutdown(self):
    self.close()
    if self.encoder:
      self.encoder.shutdown(wait=False, cancel_futures=True)

  def paint(self):
    w, h = gui_app.width, gui_app.height
    scale = min(w/536, h/240)
    if self.encoding and self.encoding.done():
      completed, self.encoding = self.encoding, None
      try:
        if self.auth and self.encoding_key == (self.session_id, self.epoch):
          png = completed.result()
          if png and time.monotonic() - self.captured_at <= MAX_TOUCH_FRAME_AGE:
            self.visible_at = self.captured_at
            self.frame(png)
          else:
            self.invalidate_frame()
            self.frame(b"")
      except (OSError, ValueError):
        self.invalidate_frame()
        self.frame(b"")
    onroad = self.mode == "road" or ui_state.started
    if self.encoding is None and self.wants_frame() and (not onroad or time.monotonic()-self.last_frame >= .4):
      self.last_frame = time.monotonic()
      # EndDrawing normally flushes raylib's queued UI (or the recording texture
      # blit). Capture before the private overlay, after submitting that batch.
      rl.rl_draw_render_batch_active()
      img = rl.load_image_from_screen()
      try:
        limit = 640 if onroad else 864
        if img.data != rl.ffi.NULL and img.width > 0 and img.height > 0:
          if img.width > limit:
            rl.image_resize_nn(img, limit, max(1, round(img.height*limit/img.width)))
          rl.image_format(img, rl.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8)
          rgba = bytes(rl.ffi.buffer(img.data, img.width*img.height*4))
          if self.encoder is None:
            self.encoder = ThreadPoolExecutor(max_workers=1, thread_name_prefix="screen-png")
          self.encoding_key = (self.session_id, self.epoch)
          self.captured_at = self.last_frame
          self.encoding = self.encoder.submit(compress_frame, img.width, img.height, rgba)
        else:
          self.invalidate_frame()
          self.frame(b"")
      finally:
        rl.unload_image(img)
    if onroad or (not self.listener and time.monotonic() >= self.notice_until):
      return
    if self.pin:
      rl.clear_background(rl.Color(17,27,25,255))
      gui_label(rl.Rectangle(.08*w,.12*h,.85*w,.17*h),tr("Remote screen"),int(25*scale))
      gui_label(rl.Rectangle(.08*w,.32*h,.85*w,.36*h), self.pin, int(64*scale))
      message = tr("Enter this code in Carrot Web")
    else:
      message = tr("Touch device to stop sharing") if self.auth else tr("Available when parked with ignition off")
    bar = rl.Rectangle(0,h-34*scale,w,34*scale)
    rl.draw_rectangle_rec(bar, rl.Color(21,64,49,255))
    gui_label(rl.Rectangle(12*scale,bar.y,w-24*scale,bar.height), message,int(19*scale))
