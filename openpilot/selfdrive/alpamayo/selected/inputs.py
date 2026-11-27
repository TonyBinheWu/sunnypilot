# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# Modified: cache checked byte patches, prompt token fields, and structural RoPE indices.
"""Exact selected CPU inputs, with bounded per-adapter caches."""
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
import threading
import ctypes
from functools import partial
from types import SimpleNamespace
import numpy as np
import torch
from torch.nn.functional import interpolate
from transformers.models.qwen2_vl.image_processing_qwen2_vl import smart_resize
from transformers.models.cosmos3_edge.modeling_cosmos3_edge import Cosmos3EdgeModel, Cosmos3EdgeVisionEmbeddings
from alpamayo2_edge.chat_template import CLOSED_THINKING, build_conversation
from alpamayo2_edge.models.delta_tokenizer import DeltaTrajectoryTokenizer
from alpamayo2_edge.sample import CAMERA_PIXEL_BOUNDS
from openpilot.selfdrive.alpamayo.inputs import InputAdapter
from openpilot.selfdrive.alpamayo.segments import FrontImages, IMAGE, IMAGE_BYTES, Patch, PatchRows

_memcmp = ctypes.CDLL(None).memcmp
_memcmp.argtypes = (ctypes.c_void_p,ctypes.c_void_p,ctypes.c_size_t)
_memcmp.restype = ctypes.c_int


def same_image(a, b):
  if a.shape != b.shape or a.dtype != b.dtype:
    return False
  if a.device.type == b.device.type == 'cpu' and a.dtype == torch.uint8 and a.is_contiguous() and b.is_contiguous():
    return _memcmp(a.data_ptr(),b.data_ptr(),a.numel()) == 0
  return torch.equal(a,b)


class SelectedInputs(InputAdapter):
  def __init__(self, checkpoint, *, native_fresh_patches=False):
    super().__init__(checkpoint)
    self.history = DeltaTrajectoryTokenizer(pad_origin_at_beginning=False)
    self.rope = SimpleNamespace(config=self.config.vlm_config)
    self.rope.get_vision_position_ids = partial(Cosmos3EdgeModel.get_vision_position_ids,self.rope)
    self.resize_cache = {camera:OrderedDict() for camera in (1,6)}
    self.position_cache = {}
    self.text_cache,self.rope_cache = OrderedDict(),OrderedDict()
    image = self.processor.image_processor
    if (list(image.image_mean) != [.5]*3 or list(image.image_std) != [.5]*3 or
        image.rescale_factor != 1/255 or image.temporal_patch_size != 1):
      raise ValueError('Selected byte inputs require the exact checkpoint pixel palette')
    if (image.patch_size,image.merge_size,image.temporal_patch_size) != (16,2,1):
      raise ValueError('Selected byte patches require the checkpoint 16/2/1 layout')
    self.sizes = {c:smart_resize(432,768,factor=32,min_pixels=CAMERA_PIXEL_BOUNDS[c][0],max_pixels=CAMERA_PIXEL_BOUNDS[c][1]) for c in (1,6)}
    self.grids = {c:(1,h//16,w//16) for c,(h,w) in self.sizes.items()}
    if any(h*w != 720*16**2 for h,w in self.sizes.values()):
      raise ValueError('Expected 720 byte patches per calibrated image')
    self.fresh_kernel = None
    if native_fresh_patches:
      from .fresh_patches import library, pack_fresh
      if any(tuple(hw) != (320,576) for hw in self.sizes.values()):
        raise ValueError('Fresh patch kernel requires the exact 320x576 output')
      library()
      self.fresh_kernel = pack_fresh
    # Process one camera on the calling thread. Propagate the runtime's Torch thread count to the other camera.
    self.worker = ThreadPoolExecutor(max_workers=1,initializer=torch.init_num_threads)
    # The live worker patches early camera pairs on a second thread; each camera's resize cache has one writer at a time.
    self.camera_locks = {camera:threading.Lock() for camera in self.resize_cache}

  def reset(self):
    for cache in self.resize_cache.values():
      cache.clear()
    self.position_cache.clear()
    self.text_cache.clear()
    self.rope_cache.clear()

  def close(self):
    self.worker.shutdown(wait=True)
    self.reset()

  def camera_patches(self, camera, entries, owned):
    with self.camera_locks[camera]:
      return self._camera_patches(camera, entries, owned)

  def _camera_patches(self, camera, entries, owned):
    cache = self.resize_cache[camera]
    patches = []
    for frame,stamp in entries:
      old = cache.get(stamp)
      frozen = type(frame) is bytes
      if old is not None and (frame is old[0] if frozen else isinstance(old[0],torch.Tensor) and same_image(frame,old[0])):
        cache.move_to_end(stamp)
        patches.append(old[1])
        continue
      # Resize the private snapshot itself; a reused timestamp or mutable source cannot poison the cache.
      if frozen and len(frame) != IMAGE_BYTES:
        raise ValueError('Wrong immutable camera frame size')
      source = frame if frozen or owned else frame.clone()
      if self.fresh_kernel is None:
        # Torch never receives a writable alias to immutable source bytes.
        floats = (torch.from_numpy(np.frombuffer(source,np.uint8).reshape(IMAGE).astype(np.float32)) if frozen
                  else source.unsqueeze(0).float())
        image = interpolate(floats,self.sizes[camera],mode='bicubic',align_corners=False,antialias=True)
        batch,_,_ = self.processor.image_processor.patchify(image.clamp_(0,255).round_().byte(),16,2,1)
        packed = batch.view(720,768)
      else:
        packed = self.fresh_kernel(source)
      if frozen:
        packed = Patch(packed.numpy())  # A cached feature key permanently names exactly these immutable patch bytes.
      cache[stamp] = source,packed
      if len(cache) > 72:
        cache.popitem(last=False)
      patches.append(packed)
    return patches

  def patch_pair(self, first, second, *, owned=False):
    future = self.worker.submit(self.camera_patches,1,first,owned)
    try:
      right = self.camera_patches(6,second,owned)
    finally:
      left = future.result()  # Finish reading both input views even if the calling thread raises.
    grids = [self.grids[1]]*len(left)+[self.grids[6]]*len(right)
    return (PatchRows(left+right) if type(left[0]) is Patch else torch.cat(left+right)),grids

  def anchor_patches(self, anchors):
    entries = []
    for (image,ref),camera in zip(anchors,(1,6),strict=True):
      if ref['view'] != camera:
        raise ValueError('Expected the calibrated current image from each front camera')
      if type(image) is bytes and len(image) == IMAGE_BYTES:
        frame = image
      elif isinstance(image,np.ndarray) and image.shape == IMAGE and image.dtype == np.uint8:
        frame = torch.from_numpy(image[0].copy())
      else:
        raise ValueError('Invalid calibrated anchor pixels')
      entries.append([(frame,ref['capture_ns']//1000)])
    pixels,grids = self.patch_pair(*entries,owned=True)
    return pixels,torch.tensor(grids,dtype=torch.int64)

  def vision_positions(self, grids):
    # The checkpoint interpolates each grid independently. Equal grids have identical position bytes.
    key = tuple(map(tuple,grids.tolist()))
    if key not in self.position_cache:
      if len(self.position_cache) >= 4:
        self.position_cache.pop(next(iter(self.position_cache)))
      chunks = {}
      for i,grid in enumerate(key):
        if grid not in chunks:
          chunks[grid] = Cosmos3EdgeVisionEmbeddings.resize_positional_embeddings(self.position_weight,grids[i:i+1],2).float().numpy()
      self.position_cache[key] = np.concatenate([chunks[grid] for grid in key])
    return self.position_cache[key]

  def tokenize(self, messages, pixels, grids):
    # Tokenization body follows NVIDIA helper._tokenize_messages (Apache-2.0).
    # Only resize reuse and retained unnormalized uint8 patches differ.
    processor = self.processor
    image_processor = processor.image_processor
    grid_tensor = torch.tensor(grids,dtype=torch.int64)
    # The selected processor expands placeholders using only the ordered grids.
    # Keep its replacement, tokenization, special-token checks, and modality IDs.
    # The pinned driving template renders roles, ordered text (including every time label), and image placeholders.
    content = tuple((m['role'],tuple(e['text'] if e['type'] == 'text' else None for e in m['content'])) for m in messages)
    prompt_key = (content,tuple(grids))
    template = self.text_cache.get(prompt_key)
    if template is None:
      text = processor.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,add_vision_id=False,
                                           continue_final_message=False,enable_thinking=False)
      if not text.endswith(CLOSED_THINKING):
        raise ValueError('Unexpected checkpoint chat suffix')
      visual = {'image_grid_thw':grid_tensor}
      replacements = [processor.replace_image_token(visual,i) for i in range(len(grids))]
      expanded,_ = processor.get_text_with_replacements([text],replacements)
      tokens = dict(processor(text=expanded,padding=False,return_tensors='pt',return_mm_token_type_ids=True))
      if len(text) <= 16384 and tokens['input_ids'].numel() <= 8192:
        self.text_cache[prompt_key] = {k:v.clone() for k,v in tokens.items()}
        if len(self.text_cache) > 16:
          self.text_cache.popitem(last=False)
    else:
      self.text_cache.move_to_end(prompt_key)
      tokens = {k:v.clone() for k,v in template.items()}
    tokens.update(pixel_values=pixels,image_grid_thw=grid_tensor)
    patches = tokens['pixel_values']
    if (type(patches) is not PatchRows and (patches.dtype != torch.uint8 or patches.ndim != 2)) or patches.shape[1] != 3*image_processor.patch_size**2:
      raise ValueError('Expected unnormalized uint8 image patches')
    if tokens['input_ids'].shape[0] != 1:
      raise ValueError('One sample is required')
    return tokens

  def prepare(self, arrays):
    fields = {'image_frames','camera_indices','absolute_timestamps','ego_history_xyz','ego_history_rot','nav_text'}
    if set(arrays) != fields:
      raise ValueError('Expected the six canonical model inputs')
    data = {k:v if k == 'nav_text' or isinstance(v,torch.Tensor) or (k == 'image_frames' and type(v) is FrontImages)
            else torch.from_numpy(np.asarray(v)) for k,v in arrays.items()}
    cameras,times,images = data['camera_indices'],data['absolute_timestamps'],data['image_frames']
    if (cameras.dtype != torch.int64 or cameras.tolist() != [1]*5+[6]*5 or times.dtype != torch.int64 or times.shape != (10,)
        or images.shape != (10,1,3,432,768) or (type(images) is not FrontImages and
        (images.dtype != torch.uint8 or not images.is_contiguous() or images.device.type != 'cpu'))
        or any(value.device.type != 'cpu' for value in (cameras,times))):
      raise ValueError('Require the complete calibrated two-front CPU input')
    if any(not bool(torch.all(times[i+1:i+5] > times[i:i+4])) for i in (0,5)):
      raise ValueError('History timestamps must advance')
    for key,shape in [('ego_history_xyz',(1,20,3)),('ego_history_rot',(1,20,3,3))]:
      value = data[key]
      if value.shape != shape or value.dtype != torch.float32 or value.device.type != 'cpu' or not torch.isfinite(value).all():
        raise ValueError('Require finite measured float32 ego history')
    nav = data['nav_text']
    if not isinstance(nav,(list,tuple)) or len(nav) != 1 or not isinstance(nav[0],str):
      raise ValueError('Require one navigation string; empty means unavailable')
    canonical = dict(data,camera_pixel_bounds=CAMERA_PIXEL_BOUNDS)
    stamps = times.tolist()
    if type(images) is FrontImages:
      canonical['image_frames'] = images.views()  # Prompt placeholders still carry all ten actual images and original times.
      entries = images
    else:
      entries = images[:,0]
    pixels,grids = self.patch_pair(zip(entries[:5],stamps[:5],strict=True),zip(entries[5:],stamps[5:],strict=True))
    tokens = self.tokenize(build_conversation(canonical),pixels,grids)
    grids = tokens['image_grid_thw']
    if grids.shape != (10,3) or not torch.all(grids.prod(dim=1) == 720):
      raise ValueError('Selected input requires 720 patches for every image')
    prepared = {'tokenized_data':tokens,'ego_history_xyz':data['ego_history_xyz'].unsqueeze(0),
                'ego_history_rot':data['ego_history_rot'].unsqueeze(0)}
    ids = tokens['input_ids'].clone()
    history = self.history.encode(None,None,prepared['ego_history_xyz'][:,0],prepared['ego_history_rot'][:,0])
    ids[ids == self.config.traj_ids['history_pad']] = (history+self.config.traj_ids['history_id0']).flatten()
    key = tuple(map(tuple,grids.tolist()))
    # Pinned get_rope_index reads ID shape/dtype, ordered modality spans and grids;
    # it does not inspect the learned IDs. The caller gets a fresh position array.
    types = tokens['mm_token_type_ids']
    structure = (tuple(ids.shape),ids.dtype,types.dtype,types.numpy().tobytes(),key,self.rope.config.vision_config.spatial_merge_size)
    cached = self.rope_cache.get(structure)
    if cached is None:
      positions,delta = Cosmos3EdgeModel.get_rope_index(self.rope,ids,types,image_grid_thw=grids)
      cached = (positions.numpy(),int(delta.item()))
      if ids.numel() <= 8192:
        self.rope_cache[structure] = cached
        if len(self.rope_cache) > 16:
          self.rope_cache.popitem(last=False)
    else:
      self.rope_cache.move_to_end(structure)
    return prepared,(ids.numpy(),cached[0].copy(),cached[1],self.vision_positions(grids))
