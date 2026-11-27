"""Ordinary uploads and synchronized small-result Chestnut BAR reads."""
import numpy as np
from tinygrad import Device, Tensor, dtypes


def upload(value, dtype=dtypes.bfloat16):
  source = value if isinstance(value, Tensor) else Tensor(np.asarray(value), device='CPU')
  return source.to(Device.DEFAULT).cast(dtype).contiguous().realize()


def submitted(device=None):
  """Timeline value of the newest submitted GPU work; wait_for(value) later waits for exactly that work."""
  dev = Device[device or Device.DEFAULT]
  return int(dev.timeline.host.view(fmt='Q')[1])


def wait_for(value, device=None):
  dev = Device[device or Device.DEFAULT]
  try:
    dev._wait_signal(dev.timeline.host.view(fmt='Q'), value)
  except RuntimeError:
    dev.on_device_hang()
    raise


def download(value):
  numpy_type = {dtypes.int32: np.int32, dtypes.float32: np.float32}.get(value.dtype)
  if numpy_type is None:
    raise TypeError(f'Unsupported direct readback dtype: {value.dtype}')
  dev = Device[value.device]
  if not dev.is_usb:
    raise ValueError('Direct BAR readback requires Chestnut')
  value = value.contiguous().realize()
  dev.synchronize()
  buffer = value._buffer()
  assert buffer.nbytes == value.numel()*4
  offset, remaining = buffer.offset, buffer.nbytes
  chunks = []
  for address, size in buffer.base.get_storage().meta.mapping.paddrs:
    if offset >= size:
      offset -= size
      continue
    take = min(remaining, size-offset)
    for start in range(0, take, 65536):
      count = min(take-start, 65536)
      view = dev.iface.pci_dev.map_bar(bar=dev.iface.vram_bar, off=address+offset+start, size=count)
      chunks.append(bytes(view[:]))
    remaining -= take
    offset = 0
    if not remaining:
      break
  assert remaining == 0
  return np.frombuffer(b''.join(chunks), dtype=numpy_type).reshape(value.shape)
