"""Release notes shared by build metadata, the updater and both UI profiles."""
from html.parser import HTMLParser
from pathlib import Path
import re


def read_release_notes(basedir: str) -> str:
  text = (Path(basedir) / "CHANGELOG.md").read_text(encoding="utf-8-sig")
  headings = list(re.finditer(r"(?m)^[^\n]+\n={3,}[ \t]*$", text))
  if headings and headings[0].start() == 0:
    return text[:headings[1].start() if len(headings) > 1 else len(text)].strip()
  return text.split("\n\n", 1)[0].strip()


class _NotesParser(HTMLParser):
  def __init__(self):
    super().__init__()
    self.lines: list[str] = []
    self.parts: list[str] = []

  def flush(self):
    line = "".join(self.parts).strip()
    if line:
      self.lines.append(line)
    self.parts.clear()

  def handle_starttag(self, tag, attrs):
    if tag in ("h1", "h2", "h3", "p", "li", "br"):
      self.flush()
    if tag == "li":
      self.parts.append("• ")

  def handle_endtag(self, tag):
    if tag in ("h1", "h2", "h3", "p", "li", "ul"):
      self.flush()

  def handle_data(self, data):
    self.parts.append(data)


def release_notes_lines(html: str) -> list[str]:
  parser = _NotesParser()
  parser.feed(html)
  parser.close()
  parser.flush()
  return parser.lines
