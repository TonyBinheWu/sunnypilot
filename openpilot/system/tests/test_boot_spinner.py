import os

import pytest

from openpilot.system.ui.boot_status import BootStatus, StatusInput, fit_lines


def test_only_reported_progress_is_shown_and_model_phases_reset_it():
  status = BootStatus()
  status.update("Preparing runtime packages")
  assert status.progress is None and status.detail == "Preparing runtime packages"
  status.update("0")
  status.update("Compiling file.cc")
  assert status.progress == 0 and status.detail == "Compiling file.cc"
  status.update("108")
  assert status.progress == 100
  status.update("USB eGPU big model")
  status.update("Checking precompiled model")
  assert status.progress is None and status.context == "USB eGPU big model"
  status.update("Downloading precompiled model 38%")
  assert (status.detail, status.progress) == ("Downloading precompiled model", 38)
  status.update("Validating precompiled model")
  assert status.progress is None
  status.update("USB eGPU model")
  status.update("Downloading 61%")
  assert (status.detail, status.progress) == ("Downloading model", 61)
  status.update("Building settings registry")
  assert not status.context and status.progress is None


def test_partial_utf8_burst_and_eof_from_the_actual_status_pipe():
  read_fd, write_fd = os.pipe()
  try:
    stream, status = StatusInput(read_fd), BootStatus()
    prefix = "準".encode()
    os.write(write_fd, prefix[:1])
    stream.poll(status)
    assert status.detail == ""
    os.write(write_fd, prefix[1:] + b"\n15\n31\n")
    stream.poll(status)
    assert status.detail == "準" and status.progress == 31
    os.write(write_fd, b"done")
    os.close(write_fd)
    write_fd = None
    stream.poll(status)
    stream.poll(status)
    assert stream.eof and status.detail == "done"
  finally:
    os.close(read_fd)
    if write_fd is not None:
      os.close(write_fd)


@pytest.mark.parametrize("text", ["short", "長標題"*100, "a"*2048, "compile " + "very-long-file-name/"*130])
def test_two_status_lines_stay_within_the_small_screen(text):
  lines = fit_lines(text, 23, len)
  assert 1 <= len(lines) <= 2 and all(0 < len(line) <= 23 for line in lines)
  if len(text) > 46:
    assert lines[-1].endswith("...")
