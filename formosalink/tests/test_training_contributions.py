import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from formosalink.server.training import Contributions
from openpilot.sunnypilot.formosalink.training_protocol import NOTICE, POLICY
from openpilot.sunnypilot.formosalink.training_upload import Uploader, choose, eligible_segments, local_state
from openpilot.sunnypilot.formosalink.identity import create


class ContributionTest(unittest.TestCase):
  def setUp(self):
    self.temp=tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root=Path(self.temp.name)
    self.store=Contributions(self.root/"server")
    self.device="device-a"

  def declaration(self,raw=b"hello",filename="rlog.zst",revision=1):
    return {"segment":"a"*64,"filename":filename,"sha256":hashlib.sha256(raw).hexdigest(),"size":len(raw),"consent_revision":revision}

  def chunk(self,upload_id,offset,raw,revision=1):
    return {"upload_id":upload_id,"offset":offset,"data":base64.b64encode(raw).decode(),"sha256":hashlib.sha256(raw).hexdigest(),"consent_revision":revision}

  def test_upload_requires_explicit_current_consent(self):
    with self.assertRaises(ValueError):
      self.store.begin(self.device,self.declaration())
    self.store.set_consent(self.device,True,0,"owner-web")
    result=self.store.begin(self.device,self.declaration())
    self.store.set_consent(self.device,False,1,"owner-web")
    with self.assertRaises(ValueError):
      self.store.chunk(self.device,self.chunk(result["upload_id"],0,b"hello"))

  def test_resume_dedup_and_whole_file_hash(self):
    self.store.set_consent(self.device,True,0,"owner-web")
    result=self.store.begin(self.device,self.declaration())
    first=self.store.chunk(self.device,self.chunk(result["upload_id"],0,b"he"))
    self.assertEqual(first["offset"],2)
    self.assertEqual(self.store.begin(self.device,self.declaration())["offset"],2)
    self.assertEqual(self.store.chunk(self.device,self.chunk(result["upload_id"],0,b"he"))["offset"],2)
    final=self.store.chunk(self.device,self.chunk(result["upload_id"],2,b"llo"))
    self.assertTrue(final["complete"])
    self.assertTrue(self.store.begin(self.device,self.declaration())["complete"])

  def test_wrong_owner_and_cabin_and_traversal_rejected(self):
    self.store.set_consent(self.device,True,0,"owner-web")
    result=self.store.begin(self.device,self.declaration())
    self.store.set_consent("device-b",True,0,"owner-web")
    with self.assertRaises(ValueError):
      self.store.chunk("device-b",self.chunk(result["upload_id"],0,b"hello"))
    for name in ("dcamera.hevc","../fcamera.hevc","audio.wav"):
      with self.assertRaises(ValueError):
        self.store.begin(self.device,self.declaration(filename=name))

  def test_web_revoke_wins_over_stale_local_enable(self):
    self.store.set_consent(self.device,True,0,"device","c"*64)
    self.store.set_consent(self.device,False,1,"owner-web")
    with self.assertRaises(ValueError):
      self.store.set_consent(self.device,True,1,"device","d"*64)
    # Lost acknowledgements must not reapply a previously consumed local event.
    result=self.store.set_consent(self.device,True,0,"device","c"*64)
    self.assertFalse(result["enabled"])
    self.assertEqual(result["revision"],2)

  def test_finalize_only_complete_dual_camera_segment(self):
    self.store.set_consent(self.device,True,0,"owner-web")
    payload={"segment":"a"*64,"route_group":"b"*64,"consent_revision":1}
    for filename in ("rlog.zst","fcamera.hevc","ecamera.hevc"):
      if filename=="ecamera.hevc":
        with self.assertRaises(ValueError):
          self.store.finalize(self.device,payload)
      result=self.store.begin(self.device,self.declaration(filename=filename))
      self.store.chunk(self.device,self.chunk(result["upload_id"],0,b"hello"))
    self.assertTrue(self.store.finalize(self.device,payload)["complete"])
    manifests=list((self.root/"server").rglob("complete.json"))
    self.assertEqual(len(manifests),1)
    self.assertEqual(json.loads(manifests[0].read_text())["route_group"],"b"*64)

  def test_local_revoke_immediate_and_closed_segments_only(self):
    directory=self.root/"identity"
    directory.mkdir()
    choose(True,directory)
    self.assertFalse(local_state(directory)["enabled"])
    self.assertTrue(local_state(directory)["pending"]["enabled"])
    choose(False,directory)
    self.assertFalse(local_state(directory)["enabled"])
    logs=self.root/"logs"
    segment=logs/"route--0"
    segment.mkdir(parents=True)
    now=time.time()
    for name in ("rlog.zst","fcamera.hevc","ecamera.hevc"):
      (segment/name).write_bytes(b"hello")
      os.utime(segment/name,(now-300,now-300))
    self.assertEqual(len(list(eligible_segments(logs,now-600,now))),1)
    (segment/"rlog.zst.lock").touch()
    self.assertEqual(list(eligible_segments(logs,now-600,now)),[])

  def test_client_resumes_after_lost_chunk_ack_without_duplicate_segment(self):
    directory=self.root/'client'
    identity,_,_=create(directory,'https://formosapilot.dinglu-t.com')
    device=identity['device_id']
    now=time.time()
    self.store.set_consent(device,True,0,'owner-web',granted_at=now-600)
    logs=self.root/'client-logs'
    segment=logs/'route--0'
    segment.mkdir(parents=True)
    for name in ('rlog.zst','fcamera.hevc','ecamera.hevc'):
      (segment/name).write_bytes(b'fixture-'+name.encode())
      os.utime(segment/name,(now-300,now-300))
    lost=[True]
    store=self.store
    class Client(Uploader):
      def call(self,operation,**fields):
        if operation=='sync':
          return {'policy':POLICY,'consent':store.consent(device),'choice_conflict':False}
        if operation=='begin':
          return store.begin(device,fields['file'])
        if operation=='chunk':
          result=store.chunk(device,fields['chunk'])
          if lost[0]:
            lost[0]=False
            raise ConnectionError('acknowledgement lost after server commit')
          return result
        return store.finalize(device,fields['segment'])
    stop=threading.Event()
    with patch('openpilot.sunnypilot.formosalink.training_upload.segment_started_at',return_value=now-300):
      first=Client(directory,logs,lambda:True,stop,None)
      with self.assertRaises(ConnectionError):
        first.once()
      second=Client(directory,logs,lambda:True,stop,None)
      second.once()
      second.once()
    with store.db() as db:
      self.assertEqual(db.execute('SELECT COUNT(*) FROM uploads').fetchone()[0],3)
      self.assertEqual(db.execute('SELECT COUNT(*) FROM datasets').fetchone()[0],1)


if __name__=="__main__":
  unittest.main()
