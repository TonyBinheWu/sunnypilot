import test from 'node:test';
import assert from 'node:assert/strict';
import {recordingMime,validPreview,mediaCursor,clipLimit} from '../web/media-view.js';
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
