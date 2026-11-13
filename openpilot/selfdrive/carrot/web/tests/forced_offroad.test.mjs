import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { canToggle } from "../src/features/tools/forced_offroad.js";

test("offroad switch stays locked on stale, pending, missing or denied state", () => {
  for (const state of [null, {}, { ok: false, can_toggle: true, pending: false },
    { ok: true, can_toggle: false, pending: false }, { ok: true, can_toggle: true, pending: true }]) {
    assert.equal(canToggle(state), false);
  }
  assert.equal(canToggle({ ok: true, requested: false, active: false, can_toggle: true, pending: false }), true);
});

test("real switch re-locks on network loss and a Park-to-Drive race is rejected and resynced", async () => {
  const original = Object.fromEntries(["document", "fetch", "setTimeout", "clearTimeout", "getUIText"].map(key => [key, globalThis[key]]));
  const button = { dataset: {}, disabled: true, attrs: {}, setAttribute(k, v) { this.attrs[k] = v; },
    addEventListener(_type, callback) { this.click = callback; } };
  const detail = {};
  let nextPoll;
  let server = { ok: true, requested: false, active: false, can_toggle: true, pending: false, reason: "" };
  let posts = 0;
  let unavailable = false;
  try {
    globalThis.document = { hidden: false, getElementById: id => id === "btnForcedOffroad" ? button : detail };
    globalThis.setTimeout = callback => { nextPoll = callback; return 1; };
    globalThis.clearTimeout = () => {};
    globalThis.getUIText = (_key, fallback) => fallback;
    globalThis.fetch = async (_url, options) => {
      if (unavailable) throw new Error("offline");
      if (options.method === "POST") {
        posts++;
        assert.deepEqual(JSON.parse(options.body), { enabled: true });
        return { ok: false, json: async () => ({ ok: false, error: "park_required" }) };
      }
      return { ok: true, json: async () => server };
    };
    const source = await readFile(new URL("../src/features/tools/forced_offroad.js", import.meta.url), "utf8");
    await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
    globalThis.CarrotForcedOffroad.init();
    await new Promise(resolve => setImmediate(resolve));
    assert.equal(button.disabled, false);
    server = { ...server, can_toggle: false, reason: "park_required" }; // Shift after render, before click.
    await button.click();
    assert.equal(posts, 1);
    assert.equal(button.disabled, true);
    assert.equal(button.attrs["aria-checked"], "false");
    assert.match(detail.textContent, /P gear/);
    await button.click();
    assert.equal(posts, 1); // Locked UI cannot send another request.
    unavailable = true;
    await nextPoll();
    assert.equal(button.disabled, true);
    assert.match(detail.textContent, /Fresh vehicle data/);
  } finally {
    for (const [key, value] of Object.entries(original)) {
      if (value === undefined) delete globalThis[key]; else globalThis[key] = value;
    }
  }
});
