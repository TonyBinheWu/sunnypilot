"""CPU-only contract test for sunnypilot's plain-artifact compiler and loader.

Run from the repository root with tinygrad_repo on PYTHONPATH.
This does not validate AMD/QCOM hardware, an actual driving model, or road safety.
"""
import dataclasses
import inspect
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import numpy as np


class TestRuntimeContract(unittest.TestCase):
  def test_import_uses_pinned_submodule(self):
    import tinygrad
    root = Path(__file__).resolve().parents[2]
    submodule = root / "tinygrad_repo"
    self.assertTrue(Path(tinygrad.__file__).resolve().is_relative_to(submodule.resolve()))
    pin = subprocess.check_output(["git", "-C", str(root), "ls-tree", "HEAD", "tinygrad_repo"], text=True).split()[2]
    actual = subprocess.check_output(["git", "-C", str(submodule), "rev-parse", "HEAD"], text=True).strip()
    self.assertEqual(actual, pin)

  def test_loader_api_contract(self):
    import tinygrad.engine.jit as jit
    from tinygrad.device import Buffer
    from tinygrad.helpers import Target
    from tinygrad.uop.ops import ParamArg, ProgramInfo, UOp
    fields = {cls: {f.name for f in dataclasses.fields(cls)} for cls in (ProgramInfo, ParamArg, Target)}
    self.assertTrue(fields[ProgramInfo] >= {"global_size", "local_size", "globals", "outs", "ins", "target"})
    self.assertTrue(fields[ParamArg] >= {"slot", "dtype", "name", "image"})
    self.assertTrue(fields[Target] >= {"device", "renderer", "arch"})
    for obj, names in ((UOp, ("param", "from_buffer", "store_call", "call")),
                       (Buffer, ("view", "ensure_allocated")),
                       (jit, ("compile_linear", "_prepare_jit_inputs"))):
      for name in names:
        self.assertTrue(callable(getattr(obj, name, None)), f"Missing API: {obj}.{name}")
    self.assertIn("expected_names", inspect.signature(jit.CapturedJit).parameters)

  def test_verified_inference_cache_and_rejection(self):
    from tinygrad import Tensor, TinyJit
    from openpilot.sunnypilot.modeld_v2.helpers import ArtifactMismatch, PlainJit, cache_is_fresh, load_model, read_parts, write_bundle
    from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame, record_kernel_linear, serialize_jit

    rng = np.random.default_rng(471)
    weights_np = rng.standard_normal((8, 4)).astype(np.float32)
    weights = Tensor(weights_np).realize()

    def model(x, bias):
      return (x @ weights + bias).relu().contiguous()

    def inputs(seed):
      random = np.random.default_rng(seed)
      return {"x": Tensor(random.standard_normal((1, 8)).astype(np.float32)).realize(),
              "bias": Tensor(random.standard_normal((1, 4)).astype(np.float32)).realize()}

    run = TinyJit(model, prune=True)
    original = inputs(1)
    with record_kernel_linear() as recorded:
      run(**original)
      run(**original)
      check, _ = capture_frame(run, original)
    self.assertEqual(len(recorded), 1)
    header, blob = serialize_jit(run, recorded[0], check)
    with tempfile.TemporaryDirectory() as directory:
      path = os.path.join(directory, "cpu_fixture.pkl")
      write_bundle(path, {"run": (header, blob)}, {"metadata": {"purpose": "runtime_contract"}})
      loaded = load_model(path, verify=True, cache=False)
      self.assertIsInstance(loaded["run"], PlainJit)
      fresh = inputs(2)
      expected = np.maximum(fresh["x"].numpy() @ weights_np + fresh["bias"].numpy(), 0)
      np.testing.assert_allclose(loaded["run"](**fresh).numpy(), expected, rtol=1e-5, atol=1e-5)
      load_model(path, verify=True, cache=True)
      self.assertTrue(cache_is_fresh(path))
      cached = load_model(path, verify=True, cache=True)
      np.testing.assert_allclose(cached["run"](**fresh).numpy(), expected, rtol=1e-5, atol=1e-5)
      parts, _ = read_parts(path)
      recorded_header, recorded_blob = parts["run"]
      poisoned = dict(recorded_header, check=dict(recorded_header["check"], outputs=[recorded_header["check"]["inputs"][0][1]]))
      with self.assertRaises(ArtifactMismatch):
        PlainJit(poisoned, recorded_blob, verify=True)


if __name__ == "__main__":
  unittest.main(verbosity=2)
