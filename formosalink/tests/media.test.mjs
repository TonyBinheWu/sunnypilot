import test from 'node:test';
import assert from 'node:assert/strict';
import {recordingMime,validPreview,mediaCursor,clipLimit,streamUrl} from '../web/media-view.js';
import {translations} from '../web/i18n.js';
import {readFileSync} from 'node:fs';

test('live camera waiting describes automatic native startup in all supported languages',()=>{
 for(const language of ['zh-TW','en','ja'])assert.ok(translations[language].mediaWaiting);
 assert.ok(translations['zh-TW'].mediaWaiting.includes('無須手動發送'));
 assert.ok(!translations['zh-TW'].mediaWaiting.includes('需先在來源端'));
 const index=readFileSync(new URL('../web/index.html',import.meta.url),'utf8');
 const app=readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
 const workspace=readFileSync(new URL('../web/device-settings.js',import.meta.url),'utf8');
 assert.ok(index.includes('/app.js?v=0.8.1'));
 assert.ok(app.includes('./i18n.js?v=0.8.1'));
 assert.ok(app.includes('./device-settings.js?v=0.8.1'));
 assert.ok(workspace.includes('./media-view.js?v=0.8.1'));
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
