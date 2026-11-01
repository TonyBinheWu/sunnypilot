"""Host tests of production firmware validation and startup scheduling, without USB I/O.

Extract hardwared's Chestnut class to avoid starting its native hardware dependencies.
The flash thread and clock are mocked; no firmware is written to a device.
"""
import ast
import importlib.util
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import zlib

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'openpilot/system/hardware'
spec = importlib.util.spec_from_file_location('chestnut_usb', ROOT / 'openpilot/common/hardware/usb.py')
assert spec is not None and spec.loader is not None
usb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(usb)


def production_nodes(path, names, namespace):
  tree = ast.parse(path.read_text(encoding='utf-8'))
  nodes = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names]
  assert len(nodes) == len(names)
  exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)
  return namespace


class TestChestnutStartup(unittest.TestCase):
  def setUp(self):
    self.clock = Mock(return_value=2.)
    self.thread = Mock()
    self.thread.is_alive.return_value = True
    self.thread_factory = Mock(return_value=self.thread)
    self.namespace = production_nodes(HARDWARE / 'hardwared.py', {'Chestnut'}, {
      'threading': SimpleNamespace(Thread=self.thread_factory),
      'time': SimpleNamespace(monotonic=self.clock),
      'cloudlog': Mock(), 'subprocess': Mock(), 'os': os, 'sys': sys, 'BASEDIR': str(ROOT),
      'CHESTNUT_FW_VERSION': usb.CHESTNUT_FW_VERSION,
      'CHESTNUT_USB_PRODUCT': usb.CHESTNUT_USB_PRODUCT,
      'is_chestnut_usb_id': usb.is_chestnut_usb_id,
    })
    self.chestnut = self.namespace['Chestnut']()
    self.old_device = [{'vendorId': 0x3801, 'productId': 1, 'product': 'custom ed4e39b7-CLEAN'}]

  def test_first_boot_update_is_not_delayed_by_retry_interval(self):
    self.chestnut.update(True, self.old_device)
    self.thread.start.assert_called_once()
    self.assertEqual(self.chestnut.attempts, 1)
    self.assertTrue(self.chestnut.flashing)

  def test_no_flash_onroad_or_when_current(self):
    self.chestnut.update(False, self.old_device)
    self.chestnut.update(True, [{**self.old_device[0], 'product': usb.CHESTNUT_USB_PRODUCT}])
    self.thread_factory.assert_not_called()

  def test_no_duplicate_thread_and_retry_budget(self):
    self.chestnut.update(True, self.old_device)
    self.clock.return_value = 40.
    self.chestnut.update(True, self.old_device)
    self.assertEqual(self.chestnut.attempts, 1)
    self.thread.is_alive.return_value = False
    self.chestnut.update(True, self.old_device)
    self.assertEqual(self.chestnut.attempts, 2)
    self.chestnut.update(True, self.old_device)
    self.assertEqual(self.chestnut.attempts, 2)
    self.clock.return_value = 61.
    self.chestnut.update(True, self.old_device)
    self.clock.return_value = 82.
    self.chestnut.update(True, self.old_device)
    self.assertEqual(self.chestnut.attempts, 3)

  def test_startup_gate_obeys_upstream_timeout_and_thread_completion(self):
    tree = ast.parse((HARDWARE / 'hardwared.py').read_text(encoding='utf-8'))
    gate = next(node.value for node in ast.walk(tree) if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Subscript) and isinstance(t.slice, ast.Constant)
                        and t.slice.value == 'not_flashing_chestnut' for t in node.targets))
    evaluate = compile(ast.Expression(gate), '<startup gate>', 'eval')
    self.chestnut.update(True, self.old_device)
    self.assertFalse(eval(evaluate, {'chestnut': self.chestnut}))
    self.clock.return_value = 31.9
    self.assertFalse(eval(evaluate, {'chestnut': self.chestnut}))
    self.clock.return_value = 32.
    self.assertTrue(eval(evaluate, {'chestnut': self.chestnut}))
    self.clock.return_value = 3.
    self.thread.is_alive.return_value = False
    self.assertTrue(eval(evaluate, {'chestnut': self.chestnut}))

  def test_flash_invokes_the_bundled_version(self):
    runner = self.namespace['subprocess']
    runner.run.return_value = SimpleNamespace(returncode=0, stdout='verified')
    self.chestnut.flash()
    self.assertEqual(runner.run.call_args.args[0][-1], usb.CHESTNUT_FW_VERSION)
    self.assertTrue(self.chestnut.flashed)


class TestBundledFirmware(unittest.TestCase):
  def test_image_integrity_and_product_match(self):
    functions = production_nodes(HARDWARE / 'chestnut/flash.py', {'validate_image', 'image_product'}, {
      'MAX_CODE_SIZE': 0x10000, 're': re, 'zlib': zlib,
    })
    image = (HARDWARE / 'chestnut/firmware_wrapped.bin').read_bytes()
    functions['validate_image'](image)
    self.assertEqual(functions['image_product'](image), usb.CHESTNUT_USB_PRODUCT)
    broken = bytearray(image)
    broken[100] ^= 1
    with self.assertRaises(ValueError):
      functions['validate_image'](broken)


if __name__ == '__main__':
  unittest.main()
