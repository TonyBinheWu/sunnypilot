import os
import shutil
import subprocess
from pathlib import Path

import pytest

from openpilot.common.basedir import BASEDIR


def _bash() -> str:
  # Windows' bash.exe alias may launch WSL instead of a usable local shell.
  git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
  executable = str(git_bash) if os.name == "nt" and git_bash.is_file() else shutil.which("bash")
  if executable is None:
    pytest.skip("bash is required for launcher integration tests")
  return executable


def _install(tmp_path: Path, *, installer="pip", offline_fail=False, online_fail=False,
             installed=False, broken_import=False, required=True, device=False, dependencies=False):
  source = (Path(BASEDIR) / "launch_chffrplus.sh").read_text(encoding="utf-8")
  functions = source[source.index("function install_runtime_python_package {"):source.index("function bootstrap_runtime_dependencies {")]
  # Simulate device markers without touching the host filesystem.
  functions = functions.replace("/TICI", "./mock_tici").replace("/AGNOS", "./mock_agnos")
  if device:
    (tmp_path / "mock_agnos").touch()
  mocks = r'''
DIR="$PWD/project with spaces"
PYDEPS="$DIR/pydeps"
installed="$MOCK_INSTALLED"
pip_ready=0
function command {
  if [[ "$*" == "-v uv" && "$MOCK_INSTALLER" != uv ]]; then return 1; fi
  builtin command "$@"
}
function fake_install {
  printf 'INSTALL:'
  printf ' <%s>' "$@"
  printf '\n'
  if [[ " $* " == *" --no-index "* ]]; then
    [[ "$MOCK_OFFLINE_FAIL" == 1 ]] && return 1
  else
    [[ "$MOCK_ONLINE_FAIL" == 1 ]] && return 1
  fi
  installed=1
  return 0
}
function python3 {
  if [[ "$1" == -c ]]; then
    [[ "$installed" == 1 && "$MOCK_BROKEN_IMPORT" != 1 ]]
  elif [[ "$*" == '-m pip --version' ]]; then
    [[ "$MOCK_INSTALLER" == pip || "$pip_ready" == 1 ]]
  elif [[ "$1 $2" == '-m ensurepip' ]]; then
    echo ENSUREPIP
    [[ "$MOCK_INSTALLER" == ensurepip ]] || return 1
    pip_ready=1
  elif [[ "$1 $2 $3" == '-m pip install' ]]; then
    fake_install pip "$@"
  else
    echo "Unexpected Python invocation: $*" >&2
    return 99
  fi
}
function uv { fake_install uv "$@"; }
'''
  script = tmp_path / "test_install.sh"
  script.write_text(mocks + functions + '\nensure_python_package serial pyserial "$MOCK_REQUIRED" "$MOCK_DEPENDENCIES"\n', encoding="utf-8")
  env = dict(os.environ, MOCK_INSTALLER=installer, MOCK_OFFLINE_FAIL=str(int(offline_fail)), MOCK_ONLINE_FAIL=str(int(online_fail)),
             MOCK_INSTALLED=str(int(installed)), MOCK_BROKEN_IMPORT=str(int(broken_import)), MOCK_REQUIRED=str(int(required)),
             MOCK_DEPENDENCIES=str(int(dependencies)))
  return subprocess.run([_bash(), script.name], cwd=tmp_path, env=env, text=True, capture_output=True, timeout=30)


def test_existing_package_needs_no_installer(tmp_path):
  result = _install(tmp_path, installed=True, installer="none")
  assert result.returncode == 0, result.stderr
  assert "INSTALL:" not in result.stdout
  assert "ENSUREPIP" not in result.stdout


@pytest.mark.parametrize('probe_ok,repair_ok', [(True, True), (False, True), (False, False)])
def test_boot_probes_one_interpreter_then_repairs_in_order(tmp_path, probe_ok, repair_ok):
  source = (Path(BASEDIR) / 'launch_chffrplus.sh').read_text()
  bootstrap = source[source.index('function bootstrap_runtime_dependencies {'):source.index('function show_agnos_update_failure {')]
  command = bootstrap + r'''
python3() { printf '%s\n' "$2" > all_imports; return "$PROBE_RC"; }
ensure_python_package() { echo "$1" >> repaired; test "$1" != msgpack || return "$REPAIR_RC"; }
bootstrap_runtime_dependencies
'''
  env = dict(os.environ, DIR=str(tmp_path), PROBE_RC=str(int(not probe_ok)), REPAIR_RC=str(int(not repair_ok)))
  result = subprocess.run([_bash(), '-c', command], cwd=tmp_path, env=env, timeout=10)
  assert result.returncode == int(not (probe_ok or repair_ok))
  probes = (tmp_path / 'all_imports').read_text().splitlines()
  assert probes[0] == 'import serial' and probes[-1] == 'import shapely'
  assert "import cv2; assert cv2.__version__ == '4.13.0'; assert hasattr(cv2.dnn, 'readNetFromONNX')" in probes
  repaired = tmp_path / 'repaired'
  if probe_ok:
    assert not repaired.exists()
  else:
    names = repaired.read_text().splitlines()
    assert names[:2] == ['serial', 'msgpack']
    assert names[-1] == ('shapely' if repair_ok else 'msgpack')


@pytest.mark.parametrize("installer", ["pip", "uv", "ensurepip"])
def test_missing_package_installs_from_wheel(tmp_path, installer):
  result = _install(tmp_path, installer=installer)
  assert result.returncode == 0, result.stderr
  assert result.stdout.count("INSTALL:") == 1
  assert "<--no-index>" in result.stdout
  assert "<--no-deps>" in result.stdout
  assert "project with spaces/pydeps>" in result.stdout
  assert "pyserial installed." in result.stdout
  if installer == "uv":
    assert "<--python> <python3> <--no-python-downloads>" in result.stdout
  if installer == "ensurepip":
    assert "ENSUREPIP" in result.stdout


@pytest.mark.parametrize("installer", ["pip", "uv"])
def test_ubuntu_retries_incompatible_wheel_online(tmp_path, installer):
  result = _install(tmp_path, installer=installer, offline_fail=True)
  assert result.returncode == 0, result.stderr
  installs = [line for line in result.stdout.splitlines() if line.startswith("INSTALL:")]
  assert len(installs) == 2
  assert "<--no-index>" in installs[0]
  assert "<--no-index>" not in installs[1]
  assert "<--no-deps>" not in installs[1]
  assert "pyserial installed." in result.stdout


def test_local_install_can_resolve_dependencies(tmp_path):
  result = _install(tmp_path, dependencies=True)
  assert result.returncode == 0, result.stderr
  assert "<--no-deps>" not in result.stdout


def test_device_never_retries_online(tmp_path):
  result = _install(tmp_path, offline_fail=True, device=True)
  assert result.returncode == 1
  assert result.stdout.count("INSTALL:") == 1
  assert "online package index" not in result.stdout


@pytest.mark.parametrize("required", [True, False])
@pytest.mark.parametrize("failure", ["install", "import", "installer"])
def test_failed_repair_blocks_only_required_packages(tmp_path, required, failure):
  result = _install(tmp_path, required=required, offline_fail=failure == "install", online_fail=failure == "install",
                    broken_import=failure == "import", installer="none" if failure == "installer" else "pip")
  assert result.returncode == int(required), result.stderr
  assert "pyserial installed." not in result.stdout
  assert ("not starting openpilot" if required else "continuing without it") in result.stdout
