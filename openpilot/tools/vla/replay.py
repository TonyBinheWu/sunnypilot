"""Run PhysicalAI-reason-VLA on recorded forward frames and measured ego motion."""
import argparse
import base64
from contextlib import contextmanager, nullcontext
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

MODEL = 'PhysicalAI-reason-VLA.Q4_K_M.gguf'
PROJECTOR = 'PhysicalAI-reason-VLA.mmproj-Q8_0.gguf'
REVISION = '841fac174b8e3da0d5ca7ee56a2b15c879b1fb29'
ARTIFACTS = {
  MODEL: (2496755488, 'ac65d271619784787fab81d31685bc4b62e46a755c07710f9a456f7af5c73968'),
  PROJECTOR: (453974240, '2cf0f9a143c8f85851bbc768086c02ee433d41cf817a91f65d6c2dfb2d1e4edc'),
}


def verify(directory):
  for name, (size, digest) in ARTIFACTS.items():
    path = directory / name
    if path.stat().st_size != size:
      raise ValueError(f'Incorrect size for {name}')
    with path.open('rb') as f:
      if hashlib.file_digest(f, 'sha256').hexdigest() != digest:
        raise ValueError(f'Incorrect checksum for {name}')


def resize_road(rgb):
  import cv2
  height, width = rgb.shape[:2]
  scaled_height = max(32, round(320 * height / width / 32) * 32)
  if not 128 <= scaled_height <= 256:
    raise ValueError('Expected a landscape forward camera')
  return cv2.resize(rgb, (320, scaled_height), interpolation=cv2.INTER_AREA)


def samples(manifest):
  from openpilot.tools.vla.model import prompts
  import cv2
  import numpy as np
  with manifest.open(encoding='utf-8-sig') as f:
    for line in f:
      row = json.loads(line)
      timestamp = row['timestamp_us']
      if type(timestamp) is not int or timestamp < 0:
        raise ValueError('Expected recorded camera timestamp_us')
      prompts(row['egomotion'])
      path = (manifest.parent / row['image']).resolve()
      if not path.is_relative_to(manifest.parent.resolve()) or path.stat().st_size > 8 << 20:
        raise ValueError('Invalid frame path or file size')
      bgr = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
      if bgr is None or min(bgr.shape[:2]) < 32:
        raise ValueError(f'Invalid image {path.name}')
      yield row, resize_road(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def decode(words):
  if len(words) != 3:
    raise ValueError('Expected longitudinal, lateral and direction outputs')
  longitudinal, maneuver, direction = words
  speed = {'stop': 'stop', 'yield': 'yield', 'follow': 'follow', 'search': 'gap search', 'pass': 'pass',
           'adapt': 'adapt speed', 'track': 'cruise'}.get(longitudinal)
  lateral = {'keep': 'keep lane', 'merge': 'merge', 'park': 'pull over', 'abort': 'abort maneuver'}.get(maneuver)
  sided = {'turn': 'turn', 'change': 'lane change', 'out': 'nudge out', 'in': 'nudge in'}
  if maneuver in sided and direction in ('left', 'right'):
    lateral = f'{sided[maneuver]} {direction}'
  return {'longitudinal': speed, 'lateral': lateral}


@contextmanager
def reference(directory, server, gpu):
  import cv2
  from openpilot.tools.vla.model import prompts
  if not re.fullmatch(r'Vulkan\d+', gpu):
    raise ValueError('Select an explicit Vulkan device from llama-server --list-devices')
  devices = subprocess.check_output([server, '--list-devices'], stderr=subprocess.STDOUT, text=True, timeout=20)
  match = re.search(rf'^\s*{gpu}: (.+)$', devices, re.MULTILINE)
  if match is None:
    raise ValueError(f'{gpu} unavailable')
  with socket.socket() as s:
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
  key = secrets.token_hex(32)
  opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

  def request(path, body=None):
    req = urllib.request.Request(f'http://127.0.0.1:{port}/{path}', data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {key}'})
    with opener.open(req, timeout=60) as response:
      return json.load(response)

  cmd = [server, '--host', '127.0.0.1', '--port', str(port), '--api-key', key, '--offline', '-m', directory/MODEL,
         '--mmproj', directory/PROJECTOR, '--device', gpu, '--mmproj-device', gpu, '-ngl', '99', '--fit', 'off', '-np', '1',
         '--ctx-size', '2048', '--image-min-tokens', '4', '--image-max-tokens', '1024']
  with tempfile.TemporaryFile() as log:
    proc = subprocess.Popen(cmd, stdout=log, stderr=log)
    try:
      until = time.monotonic() + 90
      while proc.poll() is None:
        try:
          if request('health').get('status') == 'ok':
            break
        except (OSError, ValueError):
          pass
        if time.monotonic() >= until:
          raise TimeoutError('VLA server startup timed out')
        time.sleep(.2)
      else:
        log.seek(0)
        raise RuntimeError(log.read()[-2000:].decode(errors='replace').replace(key, '[redacted]'))
      props = request('props')
      if not props['modalities']['vision'] or not props['build_info'].startswith('b12676-'):
        raise ValueError('Expected multimodal llama.cpp build b12676')
      marker = props['media_marker']

      def predict(rgb, history):
        ok, png = cv2.imencode('.png', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        if not ok:
          raise ValueError('Could not encode frame')
        image = base64.b64encode(png).decode('ascii')
        before, tails = prompts(history)
        return [request('completion', {'prompt': {'prompt_string': before+marker+tail, 'multimodal_data': [image]},
                                       'n_predict': 1, 'temperature': 0, 'cache_prompt': False})['content'] for tail in tails]
      yield match[1].strip(), predict
    finally:
      proc.terminate()
      try:
        proc.wait(timeout=10)
      except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def load_native(directory, device, checkpoint=None):
  from tinygrad import Device
  from tinygrad.llm.cli import SimpleTokenizer
  from openpilot.tools.vla.model import Weights, classify, encode_image
  weights = Weights(directory/MODEL, device)
  vision = Weights(directory/PROJECTOR, device)
  tokenizer = SimpleTokenizer.from_gguf_kv(weights.meta)
  Device[device].synchronize()

  def predict(rgb, history):
    return classify(weights, tokenizer, rgb, encode_image(vision, rgb, checkpoint), history, checkpoint)
  return device + ' ' + str(getattr(Device[device], 'arch', '')), predict


def native(directory, backend):
  if backend == 'chestnut':
    from openpilot.selfdrive.modeld.precompiled_worker import claim_gpu_owner
    claim_gpu_owner()
  from tinygrad import Device
  device = 'AMD' if backend == 'chestnut' else 'CUDA'
  if backend == 'chestnut' and not Device[device].is_usb():
    raise RuntimeError('Expected USB AMD backend')
  return load_native(directory, device)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--weights', type=Path, required=True)
  parser.add_argument('--fetch', action='store_true', help='Download the pinned and verified GGUFs into --weights')
  inputs = parser.add_mutually_exclusive_group(required=True)
  inputs.add_argument('--segment', type=Path, help='Local segment directory containing an rlog and fcamera.hevc')
  inputs.add_argument('--manifest', type=Path, help='Local JSONL with image, timestamp_us and egomotion')
  parser.add_argument('--backend', choices=('chestnut', 'cuda', 'vulkan'), required=True)
  parser.add_argument('--server', type=Path, help='llama.cpp b12676 llama-server (Vulkan reference)')
  parser.add_argument('--device', help='Explicit Vulkan device, for example Vulkan0')
  args = parser.parse_args()
  if args.backend == 'vulkan' and not (args.server and args.device):
    parser.error('--backend vulkan requires --server and --device')
  if Path('/AGNOS').exists():
    # On a device the replay is allowed only while parked. Release even during a long native kernel or compilation.
    from openpilot.common.params import Params
    import threading
    params = Params()
    def parked():
      return params.get_bool('IsOffroad') and not params.get_bool('IsOnroad')
    if not parked() or args.backend != 'chestnut':
      raise RuntimeError('On AGNOS use the Chestnut backend on an offroad bench')
    def watch_ignition():
      while parked():
        time.sleep(.05)
      os._exit(2)
    threading.Thread(target=watch_ignition, daemon=True).start()
  if args.backend == 'chestnut':
    os.environ.update(DEV='USB+AMD:LLVM', GMMU='0')
  elif args.backend == 'cuda':
    os.environ['DEV'] = 'CUDA'
  if args.fetch:
    from openpilot.common.sunny_models import download
    base = f'https://huggingface.co/mradermacher/PhysicalAI-reason-VLA-GGUF/resolve/{REVISION}'
    for name, (size, digest) in ARTIFACTS.items():
      download(f'{base}/{name}', digest, args.weights/name, lambda: True, size)
  else:
    verify(args.weights)
  runner = (reference(args.weights, args.server, args.device) if args.backend == 'vulkan'
            else nullcontext(native(args.weights, args.backend)))
  from openpilot.tools.vla.segment import segment_samples
  from openpilot.selfdrive.modeld.vla_status import scene_assessment
  frames = segment_samples(args.segment) if args.segment else samples(args.manifest)
  count = 0
  with runner as (device, predict):
    for row, rgb in frames:
      count += 1
      start = time.perf_counter()
      words = predict(rgb, row['egomotion'])
      elapsed = (time.perf_counter()-start)*1000
      action = decode(words)
      identity = ({'frame_id': row['frame_id'], 'primary': row['primary'], 'timestamp_eof_ns': row['timestamp_eof_ns'],
                   'scene': scene_assessment(row['primary'], action)}
                  if args.segment else {'image': row['image']})
      print(json.dumps({**identity, 'timestamp_us': row['timestamp_us'], 'backend': args.backend, 'device': device,
                        'vla': 'mjf-su/PhysicalAI-reason-VLA', 'weights_revision': REVISION,
                        'action': action, 'inference_ms': round(elapsed, 2)}), flush=True)
  if not count:
    raise ValueError('No aligned and valid VLA frames in input')


if __name__ == '__main__':
  main()
