import assert from "node:assert/strict";
import test from "node:test";
import { scaledFontSize, installDisplayPreferences } from "../src/shared/web/display_preferences.js";

test("text scaling preserves nested relative fonts and existing font scaling", () => {
  for (const size of ["", "inherit", "1.2em", "90%", "calc(12px * var(--carrot-text-scale))"])
    assert.equal(scaledFontSize(size), null, size);
  for (const size of ["14px", "1rem", "clamp(12px, 2vw, 20px)", "var(--fs-label-md)"])
    assert.match(scaledFontSize(size), /--carrot-text-scale/);
});

test("preference changes affect text only and reject invalid saved sizes", () => {
  const props = new Map();
  const root = { style: { setProperty: (k,v) => props.set(k,v) }, dataset: {} };
  const document = { documentElement: root, readyState: "loading", addEventListener() {} };
  const target = { document, __CARROT_BOOTSTRAP__: { webSettings: { web_text_scale: "150" } } };
  const api = installDisplayPreferences(target);
  assert.equal(props.get("--carrot-text-scale"), "1.5");
  assert.equal(root.dataset.textScale, "150");
  api.apply({ web_text_scale: "200" });
  assert.equal(props.get("--carrot-text-scale"), "2");
  api.apply({ web_text_scale: "9999" });
  assert.equal(props.get("--carrot-text-scale"), "1");
  assert.deepEqual([...props.keys()], ["--carrot-text-scale"]);
});
