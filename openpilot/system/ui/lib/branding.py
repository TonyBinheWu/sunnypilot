"""Formosa display identity. Never use these functions for service or Git metadata."""
import re

PRODUCT = "FormosaPilot"
LOGO_ASSET = "../../sunnypilot/formosalink/assets/formosapilot-logo.png"
_BRAND = re.compile(r"(?<![\w/])sunnypilot(?![\w/])", re.IGNORECASE)
_REFERENCE = re.compile(r"(?:https?://|git@)[^\s<>\"']+|(?:[\w-]+\.)*sunnypilot\.(?:ai|com|org)(?:/[^\s<>\"']*)?", re.IGNORECASE)
_ATTRIBUTION = re.compile(r"copyright|\blicen[cs]e\b|\bSPDX\b|\bsponsor\b|著作權|版權|授權條款|贊助|スポンサー|著作権", re.IGNORECASE)
_LOGOS = frozenset((
  "../../sunnypilot/selfdrive/assets/logo.png",
  "../../sunnypilot/selfdrive/assets/images/spinner_sunnypilot.png",
))


def display_text(text: str) -> str:
  # Keep attribution and actual third-party funding/terms references truthful.
  if not isinstance(text, str) or "sunnypilot" not in text.lower() or _ATTRIBUTION.search(text):
    return text
  result, start = [], 0
  for reference in _REFERENCE.finditer(text):
    result.extend((_BRAND.sub(PRODUCT, text[start:reference.start()]), reference.group()))
    start = reference.end()
  result.append(_BRAND.sub(PRODUCT, text[start:]))
  return "".join(result)


def display_asset(asset: str) -> str:
  return LOGO_ASSET if asset in _LOGOS else asset
