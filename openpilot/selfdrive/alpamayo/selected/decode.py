"""Target-verified decoding: prefill-head draft check, lookup verification, block-six serial fallback."""
from functools import partial
import math
import numpy as np
from tinygrad import Tensor, dtypes
from tinygrad.uop.ops import UOp
from .graph_cache import CachedJit
from .policy import accepted_prefix, validate_draft
from .transport import download
from .serial_coordinates import block_six


class Decoder:
  def __init__(self, model, draft, anchor):
    self.model = model
    self.draft,self.anchor = validate_draft(draft,anchor),anchor
    self.history,self.statistics = [],{}
    self.jits,self.verifiers,self.select_jits,self.proposals = {},{},{},{}
    self.choose_jit = CachedJit(lambda logits: model.output_token_mapping[logits.reshape(-1).argmax()].float().realize(),'choose')

  def reset(self):
    self.history.clear()
    self.statistics = {}
    self.jits.clear()
    self.verifiers.clear()
    self.select_jits.clear()
    self.choose_jit.reset()

  def first_token(self, logits):
    return int(download(self.choose_jit(logits)).item())

  def select_logits(self, logits, index):
    count = logits.shape[1]
    if count not in self.select_jits:
      self.select_jits[count] = CachedJit(lambda values,row: values[:,row:row+1].clone().realize(),f'select-{count}')
    row = UOp.variable('selected_draft_row',0,count-1).bind(index)
    return self.select_jits[count](logits,row)

  def decode(self, logits, cos, sin, position, step, count):
    key = (cos.shape,count,self.model.cache[0].shape[3])
    if key not in self.jits:
      if (count == 6 and self.model.amd and not self.model.images and len(self.model.cache) == 28
          and self.model.cache[0].shape == (2,1,8,2304,128) and cos.shape == sin.shape == (1,1,64,128)
          and logits.shape == (1,1,2112)):
        self.jits[key] = CachedJit(partial(block_six,self.model),f'block6-{key}')
      else:
        def run(logits, c, s, pos, offset):
          tokens = []
          for i in range(count):
            logits,token = self.model._greedy_decode(logits,c,s,pos+i,offset+i)
            tokens.append(token.reshape(1))
          return logits,Tensor.cat(*tokens).realize()
        self.jits[key] = CachedJit(run,f'decode-{key}')
    position = UOp.variable('block_position',0,self.model.cache[0].shape[3]-count).bind(position)
    step = UOp.variable('block_step',0,cos.shape[2]-count).bind(step)
    return self.jits[key](logits,cos,sin,position,step)

  def proposal(self, values, device):
    """Write a draft into a persistent CPU buffer. The verifier graph copies it to the GPU itself.

    A fresh Tensor(...).to(device) per round costs 20-60 ms of host scheduling on the Dragon; this costs a memcpy.
    """
    count = len(values)
    if count not in self.proposals:
      buffer = Tensor.empty(count,dtype=dtypes.int32,device='CPU').realize()
      self.proposals[count] = buffer,np.frombuffer(buffer._buffer().as_memoryview(allow_zero_copy=True),dtype=np.int32)
    buffer,view = self.proposals[count]
    view[:] = values
    return buffer

  def verify(self, token_ids, cos, sin, position, step):
    model = self.model
    count = token_ids.shape[0]
    if token_ids.device != model.cache[0].device:
      token_ids = token_ids.to(model.cache[0].device)
    x = model.weights['vlm.model.language_model.embed_tokens.weight'][token_ids].reshape(1,count,-1)
    c,s = cos[:,:,step:step+count],sin[:,:,step:step+count]
    mask = (Tensor.arange(model.cache[0].shape[3]).reshape(1,-1) > (Tensor.arange(count)+position).reshape(-1,1)).where(-math.inf,0)
    with model.verification():
      for i in range(model.config['vlm_config']['text_config']['num_hidden_layers']):
        x = model.text_layer(x,c,s,f'vlm.model.language_model.layers.{i}',model.cache[i],mask,cache_pos=position)
      logits = model.linear(model.norm(x,'vlm.model.language_model.norm',rms=True),'vlm.lm_head').realize()
    tokens = model.output_token_mapping[logits.argmax(axis=-1)].realize()
    return logits,tokens

  def continuation(self, context, limit):
    # Consecutive slots usually repeat a recent text. An identical prefix aligns the draft at its true position;
    # suffix matching alone can align a repeated token at a later occurrence and cost extra verification rounds.
    for previous in reversed(self.history):
      if len(previous) > len(context) and previous[:len(context)] == context:
        return previous[len(context):len(context)+limit]
    for width in range(min(8,len(context)),0,-1):
      suffix = context[-width:]
      for previous in reversed(self.history):
        for end in range(len(previous)-1,width-1,-1):
          if previous[end-width:end] == suffix:
            return previous[end:end+limit]
    return []

  def prefill_draft(self):
    """Tokens to verify inside the prefill: the latest generated text (consecutive slots usually repeat it)."""
    return tuple(self.history[-1]) if self.history else self.draft

  def generate_lookup(self, logits, dc, ds, prompt, max_tokens, next_token=None, generated=None, pending_logits=None):
    model = self.model
    generated = [] if generated is None else list(generated)
    stats = {'lookup_rounds':0,'verified_tokens':0,'serial_tokens':0}
    while len(generated) < max_tokens:
      offset = len(generated)
      remaining = max_tokens-offset
      proposed = []
      if self.history and remaining >= 16:
        first = self.first_token(logits) if next_token is None else next_token
        # At most 32 rows per check: only two verifier widths exist, and both are compiled during warmup.
        proposed = [first]+self.continuation(generated+[first],min(32,remaining)-1)
      # The serial block chooses its own first token. Only a possible verifier call needs it on the host.
      next_token = None
      count = ((len(proposed)+15)//16)*16
      if len(proposed) <= 1 or count > remaining:
        if pending_logits is not None:
          logits = self.select_logits(*pending_logits)
          pending_logits = None
        logits,tokens = self.decode(logits,dc,ds,prompt+offset,offset,min(6,remaining))
        accepted = download(tokens).reshape(-1).astype(int).tolist()
        stats['serial_tokens'] += len(accepted)
      else:
        tokens = self.proposal(proposed+[proposed[-1]]*(count-len(proposed)),logits.device)
        pos = UOp.variable('draft_position',0,model.cache[0].shape[3]-count).bind(prompt+offset)
        step = UOp.variable('draft_step',0,dc.shape[2]-count).bind(offset)
        key = (count,dc.shape,model.cache[0].shape[3])
        if key not in self.verifiers:
          self.verifiers[key] = CachedJit(self.verify,f'verify-{key}')
        verified,predicted = self.verifiers[key](tokens,dc,ds,pos,step)
        choices = [first,*download(predicted).reshape(-1).astype(int).tolist()]
        accepted = []
        for candidate,choice in zip(proposed,choices,strict=False):
          if candidate != choice:
            break
          accepted.append(candidate)
          if candidate == self.anchor:
            break
        assert accepted
        if accepted[-1] != self.anchor:
          next_token = choices[len(accepted)]
          pending_logits = (verified,len(accepted)-1)
        stats['lookup_rounds'] += 1
        stats['verified_tokens'] += len(accepted)
      for token in accepted:
        generated.append(token)
        if token == self.anchor:
          self.remember(generated)
          self.statistics = stats
          return generated
    from .policy import NoTrajectoryAnchor
    raise NoTrajectoryAnchor(f'No trajectory anchor after {max_tokens} tokens')

  def remember(self, generated):
    self.history = [old for old in self.history if old != generated][-63:]+[list(generated)]

  def generate(self, prefill, logits, dc, ds, prompt, placed, max_tokens=64):
    if prefill.last_prompt != prompt:
      raise ValueError('Prefill used a stale actual prompt length')
    heads = prefill.heads
    record = {'heads':heads,'placed':len(placed),'accepted':0,'actual_prompt':prompt}
    if heads == 0 or prefill.last_targets is None:
      generated = self.generate_lookup(logits,dc,ds,prompt,max_tokens)
      self.statistics['prefill_draft'] = record
      return generated
    payload = download(prefill.last_targets).reshape(-1)
    if payload.shape != (2*heads,):
      raise ValueError('Incomplete target token and finiteness payload')
    targets,finite = payload[:heads].astype(np.int64),payload[heads:] == 1
    # A draft token is usable only where this prefill wrote its KV row (the placed tokens).
    accepted = accepted_prefix(targets,finite,placed[:heads],self.anchor)
    if len(accepted) == heads and accepted[-1] != self.anchor:
      accepted = accepted[:-1]  # keep one head for the next token
    record.update(accepted=len(accepted),all_targets_finite=bool(finite.all()))
    if accepted and accepted[-1] == self.anchor:
      self.remember(accepted)
      self.statistics = {'lookup_rounds':0,'verified_tokens':len(accepted),'serial_tokens':0,'prefill_draft':record}
      return accepted
    j = len(accepted)
    first = int(targets[j]) if finite[j] else None  # the prefill already read back the argmax of these exact logits
    pending = (prefill.last_logits,j) if j else None
    if pending is not None and first is None:
      logits,pending = self.select_logits(*pending),None
    generated = self.generate_lookup(logits,dc,ds,prompt,max_tokens,first,accepted,pending)
    self.statistics['prefill_draft'] = record
    return generated
