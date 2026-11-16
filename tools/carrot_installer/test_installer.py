import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[2]
ORIGIN='https://github.com/TonyBinheWu/sunnypilot.git'


def git(path,*args,check=True):
  return subprocess.run(['git','-C',str(path),*args],check=check,text=True,capture_output=True)


@pytest.fixture
def entry(tmp_path):
  if sys.platform!='linux' or not shutil.which('gcc'):pytest.skip('Native POSIX compiler required')
  data=tmp_path/'data';data.mkdir();checkout=data/'openpilot';checkout.mkdir()
  git(checkout,'init');git(checkout,'remote','add','origin','https://github.com/commaai/openpilot.git')
  model=tmp_path/'model';model.write_text('comma c4\0')
  def build(script):
    payload=tmp_path/'payload.c';blob=script.encode()
    payload.write_text('#include <stddef.h>\nconst unsigned char installer_payload[]={'+','.join(map(str,blob))+'};\nconst size_t installer_size=sizeof(installer_payload);\n')
    binary=tmp_path/'entry'
    subprocess.run(['gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-static',f'-DDATA_ROOT="{data}"',f'-DMODEL_PATH="{model}"',str(ROOT/'tools/carrot_installer/bootstrap.c'),str(payload),'-o',str(binary)],check=True)
    return subprocess.run([str(binary)],env={**os.environ,'TEST_DATA_ROOT':str(data)},text=True,capture_output=True)
  return data,checkout,model,build


SUCCESS='#!/bin/sh\nprintf "#!/bin/sh\\nexit 0\\n" > "$TEST_DATA_ROOT/continue.sh"\nchmod 755 "$TEST_DATA_ROOT/continue.sh"\n'


def test_c4_marked_factory_cache_origin_is_corrected_before_child(entry):
  data,checkout,_,build=entry;(data/'.openpilot_cache').touch()
  result=build(SUCCESS)
  assert result.returncode==0
  assert git(checkout,'remote','get-url','origin').stdout.strip()==ORIGIN
  assert 'handoff verified' in (data/'carrot-installer.log').read_text()
  assert (data/'.openpilot_cache').exists()


@pytest.mark.parametrize('installed',[False,True])
def test_unmarked_or_installed_checkout_is_not_retargeted(entry,installed):
  data,checkout,_,build=entry
  if installed:
    (data/'.openpilot_cache').touch();(data/'continue.sh').write_text('existing')
  assert build(SUCCESS).returncode==0
  assert git(checkout,'remote','get-url','origin').stdout.strip()=='https://github.com/commaai/openpilot.git'


@pytest.mark.parametrize('script,reason',[
  ('#!/bin/sh\nexit 17\n','installer_process_failed'),
  ('#!/bin/sh\nexit 0\n','handoff_missing'),
  ('#!/bin/sh\ntouch "$TEST_DATA_ROOT/continue.sh"\n','handoff_invalid_or_not_durable'),
])
def test_failure_is_logged_and_child_is_not_retried(entry,script,reason):
  data,_,_,build=entry
  result=build(script)
  assert result.returncode==1
  assert (data/'carrot-installer-error.txt').read_text().strip()==reason


def test_c3_cannot_launch_wayland_c4_payload(entry):
  data,_,model,build=entry;model.write_text('comma c3')
  assert build(SUCCESS).returncode==1
  assert not (data/'continue.sh').exists()


def test_actual_cached_fetch_command_fails_with_factory_origin_then_works_with_fork(tmp_path):
  stock=tmp_path/'stock';fork=tmp_path/'fork';cache=tmp_path/'cache'
  for directory,branch in ((stock,'master'),(fork,'carrot-wip')):
    directory.mkdir();git(directory,'init','-b',branch)
    git(directory,'-c','user.email=test@example.invalid','-c','user.name=InstallerTest','commit','--allow-empty','-m','fixture')
  subprocess.run(['git','clone',str(stock),str(cache)],check=True,capture_output=True)
  git(cache,'remote','set-branches','--add','origin','carrot-wip')
  assert git(cache,'fetch','origin','carrot-wip',check=False).returncode!=0
  git(cache,'remote','set-url','origin',str(fork))
  assert git(cache,'fetch','origin','carrot-wip',check=False).returncode==0
  source=(ROOT/'openpilot/selfdrive/ui/installer/installer.cc').read_text()
  body=source[source.index('int cachedFetch(const std::string &cache) {'):source.index('int executeGitCommand(const std::string &cmd) {')]
  assert body.index('remote set-url origin')<body.index('git fetch --progress origin')


def test_payload_pin_rejects_unknown_or_wrong_architecture():
  import importlib.util
  spec=importlib.util.spec_from_file_location('carrot_installer_build',Path(__file__).with_name('build.py'))
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with pytest.raises(ValueError,match='changed'):module.validate(b'not an installer')
