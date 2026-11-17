#!/usr/bin/env bash

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

# models get lower priority than ui
# - ui is ~5ms
# - modeld is 20ms
# - DM is 10ms
# in order to run ui at 60fps (16.67ms), we need to allow
# it to preempt the model workloads. we have enough
# headroom for this until ui is moved to the CPU.
export QCOM_PRIORITY=12

if [ -z "$AGNOS_VERSION" ]; then
  export AGNOS_VERSION="19.8-carrot-bt1"
fi

export STAGING_ROOT="/data/safe_staging"

# A manually selected, verified Studio release takes effect only on the next boot.
if [ -z "${CARROT_BIG_MODEL_MANIFEST:-}" ]; then
  studio_manifest="$(python3 -m openpilot.sunnypilot.formosalink.training_models manifest-url 2>/dev/null)"
  if [ -n "$studio_manifest" ]; then export CARROT_BIG_MODEL_MANIFEST="$studio_manifest"; fi
  unset studio_manifest
fi
