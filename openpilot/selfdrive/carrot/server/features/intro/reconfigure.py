"""Repeat onboarding with staged choices and a bounded, checked write boundary."""
import hashlib
import json
import threading

from .presets import PRESET_NAMES, get_preset

KEYS = ('CarSelected3', 'CanfdHDA2', *get_preset('stock'))
LOCK = threading.RLock()
LANGUAGES = {'en', 'ko', 'zh', 'zh-tw'}


class SetupError(Exception):
  def __init__(self, code, *, rollback_failed=None):
    super().__init__(code)
    self.code = code
    self.rollback_failed = rollback_failed or []


def text(value):
  return value.decode('utf-8') if isinstance(value, bytes) else value


def snapshot(params, read_web):
  raw = {name: text(params.get(name)) for name in KEYS}
  language = read_web().get('web_language', '')
  revision = hashlib.sha256(json.dumps([raw, language], sort_keys=True).encode()).hexdigest()
  values = {}
  for name, value in raw.items():
    try:
      values[name] = int(value) if name != 'CarSelected3' else value
    except (ValueError, TypeError):
      values[name] = value
  return {'revision': revision, 'car': raw['CarSelected3'] or '', 'lang': language, 'values': values, 'raw': raw}


def choices(current, body, makers):
  if not isinstance(body, dict) or set(body) != {'revision', 'lang', 'car', 'hda', 'preset'}:
    raise SetupError('invalid_selection')
  if body['revision'] != current['revision']:
    raise SetupError('settings_changed')
  car, lang, hda, preset = (body[key] for key in ('car', 'lang', 'hda', 'preset'))
  if not isinstance(car, str) or not car.strip() or len(car) > 200 or 'mock' in car.lower() or not isinstance(lang, str) or lang not in LANGUAGES:
    raise SetupError('invalid_selection')
  if car != current['car'] and not any(car in names for names in makers.values()):
    raise SetupError('unknown_car')
  if hda is not None and (type(hda) is not int or hda not in (0, 1) or car.split(' ', 1)[0] not in {'Hyundai', 'Kia', 'Genesis'}):
    raise SetupError('invalid_hda')
  if preset is not None and (not isinstance(preset, str) or preset not in PRESET_NAMES):
    raise SetupError('invalid_preset')
  desired = {'CarSelected3': car}
  if hda is not None:
    desired['CanfdHDA2'] = hda
  if preset is not None:
    desired.update(get_preset(preset))
  return {key: value for key, value in desired.items() if current['raw'][key] != str(value)}, lang


def apply(params, body, *, read_web, update_web, makers, write, guard, record):
  """No claims of filesystem-wide atomicity: failed writes are read back and restored.

  A concurrent third-party value is never overwritten during rollback. The
  caller must surface an incomplete rollback instead of reporting success.
  """
  with LOCK:
    guard()
    before = snapshot(params, read_web)
    desired, lang = choices(before, body, makers)
    written = []
    language_written = False
    try:
      for name, value in desired.items():
        guard()
        if text(params.get(name)) != before['raw'][name]:
          raise SetupError('settings_changed')
        written.append((name, str(value)))  # also repair a write that raises after landing
        write(name, value)
        if text(params.get(name)) != str(value):
          raise SetupError('write_failed')
      guard()
      if read_web().get('web_language', '') != before['lang']:
        raise SetupError('settings_changed')
      if lang != before['lang']:
        language_written = True
        update_web({'web_language': lang})
        if read_web().get('web_language') != lang:
          raise SetupError('write_failed')
      guard()
      expected = {**before['raw'], **{key: str(value) for key, value in desired.items()}}
      after = snapshot(params, read_web)
      if after['raw'] != expected or after['lang'] != lang:
        raise SetupError('settings_changed')
    except Exception as exc:
      failed = []
      if language_written:
        try:
          current = read_web().get('web_language', '')
          if current == lang:
            update_web({'web_language': before['lang']})
            if read_web().get('web_language', '') != before['lang']:
              failed.append('web_language')
          elif current != before['lang']:
            failed.append('web_language')
        except Exception:
          failed.append('web_language')
      for name, intended in reversed(written):
        try:
          actual = text(params.get(name))
          if actual == before['raw'][name]:
            continue
          if actual != intended:
            failed.append(name)
            continue
          if before['raw'][name] is None:
            params.remove(name)
          else:
            params.put(name, before['raw'][name])
          if text(params.get(name)) != before['raw'][name]:
            failed.append(name)
        except Exception:
          failed.append(name)
      raise SetupError('rollback_incomplete' if failed else getattr(exc, 'code', 'write_failed'), rollback_failed=failed) from exc
    for name, value in desired.items():
      try:
        record(name, before['values'][name], value)
      except Exception:
        pass  # History must not turn a committed setting into a reported failure.
    return {'ok': True, 'applied': desired, 'webLanguage': lang, 'requiresRestart': bool(desired)}
