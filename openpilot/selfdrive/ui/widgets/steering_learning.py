"""Shared read-only learner view for C3/C3X and C4 device menus."""
import html
import time

from openpilot.common.steering_learning import LearningReader
from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

TITLE = 'Steering learning progress'
SOURCE = {'live': 'Live data', 'stale': 'Data expired (last received)',
          'cached': 'Last saved record (not live)', 'unavailable': 'No learning data available'}
STATUS = {'valid': 'Verified', 'learning': 'Collecting data', 'invalid': 'Estimate not verified',
          'unsupported': 'Live torque tuning is not used', 'unavailable': 'Waiting for data'}


def value(number, digits=0):
  return f'{number:.{digits}f}' if number is not None else '—'


def learning_html(snapshot):
  def text(s):
    return html.escape(tr(s))
  parts = [f'<h2>{text(TITLE)}</h2>']
  for key, title in [('delay', 'Steering delay learning'), ('torque', 'Steering torque learning')]:
    state = snapshot[key]
    parts.extend([f'<h3>{text(title)}</h3>', f'<p>{text(SOURCE.get(state["source"], SOURCE["unavailable"]))}</p>',
                  f'<p>{text("Data progress")}: {value(state["progress"]) + "%" if state["progress"] is not None else "—"} · {text(STATUS.get(state["status"], STATUS["unavailable"]))}</p>'])
    if state['source'] == 'unavailable':
      continue
    if state['custom']:
      parts.append(f'<p>{text("Custom tuning is active; learned values do not override it.")}</p>')
    if key == 'delay':
      parts.append(f'<p>{text("Selected delay")}: {value(state.get("applied"), 3)} s<br/>'
                   f'{text("Candidate delay")}: {value(state.get("estimate"), 3)} s<br/>'
                   f'{text("Valid data blocks")}: {value(state.get("blocks"))}</p>')
    else:
      parts.append(f'<p>{text("Selected acceleration factor")}: {value(state.get("factor"), 3)}<br/>'
                   f'{text("Selected friction compensation")}: {value(state.get("friction"), 4)}<br/>'
                   f'{text("Collected samples")}: {value(state.get("samples"))}</p>')
  parts.append(f'<p>{text("Progress measures data coverage, not driving time. Similar straight-road samples may not advance it. This view does not reset or change tuning.")}</p>')
  return ''.join(parts)


class LearningDialog(ConfirmDialog):
  def __init__(self):
    self._learning_reader = LearningReader(Params())
    self._next_learning_update = 0.
    self._learning_html = ''
    super().__init__('', tr('Close'), cancel_text='', rich=True)

  def _update_state(self):
    super()._update_state()
    if time.monotonic() >= self._next_learning_update:
      self._next_learning_update = time.monotonic() + .5
      content = learning_html(self._learning_reader.snapshot(ui_state.sm))
      if content != self._learning_html:
        self._learning_html = content
        self.set_text(content)


def learning_item():
  from openpilot.system.ui.widgets.list_view import button_item
  return button_item(lambda: tr(TITLE), lambda: tr('VIEW'), callback=lambda: gui_app.push_widget(LearningDialog()))


def learning_big_button():
  from openpilot.selfdrive.ui.mici.widgets.button import BigButton
  button = BigButton(tr('steering\nlearning'), '', gui_app.texture('icons_mici/settings/device/info.png', 64, 64))
  button.set_click_callback(lambda: gui_app.push_widget(LearningDialog()))
  return button
