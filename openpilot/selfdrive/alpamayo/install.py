#!/usr/bin/env python3
"""Install the pinned lat2v runtime, weights and GPU graphs during parked selection."""
import functools
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time
import tomllib
import urllib.request

from openpilot.common.big_model_catalog import storage
from openpilot.selfdrive.alpamayo.inference import NVIDIA_REVISION, TINYGRAD_REVISION

HERE = Path(__file__).resolve().parent

ROOT = storage()/'lat2v'
CONFIG = ROOT/'config.json'
STATUS = ROOT/'status.json'
RELEASE = HERE/'release.json'
SOURCES = (('nvidia', 'https://github.com/NVlabs/alpamayo2-edge.git', NVIDIA_REVISION),
           ('tinygrad', 'https://github.com/commaai/tinygrad.git', TINYGRAD_REVISION))


@functools.lru_cache(maxsize=1)
def identity():
  """Invalidate previously accepted packages when the Carrot adapter or pinned release changes."""
  digest = hashlib.sha256()
  repo = HERE.parents[2]
  files = [RELEASE, HERE/'extras.txt', HERE/'subtitle-wheels.txt', HERE/'selected/assets/manifest.json',
           repo/'openpilot/selfdrive/modeld/modeld.py', repo/'openpilot/cereal/log.capnp',
           repo/'openpilot/cereal/custom.capnp', repo/'opendbc_repo/opendbc/car/vehicle_model.py']
  for path in sorted(files + list(HERE.glob('*.py')) + list((HERE/'selected').rglob('*.py'))):
    digest.update(hashlib.sha256(path.read_bytes()).digest())
  return digest.hexdigest()


def config_path():
  return CONFIG


def complete():
  try:
    return (ROOT/'installed').read_text().strip() == hashlib.sha256(CONFIG.read_bytes() + identity().encode()).hexdigest()
  except OSError:
    return False


def ready():
  try:
    return complete() and (ROOT/'qualified').read_text().strip() == qualification_id()
  except (OSError, ValueError):
    return False


def qualification_id():
  # A copied install on another C4 must pass its own GPU replay.
  machine = Path('/etc/machine-id').read_bytes().strip()
  if not machine:
    raise ValueError('Missing machine identity')
  return hashlib.sha256(machine + CONFIG.read_bytes() + identity().encode()).hexdigest()


def write(path, text):
  temporary = path.with_name(path.name+'.tmp')
  temporary.write_text(text)
  os.replace(temporary, path)


def status(step, text, **progress):
  """Progress for the log and for the app."""
  print(f'alpamayo install: {step}: {text}', flush=True)
  write(STATUS, json.dumps({'step': step, 'text': text, 'time': time.time(), **progress})+'\n')


def file_sha256(path):
  with path.open('rb') as stream:
    return hashlib.file_digest(stream, 'sha256').hexdigest()


def verified(path, sha256, size):
  """Hash a file once; later checks compare its size and modification time with the record."""
  if not path.is_file() or path.stat().st_size != size:
    return False
  records_path = ROOT/'verified.json'
  try:
    records = json.loads(records_path.read_text())
  except (OSError, ValueError):
    records = {}
  if not isinstance(records, dict):
    records = {}
  stat = path.stat()
  record = [sha256, stat.st_size, stat.st_mtime_ns]
  if records.get(str(path)) == record:
    return True
  if file_sha256(path) != sha256:
    return False
  records[str(path)] = record
  write(records_path, json.dumps(records, indent=1)+'\n')
  return True


def download(url, path, sha256, size, label):
  """Download with resume into `path`. The file appears only after its SHA-256 matches."""
  if verified(path, sha256, size):
    return
  path.parent.mkdir(parents=True, exist_ok=True)
  part = path.with_name(path.name+'.part')
  if part.is_file() and part.stat().st_size > size:
    part.unlink()
  digest, done = hashlib.sha256(), 0
  if part.is_file():
    with part.open('rb') as stream:
      while chunk := stream.read(1 << 20):
        digest.update(chunk)
        done += len(chunk)
  if done < size:
    request = urllib.request.Request(url, headers={'Range': f'bytes={done}-', 'User-Agent': 'openpilot-alpamayo-install'})
    with urllib.request.urlopen(request, timeout=60) as response:
      if done and response.status != 206:  # the server ignored the range: start again
        digest, done = hashlib.sha256(), 0
      shown = time.monotonic()
      with part.open('ab' if done else 'wb') as out:
        while chunk := response.read(1 << 20):
          if done + len(chunk) > size:
            raise ValueError(f'{label} exceeds its pinned size')
          out.write(chunk)
          digest.update(chunk)
          done += len(chunk)
          if time.monotonic()-shown > 5:
            shown = time.monotonic()
            status('download', label, phase='downloading', received=done, total=size)
  if done < size:
    raise OSError(f'{label} transfer interrupted at {done} of {size} bytes; partial download retained')
  if done != size or digest.hexdigest() != sha256:
    part.unlink(missing_ok=True)
    raise RuntimeError(f'{label} differs from its pinned SHA-256')
  os.replace(part, path)
  verified(path, sha256, size)


def install_dependencies(project, environment):
  packages = {package['name']: package for package in tomllib.loads((project/'uv.lock').read_text())['package']}
  antlr = packages['antlr4-python3-runtime']
  # This reviewed source distribution uses ordinary setuptools without custom build hooks.
  if antlr['version'] != '4.9.3' or antlr['sdist']['hash'] != 'sha256:f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b':
    raise RuntimeError('Review the changed ANTLR build before installation')
  environment = dict(environment, UV_PROJECT_ENVIRONMENT=str(project/'.venv'), UV_PYTHON_DOWNLOADS='never')
  uv = shutil.which('uv', path=environment['PATH'])
  # The environment uses openpilot's own interpreter version, not another Python 3.12 that uv finds first.
  if sys.version_info[:2] != (3, 12):
    raise RuntimeError('The Alpamayo runtime requires Python 3.12')
  subprocess.run([uv, 'venv', '--python', sys.executable, str(project/'.venv')], env=environment, check=True)
  python = project/'.venv/bin/python'
  setuptools = packages['setuptools']
  requirement = f'setuptools=={setuptools["version"]} '+' '.join(f'--hash={wheel["hash"]}' for wheel in setuptools['wheels'])+'\n'
  subprocess.run([uv, 'pip', 'install', '--python', str(python), '--no-deps', '--only-binary=:all:', '--require-hashes', '-r', '-'],
                 input=requirement, text=True, env=environment, check=True)
  command = [uv, 'sync', '--frozen', '--no-dev', '--no-install-project', '--no-build-isolation-package', antlr['name'],
             '--project', str(project)]
  for name in sorted(packages.keys()-{antlr['name']}):
    command.extend(['--no-build-package', name])
  subprocess.run(command, env=environment, check=True)
  subprocess.run([uv, 'pip', 'install', '--python', str(python), '--no-deps', '--only-binary=:all:', '--require-hashes',
                  '-r', str(HERE/'extras.txt')], env=environment, check=True)
  site = Path(subprocess.check_output([str(python), '-c', 'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip())
  # Import the pinned checkout directly, without invoking its unpinned hatchling build environment.
  (site/'alpamayo-source.pth').write_text(str(project/'src')+'\n')


def install_runtime(root):
  """Pinned sources and a frozen, hash-checked Python environment. Existing Python 3.12 only; nothing is built except ANTLR."""
  marker = root/'installed'
  wanted = f'{NVIDIA_REVISION} {TINYGRAD_REVISION} {hashlib.sha256((HERE/"extras.txt").read_bytes()).hexdigest()}'
  if marker.is_file() and marker.read_text().strip() == wanted:
    return
  status('runtime', 'fetching the pinned tinygrad and NVIDIA sources')
  shutil.rmtree(root, ignore_errors=True)
  root.mkdir(parents=True)
  for name, url, revision in SOURCES:
    path = root/name
    subprocess.run(['git', 'init', '-q', str(path)], check=True)
    subprocess.run(['git', '-C', str(path), 'remote', 'add', 'origin', url], check=True)
    subprocess.run(['git', '-C', str(path), 'fetch', '-q', '--depth=1', 'origin', revision], check=True)
    subprocess.run(['git', '-C', str(path), 'checkout', '-q', '--detach', revision], check=True)
  status('runtime', 'installing the locked Python packages (about 1 GB)')
  uv_cache = root/'uv-cache'
  # The device puts wrapper scripts for system-wide installs before the real tools: /usr/comma/shims/uv remounts the root
  # filesystem and runs a system uv. Use the real uv, and keep openpilot's own environment settings away from it.
  install_dependencies(root/'nvidia', dict(uv_environment(), UV_CACHE_DIR=str(uv_cache), UV_LINK_MODE='copy'))
  shutil.rmtree(uv_cache, ignore_errors=True)
  write(marker, wanted+'\n')


def uv_environment():
  environment = {k: v for k, v in os.environ.items() if k not in ('VIRTUAL_ENV', 'PYTHONPATH') and not k.startswith('UV_')}
  environment['PATH'] = os.pathsep.join(d for d in os.environ.get('PATH', os.defpath).split(os.pathsep) if not d.endswith('/shims'))
  if shutil.which('uv', path=environment['PATH']) is None:
    raise RuntimeError('uv is not installed')
  return environment


@functools.lru_cache(maxsize=1)
def subtitle_version():
  pin = json.loads(RELEASE.read_bytes())['subtitles']
  return hashlib.sha256(json.dumps(pin, sort_keys=True).encode() + (HERE/'subtitle-wheels.txt').read_bytes()).hexdigest()


def subtitles_ready():
  try:
    return (ROOT/'subtitles/installed').read_text().strip() == subtitle_version()
  except OSError:
    return False


def install_subtitles(pin):
  root = ROOT/'subtitles'
  for name, artifact in pin['files'].items():
    url = f'https://huggingface.co/{pin["repository"]}/resolve/{pin["revision"]}/{name}'
    download(url, root/name, artifact['sha256'], artifact['bytes'], 'Chinese subtitles: '+name)
  packages = HERE/'subtitle-wheels.txt'
  subprocess.run(['uv', 'pip', 'install', '--python', sys.executable, '--target', str(root/'packages'), '--no-deps',
                  '--only-binary=:all:', '--require-hashes', '-r', str(packages)], env=uv_environment(), check=True)
  write(root/'installed', subtitle_version()+'\n')


def install_model(release, model):
  base = f'https://huggingface.co/{release["repository"]}/resolve/{release["revision"]}/{release["prefix"]}'
  for name, pin in release['files'].items():
    download(base+name, model/name, pin['sha256'], pin['bytes'], name)
  noise = model/'initial_noise-zero.npy'  # the model is trained and validated with zero initial diffusion noise
  import numpy as np
  with noise.with_suffix('.tmp').open('wb') as stream:
    np.save(stream, np.zeros((1, 64, 2), np.float32))
  os.replace(noise.with_suffix('.tmp'), noise)


def install_firmware(release, cache):
  firmware = release['firmware']
  for name, sha256 in firmware['files'].items():
    url = firmware['url']+name
    path = cache/'tinygrad/downloads/fw'/hashlib.md5(url.encode()).hexdigest()  # tinygrad's download cache name
    if not path.is_file() or file_sha256(path) != sha256:
      path.parent.mkdir(parents=True, exist_ok=True)
      status('firmware', name)
      with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'openpilot-alpamayo-install'}), timeout=60) as response:
        raw = response.read()
      if hashlib.sha256(raw).hexdigest() != sha256:
        raise RuntimeError(f'GPU firmware {name} differs from its pinned SHA-256')
      temporary = path.with_name(path.name+'.tmp')
      temporary.write_bytes(raw)
      os.replace(temporary, path)


def install_graphs(release, cache, target='gfx1200'):
  """Compiled GPU graphs and kernels for this code, model and GPU type. Without them the first start compiles for 10-20 min."""
  pin = release['graph_cache'].get(target)
  marker = cache/'graph-cache.installed'
  if pin is None or (marker.is_file() and marker.read_text().strip() == pin['sha256']):
    return
  archive = ROOT/'downloads'/Path(pin['path']).name
  base = f'https://huggingface.co/{release["repository"]}/resolve/{release["revision"]}/{release["prefix"]}'
  download(base+pin['path'], archive, pin['sha256'], pin['bytes'], 'compiled GPU graphs')
  status('graphs', 'unpacking the compiled GPU graphs')
  staging = cache/'graph-cache.tmp'
  shutil.rmtree(staging, ignore_errors=True)
  with tarfile.open(archive) as tar:
    tar.extractall(staging, filter='data')
  shutil.rmtree(cache/'graphs', ignore_errors=True)
  for stale in cache.glob('tinygrad.db*'):
    stale.unlink()
  for item in staging.iterdir():
    os.replace(item, cache/item.name)
  staging.rmdir()
  write(marker, pin['sha256']+'\n')
  archive.unlink()


LLVM_FILE = 'libLLVM.so.22.1'
LLVM_HASH = '901f390e839b2168fa97c1b30af3a9c97e187a3af35bc1cafd1f4bd188dd9e0b'


def install_compiler():
  target = ROOT/'runtime'/LLVM_FILE
  if verified(target, LLVM_HASH, 144692360):
    return
  # Ubuntu Noble arm64, the same userspace ABI as C4 AGNOS. Extract locally;
  # dpkg-deb --extract does not install a system package or run maintainer scripts.
  import tempfile
  package = 'libllvm22_22.1.8~++20260714014902+ca7933e47d3a-1~exp1~20260714135019.80_arm64.deb'
  archive = ROOT/'downloads'/package
  download('https://apt.llvm.org/noble/pool/main/l/llvm-toolchain-22/'+package, archive,
           '73dd23fb06588c63b3e6ddb9f35c464e874e0967a88b706c97eb64ddb8580970', 30997114, 'LLVM 22')
  with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
    subprocess.run(['dpkg-deb', '--extract', str(archive), tmp], check=True)
    source = Path(tmp)/'usr/lib/aarch64-linux-gnu'/LLVM_FILE
    if file_sha256(source) != LLVM_HASH:
      raise ValueError('LLVM 22 library digest mismatch')
    os.replace(source, target)


def configuration(release):
  """The pinned defaults with this device's paths. `overrides.json` changes single settings."""
  model = ROOT/'models'/release['model']
  config = json.loads(json.dumps(release['config']))
  from openpilot.common.transformations.camera import DEVICE_CAMERAS
  cameras = DEVICE_CAMERAS[('mici', 'os04c10')]
  for key, source in (('1', cameras.ecam), ('6', cameras.fcam)):
    lens = config['geometry']['cameras'][key]
    left, top, right, bottom = lens['content_box']
    lens['focal_pixels'] = [source.focal_length * (right-left) / source.width,
                            source.focal_length * (bottom-top) / source.height]
  config['geometry']['method'] = 'C4 OS04C10 intrinsics, equidistant wide and pinhole road, live extrinsic calibration'
  config.update(python=str(ROOT/'runtime/nvidia/.venv/bin/python'), tinygrad=str(ROOT/'runtime/tinygrad'),
                cache=str(ROOT/'cache'), output=str(ROOT/'output'))
  config['inference'].update(variant='selected', checkpoint=str(model/'checkpoint'), fp8_cache=str(model/'fp8-cache'),
                             prefill_calibration=str(model/'prefill-scales.json'), initial_noise=str(model/'initial_noise-zero.npy'))
  return config


def install():
  release = json.loads(RELEASE.read_text())
  for name in ('cache', 'output', 'downloads', 'models'):
    (ROOT/name).mkdir(parents=True, exist_ok=True)
  install_runtime(ROOT/'runtime')
  install_compiler()
  status('download', 'model files')
  install_model(release, ROOT/'models'/release['model'])
  install_firmware(release, ROOT/'cache')
  install_graphs(release, ROOT/'cache')
  write(CONFIG, json.dumps(configuration(release), indent=1)+'\n')
  write(ROOT/'installed', hashlib.sha256(CONFIG.read_bytes() + identity().encode()).hexdigest()+'\n')
  status('done', f'{release["model"]} installed')


if __name__ == '__main__':
  if sys.argv[1:] == ['--subtitles']:
    status('subtitles', 'Preparing offline Chinese subtitles')
    install_subtitles(json.loads(RELEASE.read_bytes())['subtitles'])
  else:
    install()
