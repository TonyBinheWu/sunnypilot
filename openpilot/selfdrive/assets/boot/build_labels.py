"""Rebuild the small startup bitmap font from the bundled KaiGen Gothic font."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from openpilot.selfdrive.assets.fonts.process import _write_bmfont
from openpilot.system.ui.lib.multilang import TRANSLATIONS_DIR, load_translations

HERE = Path(__file__).resolve().parent
LABELS = ("Starting up", "Building software", "Preparing runtime packages", "Building settings registry", "registering device",
          "Downloading model", "Downloading precompiled model", "Checking precompiled model", "Validating precompiled model",
          "Recovery", "Offline")


def main():
  chars = {chr(i) for i in range(32, 127)} | {"·"}
  for locale in ("zh-CHT", "zh-CHS", "ja", "ko"):
    messages, _ = load_translations(TRANSLATIONS_DIR / f"app_{locale}.po")
    for label in LABELS:
      chars.update(messages[label])
  size, width = 44, 1024
  font = ImageFont.truetype(str(HERE.parent / "fonts/KaiGenGothicKR-Bold.ttf"), size)
  sheet = Image.new("RGBA", (width, 1024), (255, 255, 255, 0))
  draw = ImageDraw.Draw(sheet)
  x = y = 2
  entries = []
  for ch in sorted(chars):
    left, top, right, bottom = font.getbbox(ch, anchor="ls")
    w, h = max(1, right-left), max(1, bottom-top)
    if x+w+2 > width:
      x, y = 2, y+size+5
    draw.text((x-left, y-top), ch, font=font, fill="white", anchor="ls")
    entries.append({"id": ord(ch), "x": x, "y": y, "width": w, "height": h, "xoffset": left,
                    "yoffset": round(size*.82)+top, "xadvance": round(font.getlength(ch))})
    x += w+4
  height = 1 << (y+size+2).bit_length()
  assert height <= sheet.height
  sheet.crop((0, 0, width, height)).save(HERE / "labels.png", optimize=True)
  _write_bmfont(HERE / "labels.fnt", size, "Carrot Boot Labels", "labels.png", size, round(size*.82), (width, height), entries)


if __name__ == "__main__":
  main()
