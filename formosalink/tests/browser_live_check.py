"""Real browser, real WebSockets and JPEG decoding; fixture images are not vehicle video."""
import argparse
from pathlib import Path
import shutil
import socket
import tempfile
import threading
import time

from playwright.sync_api import expect, sync_playwright
import uvicorn

from formosalink.server.app import COOKIE, create_app
from formosalink.server.config import initialize
from formosalink.tests.test_media import JPEG
from openpilot.sunnypilot.formosalink import cameras
from openpilot.sunnypilot.formosalink.identity import create
from openpilot.sunnypilot.formosalink.protocol import fingerprint

ROOT = Path(__file__).resolve().parents[2]


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--executable', help='Optional installed Chrome/Edge path; otherwise Playwright Chromium')
  args = parser.parse_args()
  with tempfile.TemporaryDirectory(prefix='formosa-browser-') as temporary:
    root = Path(temporary)
    web = root/'web'
    web.mkdir()
    for name in ('media-view.js', 'i18n.js'):
      shutil.copyfile(ROOT/'formosalink/web'/name, web/name)
    (web/'index.html').write_text('<!doctype html><html><body><main id="test"></main><script type="module" src="/harness.js"></script></body></html>', encoding='utf-8')
    (web/'harness.js').write_text('''import {mediaViewer} from './media-view.js';import {translations} from './i18n.js';
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const viewer=mediaViewer({api:()=>{},t:k=>translations['zh-TW'][k]||k,el});viewer.open(document.getElementById('test'),location.hash.slice(1));''', encoding='utf-8')
    listener = socket.socket()
    listener.bind(('127.0.0.1', 0))
    port = listener.getsockname()[1]
    origin = f'http://127.0.0.1:{port}'
    initialize(root/'state', origin, 'test-owner-browser-only')
    app = create_app(root/'state', web_dir=web)
    identity, private, public = create(root/'device', origin)
    enrolled = app.state.store.enroll(identity['device_id'], public, fingerprint(public))
    app.state.store.pair(enrolled['pair_code'], enrolled['fingerprint'], 'Browser fixture')
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=port, log_level='error', ws_max_size=262144,
                                          ws_per_message_deflate=False, proxy_headers=False))
    thread = threading.Thread(target=server.run, kwargs={'sockets':[listener]}, daemon=True)
    original_source = cameras.NativeCamera
    source_state = {'invalid_jpeg':False}
    # Valid SOF dimensions for the wire parser, but no JPEG scan to decode.
    damaged_jpeg = bytes.fromhex('ffd8ffc00011080168028003011100021100031100ffd9')
    class CameraFixture:
      def __init__(self, *args, **kwargs): pass
      def __call__(self): return damaged_jpeg if source_state['invalid_jpeg'] else JPEG, time.time(), {'speed_kph':None, 'engaged':None}
      def close(self): pass
    cameras.NativeCamera = CameraFixture
    thread.start()
    try:
      deadline = time.monotonic()+5
      while not server.started and time.monotonic() < deadline:
        time.sleep(.01)
      assert server.started
      with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, **({'executable_path':args.executable} if args.executable else {}))
        try:
          # A one-day PC clock error must not reject fresh cloud-validated images.
          for camera, skew, blocked in [('wide-road',0,False), ('driver',86_400_000,False), ('wide-road',-86_400_000,False), ('driver',0,True)]:
            source_state['invalid_jpeg'] = blocked
            stop = threading.Event()
            publisher = threading.Thread(target=cameras.stream_camera, args=(identity, private, camera, stop), daemon=True)
            context = browser.new_context()
            context.add_cookies([{'name':COOKIE, 'value':app.state.store.session(), 'url':origin}])
            page = context.new_page()
            console = []
            page.on('console', lambda message: console.append(message.text[:160]))
            page.add_init_script(f'const originalNow=Date.now.bind(Date);Date.now=()=>originalNow()+{skew};')
            try:
              page.goto(origin+'/#'+identity['device_id'])
              page.locator('select').select_option(camera)
              page.get_by_role('button', name='開始觀看', exact=True).click()
              publisher.start()
              if blocked:
                expect(page.locator('.media-status')).to_contain_text('無法解碼 JPEG', timeout=10000)
                assert '已顯示影格數: 0' in page.locator('[role="status"]').last.text_content()
              else:
                expect(page.locator('.media-status')).to_have_text('即時串流中', timeout=10000)
                pixel = page.locator('canvas').evaluate('(c)=>Array.from(c.getContext("2d").getImageData(200,200,1,1).data)')
                assert pixel[:3] != [16,21,29] and pixel[3] == 255, pixel
              page.get_by_role('button', name='停止觀看', exact=True).click()
              page.wait_for_timeout(250)
              assert page.locator('.media-status').text_content() == '觀看已停止'
              print(f'Browser live passed: camera={camera}, clock_skew_ms={skew}, invalid_jpeg={blocked}', flush=True)
            except Exception:
              print('Browser failure diagnostics:', page.locator('[role="status"]').all_text_contents(), console[-5:], flush=True)
              raise
            finally:
              stop.set()
              if publisher.ident is not None:
                publisher.join(timeout=5)
                assert not publisher.is_alive()
              context.close()
        finally:
          browser.close()
    finally:
      cameras.NativeCamera = original_source
      server.should_exit = True
      thread.join(timeout=10)
      listener.close()
    assert not thread.is_alive()


if __name__ == '__main__':
  main()
