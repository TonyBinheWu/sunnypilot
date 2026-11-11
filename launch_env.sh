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

if [ -z "${AGNOS_VERSION:-}" ]; then
  # Read the hardware identity before native Python dependencies are available.
  _agnos_model_path="${AGNOS_DEVICE_MODEL_PATH:-/sys/firmware/devicetree/base/model}"
  _agnos_model=""
  if [ -r "$_agnos_model_path" ]; then
    _agnos_model="$(tr -d '\0' < "$_agnos_model_path")"
  fi
  case "$_agnos_model" in
    "comma tizi"|tizi) export AGNOS_VERSION="19.9" ;;
    *) export AGNOS_VERSION="20.1" ;;
  esac
  unset _agnos_model_path _agnos_model
fi

# Always pair an explicit version override with its matching, checked-in image.
case "$AGNOS_VERSION" in
  19.9) export AGNOS_MANIFEST="openpilot/common/hardware/comma/agnos-19.9.json" ;;
  20.1) export AGNOS_MANIFEST="openpilot/common/hardware/comma/agnos.json" ;;
  *) echo "Unsupported AGNOS target: $AGNOS_VERSION" >&2; return 1 ;;
esac

export STAGING_ROOT="/data/safe_staging"
