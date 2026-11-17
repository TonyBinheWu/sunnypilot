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

test('passive low-speed records display actual units and expire with the same live deadline',()=>{
  const snapshot={lowSpeed:{source:'live',enabled:true,current:{reason:'rate_or_yield',requested:405,command:300,
    targetAngle:25,angle:20,angleRate:10,base:270,ceiling:405,up:2,down:3},
    stats:{samples:50,left:{command:300,angle:20,angleRate:10},right:{command:200,angle:15,angleRate:9}}}};
  const html=learningHtml(snapshot);
  assert.match(html,/405 \/ 300/); assert.match(html,/2 \/ 3/);assert.match(html,/20\.0 ° \/ 10\.0 °\/s/);
  assert.match(html,/not hardware limits/);assert.match(html,/rate limit or steering yield/);
  const expired=expireSnapshot(snapshot);
  assert.equal(expired.lowSpeed.source,'stale');assert.equal(snapshot.lowSpeed.source,'live');
  assert.match(learningHtml(expired,true),/Data expired/);
});
