import test from 'node:test';
import assert from 'node:assert/strict';
import {recordingMime,validPreview,mediaCursor,clipLimit,streamUrl,cameraDiagnosticLines,serverClockSample,freshServerFrame} from '../web/media-view.js';
import {translations} from '../web/i18n.js';
import {readFileSync} from 'node:fs';

test('frame freshness follows the bounded server clock without the browser wall clock',()=>{
 const clock=serverClockSample('Wed, 11 Nov 2026 17:30:00 GMT',100,200);
 const server=Date.parse('2026-11-11T17:30:00Z');
 assert.equal(clock.uncertainty,550);
 assert.ok(freshServerFrame((server+700)/1000,clock,350));
 assert.equal(freshServerFrame((server-10000)/1000,clock,350),false);
 assert.equal(freshServerFrame((server+10000)/1000,clock,350),false);
 assert.equal(freshServerFrame(NaN,clock,350),false);
 assert.equal(freshServerFrame(server/1000,clock,100),false);
 assert.throws(()=>serverClockSample(null,100,200));
 assert.throws(()=>serverClockSample('invalid',100,200));
 assert.throws(()=>serverClockSample('Wed, 11 Nov 2026 17:30:00 GMT',100,6000));
 for(const locale of ['zh-TW','en','ja'])for(const code of ['clock_unavailable','invalid_message','invalid_frame','expired_frame','decode_failed','decode_timeout','draw_failed','connection_closed'])assert.ok(translations[locale]['mediaError_'+code]);
});

test('camera diagnostics distinguish stale health, old devices, pipeline failures and real acknowledgements',()=>{
 const t=key=>translations['zh-TW'][key]||key;
 assert.ok(cameraDiagnosticLines({},false,'driver',t)[0].includes('無法判定'));
 assert.ok(cameraDiagnosticLines({},true,'driver',t)[0].includes('重新啟動'));
 const info={camera_diagnostics_version:1,camera_watch_state:'requested',camera_driver_state:'encoding',camera_driver_error:'TimeoutError',camera_driver_frames:0,camera_driver_frame_age_s:null};
 const failed=cameraDiagnosticLines(info,true,'driver',t).join(' ');
 assert.ok(failed.includes('已收到觀看請求'));
 assert.ok(failed.includes('影像編碼中 (TimeoutError)'));
 assert.ok(failed.includes('影格數: 0'));
 info.camera_driver_state='streaming';info.camera_driver_frames=8;info.camera_driver_error=null;info.camera_driver_frame_age_s=.2;
 assert.ok(cameraDiagnosticLines(info,true,'driver',t).join(' ').includes('雲端已確認收到影格'));
 assert.ok(!cameraDiagnosticLines(info,false,'driver',t).join(' ').includes('雲端已確認收到影格'));
 for(const locale of ['zh-TW','en','ja'])assert.ok(translations[locale].mediaStage_connecting_camera);
});

test('live camera waiting describes automatic native startup in all supported languages',()=>{
 for(const language of ['zh-TW','en','ja'])assert.ok(translations[language].mediaWaiting);
 assert.ok(translations['zh-TW'].mediaWaiting.includes('無須手動發送'));
 assert.ok(!translations['zh-TW'].mediaWaiting.includes('需先在來源端'));
 const index=readFileSync(new URL('../web/index.html',import.meta.url),'utf8');
 const app=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
 const workspace=readFileSync(new URL('../web/device-settings.js',import.meta.url),'utf8');
 assert.ok(index.includes('/app.js?v=0.8.4'));
 assert.ok(app.includes('./i18n.js?v=0.8.4'));
 assert.ok(app.includes('./device-settings.js?v=0.8.4'));
 assert.ok(workspace.includes('./media-view.js?v=0.8.3'));
});
test('stream uses same self-hosted HTTPS authority, LAN addresses and supported cameras only',()=>{
 assert.equal(streamUrl('https://formosapilot.dinglu-t.com','abc','driver'),'wss://formosapilot.dinglu-t.com/api/v1/devices/abc/media/stream?camera=driver');
 assert.equal(streamUrl('https://link.home','abc','wide-road'),'wss://link.home/api/v1/devices/abc/media/stream?camera=wide-road');
 assert.throws(()=>streamUrl('https://link.home','abc','other'));
});
test('media chooses only browser-supported recording types',()=>{
 assert.equal(recordingMime(undefined),null);
 assert.equal(recordingMime({isTypeSupported:type=>type==='video/mp4'}),'video/mp4');
 assert.equal(recordingMime({isTypeSupported:()=>false}),null);assert.equal(clipLimit,60);
});
test('media distinguishes demo and bounded road previews and both native cameras from invalid or oversized images',()=>{
 const frame={source:'demo',stream:'00000000-0000-0000-0000-000000000001',sequence:0,width:640,height:360,jpeg:'validity-is-checked-by-server'};
 assert.ok(validPreview({...frame,source:"driver"}));assert.ok(validPreview({...frame,source:"wide-road"}));
 assert.ok(validPreview(frame));assert.equal(mediaCursor(frame),frame.stream+':0');
 for(const changes of [{source:'unknown-camera'},{width:20000},{height:0},{sequence:-1},{sequence:Infinity},{jpeg:'x'.repeat(240005)}])assert.ok(!validPreview({...frame,...changes}));
});
