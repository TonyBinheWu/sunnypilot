from openpilot.selfdrive.carrot.server.services import web_settings


def test_road_models_are_separate_opt_in_and_preserve_existing_preferences():
  settings = web_settings.sanitize_web_settings({"vision_object_detection": True, "vision_presentation": "bev"})
  assert settings["vision_road_detection"] is False
  assert settings["vision_object_detection"] is True
  assert settings["vision_presentation"] == "bev"
  enabled = web_settings.sanitize_web_settings({**settings, "vision_road_detection": "true"})
  assert enabled["vision_road_detection"] is True
  assert enabled["vision_presentation"] == "bev"
  spec = {field["key"]: field for field in web_settings.web_settings_client_spec()}
  assert spec["vision_road_detection"]["type"] == "bool"
  assert spec["vision_road_detection"]["default"] is False
