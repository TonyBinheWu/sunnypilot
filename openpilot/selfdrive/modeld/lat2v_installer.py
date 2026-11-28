"""Resume an explicitly selected C4 lat2v installation across parking sessions."""
import time

from openpilot.common import sunny_models as sunny
from openpilot.selfdrive.alpamayo import carrot, install
from openpilot.system.hardware.usbgpu import get_usbgpu_device


def gpu_connected():
  bridge = get_usbgpu_device()
  return bridge is not None and bridge.speed_mbps >= 5000


def prepare_once(params, request):
  """Return seconds to the next check, or stop until the manager sees a new request."""
  request_id = request['id']

  def current():
    return carrot.strictly_parked(params) and sunny.lat2v_request().get('id') == request_id

  if request['state'] == 'failed' or not current():
    return None
  if request['state'] == 'waiting_egpu' and install.complete() and not gpu_connected():
    return 5
  if not sunny.update_lat2v_request(request_id, 'preparing'):
    return None

  watching_gpu = False
  gpu_lost = False

  def can_continue():
    nonlocal watching_gpu, gpu_lost
    if not current():
      return False
    if watching_gpu:
      gpu_lost = gpu_lost or not gpu_connected()
      return not gpu_lost
    # Files can be prepared without a bridge. Once present for a complete
    # package, unplugging also interrupts the supervised GPU replay.
    watching_gpu = install.complete() and gpu_connected()
    return True

  try:
    carrot.prepare_selection(can_continue)
    if not current():
      return None
    if gpu_lost or not gpu_connected():
      sunny.update_lat2v_request(request_id, 'waiting_egpu')
      return 5
    if not install.ready():
      raise ValueError('Parked GPU replay did not qualify this installation')
    sunny.update_lat2v_request(request_id, 'saved',
                               verified=lambda: carrot.strictly_parked(params) and gpu_connected() and install.ready())
    return None
  except (OSError, ValueError, RuntimeError) as exc:
    if not current():
      return None
    if not install.complete():
      sunny.update_lat2v_request(request_id, 'retry_download', str(exc))
      return 60
    if gpu_lost or not gpu_connected():
      sunny.update_lat2v_request(request_id, 'waiting_egpu')
      return 5
    sunny.update_lat2v_request(request_id, 'failed', str(exc))
    return None


def main():
  from openpilot.common.params import Params
  params = Params()
  while request := sunny.lat2v_request():
    delay = prepare_once(params, request)
    if delay is None:
      return
    time.sleep(delay)


if __name__ == '__main__':
  main()
