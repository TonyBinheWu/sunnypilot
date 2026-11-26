import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../js/shared/management_route.js", import.meta.url), "utf8");

function route({ hash = "", search = "", ua = "", nested = false, remote = false, setting = "last", saved = {}, blockedStorage = false } = {}) {
  const window = { __CARROT_BOOTSTRAP__: { webSettings: { start_page: setting } } };
  window.top = nested ? {} : window;
  if (remote) window.FormosaCarrotRemote = {};
  const localStorage = { getItem(key) {
    if (blockedStorage) throw new Error("Storage unavailable");
    return saved[key] ?? null;
  }};
  vm.runInNewContext(source, { window, location: { hash, search }, navigator: { userAgent: ua }, localStorage });
  return window.CarrotManagementRoute;
}

test("management overview honors explicit start pages and the last native page", () => {
  assert.equal(route().startPage(), "overview");
  assert.equal(route({ blockedStorage: true }).startPage(), "overview");
  assert.equal(route({ setting: "tools" }).startPage(), undefined);
  assert.equal(route({ saved: { carrot_web_last_page: "carrot" } }).startPage(), undefined);
  assert.equal(route({ saved: { carrot_web_last_page: "tools", carrot_manager_last_overview: "true" } }).startPage(), "overview");
});

test("each shareable management destination restores the same native page", () => {
  for (const [hash, page] of Object.entries({home:"overview", vision:"carrot", settings:"setting", tools:"tools", logs:"logs", terminal:"terminal"})) {
    const router = route({ hash: "#" + hash, setting: "setting" });
    assert.equal(router.startPage(), page);
    assert.equal(router.pageUrl(page), "#" + hash);
  }
  assert.equal(route().pageUrl("branch"), undefined);
});

test("embedded, remote and native app sessions retain their own navigation", () => {
  for (const options of [{ nested:true }, { search:"?cockpit_embed=1" }, { search:"?mini_hud=force" }, { ua:"CarrotWebAndroid/0.1" }, { remote:true }]) {
    assert.equal(route(options), undefined);
  }
});
