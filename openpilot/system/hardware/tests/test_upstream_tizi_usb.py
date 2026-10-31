"""Check hardwared startup USB enumeration on tizi without touching mici."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

SOURCE = Path(__file__).resolve().parents[4] / "openpilot/system/hardware/hardwared.py"


def initial_usb_expr():
  tree = ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))
  for node in ast.walk(tree):
    if isinstance(node, ast.Call):
      for kw in node.keywords:
        if kw.arg == "usb_state" and isinstance(kw.value, ast.IfExp):
          return compile(ast.Expression(body=kw.value), str(SOURCE), "eval")
  raise AssertionError("hardwared no longer has the device-specific initial USB state")


class TestInitialUSBState(unittest.TestCase):
  def test_tizi_matches_upstream_immediate_enumeration(self):
    calls = []
    expected = [{"vendorId": 1, "productId": 2}]
    source = {"HARDWARE": SimpleNamespace(get_device_type=lambda: "tizi"),
              "get_usb_state": lambda: calls.append(True) or expected}
    self.assertIs(eval(initial_usb_expr(), source), expected)
    self.assertEqual(len(calls), 1)

  def test_mici_preserves_old_empty_startup_state(self):
    def must_not_enumerate():
      raise AssertionError("mici initial USB enumeration behavior changed")
    source = {"HARDWARE": SimpleNamespace(get_device_type=lambda: "mici"),
              "get_usb_state": must_not_enumerate}
    self.assertEqual(eval(initial_usb_expr(), source), [])

  def test_non_tizi_preserves_other_devices(self):
    source = {"HARDWARE": SimpleNamespace(get_device_type=lambda: "pc"),
              "get_usb_state": lambda: self.fail("PC should not enumerate during initial state")}
    self.assertEqual(eval(initial_usb_expr(), source), [])


if __name__ == "__main__":
  unittest.main(verbosity=2)
