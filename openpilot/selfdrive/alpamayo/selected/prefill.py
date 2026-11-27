"""Padded prefill (2112 rows) with draft verification heads."""
from tinygrad import Tensor, TinyJit, dtypes
from tinygrad.helpers import round_up
from tinygrad.uop.ops import UOp
from .model import PREFILL_SPLITS


class PaddedPrefill:
  """KV allocation shared by the split prefill."""
  def __init__(self, model):
    self.model = model
    self.shape = None

  def allocate(self, x, cos, max_tokens):
    model = self.model
    capacity = round_up(x.shape[1]+max_tokens,256)
    if capacity != 2304:
      raise ValueError('Selected KV allocation must contain 2304 rows')
    if model.cache is None or model.cache[0].shape[3] != capacity:
      model.cache = [Tensor.zeros(2,1,8,capacity,128,dtype=model.dtype).realize()
                     for _ in range(model.config['vlm_config']['text_config']['num_hidden_layers'])]
      model.prefill_jit.reset()
      model.decode_jit.reset()
      model.trajectory_jits.clear()
      self.reset()
    shape = (x.shape,cos.shape,capacity)
    if self.shape != shape:
      self.reset()
      self.shape = shape
    model.prompt_length = x.shape[1]

  def reset(self):
    self.shape = None


class SpeculativePrefill(PaddedPrefill):
  """Prefill that also verifies a draft placed in the padded rows after the prompt.

  With H heads, H-1 draft tokens are placed and head i holds the target after draft token i-1 (head 0 follows the
  prompt). The decoder accepts the matching draft prefix, whose KV rows this prefill wrote, and continues from the
  first differing head. Prompts up to 2081 tokens fit 32 heads (31 draft tokens); the frontend caps navigation text.
  """
  HEADS = 32

  def __init__(self, model):
    super().__init__(model)
    self.jits = {}
    self.part_jits = {}
    self.last_targets = self.last_prompt = self.last_logits = None
    self.heads = 0

  def part_language(self, x, cos, sin, start):
    model = self.model
    for i in range(model.config['vlm_config']['text_config']['num_hidden_layers']):
      x = model.text_layer(x,cos,sin,f'vlm.model.language_model.layers.{i}',model.cache[i],None,cache_pos=start)
    return x  # only the KV rows it wrote are used

  @staticmethod
  def rows(t, start, end, axis=-2):
    # A row slice of a contiguous buffer can realize as a view of that buffer, which a JIT cannot take as an input.
    # Copy it into its own buffer.
    shape,index = list(t.shape),[slice(None)]*t.ndim
    shape[axis],index[axis] = end-start,slice(start,end)
    return Tensor.empty(*shape,dtype=t.dtype,device=t.device).assign(t[tuple(index)]).realize()

  def part_rows(self, part, x, cos, sin, x_axis=-2):
    """Copies of one part's rows of x (embedding rows, or token ids with x_axis=-1), cos and sin, as a captured graph.

    Scheduling the copies outside a graph costs 50-100 ms of host time each on the Dragon. The outputs are the graph's
    reused buffers: they hold this call's rows until the next call with the same shapes.
    """
    start,end = PREFILL_SPLITS[part:part+2]
    key = ('rows',part,x_axis,x.shape,x.dtype,cos.shape)
    if key not in self.part_jits:
      from .graph_cache import CachedJit
      self.part_jits[key] = CachedJit(lambda x,c,s: (self.rows(x,start,end,x_axis),self.rows(c,start,end),self.rows(s,start,end)),
                                      f'prefill-rows-{key}')
    return self.part_jits[key](x,cos,sin)

  def part(self, part, x, cos, sin):
    """Prefill one early part of the prompt into the KV cache. Earlier parts must already be in the cache."""
    start,end = PREFILL_SPLITS[part:part+2]
    assert part < len(PREFILL_SPLITS)-1 and x.shape == (1,end-start,2048)
    assert self.model.cache is not None and self.model.cache[0].shape[3] == 2304
    key = (part,x.shape,cos.shape)
    if key not in self.part_jits:
      from .graph_cache import CachedJit
      self.part_jits[key] = CachedJit(lambda x,c,s: self.part_language(x,c,s,start),f'prefill-part-{key}')
    self.part_jits[key](x,cos,sin)

  def language(self, x, cos, sin, length, heads):
    # The last part attends to the KV rows that the earlier parts wrote.
    model,start = self.model,PREFILL_SPLITS[-1]
    x,cos,sin = x[:,start:],cos[:,:,start:],sin[:,:,start:]
    for i in range(model.config['vlm_config']['text_config']['num_hidden_layers']):
      x = model.text_layer(x,cos,sin,f'vlm.model.language_model.layers.{i}',model.cache[i],None,cache_pos=start)
    rows = []
    for index in range(heads):
      hidden = model.norm(x[:,length-1+index-start:length+index-start],'vlm.model.language_model.norm',rms=True)
      rows.append(model.linear(hidden,'vlm.lm_head').realize())
    logits = Tensor.cat(*rows,dim=1).contiguous().realize()
    # One batched argmax and finiteness check. Per-head reductions fused into one serial 2.6 ms kernel.
    table = logits.reshape(heads,-1)
    targets = model.output_token_mapping[table.argmax(axis=1)]
    checks = table.isfinite().all(axis=1).cast(dtypes.int32)
    return rows[0],logits,Tensor.cat(targets,checks).contiguous().realize()

  def __call__(self, x, cos, sin, max_tokens, length):
    from .policy import PromptTooLong
    self.last_targets = self.last_logits = None
    self.last_prompt = int(length)
    heads = self.HEADS
    if length+heads-1 > x.shape[1] or max_tokens < heads:
      raise PromptTooLong(f'Prompt uses {length} tokens; the draft prefill holds {x.shape[1]-heads+1}')
    self.allocate(x,cos,max_tokens)
    key = (heads,self.shape)
    if key not in self.jits:
      from .graph_cache import CachedJit
      self.jits[key] = CachedJit(lambda x,c,s,n: self.language(x,c,s,n,heads),f'prefill-{heads}-{self.shape}')
    if length <= PREFILL_SPLITS[-1]:
      raise PromptTooLong(f'Prompt uses {length} tokens; the split prefill needs more than {PREFILL_SPLITS[-1]}')
    valid = UOp.variable(f'valid_prefill_heads{heads}_length',PREFILL_SPLITS[-1]+1,x.shape[1]-heads+1).bind(length)
    first_logits,self.last_logits,self.last_targets = self.jits[key](x,cos,sin,valid)
    self.heads = heads
    return first_logits

  def reset(self):
    super().reset()
    self.jits.clear()
    self.part_jits.clear()
    self.last_targets = self.last_prompt = self.last_logits = None
