import assert from "node:assert/strict";
import test from "node:test";
import { liveViewData, createLiveView } from "../src/features/drive/contents/vision/hud/live_view.js";
import { mapPayload } from "../src/features/drive/contents/vision/hud/index.js";
import { createLiveFrameHealth } from "../src/features/drive/contents/vision/hud/live_health.js";
import { installAndroidVision } from "../src/features/drive/contents/vision/android_vision.js";
import { currentVisionEvents, visionEventSnapshot } from "../src/features/drive/contents/vision/hud/live_events.js";

class Node {
  children = []; attrs = {}; listeners = {}; hidden = false; textContent = "";
  classList = { toggle() {} };
  appendChild(child) { this.children.push(child); return child; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(k, fn) { this.listeners[k] = fn; }
}
const find = (root, name) => root.className === name ? root : root.children.map(n => find(n, name)).find(Boolean);

test('Android Vision requires a trusted host opt-in, restores on exit and does not immediately reenter', () => {
  let active = true, replay = false, focused;
  const target = {document:{body:{dataset:{page:'carrot'},classList:{toggle:(_,v) => focused=v}}},
    CarrotVisionContentRuntime:{isActive:() => active}, CarrotVisionReplay:{isActive:() => replay},
    CarrotWebSettingsState:{vision_fullscreen_default:true}};
  const api = installAndroidVision(target);
  assert.equal(api.sync(), false);
  assert.equal(api.sync(true), true); assert.equal(focused, true);
  assert.equal(api.displayMode(), 'fit'); api.setDisplayMode('crop'); assert.equal(api.displayMode(),'crop');
  api.exit(); assert.equal(focused, false); assert.equal(api.sync(true), false);
  assert.equal(api.displayMode(),null);
  api.toggle(); assert.equal(focused, true);
  active = false; api.sync(); assert.equal(focused, false);
  active = true; assert.equal(api.sync(), true);
  replay = true; assert.equal(api.sync(), false);
  replay = false; target.CarrotWebSettingsState.vision_fullscreen_default = false;
  assert.equal(api.sync(), false); api.toggle(); assert.equal(focused, true);
  assert.equal(api.sync(false), false);
});

test('current events retain independent source freshness and do not fabricate missing driver inputs', () => {
  const state = {carState:{leftBlinker:true, leftBlindspot:true}, carControl:{latActive:true},
    selfdriveState:{enabled:true,alertSize:'small',alertText1:'請接管'}};
  const events = currentVisionEvents(state);
  assert.ok(events.some(e => e.text === '請接管'));
  assert.ok(events.some(e => e.key === 'replay_event_left_blindspot'));
  assert.ok(!events.some(e => e.key === 'replay_event_brake_pressed'));
  const target = {CarrotHudState:state,CarrotStateReceivedAtMonotonic:{carState:0,carControl:1900,selfdriveState:100}};
  const live = visionEventSnapshot(target,false,2000,99999);
  assert.deepEqual(live.rows.map(e => e.key),['replay_event_lateral_control_on']);
  assert.equal(visionEventSnapshot(target,false,4000,99999).available,false);
  assert.equal(visionEventSnapshot(target,true,4000,99999).rows.length,events.length);
  target.CarrotDeviceRuntimeState={isOffroad:true,isOnroad:false};
  assert.deepEqual(visionEventSnapshot(target,false,2000,99999).rows,[]);
});

test("Live View reuses normalized units and distinguishes absent speed from zero", () => {
  const mph = mapPayload({ vEgoKph: 100, vSetKph: 110, speedLimitKph: 90, isMetric: false, latActive: true });
  assert.deepEqual(liveViewData(mph, { metric: false }), {
    speed: "62", max: "68", limit: "56", unit: "mph", state: "vision_live_lateral",
  });
  assert.equal(liveViewData(mapPayload({ vEgoKph: 0 })).speed, "0");
  assert.equal(liveViewData(mapPayload({})).speed, "—");
  assert.equal(liveViewData(mph, { stale: true }).max, "—");
});

test("only actually presented frames prove video progress; HUD and WebRTC stats cannot", () => {
  const health = createLiveFrameHealth();
  const perf = { collectedAtMs: 10000, connectionState: "connected", network: {
    resolutionLabel: "1920 × 1080", rttMs: 12, bitrateMbps: 2.5,
  } };
  assert.equal(health.snapshot({ now: 1000, wallNow: 10001, perf }).state, "waiting");
  health.observe({ sequence: 0, source: "live", reason: "late-rtp-mapping" }, 900);
  assert.equal(health.snapshot({ now: 1000, wallNow: 10001, perf }).state, "waiting");
  health.observe({ sequence: 1, source: "live" }, 1000);
  health.observe({ sequence: 2, source: "live" }, 1100);
  health.observe({ sequence: 2, source: "live" }, 1150); // duplicate must not inflate FPS
  const live = health.snapshot({ now: 1200, wallNow: 10001, perf });
  assert.equal(live.state, "playing"); assert.equal(live.fps, 10); assert.equal(live.rttMs, 12);
  assert.equal(health.snapshot({ now: 3101, wallNow: 10002, perf }).state, "stalled");
  const stale = health.snapshot({ now: 3101, wallNow: 17000, perf });
  assert.equal(stale.rttMs, null); assert.equal(stale.resolution, "—");
  const replay = health.snapshot({ now: 90000, wallNow: 17000, perf, replay: true });
  assert.equal(replay.state, "replay"); assert.equal(replay.fps, null);
  health.reset();
  assert.equal(health.snapshot({ now: 5000, wallNow: 10000, perf: null }).state, "waiting");
});

test("presentation observers leave no subscription behind and framing failures preserve saved values", async () => {
  let listener, listeners = 0, fail = false, notice = false;
  const target = {
    getUIText: key => key, performance: { now: () => 100 },
    CarrotWebSettingsState: { vision_display_mode: "normal" },
    DriveVisionPresentedFrames: { subscribe(fn) { listener = fn; listeners++; return () => listeners--; } },
    async setWebSettingByKey(key, value) { if (fail) throw Error("offline"); this.CarrotWebSettingsState[key] = value; },
    showAppToast() { notice = true; },
  };
  const view = createLiveView({ createElement: () => new Node() }, target, { classic() {} });
  view.setActive(true); view.setActive(true);
  assert.equal(listeners, 1);
  listener({ sequence: 1, source: "live" }); view.render();
  assert.equal(find(view.root, "clive-health").textContent, "vision_live_stream_playing");
  const buttons = find(view.root, "clive-rail").children.slice(1);
  const click = node => node.listeners.click({ stopPropagation() {} });
  await click(buttons[3]);
  assert.equal(find(view.root, "clive-cluster").hidden, true);
  await click(buttons[4]);
  assert.equal(target.CarrotWebSettingsState.vision_display_mode, "crop");
  fail = true;
  await click(buttons[4]);
  assert.equal(target.CarrotWebSettingsState.vision_display_mode, "crop");
  assert.equal(notice, true);
  view.toggleTools();
  assert.equal(find(view.root, "clive-rail").hidden, true);
  assert.equal(find(view.root, "clive-tools-toggle").attrs["aria-expanded"], "false");
  view.setActive(false); view.setActive(false);
  assert.equal(listeners, 0);
  view.setActive(true); view.render();
  assert.equal(listeners, 1);
  assert.equal(find(view.root, "clive-health").textContent, "vision_live_stream_waiting");
  view.setActive(false);
});

test("stopped live updates clear values; paused replay retains its timeline; actions are display-only", () => {
  let clock = 0, fullscreen = 0, classic = 0, replay = false;
  const target = { getUIText: key => key, performance: { now: () => clock },
    ToggleCarrotFullscreen() { fullscreen++; }, CarrotVisionReplay: { status: () => ({ active: replay }) } };
  const view = createLiveView({ createElement: () => new Node() }, target, { classic: () => classic++ });
  view.update(mapPayload({ vEgoKph: 50, vSetKph: 65 }), {});
  assert.equal(find(view.root, "clive-speed").textContent, "50");
  clock = 2001; view.render();
  assert.equal(find(view.root, "clive-speed").textContent, "—");
  assert.equal(find(view.root, "clive-state").textContent, "vision_live_stale");
  replay = true; view.render();
  assert.equal(find(view.root, "clive-speed").textContent, "50");
  const buttons = find(view.root, "clive-rail").children.slice(1);
  const click = node => node.listeners.click({ stopPropagation() {} });
  click(buttons[0]); click(buttons[1]); click(buttons[2]);
  assert.equal(classic, 1); assert.equal(fullscreen, 1);
  assert.equal(find(view.root, "clive-details").hidden, false);
  view.reset();
  assert.equal(find(view.root, "clive-speed").textContent, "—");
});
