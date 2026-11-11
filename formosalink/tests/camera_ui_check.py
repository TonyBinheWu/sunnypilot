"""Native camera IPC and encoder acceptance using synthetic frames, never a real camera."""
import errno
import io
import struct
import subprocess
import tempfile
import threading
import time
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from PIL import Image
from msgq.visionipc import VisionIpcServer
from openpilot.cereal.visionipc import VisionStreamType
from openpilot.sunnypilot.formosalink.cameras import NativeCamera
from openpilot.sunnypilot.formosalink.cellular_link import sample_link


class TestNativeCamera(unittest.TestCase):
  def test_real_manager_camera_condition_all_modes(self):
    import itertools
    from openpilot.system.manager.process_config import managed_processes
    predicate=managed_processes['camerad'].should_run
    for started,driver,live,enabled,leased in itertools.product((False,True),repeat=5):
      flags={'IsDriverViewEnabled':driver,'IsLiveStreaming':live,'FormosaLinkEnabled':enabled}
      params=SimpleNamespace(get_bool=lambda key:flags.get(key,False))
      with patch('openpilot.sunnypilot.formosalink.cameras.camera_requested',return_value=leased):
        self.assertEqual(predicate(started,params,None),started or driver or live or enabled and leased)

  def test_persistent_encoder_reuses_process_for_both_camera_streams(self):
    from openpilot.sunnypilot.formosalink.stream_encoder import StreamEncoder
    width,height,stride,offset=64,48,80,4096
    raw=np.zeros(offset+stride*height//2,dtype=np.uint8)
    raw[:stride*height]=96;raw[offset:]=128
    frame=SimpleNamespace(width=width,height=height,stride=stride,uv_offset=offset,data=raw)
    for camera in ('wide-road','driver'):
      encoder=StreamEncoder()
      try:
        pid=None
        for _ in range(8):
          data=encoder(frame)
          image=Image.open(io.BytesIO(data)).convert('RGB')
          self.assertEqual(image.size,(480,360))
          self.assertTrue(all(80 <= value <= 105 for value in image.getpixel((240,180))))
          if pid is None:pid=encoder.process.pid
          self.assertEqual(encoder.process.pid,pid)
      finally:
        process=encoder.process
        encoder.close()
        if process is not None:self.assertIsNotNone(process.poll())

  def test_only_fresh_owner_lease_requests_offroad_cameras(self):
    from openpilot.common.params import Params
    from openpilot.system.manager.process_config import formosalink_cameras
    from openpilot.sunnypilot.formosalink.cameras import save_lease
    from pathlib import Path
    with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'FORMOSALINK_CAMERA_LEASE':str(Path(directory)/'lease')}):
      params=Params(directory)
      params.put_bool('FormosaLinkEnabled',True,block=True)
      self.assertFalse(formosalink_cameras(False,params,None))
      with patch('time.monotonic',return_value=100):
        save_lease(['driver'])
        self.assertTrue(formosalink_cameras(False,params,None))
        params.put_bool('FormosaLinkEnabled',False,block=True)
        self.assertFalse(formosalink_cameras(False,params,None))
      params.put_bool('FormosaLinkEnabled',True,block=True)
      with patch('time.monotonic',return_value=116):
        self.assertFalse(formosalink_cameras(False,params,None))
      self.assertFalse(params.get_bool('IsDriverViewEnabled'))
      self.assertFalse(params.get_bool('IsLiveStreaming'))

  def test_both_native_streams_encode_fresh_padded_nv12(self):
    from openpilot.sunnypilot.formosalink.stream_encoder import StreamEncoder
    for camera,stream in (('wide-road',VisionStreamType.VISION_STREAM_WIDE_ROAD),('driver',VisionStreamType.VISION_STREAM_CABIN)):
      name='formosa-test-'+uuid.uuid4().hex
      server=VisionIpcServer(name)
      width,height,stride,offset=64,48,80,4096
      size=offset+stride*height//2
      server.create_buffers_with_sizes(stream,4,width,height,size,stride,offset)
      server.start_listener()
      source=NativeCamera(camera,name,encoder=StreamEncoder())
      deadline=time.monotonic()+2
      while not source.client.connect(False) and time.monotonic()<deadline:
        time.sleep(.01)
      self.assertTrue(source.client.is_connected())
      raw=np.zeros(size,dtype=np.uint8);raw[:stride*height]=96;raw[offset:]=128
      def send():
        for index in range(100):
          now=time.monotonic_ns()
          server.send(stream,raw,index,now,now)
          time.sleep(.01)
      worker=threading.Thread(target=send);worker.start()
      try:
        try:
          for _ in range(3):
            jpeg,sampled,_=source()
        except subprocess.CalledProcessError as exc:
          self.fail(exc.stderr.decode(errors="replace"))
      finally:
        worker.join()
        source.close()
      image=Image.open(io.BytesIO(jpeg)).convert('RGB')
      self.assertLessEqual(image.width,640);self.assertLessEqual(image.height,360)
      self.assertLess(time.time()-sampled,3)
      self.assertTrue(all(80 <= channel <= 105 for channel in image.getpixel((image.width//2,image.height//2))))

  def test_ppp_kernel_check_survives_slow_modem_poll_and_reports_real_loss(self):
    import fcntl
    def ioctl(fd, operation, request):
      if operation==0x8913:return b'\0'*16+struct.pack('H',0x41)+b'\0'*238
      return b'\0'*20+bytes((10,1,2,3))+b'\0'*232
    with patch.object(fcntl,'ioctl',side_effect=ioctl):
      self.assertTrue(sample_link()['connected'])
      self.assertEqual(sample_link()['ip_address'],'10.1.2.3')
    with patch.object(fcntl,'ioctl',side_effect=OSError(errno.ENODEV,'fixture')):
      self.assertFalse(sample_link()['connected'])
