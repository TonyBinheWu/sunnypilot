"""Process-local LLVM backend configuration for the selected recipe."""
import ctypes
from tinygrad import Device, dtypes
from tinygrad.device import Compiled
from tinygrad.runtime.support.compiler_llvm import AMDLLVMCompiler, LLVMCompiler
from tinygrad.uop.ops import UOp
from .frozen import verify_assets


class WGPCompiler(AMDLLVMCompiler):
  def __init__(self, arch):
    self.arch = arch
    LLVMCompiler.__init__(self, 'AMDGPU', arch, '-cumode')

  def __reduce__(self):
    return WGPCompiler, (self.arch,)


class Backend:
  active = False

  def __init__(self, timeout_ms):
    if Backend.active:
      raise RuntimeError('Use one selected runtime per dedicated process')
    if timeout_ms <= 0:
      raise ValueError('Device timeout must be positive')
    verify_assets()
    from tinygrad.runtime.autogen import llvm
    major, minor, patch = (ctypes.c_uint32() for _ in range(3))
    llvm.LLVMGetVersion(ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch))
    if major.value != 22:
      raise RuntimeError(f'Selected arithmetic requires LLVM22; found {major.value}')
    from tinygrad.runtime import ops_amd
    self.device = Device[Device.DEFAULT]
    if self.device.arch != 'gfx1200' or str(self.device.renderer.target) != 'USB+AMD:LLVM:gfx1200':
      raise ValueError('Selected inference requires USB+AMD:LLVM:gfx1200')
    if not isinstance(self.device.renderer.compiler, AMDLLVMCompiler):
      raise ValueError('Selected inference requires AMD LLVM')
    self.compiler = self.device.renderer.compiler
    self.old_packet = ops_amd.dispatch_packet
    self.old_timeout = Compiled.wait_timeout_ms
    self.closed = False
    self.device.renderer.compiler = WGPCompiler(self.device.arch)
    original = self.old_packet
    def typed_packet(*args, **kwargs):
      return [UOp.const(word, dtypes.uint32) if isinstance(word, int) else word for word in original(*args, **kwargs)]
    ops_amd.dispatch_packet = self.packet = typed_packet
    Compiled.wait_timeout_ms = timeout_ms
    Backend.active = True

  def close(self):
    if self.closed:
      return
    from tinygrad.runtime import ops_amd
    try:
      self.device.synchronize()
    finally:
      self.device.renderer.compiler = self.compiler
      ops_amd.dispatch_packet = self.old_packet
      Compiled.wait_timeout_ms = self.old_timeout
      self.closed = True
      Backend.active = False
