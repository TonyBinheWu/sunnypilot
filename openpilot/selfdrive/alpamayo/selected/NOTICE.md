# Third-party attribution

The selected runtime adapts comma's Alpamayo prototype and its tinygrad numerical kernels.
Their MIT notices are preserved in `licenses/comma-MIT.txt` and `licenses/tinygrad-MIT.txt`.
The tinygrad notice is an unchanged copy of the archive's `agent-upstream-LICENSE`.

`inputs.py` adapts NVIDIA Alpamayo 2 Edge input preparation.
It retains NVIDIA's copyright and Apache-2.0 identifiers, with a modification notice.
The complete license is in `licenses/NVIDIA-Apache-2.0.txt`.
The dependency remains pinned to revision `02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e`.

`licenses/AMD-CK-MIT.txt` preserves the unchanged AMD Composable Kernel license from the experiment archive.
This selected package uses the fixed HIP source/object inventory in `assets/manifest.json`.
It does not include the archive's CK attention headers, CK attention objects, or flash-attention sources.

Frozen source/object pairs retain their exact original bytes and symbols.
Their notices apply through this accompanying file; source comments were not rewritten during extraction.
No checkpoint weights, firmware, compiler libraries, or third-party Python distributions are bundled.
