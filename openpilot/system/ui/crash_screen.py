"""Small independent error screen: no cereal, Params, UI widgets or translations."""
import argparse
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LABELS = "系統錯誤先接管並安全停車再拍照點螢幕下一頁記錄已儲存"


def screen_size(device: str) -> tuple[int, int]:
  return (2160, 1080) if device in ("tici", "tizi") else (536, 240)


def ascii_text(text: str) -> str:
  return "".join(c if 32 <= ord(c) < 127 or c == "\n" else f"\\u{ord(c):04x}" for c in str(text))


def pages(data: dict, columns: int = 62, rows: int = 7) -> list[list[str]]:
  def wrap(text):
    return [part for line in ascii_text(text).splitlines() for part in (textwrap.wrap(line, columns) or [""])]

  location = str(data.get("location", "unknown"))
  short_location = "/".join(location.split("/")[-2:])
  summary = [f"{data.get('stage', '?')}: {data.get('exit', '?')}"]
  summary += wrap(short_location)[:2]
  error_lines = wrap(data.get("summary", "No error detail recorded"))
  room = rows - len(summary)
  summary += error_lines[:room]
  if len(error_lines) > room:
    summary[-1] = summary[-1][:columns - 3] + "..."
  detail = wrap(f"{location}\n{data.get('summary', '')}\n\n{data.get('detail', '')}")
  return [summary] + [detail[i:i + rows] for i in range(0, len(detail), rows)]


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("report", type=Path)
  parser.add_argument("--device", choices=("tizi", "mici"), help="Host rendering tests only")
  parser.add_argument("--frames", type=int, default=0, help="Host rendering tests only")
  parser.add_argument("--screenshot", type=Path, help="Host rendering tests only")
  args = parser.parse_args()
  data = json.loads(args.report.read_text(encoding="utf-8"))
  on_device = Path("/AGNOS").exists()
  device = data.get("device", "pc") if on_device else (args.device or data.get("device", "pc"))

  # Imported here so formatting/tests need only the Python standard library.
  import pyray as rl

  width, height = screen_size(device)
  scale = width / 536
  font_size = 14 * scale
  margin = 12 * scale
  line_height = 19 * scale
  rl.init_window(width, height, "sunnypilot diagnostic - photograph when parked")
  rl.set_target_fps(5)
  rl.set_exit_key(0)
  default_font = rl.get_font_default()
  chinese_font = None
  try:
    # Load only our small fixed label alphabet. Never load the full UI font atlas.
    try:
      path = ROOT / "openpilot/selfdrive/assets/fonts/SourceHanSansTC-Regular.otf"
      if path.exists():
        with path.open("rb") as f:
          is_font = f.read(4) == b"OTTO"
        if is_font:
          points = sorted({ord(c) for c in LABELS})
          buffer = rl.ffi.new("int[]", points)
          candidate = rl.load_font_ex(str(path), int(18 * scale), rl.ffi.cast("int *", buffer), len(points))
          if candidate.texture.id != default_font.texture.id and candidate.texture.id:
            chinese_font = candidate
    except Exception as e:
      print(f"Optional label font unavailable: {e}", flush=True)
    print("Diagnostic font: " + ("Traditional Chinese" if chinese_font else "built-in ASCII"), flush=True)

    # Measure the widest ASCII glyph; long paths and unbroken tokens cannot clip.
    char_width = max(rl.measure_text_ex(default_font, chr(c), font_size, 0).x for c in range(32, 127))  # noqa: TID251
    columns = max(16, int((width - 2 * margin) / max(char_width, 1)))
    content = pages(data, columns=columns)
    page = 0
    count = 0

    def draw(text, y, size, color, chinese=False):
      font = chinese_font if chinese and chinese_font is not None else default_font
      rl.draw_text_ex(font, text, rl.Vector2(margin, y * scale), size * scale, 0, color)

    while not rl.window_should_close():
      # Deliberately independent of the failed main UI event/widget infrastructure.
      if rl.is_mouse_button_pressed(0) or rl.is_key_pressed(rl.KeyboardKey.KEY_RIGHT):  # noqa: TID251
        page = (page + 1) % len(content)
      if rl.is_key_pressed(rl.KeyboardKey.KEY_LEFT):
        page = (page - 1) % len(content)
      rl.begin_drawing()
      rl.clear_background(rl.BLACK)
      draw("系統錯誤" if chinese_font else "SYSTEM ERROR", 8, 20, rl.RED, chinese=True)
      draw("先接管並安全停車再拍照" if chinese_font else "TAKE CONTROL. STOP SAFELY. THEN PHOTOGRAPH.",
           33, 12, rl.YELLOW, chinese=True)
      for i, line in enumerate(content[page]):
        rl.draw_text_ex(default_font, line, rl.Vector2(margin, 55 * scale + i * line_height), font_size, 0, rl.WHITE)
      # Fixed footer remains visible on every page. It never auto-advances.
      footer = f"{device} | {data.get('commit', '?')} | ID {str(data.get('id', '?'))[-8:]}"
      draw(footer, height / scale - 38, 12, rl.YELLOW)
      label = f"Tap: next page  {page + 1}/{len(content)} | logs saved"
      draw(label, height / scale - 20, 12, rl.WHITE)
      rl.end_drawing()
      count += 1
      if not on_device and args.frames and count >= args.frames:
        if args.screenshot:
          args.screenshot.parent.mkdir(parents=True, exist_ok=True)
          rl.take_screenshot(str(args.screenshot))
        break
  finally:
    if chinese_font is not None:
      rl.unload_font(chinese_font)
    rl.close_window()


if __name__ == "__main__":
  main()
