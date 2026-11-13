import assert from "node:assert/strict";
import test from "node:test";
import { liveViewData, createLiveView } from "../src/features/drive/contents/vision/hud/live_view.js";
import { mapPayload } from "../src/features/drive/contents/vision/hud/index.js";

class Node {
  children = []; attrs = {}; listeners = {}; hidden = false; textContent = "";
  classList = { toggle() {} };
  appendChild(child) { this.children.push(child); return child; }
  append(...children) { this.children.push(...children); }
  setAttribute(k, v) { this.attrs[k] = v; }
  addEventListener(k, fn) { this.listeners[k] = fn; }
}
const find = (root, name) => root.className === name ? root : root.children.map(n => find(n, name)).find(Boolean);

test("Live View reuses normalized units and distinguishes absent speed from zero", () => {
  const mph = mapPayload({ vEgoKph: 100, vSetKph: 110, speedLimitKph: 90, isMetric: false, latActive: true });
  assert.deepEqual(liveViewData(mph, { metric: false }), {
    speed: "62", max: "68", limit: "56", unit: "mph", state: "vision_live_lateral",
  });
  assert.equal(liveViewData(mapPayload({ vEgoKph: 0 })).speed, "0");
  assert.equal(liveViewData(mapPayload({})).speed, "—");
  assert.equal(liveViewData(mph, { stale: true }).max, "—");
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
