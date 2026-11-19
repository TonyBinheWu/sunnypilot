from openpilot.selfdrive.carrot.server.services import web_settings


def test_unconfigured_display_defaults():
  settings = web_settings.sanitize_web_settings({})
  assert settings['web_text_scale'] == '100'
  assert settings['vision_stream_resolution'] == 'standard'
  assert settings['vision_render_quality'] == 'auto'
  assert settings['vision_vehicle_color'] == 'red'
  assert web_settings.sanitize_web_settings({'vision_vehicle_color':'white'})['vision_vehicle_color'] == 'white'


def test_vehicle_paint_is_display_only_validated_and_persisted(tmp_path, monkeypatch):
  monkeypatch.setattr(web_settings,'CARROT_WEB_SETTINGS_PATH',str(tmp_path/'web_settings.json'))
  before=web_settings.sanitize_web_settings({})
  changed=web_settings.update_web_settings({'vision_vehicle_color':'blue'})
  assert web_settings.sanitize_web_settings({'vision_vehicle_color':'#A4B6C8'})['vision_vehicle_color']=='#a4b6c8'
  assert changed['vision_vehicle_color']=='blue'
  assert web_settings.read_web_settings()['vision_vehicle_color']=='blue'
  assert all(changed[key]==value for key,value in before.items() if key!='vision_vehicle_color')
  assert web_settings.sanitize_web_settings({'vision_vehicle_color':'url(https://bad)'})['vision_vehicle_color']=='red'


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
  assert settings['vision_presentation'] == 'tesla'
  assert settings['vision_custom_metrics'] is False and settings['vision_rainbow_lane'] is False
  assert settings['recording_quota_percent'] == '0'
  settings = web_settings.sanitize_web_settings({'vision_presentation': 'tesla', 'recording_quota_percent': '50',
    'vision_metric_layout': '{"speed":[9,-2,99],"limit":[true,0,1],"extra":"ignored"}'})
  assert settings['vision_presentation'] == 'tesla' and settings['recording_quota_percent'] == '50'
  layout = json.loads(settings['vision_metric_layout'])
  assert layout['speed'] == [1,0,2.2] and set(layout) == {'speed','limit','set'}
  assert layout['limit'] == [.04,.43,1.]
  assert web_settings.sanitize_web_settings({'recording_quota_percent': '100'})['recording_quota_percent'] == '0'


def test_bev_annotation_options_do_not_change_existing_presentation_or_driving_settings():
  settings=web_settings.sanitize_web_settings({})
  assert settings['vision_presentation']=='tesla'
  assert settings['vision_bev_range']=='50' and settings['vision_bev_grid'] is True
  enabled=web_settings.sanitize_web_settings({'vision_presentation':'bev','vision_bev_range':'30','vision_bev_details':False})
  assert enabled['vision_presentation']=='bev' and enabled['vision_bev_range']=='30'
  assert enabled['vision_bev_details'] is False
  assert web_settings.sanitize_web_settings({'vision_bev_range':'999'})['vision_bev_range']=='50'


def test_front_camera_recognition_is_opt_in_and_independent_of_vehicle_display_setting():
  defaults = web_settings.sanitize_web_settings({})
  assert defaults['vision_object_detection'] is False
  enabled = web_settings.sanitize_web_settings({'vision_object_detection': True, 'RainbowMode': True})
  assert enabled['vision_object_detection'] is True
  assert 'RainbowMode' not in enabled  # Native vehicle Params has its own setting API.
