"""Validate the shipped Traditional catalog without native device modules."""
import ast
from pathlib import Path
from string import Formatter
from types import SimpleNamespace

from openpilot.selfdrive.ui.translations.potools import extract_strings, parse_po

ROOT = Path(__file__).resolve().parents[4]
UI = ROOT / "openpilot/selfdrive/ui"


def test_marked_device_messages_have_complete_traditional_translations():
  _, entries = parse_po(UI / "translations/app_zh-CHT.po")
  translations = {entry.msgid: entry for entry in entries}
  files = [str(path.relative_to(ROOT)) for root in (UI, ROOT / "openpilot/system/ui")
           for path in root.rglob("*.py") if not {"tests", "translations"} & set(path.parts)]
  source = ast.parse((UI / "update_translations.py").read_text(encoding="utf-8"))
  config = next(node.value for node in source.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "ALERT_TRANSLATION_CALL_ARGS" for target in node.targets))
  messages = extract_strings(files, str(ROOT)) + extract_strings(
    ["openpilot/selfdrive/selfdrived/events.py"], str(ROOT), ast.literal_eval(config))
  for message in messages:
    assert message.msgid in translations, message.msgid
    entry = translations[message.msgid]
    values = list(entry.msgstr_plural.values()) if message.msgid_plural else [entry.msgstr]
    assert values and all(values), message.msgid
    fields = lambda text: sorted(field for _, field, _, _ in Formatter().parse(text) if field is not None)
    for value in values:
      assert fields(message.msgid) == fields(value), message.msgid


def test_network_choice_translation_keeps_callback_token():
  tree = ast.parse((UI / "mici/widgets/button.py").read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "BigMultiToggle")
  cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "set_value"]

  class Base:
    def set_value(self, value):
      self.value = value

  scope = {"BigToggle": Base, "tr": lambda value: {"metered": "按流量計費"}.get(value, value)}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), "button.py", "exec"), scope)
  widget = scope["BigMultiToggle"]()
  shown = []
  widget._sub_label = SimpleNamespace(set_text=shown.append)
  widget.set_value("metered")
  assert widget.value == "metered"
  assert shown == ["按流量計費"]


def test_updater_translation_keeps_raw_update_action():
  tree = ast.parse((UI / "mici/layouts/settings/device.py").read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "UpdateOpenpilotBigButton")
  cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "set_value"]

  class Base:
    def set_value(self, value):
      self.value = value

    def set_text(self, value):
      self.text = value

  scope = {"BigButton": Base, "tr": lambda value: {"update now": "立即更新"}.get(value, value)}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), "device.py", "exec"), scope)
  widget = scope["UpdateOpenpilotBigButton"]()
  shown = []
  widget._sub_label = SimpleNamespace(set_text=shown.append)
  widget.set_value("update now")
  assert widget.value == "update now"
  assert shown == ["立即更新"]


def test_recovery_traditional_does_not_import_native_params():
  path = ROOT / "openpilot/system/ui/startup_recovery.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "configure_language")
  scope = {"LABELS": {"idle": ("Korean", "Startup failed")}}
  exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), "exec"), scope)
  assert scope["configure_language"]("main_zh-CHT")
  assert scope["LABELS"]["idle"] == ("啟動失敗・等待更新", "Startup failed")
  assert scope["BUTTON_KO"] == "Git 更新並重新啟動"


def test_c4_language_selection_waits_for_offroad_and_never_reboots():
  tree = ast.parse((UI / "mici/layouts/settings/language.py").read_text(encoding="utf-8"))
  cls = next(node for node in tree.body if isinstance(node, ast.ClassDef))
  cls.body = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "_select"]
  parked = [False]
  writes, dialogs = [], []
  scope = {"NavScroller": object, "ui_state": SimpleNamespace(is_offroad=lambda: parked[0]),
           "gui_app": SimpleNamespace(push_widget=dialogs.append), "BigDialog": lambda *args: args,
           "tr": lambda value: value}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), "language.py", "exec"), scope)
  widget = scope["LanguageLayoutMici"]()
  widget._buttons = {"zh-CHT": object()}
  widget._params = SimpleNamespace(put=lambda *args: writes.append(args))
  widget.show_event = lambda: None
  widget._select("zh-CHT")
  assert not writes and not dialogs
  parked[0] = True
  widget._select("invalid")
  assert not writes
  widget._select("zh-CHT")
  assert writes == [("LanguageSetting", "zh-CHT")]
  assert len(dialogs) == 1
