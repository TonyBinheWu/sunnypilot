"""Display-only, offline OPUS-MT English to Chinese translation."""
from functools import lru_cache
import os
import sys
import time


class ChineseTranslator:
  def __init__(self, root):
    import ctranslate2
    import sentencepiece
    from opencc import OpenCC
    self.source = sentencepiece.SentencePieceProcessor(model_file=str(root/'source.spm'))
    self.target = sentencepiece.SentencePieceProcessor(model_file=str(root/'target.spm'))
    self.model = ctranslate2.Translator(str(root), device='cpu', compute_type='int8', inter_threads=1, intra_threads=1)
    self.to_traditional = OpenCC('s2twp')

  @lru_cache(maxsize=128)
  def translate(self, text):
    pieces = self.source.encode(text, out_type=str)
    result, = self.model.translate_batch([pieces + ['</s>']], beam_size=2, max_decoding_length=160)
    simplified = self.target.decode(result.hypotheses[0]).strip()
    return simplified, self.to_traditional.convert(simplified)


def main():
  from openpilot.cereal import messaging
  from openpilot.selfdrive.alpamayo.install import ROOT
  from openpilot.selfdrive.alpamayo.planner import MAX_PLAN_AGE
  os.nice(10)
  little = os.sched_getaffinity(0).intersection(range(4))
  if little:
    os.sched_setaffinity(0, little)
  root = ROOT/'subtitles'
  sys.path.insert(0, str(root/'packages'))
  sm = messaging.SubMaster(['alpamayoPlan'], poll='alpamayoPlan')
  pm = messaging.PubMaster(['alpamayoSubtitle'])
  translator = None
  while True:
    sm.update(1000)
    plan = sm['alpamayoPlan']
    if not sm.updated['alpamayoPlan'] or not sm.valid['alpamayoPlan'] or not 0 <= time.monotonic_ns()-plan.queryMonoTime < MAX_PLAN_AGE:
      continue
    raw = plan.reasoning.strip()[:512]
    if not raw or raw == '<NOMINAL>':
      continue  # The HUD can render this explicit model tag immediately.
    if translator is None:
      translator = ChineseTranslator(root)
    simplified, traditional = translator.translate(raw)
    msg = messaging.new_message('alpamayoSubtitle', valid=True)
    msg.alpamayoSubtitle = dict(queryMonoTime=plan.queryMonoTime, original=raw, simplified=simplified, traditional=traditional)
    pm.send('alpamayoSubtitle', msg)


if __name__ == '__main__':
  main()
