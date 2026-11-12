"""Exercise the real portal and bridge in a browser with owner-scoped HTTP fixtures."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import time

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--executable')
  args = parser.parse_args()
  class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_): pass
  server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT/'formosalink/web')))
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  origin = f'http://127.0.0.1:{server.server_port}'
  bridge = (ROOT/'formosalink/web/carrot-bridge.js').read_text(encoding='utf-8')
  navigation = (ROOT/'openpilot/selfdrive/carrot/web/js/shared/ui/navigation.js').read_text(encoding='utf-8')
  resolve = re.search(r'function resolveWebStartPage\(\) \{[\s\S]*?\n\}', navigation).group()
  native = ('<!doctype html><script src="__formosa_bridge.js"></script><body><script>'
            'const PAGE_ELEMENTS={setting:{},carrot:{}};window.getWebStartPage=()=>"carrot";'
            +resolve+';document.body.dataset.page=resolveWebStartPage();'
            'fetch("/docs/settings/fixture.json",{credentials:"omit"}).then(r=>{if(!r.ok)throw Error("guide auth");'
            'return r.json()}).then(d=>document.body.dataset.guide=d.language);</script>')
  now = time.time()
  device = {'id':'fixture-device', 'name':'Carrot browser fixture', 'state':'paired', 'online':True, 'stale':False,
            'snapshot':{'sampled_at':now, 'metrics':{'branch':'origin/carrot-wip','device_type':'DEMO-CARROT','started':False}}, 'health':{}}
  state = {'fresh':True, 'commands':[], 'snapshot':{'offroad':True, 'remote_enabled':False, 'catalog':[],
           'values':{}, 'info':{}, 'session':'fixture', 'revision':'1','catalog_revision':'1'}}
  def route_api(route):
    assert route.request.method == 'GET', 'Navigation must not write settings or grant consent'
    path = route.request.url.split(origin)[1].split('?')[0]
    if path.endswith('/carrot/__formosa_bridge.js'):
      route.fulfill(body=bridge, content_type='application/javascript')
      return
    if path.endswith('/carrot/'):
      route.fulfill(body=native, content_type='text/html')
      return
    if path.endswith('/carrot/docs/settings/fixture.json'):
      assert 'fixture-owner=authenticated' in route.request.headers.get('cookie',''), 'Guide needs relay owner cookie'
      route.fulfill(body=json.dumps({'language':'zh-tw'}), content_type='application/json')
      return
    data = {'/api/v1/auth/me':{'user':{'id':'fixture-owner','github_login':'fixture'},'github_enabled':True},
            '/api/v1/devices':{'devices':[device], 'server_time':now},
            '/api/v1/devices/fixture-device/settings':state}.get(path)
    assert data is not None, f'Unexpected fixture API: {path}'
    route.fulfill(body=json.dumps(data), content_type='application/json')
  try:
    with sync_playwright() as p:
      browser = p.chromium.launch(headless=True, **({'executable_path':args.executable} if args.executable else {}))
      try:
        for viewport in [{'width':1280,'height':900}, {'width':390,'height':844}]:
          context = browser.new_context(viewport=viewport)
          context.add_cookies([{'name':'fixture-owner','value':'authenticated','url':origin,'httpOnly':True}])
          context.route('**/api/v1/**', route_api)
          page = context.new_page()
          errors = []
          page.on('pageerror', lambda error: errors.append(str(error)))
          page.goto(origin+'/#dashboard')
          entry = page.locator('#device-grid').get_by_role('link', name='Carrot 設定', exact=True)
          expect(entry).to_have_attribute('href', '/api/v1/devices/fixture-device/carrot/?formosa_page=setting')
          with page.expect_popup() as popup:
            entry.click()
          expect(popup.value.locator('body')).to_have_attribute('data-page', 'setting')
          expect(popup.value.locator('body')).to_have_attribute('data-guide', 'zh-tw')
          popup.value.close()
          page.get_by_role('button', name='裝置資訊', exact=True).click()
          expect(page.locator('#settings-banner-text')).to_contain_text('此分支不使用「停車遠端設定」')
          expect(page.locator('#settings-search')).to_be_disabled()
          expect(page.locator('#settings-nav [data-section="steering"]')).to_have_count(0)
          expect(page.locator('#settings-body .carrot-entry')).to_contain_text('遠端 Carrot 網頁：關')
          expect(page.locator('#settings-body').get_by_role('link', name='Carrot 設定', exact=True)).to_have_attribute('target','_blank')
          assert not errors, errors
          context.close()
          print(f'PASS Carrot settings entry {viewport["width"]}px')
      finally:
        browser.close()
  finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


if __name__ == '__main__':
  main()
