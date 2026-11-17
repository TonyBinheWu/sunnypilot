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
  low = snapshot.get('lowSpeed') or {'source': 'unavailable'}
  parts.extend([f'<h3>{text("Low-speed demand follow · observed response")}</h3>',
                f'<p>{text(SOURCE.get(low["source"], SOURCE["unavailable"]))}</p>'])
  reasons = {
    'off': 'Mode disabled', 'inactive': 'Lateral control inactive', 'can': 'CAN unavailable', 'fault': 'Steering fault',
    'driver': 'Driver takeover', 'stationary': 'Stationary', 'gear': 'Not in Drive',
    'factory': 'Factory limit at 40 km/h or above', 'model': 'Model data missing or expired',
    'invalid': 'Invalid data or configuration', 'demand': 'Within baseline demand',
    'qualifying': 'Confirming sustained demand (0.30 s)', 'following': 'Following demand within limits',
    'taper': '30–40 km/h taper', 'ceiling': 'Demand exceeds available software ceiling',
    'request_cut': 'Existing steering request inhibition', 'rate_or_yield': 'Command rate limit or steering yield',
  }
  if isinstance(low.get('enabled'), bool):
    parts.append(f'<p>{text("Enabled" if low["enabled"] else "Disabled")}</p>')
  current = low.get('current')
  if current:
    parts.append(f'<p>{text("Current restriction / phase")}: {text(reasons.get(current.get("reason"), reasons["invalid"]))}</p>')
    for label, a, b, unit in [('Requested / sent torque command', 'requested', 'command', ''),
                             ('Target / measured steering angle', 'targetAngle', 'angle', '°'),
                             ('Factory baseline / available ceiling', 'base', 'ceiling', ''),
                             ('Command increase / decrease per 10 ms', 'up', 'down', '')]:
      parts.append(f'<p>{text(label)}: {value(current.get(a), 1)} / {value(current.get(b), 1)} {unit}</p>')
    parts.append(f'<p>{text("Measured steering angle rate")}: {value(current.get("angleRate"), 1)} °/s</p>')
  stats = low.get('stats')
  if stats:
    parts.append(f'<p>{text("Samples (not learning progress)")}: {value(stats["samples"])}</p>')
    for side, title in [('left', 'Left-command observed peaks'), ('right', 'Right-command observed peaks')]:
      peak = stats[side]
      parts.append(f'<p>{text(title)}: {value(peak["command"])} / {value(peak["angle"], 1)} ° / {value(peak["angleRate"], 1)} °/s</p>')
    parts.append(f'<p>{text("Command / angle / angle rate")}</p>')
  parts.append(f'<p>{text("Hyundai/Kia CAN-FD torque control only. Command units are not Nm; up/down is CAN units per 10 ms. Observed peaks are not hardware limits and never increase control limits. No physical limit probing.")}</p>')
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


def learning_mici_dialog():
  # Mici is 536x240: the tici ConfirmDialog's 100px margins and 160px
  # action button cannot fit. Use its native full-page scroll/back navigation.
  import pyray as rl
  from openpilot.system.ui.widgets.scroller import NavRawScrollPanel
  from openpilot.system.ui.widgets.html_render import HtmlRenderer, ElementType

  class MiciLearningPanel(NavRawScrollPanel):
    def __init__(self):
      super().__init__()
      self._reader = LearningReader(Params())
      self._next_update = 0.
      self._last_html = ''
      self._content = HtmlRenderer(text='', text_size={ElementType.P: 24})

    def _update_state(self):
      super()._update_state()
      if time.monotonic() >= self._next_update:
        self._next_update = time.monotonic() + .5
        content = learning_html(self._reader.snapshot(ui_state.sm))
        if content != self._last_html:
          self._last_html = content
          self._content.parse_html_content(content)

    def _render(self, rect):
      viewport = rl.Rectangle(rect.x + 12, rect.y + 8, max(1, rect.width - 24), max(1, rect.height - 16))
      height = self._content.get_total_height(int(viewport.width))
      offset = self._scroll_panel.update(viewport, height)
      content_rect = rl.Rectangle(viewport.x, viewport.y + round(offset), viewport.width, height)
      rl.begin_scissor_mode(int(viewport.x), int(viewport.y), int(viewport.width), int(viewport.height))
      try:
        self._content.render(content_rect)
      finally:
        rl.end_scissor_mode()

  return MiciLearningPanel()


def learning_big_button():
  from openpilot.selfdrive.ui.mici.widgets.button import BigButton
  button = BigButton(tr('steering\nlearning'), '', gui_app.texture('icons_mici/settings/device/info.png', 64, 64))
  button.set_click_callback(lambda: gui_app.push_widget(learning_mici_dialog()))
  return button
