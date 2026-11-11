import pytest

from openpilot.selfdrive.carrot.server.services import web_settings
from openpilot.selfdrive.carrot.server.services.settings import build_menu_categories


@pytest.mark.parametrize("tag", ["zh-tw", "zh-TW", "zh-Hant", "zh-Hant-TW", "zh-HK", "zh-MO", "zh_CHT", "main_zh-CHT"])
def test_traditional_web_language_survives_save_and_reload(tag):
  saved = web_settings.sanitize_web_settings({"web_language": tag})
  assert saved["web_language"] == "zh-tw"
  assert web_settings.sanitize_web_settings(saved)["web_language"] == "zh-tw"


@pytest.mark.parametrize("tag", ["zh", "zh-CN", "zh-Hans", "main_zh-CHS"])
def test_simplified_web_language_stays_simplified(tag):
  assert web_settings.sanitize_web_settings({"web_language": tag})["web_language"] == "zh"


def test_menu_categories_keep_traditional_labels_at_every_level():
  data = {"menu": [{"id": "cat", "zh-tw": "駕駛", "groups": [
    {"id": "group", "zh-tw": "車道", "groups": [{"id": "section", "zh-tw": "轉向", "params": ["Example"]}]}
  ]}]}
  categories = build_menu_categories(data, {"Example": {"name": "Example"}})
  assert categories[0]["zh-tw"] == "駕駛"
  assert categories[0]["groups"][0]["zh-tw"] == "車道"
  assert categories[0]["groups"][0]["sections"][0]["zh-tw"] == "轉向"
