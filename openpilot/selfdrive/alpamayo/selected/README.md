# Selected Alpamayo inference

This package specializes the shared `openpilot.selfdrive.alpamayo.model.EdgeModel`.
It implements one recipe: four-bit weights in the serial language MLP and mixed FP8 and BF16 elsewhere.
The car uses a 100 ms slot grid and two Euler steps. Four-bit and FP8 weights can change reasoning and trajectories relative to BF16.

## API

Use the isolated Alpamayo interpreter in a fresh worker process.
Import this package before importing tinygrad. The constructor sets the selected compiler environment.

```python
from pathlib import Path
from openpilot.selfdrive.alpamayo.selected import Config, Runtime

config = Config(
  checkpoint=Path('/path/to/checkpoint'),
  fp8_cache=Path('/path/to/fp8-cache'),
  prefill_calibration=Path('/path/to/prefill-scales.json'),
  cache_dir=Path('/path/to/persistent-cache'),
  initial_noise=Path('/path/to/initial_noise.npy'),
)
runtime = Runtime(config)
try:
  prediction = runtime.predict(sample)  # Or predict(sample, explicit_float32_noise).
  metrics = runtime.metrics
  runtime.synchronize()
finally:
  runtime.close()
```

`sample` contains the six canonical fields from the shared README.
Images use `(10,1,3,432,768)` uint8 calibrated RGB, with five camera-1 images followed by five camera-6 images.
All images retain 720 patches. Noise must be finite float32 with shape `(1,64,2)`.
Measured ego history is consumed unchanged. An empty navigation string means unavailable guidance.

`predict` returns all 64 positions, rotations, generated token IDs, reasoning, stage timings, and the supplied noise hash.
`metrics` separately records cache hits, misses, pixel upload bytes, and speculation outcomes.
`reset()` clears sample state, feature caches, decode history, and captured graphs while retaining model weights.
`close()` synchronizes and restores process-local backend overrides. Calls after close are rejected.
`manifest` records the exact numerical recipe and artifact identities; `device` identifies the selected backend.

`selected.ShadowAdapter(config)` implements the shared `runtime.run_prediction(adapter, arrays, metadata)` contract.
This adapter requires `initial_noise`. The shared worker, scheduler and frontend retain their existing responsibilities.

## Fixed arithmetic

| Component | Selected setting |
| --- | --- |
| Inputs | Two front cameras, 120/30 degrees, history `(-2,-1,-0.5,-0.1,0)` seconds |
| Vision | 144-image content cache; missing images encoded in groups of at most two |
| Vision precision | BF16 patch embedding and first two layers; dynamic per-image FP8 scales thereafter |
| Language | Fixed 112 activation scales, packed FP8, 2112-row prefill in parts at rows 0, 576 and 768, 2304-row KV allocation |
| Serial language MLP | Signed four-bit FC1 and FC2 weights with one FP16 scale per 32 weights; FP8 activations |
| Reasoning | Reduced CoC vocabulary; the prefill verifies up to 31 draft tokens with 32 independent heads |
| Continuation | Target-verified lookup carry, per-row FP8 draft verification, serial blocks of six, maximum 64 tokens |
| Expert | One Euler step (`diffusion_steps`, 1 to 10); restored BF16 action projections; one fused attention launch per layer; 64-row FP8 tiles 2x2 (1x2 for 512 outputs) |
| Compiler | WGP AMD LLVM22; isolated tinygrad `89846dcfb383a98ee01cfec3bba440ae7dcf9b1e` |

Each prediction uploads uncached images in one pixel transfer. The GPU expands the byte patches to BF16 and encodes up to two images per call.
Ten distinct images need 5,529,600 bytes on startup. Four misses need 2,211,840 bytes. A full cache hit sends only metadata.
At a warmed 500 ms cadence, four missing images require two groups; six older images remain cached.
At a warmed 100 ms cadence, two missing images require one group; eight older images remain cached.
Actual reuse follows image content and the capture schedule, including missing or repeated source frames.

Prefill schedules long causal attention blocks first and adds both residuals in the o_proj and second MLP projections, preserving both BF16 rounding steps.
Prefill RMS norms write packed FP8 with the layer's fixed scale directly; their BF16 output, rounded exactly as before, is never stored.
The prefill draft is the latest generated text, or the six-token nominal text before the first prediction. Draft tokens fill the padded rows
after the prompt. Head `i` holds the argmax after draft token `i-1`. The decoder accepts the matching prefix, whose KV rows the prefill wrote,
and continues from the first differing head. Accepted tokens have the same target-verified status as lookup verification.
A 2025-token prompt plus compact navigation text leaves room for all 32 heads; a prompt above 2081 tokens is rejected.
Padding rows follow the prompt, so real prompt rows and their KV are identical for any padded length.
Every padding row has the position of a placed draft token, placed or not. The ~1 MB prefill rotary tables thus change only with the
actual prompt length. A changed draft length previously re-uploaded them, which cost about 29 ms on 23% of slots.
Expert attention is one frozen launch per layer and Euler step: BF16 scores, FP32 key mask, softmax and PV with the original rounding,
summation trees and WMMA slot order. It reads the 2304 prompt KV rows straight from the layer's cache; no per-diffusion packing remains.
Each expert layer (`expert_block`) runs 24 instead of 35 launches with the same rounding: one Q/K/V GEMM with per-column weight scales,
FP8 casts fused into GEMM input packing, O and FC2 residuals in the GEMM epilogue, and order-free maxima without stored copies.
The expert step stays 4.5 ms on the Chestnut at 100 W: attention takes about 2.2 ms per step; 8 of its 64 workgroups wait for a second round.
During serial reasoning, 256 threads reduce the 9,216 expansion values to the same FP32 activation scale.
Startup creates the 56 four-bit matrices from the verified FP8 weights. They use 567 MiB of additional GPU memory; prompt processing still uses FP8 weights.
Draft attention retains its original QK, softmax, and PV arithmetic. Its 16- and 32-row products use 1x2 and 2x2 output tiles.
Output tiles change only which outputs one wave computes. Each output keeps its reduction order, so results stay bit-identical.
Smaller expert tiles reduced diffusion from 27.6 to 21.9 ms on the test car. The 32 prefill heads take one batched argmax (2.6 ms less).
Prefill attention reads K and V rows below 2112 straight from the KV cache (no K copy or V packing). Each 64-thread workgroup holds the
two query heads of one KV head for one 16-row tile; V uses the gfx12 transposing load. Online softmax rescales skip rows whose maximum did not change.
Two-image FP8 vision layers use fused frozen objects: LayerNorm and attention also emit |output| maxima for the next FP8 scale,
one merged Q/K/V projection writes attention heads directly, FC1 applies GELU and emits maxima, and O and FC2 add the residual.
Each image's FP8 scale still uses the `grouped_quantize` expressions. Single-image encodes keep the general path.
Vision attention waves read K and the transposed V straight from memory (gfx12 transposing load). Shared-memory staging and workgroup barriers are removed.
Score, softmax and PV arithmetic are unchanged; the attention launch takes 231 instead of 251 us on the test car at 100 W.
The FC1 GELU uses the plain exp2 instruction. The removed range scaling changes no result for any BF16 input (all 65,536 checked).
The frozen pair plan holds 38 programs. A regenerated plan keeps the programs of unchanged operations and compiles only changed ones.
Serial decoding reads both KV planes directly after each write. Full blocks keep six tokens' cache and rotary coordinates on the GPU.
In full blocks each serial layer is eleven launches with the original arithmetic: norm and FP8 quantize, one Q/K/V GEMV with RoPE
and the KV row store, scores, softmax, values, output quantize, o_proj, residual and norm, W4 FC1, ReLU^2 quantize, and W4 FC2 with
the residual add. Tokens, logits and KV rows matched the previous layer at positions 2025-2083; about 0.6 ms less per token.
The prefill runs in three parts with the same kernels per row: rows 0-575 (system prompt and the three older front images),
rows 576-767 (to the end of the -0.1 s front image) and rows 768-2111. Each part's attention reads the earlier parts' KV rows.
The three parts give the same bits as one 2112-row prefill. The older front images are earlier slots' current exposures,
and the -0.1 s pair is encoded before the slot opens. After each plan the worker queues the next slot's first part; after
the early -0.1 s encode it queues the second (`prefill_ahead`). A prediction skips an early part only when its token ids,
positions and image keys match the queued part; after any change it runs that part and every later part again.
The early parts move about 26 ms of prefill off the critical path.
The trajectory start state depends only on the ego history. It is estimated on the CPU while the GPU runs the prefill.
Each Euler step takes about 6 ms. On 24 real samples (city turns, fast curves, cruise) the mean 3 s heading error to the
driven path was 9.3 deg with one or two steps, 9.4 with three and 9.9 with ten; turns reached 66-68% of the driven heading at
1 s with every step count. A 160-token image budget raised the 3 s error to 14.0 deg.
Signed 4-bit language weights (one FP16 scale per 32) in the BF16 reference raised the 3 s error from 9.28 to 9.62 deg
(MLP only) and 9.77 deg (all projections), changed 2 of 24 reasoning texts and lowered the 1 s turn ratio from 66% to 63-64%.
Prompt processing is compute-bound, so four-bit weights would only shorten verification rounds (about 2 ms per plan).
The native camera sampler takes NV12 frames directly. It converts only the sampled region (plus an 8-pixel margin) to RGB
and reads interleaved RGB, which removes the full-frame conversion and planar copy. Each new crop is checked once against
full-frame conversion; libswscale converts widths that are multiples of 16 with other rounding, so crops avoid them.
No runtime recipe switches or experimental installers are exposed.

### Graph cache

Captured graphs persist under `<cache>/graphs` after code generation and before command building.
Buffers are stored as owners: model attribute paths, JIT outputs, fresh scratch, or small constants.
Entries are keyed by graph name, the graph-building sources (`selected/`, `model.py`, `amd_attention.py`), the checkpoint digest, kernel manifest, compiler settings and calibration.
Entries from other keys are deleted at startup. An entry that fails to bind is recaptured normally.

## Required assets and shared code

`install.py` installs the runtime with its pinned dependency lock and the published model files. Normal openpilot tinygrad stays unchanged.
NVIDIA code remains at `02f55a7aeabc1a2b9f7a80445c08e40bddc89f5e`.
To prepare the BF16 tensors of another full checkpoint for this recipe:

```sh
python -m openpilot.selfdrive.alpamayo.selected.prepare_checkpoint /path/to/original /path/to/selected-checkpoint
```

Set `inference.checkpoint` to the resulting directory. It contains the tokenizer, configuration and a 102 MB BF16 shard.
Preparation verifies the original 5.30 GB of shards. Startup verifies the complete compact shard and index against independently pinned hashes.
The runtime records both the source checkpoint identity and the hashes of the files actually loaded.
The full original checkpoint is also supported.
The separate FP8 `weights.bin`/`index.json`, fixed calibration, and per-upload verification remain required.
The first startup checks the complete `weights.bin` digest and stores per-4 KiB SHA-256 proofs (`leaf-proofs.bin`, zero nonce).
Each upload then recomputes the proofs on the GPU into randomly initialized memory and compares them with the stored file.
The tokenizer and input adapter load on a thread while the weights upload. Packing runs as batched schedules.
The GPU runs at its highest clock level (`AM_PERF_LEVEL=high`) under the 144 W power limit, so short idle gaps do not slow the next stage.
Below 144 W the clocks are automatic and the first graphs after an idle gap run up to 1.7 times slower.
`compute_profile` (default `false`) selects the SMU compute workload profile, which shortens this ramp; the power limit stays unchanged.
The profile stays set in the GPU until a full reset. Full-pipeline timing with it is unverified.
Changing these artifacts requires a separate numerical qualification.

The selected dispatcher uses 30 HIP source/object pairs under `assets/gfx1200`.
Startup checks their hashes against `assets/manifest.json`.
HIP/COMGR compilation is unnecessary on ARM. Ordinary tinygrad LLVM kernels still require LLVM22.
The compiler pool uses at most one process per CPU available to the worker. Its SQLite cache persists across production launches.
The worker reports import, verification, frontend, GPU setup and weight-loading times during startup. Ready does not mean a driving plan is available.
The constructor requires existing, hash-checked gfx1200 firmware in the configured persistent cache.
Inference does not fetch firmware or weights; `install.py` stages both.

Shared modules remain `model`, `amd_attention`, `inputs`, `geometry`, and `inference` identity helpers.
`camera.calibrated_image` provides the original portable C sampler using shared projection geometry.
Its caller supplies `cache_dir`; it compiles for the current CPU and does not include a host-specific library.
The selected live worker uses this sampler through the shared frontend.
CPU regression checks require exact agreement with the original projection and calibrated inputs.

Required notices are preserved in [NOTICE.md](NOTICE.md) and `licenses/`.
