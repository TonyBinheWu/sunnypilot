"""Private, offline lookup of OSM road geometry. Roads are map context only."""

import json
import math
import sqlite3
from pathlib import Path


def road_context(index, fix):
  if not fix or not Path(index).is_file():
    return []
  lat, lon = fix["lat"], fix["lon"]
  scale = 111_320 * math.cos(math.radians(lat))
  dx, dy = 150 / scale, 150 / 111_320
  with sqlite3.connect(Path(index).resolve().as_uri() + "?mode=ro", uri=True) as db:
    roads = db.execute(
      """SELECT way, kind, nodes FROM bounds JOIN roads ON roads.id=bounds.id
      WHERE west<=? AND east>=? AND south<=? AND north>=? LIMIT 256""",
      (lon + dx, lon - dx, lat + dy, lat - dy),
    ).fetchall()
  result = []
  for way, kind, nodes in roads:
    line = json.loads(nodes)
    xy = [((x - lon) * scale, (y - lat) * 111_320) for x, y in line]
    distance = math.inf
    for (x, y), (xx, yy) in zip(xy, xy[1:]):
      a, b = xx - x, yy - y
      t = min(1, max(0, -(x * a + y * b) / (a * a + b * b))) if a or b else 0
      distance = min(distance, math.hypot(x + t * a, y + t * b))
    if distance <= 125:
      result.append(dict(way=way, highway=kind, distance_m=round(distance, 1), lonlat=line))
  return sorted(result, key=lambda r: r["distance_m"])[:24]


def build_index(source, output):
  """Run on a workstation with pyosmium. Replace only after a successful import."""
  import os
  import tempfile
  import osmium

  output = Path(output)
  with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as tmp:
    staging = Path(tmp.name)
  try:
    db = sqlite3.connect(staging)
    try:
      db.executescript("""PRAGMA journal_mode=OFF;
        CREATE TABLE roads(id INTEGER PRIMARY KEY, way INTEGER,kind TEXT,nodes TEXT);
        CREATE VIRTUAL TABLE bounds USING rtree(id,west,east,south,north);""")

      class Roads(osmium.SimpleHandler):
        def way(self, way):
          kind = way.tags.get("highway")
          if not kind or way.tags.get("area") == "yes":
            return
          try:
            line = [(round(n.lon, 7), round(n.lat, 7)) for n in way.nodes]
          except osmium.InvalidLocationError:
            return
          for i in range(0, len(line) - 1, 12):
            part = line[i : i + 13]
            x, y = zip(*part)
            key = db.execute(
              "INSERT INTO roads(way,kind,nodes) VALUES(?,?,?)", (way.id, kind, json.dumps(part, separators=(",", ":")))
            ).lastrowid
            db.execute("INSERT INTO bounds VALUES(?,?,?,?,?)", (key, min(x), max(x), min(y), max(y)))

      Roads().apply_file(str(source), locations=True, idx="flex_mem")
      n = db.execute("SELECT COUNT(*) FROM roads").fetchone()[0]
      if n == 0:
        raise ValueError("OSM extract has no highway geometry")
      db.commit()
    finally:
      db.close()
    os.replace(staging, output)
    return n
  finally:
    staging.unlink(missing_ok=True)


if __name__ == "__main__":
  import argparse

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("extract")
  parser.add_argument("output")
  args = parser.parse_args()
  print(build_index(args.extract, args.output))
