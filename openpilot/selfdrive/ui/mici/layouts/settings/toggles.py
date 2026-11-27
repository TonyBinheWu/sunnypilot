from openpilot.system.ui.lib.multilang import tr
from openpilot.cereal import log

from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, BigMultiParamToggle, BigMultiToggle, BigToggle
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog
from openpilot.system.ui.lib.application import gui_app
from openpilot.selfdrive.ui.layouts.settings.common import restart_needed_callback, set_openpilot_enabled
from openpilot.selfdrive.ui.ui_state import ui_state

PERSONALITY_TO_INT = log.LongitudinalPersonality.schema.enumerants


class TogglesLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    self._personality_toggle = BigMultiParamToggle(tr("driving personality"), "LongitudinalPersonality",
                                                 [tr("aggressive"), tr("standard"), tr("relaxed"), tr("moreRelaxed")])
    self._experimental_btn = BigParamControl(tr("experimental mode"), "ExperimentalMode")
    is_metric_toggle = BigParamControl(tr("use metric units"), "IsMetric")
    rainbow_toggle = BigParamControl(tr("Rainbow Road (SP style)"), "RainbowMode")
    ldw_toggle = BigParamControl(tr("lane departure warnings"), "IsLdwEnabled")
    always_on_dm_toggle = BigParamControl(tr("always-on driver monitor"), "AlwaysOnDM")
    record_front = BigParamControl(tr("record & upload driver camera"), "RecordFront", toggle_callback=restart_needed_callback)
    record_mic = BigParamControl(tr("record & upload mic audio"), "RecordAudio", toggle_callback=restart_needed_callback)
    self._enable_openpilot = BigToggle(tr("enable openpilot"), "", toggle_callback=self._toggle_openpilot)

    self._scene_view = BigMultiToggle(tr("Driving view"), [tr("3D scene"), tr("Camera"), tr("3D model")],
                                     select_callback=lambda value: ui_state.params.put("DrivingSceneView", self._scene_view._options.index(value)))
    lane_center = BigParamControl(tr("Lane centering"), "SunnyLaneCenter")
    lane_turn = BigParamControl(tr("Low-speed signaled turns"), "SunnyLaneTurn")
    self._scroller.add_widgets([
      lane_center, lane_turn,
      self._scene_view,
      self._personality_toggle,
      self._experimental_btn,
      is_metric_toggle,
      rainbow_toggle,
      ldw_toggle,
      always_on_dm_toggle,
      record_front,
      record_mic,
      self._enable_openpilot,
    ])

    # Toggle lists
    self._refresh_toggles = (
      ("SunnyLaneCenter", lane_center), ("SunnyLaneTurn", lane_turn),
      ("ExperimentalMode", self._experimental_btn),
      ("IsMetric", is_metric_toggle),
      ("RainbowMode", rainbow_toggle),
      ("IsLdwEnabled", ldw_toggle),
      ("AlwaysOnDM", always_on_dm_toggle),
      ("RecordFront", record_front),
      ("RecordAudio", record_mic),
      ("OpenpilotEnabledToggle", self._enable_openpilot),
    )

    self._enable_openpilot.set_enabled(lambda: not ui_state.engaged)
    record_front.set_enabled(False if ui_state.params.get_bool("RecordFrontLock") else (lambda: not ui_state.engaged))
    record_mic.set_enabled(lambda: not ui_state.engaged)

    if ui_state.params.get_bool("ShowDebugInfo"):
      gui_app.set_show_touches(True)
      gui_app.set_show_fps(True)

    ui_state.add_engaged_transition_callback(self._update_toggles)

  def _toggle_openpilot(self, enabled: bool):
    current = ui_state.params.get_bool("OpenpilotEnabledToggle")
    self._enable_openpilot.set_checked(current)
    if ui_state.engaged or enabled == current:
      return
    if enabled:
      self._enable_openpilot.set_checked(set_openpilot_enabled(True))
    else:
      icon = gui_app.texture("icons_mici/settings/device/power.png", 64, 64)
      gui_app.push_widget(BigConfirmationDialog(tr("Slide to turn off openpilot"), icon,
                                                lambda: self._enable_openpilot.set_checked(set_openpilot_enabled(False)), red=True))

  def _update_state(self):
    super()._update_state()

    if ui_state.sm.updated["selfdriveState"]:
      personality = PERSONALITY_TO_INT[ui_state.sm["selfdriveState"].personality]
      if personality != ui_state.personality and ui_state.started:
        self._personality_toggle.set_value(self._personality_toggle._options[personality])
      ui_state.personality = personality

  def show_event(self):
    super().show_event()
    self._update_toggles()

  def _update_toggles(self):
    ui_state.update_params()
    self._scene_view.set_value(self._scene_view._options[max(0, ui_state.driving_scene_view)])

    # CP gating for experimental mode
    if ui_state.CP is not None:
      if ui_state.has_longitudinal_control:
        self._experimental_btn.set_visible(True)
        self._personality_toggle.set_visible(True)
      else:
        # no long for now
        self._experimental_btn.set_visible(False)
        self._experimental_btn.set_checked(False)
        #self._personality_toggle.set_visible(False)
        ui_state.params.remove("ExperimentalMode")

    # Refresh toggles from params to mirror external changes
    for key, item in self._refresh_toggles:
      item.set_checked(ui_state.params.get_bool(key))
