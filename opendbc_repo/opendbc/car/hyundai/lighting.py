"""Read-only display lamps. Switch positions are not actual lamp states."""
def classic_lighting_state(cp):
  names = ('CF_Gway_HeadLampLow', 'CF_Gway_HeadLampHigh')
  stamps = cp.ts_nanos.get('CGW1', {})
  signals = cp.vl.get('CGW1', {})
  valid = not cp.bus_timeout and len(cp.dat.get(1345, b'')) == 8
  for name in names:
    stamp = stamps.get(name, 0)
    valid = valid and stamp > 0 and 0 <= cp._last_update_nanos - stamp <= 500_000_000 and signals.get(name) in (0, 1)
  return (True, bool(signals[names[0]]), bool(signals[names[1]])) if valid else (False, False, False)
