import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";

const source = name => readFileSync(new URL(`../js/realtime/${name}.js`, import.meta.url), "utf8");
const section = (s, start, end) => s.slice(s.indexOf(start), s.indexOf(end, s.indexOf(start)));

test("parked viewing is not a source block; replay and hidden modes retain their own policy", () => {
  const context = vm.createContext({ isCarrotPageActive: () => true, isCarrotVisionActive: () => true,
    isCarrotRecordedReplayActive: () => false, isCarrotVisionParked: () => true, window: {} });
  vm.runInContext(section(source("app_realtime"), "function getCarrotVisionRealtimeBlockReason", "function isCarrotVisionRealtimeSourceReady"), context);
  assert.equal(vm.runInContext("getCarrotVisionRealtimeBlockReason()", context), "");
  context.isCarrotRecordedReplayActive = () => true;
  assert.equal(vm.runInContext("getCarrotVisionRealtimeBlockReason()", context), "recorded-replay");
});

test("parked source drops retained driving messages but recorded replay keeps its data", () => {
  let replay = false;
  const context = vm.createContext({ window: { CarrotDeviceRuntimeState: { isOffroad: true, isOnroad: false } },
    recordedReplayActive: () => replay, RAW_HUD_STATE: { carState: { vEgo: 20 } }, RAW_OVERLAY_STATE: {},
    RAW_STATE_UPDATED_AT: {}, RAW_STATE_RECEIVED_AT_MONOTONIC: {}, RAW_HUD_SERVICES: ["carState"],
    isOverlayStateService: () => false, setCarrotVisionState() {}, _hudMarkDirty() {}, emitCarrotRenderRequest() {} });
  vm.runInContext(section(source("vision_raw"), "const PARKED_DRIVING_SERVICES", "function applyCompactFrames"), context);
  assert.equal(vm.runInContext('applyCompactFrame("carState", {vEgo:30})', context), false);
  assert.equal(context.RAW_HUD_STATE.carState, undefined);
  replay = true;
  assert.equal(vm.runInContext('applyCompactFrame("carState", {vEgo:30})', context), true);
  assert.equal(context.RAW_HUD_STATE.carState.vEgo, 30);
  replay = false; context.window.CarrotDeviceRuntimeState.isOnroad = true;
  assert.equal(vm.runInContext('applyCompactFrame("carState", {vEgo:10})', context), true);
});

test("parked phase text follows actual stream progress instead of forcing the old parked wait", () => {
  const window = { addEventListener() {}, dispatchEvent() {} };
  const context = vm.createContext({ window, getUIText: key => key, CustomEvent: class {} });
  vm.runInContext(source("vision_state"), context);
  window.CarrotVisionSetState({ active: true, environment: { isOffroad: true, testActive: false } });
  window.CarrotVisionSetPhase(window.CarrotVisionPhase.RTC_CONNECTING);
  assert.equal(window.CarrotVisionState.statusText, "connecting");
  window.CarrotVisionSetPhase(window.CarrotVisionPhase.READY);
  assert.equal(window.CarrotVisionState.statusText, "connected");
});
