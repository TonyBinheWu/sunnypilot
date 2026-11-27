"""Select the internal model compiler backend in a disposable interpreter."""


def preferred_backend(devices):
  for name in ('CUDA', 'QCOM'):
    try:
      if devices[name].device == name:
        return name
    except Exception:
      # tinygrad raises backend-specific errors when the hardware is absent.
      continue
  return 'CPU'


if __name__ == '__main__':
  from tinygrad import Device
  print(preferred_backend(Device))
