from openpilot.system.ui.lib.branding import display_text, display_asset, LOGO_ASSET


def test_product_text_is_replaced_in_all_languages():
  for message in ("Enable sunnypilot", "啟用 sunnypilot", "sunnypilot を有効にする", "SUNNYPILOT unavailable."):
    assert "sunnypilot" not in display_text(message).lower()
    assert "FormosaPilot" in display_text(message)
    assert display_text(display_text(message)) == display_text(message)


def test_real_references_and_internal_identifiers_are_preserved():
  for reference in ("https://github.com/sunnypilot/sunnypilot", "https://sunnypilot.ai/terms", "community.sunnypilot.ai", "openpilot/sunnypilot/models", "SUNNYPILOT_UI", "sunnylink"):
    assert display_text(reference) == reference
  for notice in ("Copyright sunnypilot contributors", "MIT License: sunnypilot", "sunnypilot sponsor", "sunnypilot 著作權"):
    assert display_text(notice) == notice
  assert display_text("Enable sunnypilot: https://sunnypilot.ai/terms") == "Enable FormosaPilot: https://sunnypilot.ai/terms"


def test_product_logos_use_original_formosa_asset_only():
  for path in ("../../sunnypilot/selfdrive/assets/logo.png", "../../sunnypilot/selfdrive/assets/images/spinner_sunnypilot.png"):
    assert display_asset(path) == LOGO_ASSET
  assert display_asset("icons_mici/settings/device/fcc_logo.png") == "icons_mici/settings/device/fcc_logo.png"
