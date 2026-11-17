"""Explicit platform scope; never infer steering authority from a model name."""

PHASE1_PLATFORMS = frozenset({
  'KIA_EV6', 'KIA_EV6_PE',
  'HYUNDAI_IONIQ_5', 'HYUNDAI_IONIQ_5_PE', 'HYUNDAI_IONIQ_5_N',
  'KIA_CARNIVAL_4TH_GEN',
  'KIA_SORENTO', 'KIA_SORENTO_4TH_GEN', 'KIA_SORENTO_2024', 'KIA_SORENTO_HEV_4TH_GEN',
})


def supports_phase1(cp):
  return (cp.brand == 'hyundai' and cp.carFingerprint in PHASE1_PLATFORMS
          and not cp.dashcamOnly and not cp.notCar and cp.steerControlType in ('torque', 'angle'))


def phase1_enabled(cp, params):
  return supports_phase1(cp) and params.get_bool('HkgPhase1Assist')
