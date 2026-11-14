"""Persistent named navigation destinations, independent of the active drive."""
import json
import math
import os
from pathlib import Path
import tempfile
import uuid

MAX_FAVORITES = 100


class FavoritesFull(Exception):
  pass


class NavigationFavorites:
  def __init__(self, path):
    self.path = Path(path)

  def read(self):
    try:
      value = json.loads(self.path.read_text(encoding='utf-8'))
    except FileNotFoundError:
      return []
    if not isinstance(value, list) or len(value) > MAX_FAVORITES:
      raise ValueError('invalid favorites file')
    identifiers = set()
    for item in value:
      if not isinstance(item, dict) or set(item) != {'id', 'name', 'place_name', 'latitude', 'longitude'}:
        raise ValueError('invalid favorite')
      identifier = item['id']
      if not isinstance(identifier, str) or len(identifier) != 32 or any(c not in '0123456789abcdef' for c in identifier) or identifier in identifiers:
        raise ValueError('invalid favorite identifier')
      identifiers.add(identifier)
      for key, limit in (('name', 80), ('place_name', 256)):
        if not isinstance(item[key], str) or not 1 <= len(item[key].strip()) <= limit:
          raise ValueError('invalid favorite text')
      for key, limit in (('latitude', 85.05112878), ('longitude', 180)):
        if type(item[key]) not in (int, float) or not math.isfinite(item[key]) or abs(item[key]) > limit:
          raise ValueError('invalid favorite coordinates')
    return value

  def write(self, favorites):
    self.path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
      with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent, delete=False) as stream:
        temporary = stream.name
        json.dump(favorites, stream, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
      os.replace(temporary, self.path)
    finally:
      if temporary:
        Path(temporary).unlink(missing_ok=True)

  def save(self, value, identifier=None):
    favorites = self.read()
    if identifier is None:
      if len(favorites) >= MAX_FAVORITES:
        raise FavoritesFull('favorites full')
      favorites.append(dict(value, id=uuid.uuid4().hex))
    else:
      index = next((i for i, item in enumerate(favorites) if item['id'] == identifier), None)
      if index is None:
        raise KeyError(identifier)
      favorites[index] = dict(value, id=identifier)
    self.write(favorites)
    return favorites

  def delete(self, identifier):
    favorites = self.read()
    remaining = [item for item in favorites if item['id'] != identifier]
    if len(remaining) == len(favorites):
      raise KeyError(identifier)
    self.write(remaining)
    return remaining
