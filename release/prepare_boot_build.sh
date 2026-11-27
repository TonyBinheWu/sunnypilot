#!/usr/bin/env bash
# Prepare a source-preserving, offline update on a matching AGNOS release builder.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd -P)"
cd "$root"
[[ -f /AGNOS && -f /TICI ]] || { echo "An AGNOS release builder is required" >&2; exit 1; }
if [[ -e /data/params/d/IsOnroad && "$(cat /data/params/d/IsOnroad)" != 0 ]]; then
  echo "Release preparation requires an offroad builder" >&2
  exit 1
fi
export PYTHONPATH="$root/pydeps:$root${PYTHONPATH:+:$PYTHONPATH}"
export SCONS_CACHE_DIR="${SCONS_CACHE_DIR:-/data/scons_cache}"
git diff --quiet HEAD -- . ':(exclude)prebuilt_assets'
targets="$(mktemp)"
trap 'rm -f -- "$targets"' EXIT
guard="${SCONS_CACHE_DIR}.build.lock"
[[ ! -L "$guard" ]] && { [[ -e "$guard" ]] || : >> "$guard"; }
[[ -f "$guard" && ! -L "$guard" ]] || exit 1
exec 8<"$guard"
flock -w 300 8
export SCONS_CACHE_LOCK_FD=8
CARROT_BUILD_TARGETS="$targets" scons --minimal "-j${JOBS:-4}" --cache-populate
python3 openpilot/system/manager/params_check.py
python3 openpilot/system/manager/boot_prebuilt.py publish "$targets"
