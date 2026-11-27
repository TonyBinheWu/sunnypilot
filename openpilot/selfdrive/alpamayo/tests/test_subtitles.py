import pytest

from openpilot.cereal import log
from openpilot.selfdrive.ui.alpamayo_caption import caption, render_caption

NOW = 6_000_000_000


class Messages(dict):
  def __init__(self):
    super().__init__(modelV2=log.ModelDataV2.new_message(alpamayoQueryMonoTime=NOW-100_000_000,
                                                        alpamayoReasoning='Do not turn left.'),
                     alpamayoSubtitle=log.Event.new_message().init('alpamayoSubtitle'))
    self.valid = dict.fromkeys(self, True)
    self.recv_frame = dict.fromkeys(self, 15)
    self.logMonoTime = dict.fromkeys(self, NOW)
    sub = self['alpamayoSubtitle']
    sub.queryMonoTime = self['modelV2'].alpamayoQueryMonoTime
    sub.original, sub.simplified, sub.traditional = 'Do not turn left.', '不要左转。', '不要左轉。'


@pytest.mark.parametrize('language,expected', [('zh-CHT','不要左轉。'), ('main_zh-CHS','不要左转。'), ('en','Do not turn left.')])
def test_current_plan_caption(language, expected):
  assert caption(Messages(), NOW, language, 12) == expected


@pytest.mark.parametrize('reason', ['fallback', 'stale_plan', 'future_plan', 'stale_model', 'invalid_model', 'prior_drive', 'empty'])
def test_clear_caption(reason):
  sm = Messages()
  if reason == 'fallback': sm['modelV2'].alpamayoQueryMonoTime = 0
  elif reason == 'stale_plan': sm['modelV2'].alpamayoQueryMonoTime = NOW-1_500_000_000
  elif reason == 'future_plan': sm['modelV2'].alpamayoQueryMonoTime = NOW+1
  elif reason == 'stale_model': sm.logMonoTime['modelV2'] = NOW-250_000_000
  elif reason == 'invalid_model': sm.valid['modelV2'] = False
  elif reason == 'prior_drive': sm.recv_frame['modelV2'] = 11
  else: sm['modelV2'].alpamayoReasoning = ''
  assert caption(sm, NOW, 'zh-CHT', 12) is None


@pytest.mark.parametrize('reason', ['different_text', 'later_query', 'older_drive', 'missing'])
def test_translation_falls_back_to_current_original(reason):
  sm = Messages()
  if reason == 'different_text': sm['alpamayoSubtitle'].original = 'Turn left.'
  elif reason == 'later_query': sm['alpamayoSubtitle'].queryMonoTime = NOW
  elif reason == 'older_drive': sm.recv_frame['alpamayoSubtitle'] = 0
  else: sm.valid['alpamayoSubtitle'] = False
  assert caption(sm, NOW, 'zh-CHT', 12) == 'Do not turn left.'


def test_nominal_tag():
  sm = Messages()
  sm['modelV2'].alpamayoReasoning = '<NOMINAL>'
  assert caption(sm, NOW, 'zh-CHT', 12) == '一般行駛'


@pytest.mark.parametrize('width,size', [(294, 14), (1188, 30)])
def test_short_caption_hugs_text_and_long_caption_uses_two_lines(width, size):
  short = render_caption('準備右轉', width, size)
  long = render_caption('等待行人穿越馬路。'*20, width, size)
  assert short.width < width//3 and short.height <= 2*size
  assert short.convert('L').getextrema()[1] > 220
  assert short.width < long.width <= width
  assert short.height < long.height <= 2*short.height
  assert long.crop((0, short.height, long.width, long.height)).convert('L').getextrema()[1] > 220
