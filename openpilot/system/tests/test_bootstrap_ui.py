from pathlib import Path
import os
import shutil
import subprocess

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]


def test_build_spinner_uses_only_bootstrap_fonts():
  spinner = (REPO_ROOT / "openpilot/system/ui/spinner.py").read_text(encoding="utf-8")
  assert 'gui_app.init_window("Spinner", font_weights=(FontWeight.NORMAL, FontWeight.PRETENDARD))' in spinner
  assert "FontWeight.DISPLAY" not in spinner[spinner.index("def main():"):]
  assert "FontWeight.UNIFONT" not in spinner[spinner.index("def main():"):]


def test_continue_script_is_durable_before_installer_waits():
  installer = (REPO_ROOT / "openpilot/selfdrive/ui/installer/installer.cc").read_text(encoding="utf-8")
  write_start = installer.index("// write continue.sh")
  wait_start = installer.index("// wait for the installed software's UI")
  write = installer[write_start:wait_start]

  expected_order = (
    "fwrite(",
    "fflush(",
    "fchmod(",
    "fsync(fileno(of))",
    "fclose(",
    "rename(CONTINUE_NEW_PATH, CONTINUE_PATH)",
    'open("/data", O_RDONLY | O_DIRECTORY)',
    "fsync(data_dir_fd)",
  )
  positions = [write.index(token) for token in expected_order]
  assert positions == sorted(positions)
  assert 'run("mv /data/continue.sh.new' not in write


def test_agnos_ui_failure_uses_independent_recovery_with_its_log(tmp_path):
  git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
  bash = str(git_bash) if os.name == "nt" and git_bash.is_file() else shutil.which("bash")
  if bash is None:
    pytest.skip("bash is required")
  source = (REPO_ROOT / "launch_chffrplus.sh").read_text(encoding="utf-8")
  function = source[source.index("function show_agnos_update_failure {"):source.index("function agnos_init {")]
  script = function + r'''
show_startup_failure() {
  printf 'RECOVERY_REASON:%s\nRECOVERY_LOG:%s\n' "$1" "$2"
}
python3() { echo 'Regular UI must not run'; exit 99; }
show_agnos_update_failure 'Missing updater dependency'
'''
  result = subprocess.run([bash, "-c", script], cwd=tmp_path, text=True, capture_output=True, timeout=5)
  assert result.returncode == 0, result.stderr
  assert "RECOVERY_REASON:AGNOS update paused." in result.stdout
  assert "Missing updater dependency" in result.stdout
  assert "RECOVERY_LOG:/data/agnos-updater-ui.log" in result.stdout
  recovery = source[source.index("function show_startup_failure {"):source.index("function launch {")]
  assert '--log "$log_path"' in recovery
