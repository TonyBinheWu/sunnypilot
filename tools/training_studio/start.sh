#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
studio_root="${1:-build/training-studio}"
studio_port="${2:-8890}"
studio_python="${STUDIO_PYTHON:-build/official-sim/venv/bin/python}"
mkdir -p "$studio_root"
if [[ -f "$studio_root/server.json" ]]; then
  if "$studio_python" -c 'import json,os,sys; s=json.load(open(sys.argv[1])); os.kill(s["pid"],0); assert "tools.training_studio.server" in open("/proc/%d/cmdline"%s["pid"]).read()' "$studio_root/server.json" 2>/dev/null; then
    echo "Training Studio already running: http://127.0.0.1:$studio_port"
    if [[ "${STUDIO_RESTART:-0}" != "1" ]]; then exit 0; fi
    studio_old_pid="$("$studio_python" -c 'import json,sys; print(json.load(open(sys.argv[1]))["pid"])' "$studio_root/server.json")"
    kill -TERM "$studio_old_pid"
    for attempt in {1..75}; do
      if ! kill -0 "$studio_old_pid" 2>/dev/null; then break; fi
      sleep .2
    done
    if kill -0 "$studio_old_pid" 2>/dev/null; then echo 'Owned Studio server did not stop; inspect its log' >&2; exit 1; fi
  fi
fi
nohup "$studio_python" -m tools.training_studio.server --root "$studio_root" --port "$studio_port" > "$studio_root/server.log" 2>&1 < /dev/null &
studio_pid=$!
for attempt in {1..50}; do
  if ! kill -0 "$studio_pid" 2>/dev/null; then
    cat "$studio_root/server.log" >&2
    exit 1
  fi
  if curl -fsS "http://127.0.0.1:$studio_port/api/state" > /dev/null 2>&1; then
    echo "Training Studio ready: http://127.0.0.1:$studio_port"
    exit 0
  fi
  sleep .2
done
echo "Training Studio startup timed out" >&2
exit 1
