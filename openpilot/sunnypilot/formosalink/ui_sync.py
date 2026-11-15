"""Refresh existing native control caches after acknowledged remote writes."""
import time

_next_poll = 0.0
_version = None


def refresh_controls(roots):
  from openpilot.system.ui.widgets import Widget
  from openpilot.system.ui.sunnypilot.widgets.toggle import ToggleSP
  from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP
  from openpilot.system.ui.sunnypilot.widgets.list_view import MultipleButtonActionSP
  from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, BigCircleParamControl, BigMultiParamToggle
  pending, seen = list(roots), set()
  while pending and len(seen)<5000:
    node = pending.pop()
    if id(node) in seen:
      continue
    seen.add(id(node))
    if isinstance(node,dict):
      pending.extend(node.values())
    elif isinstance(node,(list,tuple)):
      pending.extend(node)
    elif isinstance(node,Widget):
      try:
        if isinstance(node,ToggleSP) and node.param_key:
          node.set_state(node.params.get_bool(node.param_key))
        elif isinstance(node,OptionControlSP):
          value = node.params.get(node.param_key,return_default=True)
          if node.value_map:
            node.current_value = next((int(k) for k,v in node.value_map.items() if v==value),node.current_value)
          else:
            node.current_value = int(round(float(value)*100)) if node.use_float_scaling else int(value)
        elif isinstance(node,MultipleButtonActionSP) and node.param_key:
          value = int(node.params.get(node.param_key,return_default=True))
          if 0<=value<len(node.buttons):
            node.selected_button = value
        elif isinstance(node,(BigParamControl,BigCircleParamControl)):
          node.refresh()
        elif isinstance(node,BigMultiParamToggle):
          node._load_value()
      except (ValueError,TypeError,KeyError,IndexError,OSError):
        pass
      pending.extend(vars(node).values())
    elif type(node).__name__ == "PanelInfo" and hasattr(node,"instance"):
      pending.append(node.instance)


def tick():
  global _next_poll, _version
  now = time.monotonic()
  if now<_next_poll:
    return
  _next_poll = now+.5
  from openpilot.selfdrive.ui.ui_state import ui_state
  from openpilot.system.ui.lib.application import gui_app
  if not ui_state.is_offroad() or not ui_state.params.get_bool("FormosaLinkEnabled"):
    return
  version = ui_state.params.get("FormosaLinkSettingsVersion")
  if version != _version:
    _version = version
    refresh_controls(gui_app._nav_stack)
