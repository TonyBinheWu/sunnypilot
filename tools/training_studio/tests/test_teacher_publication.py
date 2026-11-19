import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from tools.training_studio.store import write_json
from tools.training_studio.teacher_adapt import candidate_publication


@unittest.skipUnless(os.name=='posix','Studio qualification runs under Linux file locks')
class TeacherPublicationTest(unittest.TestCase):
  def test_waiting_publisher_cannot_replace_a_candidate_that_qualified_while_locked(self):
    with tempfile.TemporaryDirectory() as directory:
      store=SimpleNamespace(root=Path(directory))
      script="""from pathlib import Path
import sys
from types import SimpleNamespace
from tools.training_studio.teacher_adapt import candidate_publication
print('waiting',flush=True)
try:
 with candidate_publication(SimpleNamespace(root=Path(sys.argv[1]))):print('published',flush=True)
except InterruptedError:print('preserved',flush=True)
"""
      child=None
      try:
        with candidate_publication(store):
          child=subprocess.Popen([sys.executable,'-u','-c',script,directory],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
          self.assertEqual(child.stdout.readline().strip(),'waiting')
          with selectors.DefaultSelector() as ready:
            ready.register(child.stdout,selectors.EVENT_READ)
            self.assertFalse(ready.select(.1),'candidate changed during qualification')
          write_json(store.root/'teacher-qualification-progress.json',{'state':'passed'})
        stdout,stderr=child.communicate(timeout=10)
        self.assertEqual(child.returncode,0,stderr)
        self.assertEqual(stdout.strip(),'preserved')
      finally:
        if child and child.poll() is None:child.kill();child.communicate()

  def test_failed_candidate_releases_the_publication_slot(self):
    with tempfile.TemporaryDirectory() as directory:
      store=SimpleNamespace(root=Path(directory))
      with self.assertRaises(RuntimeError):
        with candidate_publication(store):raise RuntimeError('episode failed')
      with candidate_publication(store):pass


if __name__=='__main__':unittest.main()
