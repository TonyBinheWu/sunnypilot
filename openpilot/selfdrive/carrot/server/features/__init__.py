from aiohttp import web

from . import (
  assistant_connection,
  assistant_drive,
  assistant_settings,
  assistant_tools,
  bluetooth,
  carrot_navi,
  cars,
  dashcam,
  egpu_model,
  environment_model,
  intro,
  mapbox_tokens,
  navigation,
  params,
  screenrecord,
  settings,
  setting_favorites,
  setting_popular_values,
  setting_profiles,
  ssh_keys,
  static,
  stream,
  support_terminal,
  system,
  terminal,
  tools,
  vision_diag,
  vision_test,
  web_sound,
  web_settings,
  ws,
  xiaoge,
)


def register_all(app: web.Application) -> None:
  from . import parking_scene
  parking_scene.register(app)
  environment_model.register(app)
  from . import training_data
  training_data.register(app)
  from . import road_scenes
  road_scenes.register(app)
  from . import lane_mapping
  lane_mapping.register(app)
  from . import self_diagnostics
  self_diagnostics.register(app)
  from . import steering_learning
  steering_learning.register(app)
  from . import forced_offroad
  forced_offroad.register(app)
  assistant_connection.register(app)
  assistant_drive.register(app)
  assistant_settings.register(app)
  assistant_tools.register(app)
  bluetooth.register(app)
  static.register(app)
  intro.register(app)
  carrot_navi.register(app)
  stream.register(app)
  support_terminal.register(app)
  ws.register(app)
  settings.register(app)
  params.register(app)
  setting_favorites.register(app)
  setting_popular_values.register(app)
  setting_profiles.register(app)
  web_settings.register(app)
  ssh_keys.register(app)
  cars.register(app)
  system.register(app)
  terminal.register(app)
  dashcam.register(app)
  egpu_model.register(app)
  screenrecord.register(app)
  tools.register(app)
  xiaoge.register(app)
  mapbox_tokens.register(app)
  navigation.register(app)
  vision_test.register(app)
  vision_diag.register(app)
  web_sound.register(app)
