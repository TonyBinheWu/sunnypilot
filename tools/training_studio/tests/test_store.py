import hashlib
from pathlib import Path
import tempfile
import unittest
import time

from tools.training_studio.server import initialize
from tools.training_studio.store import Store, read_json, split_for, write_json, teacher_runs
from openpilot.sunnypilot.formosalink.training_protocol import POLICY, digest_file


class StoreTest(unittest.TestCase):
  def test_partial_teacher_history_is_retained_without_claiming_training_completed(self):
    with tempfile.TemporaryDirectory() as directory:
      cycle=Path(directory)/'teacher-cycles'/'cycle-011'
      write_json(cycle/'interrupted.json',{'history':[{'epoch':8,'train_loss':1.}], 'reason':'training correction'})
      rows=teacher_runs(directory)
      self.assertEqual(len(rows),1)
      self.assertFalse(rows[0]['completed'])
      self.assertEqual(rows[0]['history'][0]['epoch'],8)
      write_json(cycle/'result.json',{'history':[{'epoch':24,'train_loss':.5}]})
      rows=teacher_runs(directory)
      self.assertEqual(len(rows),1)
      self.assertTrue(rows[0]['completed'])
      self.assertEqual(rows[0]['history'][0]['epoch'],24)

  def setUp(self):
    self.temp=tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.root=Path(self.temp.name)
    self.inbox=self.root/"inbox"
    self.inbox.mkdir()
    self.store=initialize(self.root/"studio",[str(self.inbox)])

  def add(self,split,*,route=None,segment=""):
    number=0
    while True:
      group=hashlib.sha256((split+str(number)).encode()).hexdigest()
      if split_for(group)==split:
        break
      number+=1
    group = route or group
    path=self.inbox/(split+str(number)+segment)
    path.mkdir()
    entries=[]
    for name in ("rlog.zst","fcamera.hevc","ecamera.hevc"):
      file=path/name
      file.write_bytes((name+split+segment).encode())
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

  def test_next_independent_route_fills_empty_holdout_after_upgrade(self):
    train = self.add("train")
    test = self.add("test")
    self.store.discover()
    # Reproduce a pre-upgrade store with only train and test represented.
    with self.store.db() as db:
      for path, split in ((train, "train"), (test, "test")):
        db.execute("UPDATE datasets SET split=? WHERE route_group=?",
                   (split, read_json(path/"complete.json")["route_group"]))
    self.add("train", segment="-late")
    self.store.discover()
    self.assertIsNone(self.store.enqueue())
    # Both independent arrivals hash to train under the old rule.
    groups = [hashlib.sha256(str(i).encode()).hexdigest() for i in range(20)]
    new, later = [group for group in groups if split_for(group) == "train"][:2]
    self.add("train", route=new, segment="-new")
    self.store.discover()
    self.store = Store(self.store.root)
    self.add("train", route=new, segment="-resumed")
    self.add("train", route=later, segment="-later")
    self.store.discover()
    plan = read_json(self.store.root/"runs"/self.store.enqueue()/"plan.json")
    self.assertEqual(plan["counts"], {"train":3, "validation":2, "test":1})
    self.assertEqual({row["route_group"] for row in plan["datasets"] if row["split"] == "validation"}, {new})
    self.assertEqual(self.store.discover(), 0)

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
