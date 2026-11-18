import hashlib
from pathlib import Path
import tempfile
import unittest
import time

from tools.training_studio.server import initialize
from tools.training_studio.store import Store, read_json, split_for, write_json
from openpilot.sunnypilot.formosalink.training_protocol import POLICY, digest_file


class StoreTest(unittest.TestCase):
  def setUp(self):
    self.temp=tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root=Path(self.temp.name)
    self.inbox=self.root/"inbox"
    self.inbox.mkdir()
    self.store=initialize(self.root/"studio",[str(self.inbox)])

  def add(self,split):
    number=0
    while True:
      group=hashlib.sha256((split+str(number)).encode()).hexdigest()
      if split_for(group)==split:
        break
      number+=1
    path=self.inbox/(split+str(number))
    path.mkdir()
    entries=[]
    for name in ("rlog.zst","fcamera.hevc","ecamera.hevc"):
      file=path/name
      file.write_bytes((name+split).encode())
      entries.append({"filename":name,"size":file.stat().st_size,"sha256":digest_file(file)})
    write_json(path/"complete.json",{"policy":POLICY,"route_group":group,"files":entries})
    return path

  def test_no_job_until_all_route_splits_exist_and_no_duplicate_optimizer(self):
    self.add("train")
    self.assertEqual(self.store.discover(),1)
    self.assertIsNone(self.store.enqueue())
    self.add("validation")
    self.add("test")
    self.assertEqual(self.store.discover(),2)
    job=self.store.enqueue()
    self.assertIsNotNone(job)
    self.assertIsNone(self.store.enqueue(force=True))
    self.store.update(job,"completed","awaiting_device_acceptance")
    self.assertIsNone(self.store.enqueue())
    self.assertEqual(self.store.discover(),0)
    next_job=self.store.enqueue(force=True)
    self.assertNotEqual(job,next_job)
    self.assertEqual(read_json(self.store.root/"runs"/next_job/"plan.json")["parent"],job)

  def test_mutation_after_import_does_not_change_snapshot(self):
    source=self.add("train")
    self.store.discover()
    with self.store.db() as db:
      row=db.execute("SELECT * FROM datasets").fetchone()
    original=(Path(row["path"])/"fcamera.hevc").read_bytes()
    (source/"fcamera.hevc").write_bytes(b"changed")
    self.assertEqual((Path(row["path"])/"fcamera.hevc").read_bytes(),original)

  def test_tampered_or_cabin_data_rejected(self):
    source=self.add("train")
    (source/"fcamera.hevc").write_bytes(b"tamper")
    self.assertEqual(self.store.discover(),0)
    self.assertEqual(self.store.state()["datasets"],[])

  def test_group_assignment_stable(self):
    group="a"*64
    self.assertEqual(split_for(group),split_for(group))
    self.assertIn(split_for(group),("train","validation","test"))

  def test_waiting_reason_preserves_whole_route_holdouts(self):
    self.add('train')
    self.store.discover()
    state=self.store.state()
    self.assertEqual(state['pipeline']['missing_splits'],['validation','test'])
    self.assertEqual(state['pipeline']['route_counts'],{'train':1})
    self.assertTrue(any('教師' in text for text in state['pipeline']['blockers']))
    self.assertEqual(state['jobs'],[])

  def test_heartbeat_advances_during_a_blocked_collector_and_stops_cleanly(self):
    from tools.training_studio.engine import worker_heartbeat
    with worker_heartbeat(self.store,interval=.01) as heartbeat:
      heartbeat(state='collecting')
      initial=read_json(self.store.root/'worker.json')['updated']
      deadline=time.monotonic()+1
      while read_json(self.store.root/'worker.json')['updated']<=initial and time.monotonic()<deadline:
        time.sleep(.01)
      value=read_json(self.store.root/'worker.json')
      self.assertGreater(value['updated'],initial)
      self.assertEqual(value['state'],'collecting')
    self.assertEqual(read_json(self.store.root/'worker.json')['state'],'stopped')

  def test_completed_teacher_losses_remain_available_while_next_round_generates_data(self):
    for cycle in (2,3):
      write_json(self.store.root/'teacher-cycles'/f'cycle-{cycle:03d}'/'result.json',
        {'history':[{'epoch':1,'train_loss':10-cycle,'validation_loss':11-cycle}],'adapter_saved':cycle==2})
    (self.store.root/'teacher-cycles'/'cycle-004'/'data').mkdir(parents=True)
    rows=self.store.state()['teacher_runs']
    self.assertEqual([row['cycle'] for row in rows],[3,2])
    self.assertEqual(rows[0]['history'][0]['train_loss'],7)


if __name__=="__main__":
  unittest.main()
