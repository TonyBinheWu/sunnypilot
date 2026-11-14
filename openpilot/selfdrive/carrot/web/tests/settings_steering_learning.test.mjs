import assert from 'node:assert/strict';
import test from 'node:test';
import {expireSnapshot, learningHtml} from '../src/features/tools/steering_learning.js';

test('progress is not invented and stale records never retain a live label',()=>{
  const html=learningHtml(null);
  assert.ok(!html.includes('value="0"'));
  assert.ok(!html.includes('0%'));
  const live={delay:{source:'live',status:'learning',progress:80,applied:.3,estimate:.153},
    torque:{source:'cached',status:'learning',progress:56,factor:2.5,friction:.1}};
  const expired=expireSnapshot(live);
  assert.equal(expired.delay.source,'stale');
  assert.equal(expired.torque.source,'cached');
  assert.equal(live.delay.source,'live');
  const body=learningHtml(expired,true);
  assert.match(body,/80%/);assert.match(body,/56%/);
  assert.match(body,/0\.300 s/);assert.match(body,/0\.153 s/);
  assert.match(body,/Data expired/);assert.match(body,/not live/);
});

test('untrusted values are escaped and invalid progress does not create a progress bar',()=>{
  const body=learningHtml({delay:{source:'<img onerror=bad>',status:'unavailable',progress:999},torque:{source:'unavailable',progress:NaN}});
  assert.ok(!body.includes('<img'));
  assert.ok(!body.includes('<progress'));
});
