from openpilot.selfdrive.carrot.server.services import web_settings


def test_existing_clients_keep_existing_display_defaults():
  settings = web_settings.sanitize_web_settings({})
  assert settings['web_text_scale'] == '100'
  assert settings['vision_stream_resolution'] == 'standard'
  assert settings['vision_render_quality'] == 'auto'


def test_display_choices_are_validated_and_persist_independently(tmp_path, monkeypatch):
  monkeypatch.setattr(web_settings, 'CARROT_WEB_SETTINGS_PATH', str(tmp_path / 'web_settings.json'))
  web_settings.update_web_settings({'web_text_scale': '150', 'vision_stream_resolution': '360', 'vision_render_quality': 'high'})
  settings = web_settings.read_web_settings()
  assert settings['web_text_scale'] == '150'
  assert settings['vision_stream_resolution'] == '360'
  assert settings['vision_render_quality'] == 'high'
  web_settings.update_web_settings({'web_text_scale': '9999', 'vision_stream_resolution': '../1080', 'vision_render_quality': 'bad'})
  settings = web_settings.read_web_settings()
  assert settings['web_text_scale'] == '100'
  assert settings['vision_stream_resolution'] == 'standard'
  assert settings['vision_render_quality'] == 'auto'


def test_tesla_view_and_recording_quota_defaults_and_validation():
  import json
  settings = web_settings.sanitize_web_settings({})
  assert settings['vision_presentation'] == 'carrot'
  assert settings['vision_custom_metrics'] is False and settings['vision_rainbow_lane'] is False
  assert settings['recording_quota_percent'] == '0'
  settings = web_settings.sanitize_web_settings({'vision_presentation': 'tesla', 'recording_quota_percent': '50',
    'vision_metric_layout': '{"speed":[9,-2,99],"limit":[true,0,1],"extra":"ignored"}'})
  assert settings['vision_presentation'] == 'tesla' and settings['recording_quota_percent'] == '50'
  layout = json.loads(settings['vision_metric_layout'])
  assert layout['speed'] == [1,0,2.2] and set(layout) == {'speed','limit','set'}
  assert layout['limit'] == [.04,.43,1.]
  assert web_settings.sanitize_web_settings({'recording_quota_percent': '100'})['recording_quota_percent'] == '0'
