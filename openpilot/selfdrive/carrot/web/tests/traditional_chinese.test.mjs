import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";
import { normalizeSettingsCatalog } from "../src/features/settings/catalog.js";
import { createSettingsDerivedModel, localizedSettingItemText, localizedSettingNodeLabel } from "../src/features/settings/derived_model.js";

const read = (path) => readFileSync(new URL(path, import.meta.url), "utf8");
function context(language = "zh-TW") {
  const window = { __CARROT_BOOTSTRAP__: {} };
  const ctx = vm.createContext({ window, navigator: { language, languages: [language] },
    localStorage: { getItem: () => null }, LANG_STORAGE_KEY: "language", btnLang: null, btnSettingLang: null });
  for (const file of ["registry", "en", "ko", "zh", "zh-tw"]) {
    vm.runInContext(read(`../js/translations/${file}.js`), ctx);
  }
  vm.runInContext(read("../js/shared/i18n.js"), ctx);
  return ctx;
}

test("Traditional aliases stay distinct from Simplified and survive language cycling", () => {
  const ctx = context();
  for (const tag of ["zh-TW", "zh-Hant", "zh-Hant-TW", "zh-HK", "zh-MO", "zh_CHT", "main_zh-CHT"]) {
    assert.equal(vm.runInContext(`normalizeLangCode(${JSON.stringify(tag)})`, ctx), "zh-tw", tag);
  }
  for (const tag of ["zh", "zh-CN", "zh-Hans", "main_zh-CHS"]) {
    assert.equal(vm.runInContext(`normalizeLangCode(${JSON.stringify(tag)})`, ctx), "zh", tag);
  }
  assert.equal(vm.runInContext("LANG", ctx), "zh-tw");
  assert.ok(ctx.window.CARROT_WEB_LANGUAGE_CODES.includes("zh-tw"));
  ctx.window.__CARROT_BOOTSTRAP__.webSettings = { web_language: "en" };
  assert.equal(vm.runInContext("detectDefaultLang()", ctx), "en");
});

test("Traditional pack covers every English key and preserves interpolation contracts", () => {
  const { packs } = context().window.CarrotTranslations;
  const placeholders = (value) => [...String(value).matchAll(/\{([a-zA-Z_]\w*)\}/g)].map((m) => m[1]).sort();
  for (const section of ["strings", "actionLabels", "driveModes", "errorMessages"]) {
    const check = (en, tw, path) => {
      for (const [key, value] of Object.entries(en)) {
        assert.ok(key in tw, `${path}.${key}`);
        if (value && typeof value === "object") check(value, tw[key], `${path}.${key}`);
        else if (typeof value === "string") assert.deepEqual(placeholders(tw[key]), placeholders(value), `${path}.${key}`);
        else if (typeof value === "function") assert.equal(typeof tw[key], "function");
      }
    };
    check(packs.en[section], packs["zh-tw"][section], section);
  }
  assert.equal(packs["zh-tw"].nativeName, "繁體中文");
});

test("Traditional catalog labels reach categories, option labels and setting search", () => {
  const data = JSON.parse(read("../../../carrot_settings.json"));
  for (const item of data.params) {
    if (item.ctitle) assert.ok(item.ttitle, item.name);
    if (item.cdescr) assert.ok(item.tdescr, item.name);
    if (item.options?.zh) assert.equal(item.options["zh-tw"].length, item.options.zh.length, item.name);
  }
  const item = data.params.find((p) => p.ttitle?.includes("車道"));
  assert.ok(item);
  const group = data.menu[0].groups[0];
  const category = { ...data.menu[0], groups: [{ ...group, sections: [{ id: "one", "zh-tw": "分類", items: [item.name] }] }] };
  const catalog = normalizeSettingsCatalog({ categories: [category], items_by_group: { original: [item] } });
  assert.equal(localizedSettingNodeLabel(catalog.groups[0], "zh-tw"), group["zh-tw"]);
  assert.equal(localizedSettingItemText(item, "title", "etitle", "", "zh-tw"), item.ttitle);
  const model = createSettingsDerivedModel({ catalog, language: "zh-tw" });
  assert.ok(model.searchItemEntries("車道").entries.some((entry) => entry.item.name === item.name));
});

test("first-run wizard offers and detects Traditional Chinese separately", () => {
  const ctx = vm.createContext({ navigator: { languages: ["zh-Hant-TW"], language: "zh-Hant-TW" } });
  vm.runInContext(read("../src/features/intro/i18n.js"), ctx);
  assert.equal(ctx.detectCarrotIntroLang(), "zh-tw");
  assert.ok(ctx.CarrotIntroLangs.some(([code, name]) => code === "zh-tw" && name === "繁體中文"));
  assert.ok(ctx.CarrotIntroI18n["zh-tw"]);
});


test("all bundled Traditional setting pages load locally with verified hashes and no fallback", async () => {
  const { installSettingsRuntimeFacade } = await import("../src/features/settings/index.js");
  const root = new URL("../docs/settings/", import.meta.url);
  const index = JSON.parse(readFileSync(new URL("Settings-Catalog.json", root), "utf8"));
  const calls = [];
  const target = new EventTarget();
  target.fetch = async (url) => {
    calls.push(url);
    assert.ok(url.startsWith("/docs/settings/"), url);
    const name = decodeURIComponent(url.split("?")[0].split("/").pop());
    return new Response(readFileSync(new URL(name, root), "utf8"));
  };
  const { runtime } = installSettingsRuntimeFacade(target, { preload: false });
  const catalog = JSON.parse(read("../../../carrot_settings.json"));
  assert.equal(Object.keys(index.settings).length, catalog.params.length);
  for (const setting of catalog.params) {
    const page = await runtime.docs.load(setting.name, "zh-tw");
    assert.equal(page.available, true, setting.name);
    assert.equal(page.language_resolved, "zh-tw", setting.name);
    assert.equal(page.fallback, false, setting.name);
    const english = readFileSync(new URL(index.settings[setting.name].locales.en.page, root), "utf8");
    if (english.includes("<!-- CARROT:SECTION:BEGIN BEHAVIOR -->")) {
      assert.ok(page.sections.some(section => section.kind === "behavior"), `${setting.name}: detailed behavior`);
    }
    if (setting.name === "PathOffset") {
      assert.ok(page.sections.find(section => section.kind === "usage").markdown.includes("平坦直路"));
    }
  }
  assert.ok(calls.length > catalog.params.length);
});

test("Bluetooth Traditional text covers every English control and preserves timing limits", async () => {
  const { BLUETOOTH_ZH_TW } = await import("../src/features/tools/bluetooth_zh_tw.js");
  const source = read("../src/features/tools/bluetooth.js");
  const english = source.slice(source.indexOf("  en: {"), source.indexOf("\n};"));
  const keys = [...english.matchAll(/(?:^|[,\n])\s*(\w+|"[12]"):\s*"/g)].map(m => m[1].replaceAll('"', ''));
  for (const key of keys) assert.ok(BLUETOOTH_ZH_TW[key], key);
  for (const limit of ["350", "700", "500", "10"]) assert.ok(BLUETOOTH_ZH_TW.gestures.includes(limit));
});
