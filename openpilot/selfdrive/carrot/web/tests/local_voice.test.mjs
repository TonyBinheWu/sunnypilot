import test from 'node:test';
import assert from 'node:assert/strict';
import { createLocalVoice } from '../src/features/tools/local_voice.js';

test('phone commands need no relay session and make one origin-bound request', async () => {
  globalThis.document = { hidden: false };
  let time = 1000, allowed = false;
  const sent = [], opened = [];
  const voice = createLocalVoice(async name => { opened.push(name); return 'opened'; }, () => allowed,
    async command => { sent.push(command); return { result: { status: 'waiting' } }; }, () => time);
  const run = async (action, key) => {
    const id = key.repeat(43);
    assert.equal(voice.start(action,id,time+3500), true);
    await new Promise(resolve => setImmediate(resolve));
    return voice.result(id);
  };
  assert.equal(await run('blinker_settings','a'), 'opened');
  assert.deepEqual(opened,['AutoBlinkerControl']);
  assert.equal(await run('lane_left','b'), 'permission');
  assert.equal(sent.length,0);
  allowed = true;
  assert.equal(await run('lane_left','c'), 'waiting');
  assert.equal(await run('lane_left','c'), 'waiting');
  assert.equal(await run('lane_right','d'), 'duplicate');
  assert.equal(sent.length,1);
  time += 11000;
  assert.equal(await run('lane_right','e'), 'waiting');
  assert.deepEqual(sent.map(x=>x.action), ['lane_left','lane_right']);
  document.hidden = true;
  assert.equal(voice.start('lane_left','x'.repeat(43),time+50), false);
  document.hidden = false;
  assert.equal(voice.start('lane_left','x'.repeat(43),time-1), false);
  assert.equal(voice.start('shell','x'.repeat(43),time+50), false);
});

test('late callbacks and competing commands do not replace an in-flight request', async () => {
  globalThis.document = {hidden:false};
  let finish, calls = 0;
  const voice = createLocalVoice(null, () => true, () => { calls++; return new Promise(r => {finish=r;}); }, () => 1000);
  assert.ok(voice.start('lane_left','a'.repeat(43),2500));
  assert.ok(voice.start('lane_left','a'.repeat(43),2500));
  assert.equal(voice.start('lane_right','b'.repeat(43),2500),false);
  assert.equal(calls,1);
  finish(null);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(voice.result('a'.repeat(43)),'unverified');
});

test('cruise uses one granted execution and status-only readback, sharing the maneuver cooldown', async () => {
  globalThis.document = { hidden: false };
  const calls = [];
  const id = 'c'.repeat(43);
  const voice = createLocalVoice(null, () => true, async command => {
    calls.push(command);
    return { result: { id, status: command.operation === 'execute' ? 'waiting' : 'applied', current: 100 } };
  }, () => 1000, null, async () => {});
  assert.ok(voice.cruise('speed_set', 100, id, 4000));
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(voice.result(id), { kind: 'cruise', status: 'applied', current: 100 });
  assert.deepEqual(calls.map(c => c.operation), ['execute', 'status']);
  assert.equal(calls[0].value, 100);
  assert.equal(calls[1].value, undefined);
  assert.ok(voice.cruise('speed_set', 100, id, 4000));
  assert.equal(calls.length, 2);
  assert.ok(voice.start('lane_left', 'd'.repeat(43), 4000));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(voice.result('d'.repeat(43)), 'duplicate');
});

test('invalid cruise values, hidden pages, absent permission and revoked grants never execute anew', async () => {
  globalThis.document = { hidden: false };
  let granted = false, executions = 0;
  const id = 'a'.repeat(43);
  const voice = createLocalVoice(null, () => granted, async command => {
    executions++;
    return { result: { id: command.id, status: 'waiting' } };
  }, () => 1000, null, async () => { granted = false; });
  for (const [action, value] of [['speed_set', 0], ['speed_set', 200], ['speed_set', 2.5], ['speed_down', -1], ['speed_up', 10], ['speed_set', null], ['lane_left', 10]]) {
    assert.equal(voice.cruise(action, value, id, 4000), false);
  }
  assert.ok(voice.cruise('speed_set', 100, id, 4000));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(voice.result(id).status, 'permission');
  assert.equal(executions, 0);
  granted = true;
  assert.ok(voice.cruise('speed_up', null, 'b'.repeat(43), 4000));
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(voice.result('b'.repeat(43)).status, 'unverified');
  assert.equal(executions, 1);
  document.hidden = true;
  assert.equal(voice.cruise('speed_down', 10, 'x'.repeat(43), 4000), false);
  document.hidden = false;
  assert.equal(voice.cruise('speed_down', 10, 'x'.repeat(43), 999), false);
});

test('cruise never reports success for mismatched identities or invalid/missing device readback', async () => {
  globalThis.document = { hidden: false };
  const id = 'a'.repeat(43);
  for (const result of [
    { id: 'b'.repeat(43), status: 'applied', current: 100 },
    { id, status: 'applied' }, { id, status: 'unchanged', current: 0 }, { id, status: 'applied', current: NaN },
  ]) {
    const voice = createLocalVoice(null, () => true, async () => ({ result }), () => 1000);
    assert.ok(voice.cruise('speed_set', 100, id, 4000));
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(voice.result(id).status, 'unverified');
  }
});
