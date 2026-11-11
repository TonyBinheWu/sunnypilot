"""Explicitly launched preview publisher; not added to native driving processes."""
import argparse
import os
import base64
import threading
import time
import uuid
from pathlib import Path

from openpilot.sunnypilot.formosalink.media_protocol import MAX_JPEG_BYTES, jpeg_size, validate_frame
from openpilot.sunnypilot.formosalink.protocol import sign


class PreviewPublisher:
  def __init__(self, identity, private, source, demo=False):
    self.identity, self.private, self.source = identity, private, source
    self.stream, self.sequence = str(uuid.uuid4()), 0
    self.demo = demo

  def once(self, session):
    # The injected source owns consent, freshness and any future camera adapter.
    data, sampled_at, hud = self.source()
    width,height = jpeg_size(data)
    frame = validate_frame({'version':1,'stream':self.stream,'sequence':self.sequence,
      'sampled_at':sampled_at,'source':'demo' if self.demo else 'road-preview',
      'width':width,'height':height,'jpeg':base64.b64encode(data).decode('ascii'),'hud':hud})
    self.sequence += 1
    response = session.post(self.identity['origin']+'/api/v1/agent/media',
      json=sign(self.private,self.identity['device_id'],'media',frame),timeout=5)
    response.raise_for_status()
    if len(response.content)>2048 or response.json()!={'accepted':True,'sequence':frame['sequence']}:
      raise ValueError('invalid media acknowledgement')


def main():
  from openpilot.sunnypilot.formosalink.identity import read
  import requests
  parser=argparse.ArgumentParser(description='FormosaLink preview publisher / 影像預覽發送 / プレビュー送信')
  parser.add_argument('--state-dir',required=True)
  parser.add_argument('--jpeg-file',required=True)
  parser.add_argument('--allow-upload',action='store_true',help='明確允許傳送至已配對伺服器 / Explicit upload consent / 送信を許可')
  parser.add_argument('--demo',action='store_true',help='測試圖片，不是實車 / Test image, not a vehicle / テスト画像')
  parser.add_argument('--seconds',type=int,default=60)
  args=parser.parse_args()
  if not args.allow_upload or not 1<=args.seconds<=3600:
    parser.error('--allow-upload and --seconds 1..3600 required')
  path=Path(args.jpeg_file)
  def source():
    if path.stat().st_size>MAX_JPEG_BYTES:
      raise ValueError('oversized JPEG')
    with path.open('rb') as handle:
      data=handle.read(MAX_JPEG_BYTES+1)
      modified=os.fstat(handle.fileno()).st_mtime
    # Production file adapters must replace the file on every new capture.
    sampled=time.time() if args.demo else modified
    return data,sampled,{'speed_kph':None,'engaged':None}
  identity,private,_=read(args.state_dir)
  publisher=PreviewPublisher(identity,private,source,args.demo)
  deadline=time.monotonic()+args.seconds
  stop=threading.Event()
  with requests.Session() as session:
    while time.monotonic()<deadline:
      try:
        publisher.once(session)
      except (OSError,ValueError,requests.RequestException) as exc:
        print('FormosaLink media: '+type(exc).__name__,flush=True)
        stop.wait(2)
      stop.wait(.5)


if __name__=='__main__':
  main()
