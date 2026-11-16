import asyncio

import pytest
from aiohttp import web

from openpilot.selfdrive.carrot.server.features import static


def test_cockpit_page_is_uncached_and_fingerprints_assets(tmp_path, monkeypatch):
  (tmp_path / 'css').mkdir()
  (tmp_path / 'js').mkdir()
  (tmp_path / 'css/cockpit.css').write_text('body{color:black}', encoding='utf-8')
  (tmp_path / 'js/cockpit.js').write_text('window.test=1;', encoding='utf-8')
  (tmp_path / 'cockpit.html').write_text(
    '<link rel="stylesheet" href="/css/cockpit.css"><script src="/js/cockpit.js"></script>', encoding='utf-8')
  monkeypatch.setattr(static, 'WEB_DIR', str(tmp_path))
  response = asyncio.run(static.handle_cockpit(None))
  assert response.status == 200
  assert response.headers['Cache-Control'] == 'no-store'
  assert '/css/cockpit.css?v=' in response.text
  assert '/js/cockpit.js?v=' in response.text


def test_missing_cockpit_page_has_explicit_update_failure(tmp_path, monkeypatch):
  monkeypatch.setattr(static, 'WEB_DIR', str(tmp_path))
  with pytest.raises(web.HTTPServiceUnavailable) as error:
    asyncio.run(static.handle_cockpit(None))
  assert '更新' in error.value.text
