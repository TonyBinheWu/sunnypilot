import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../js/pages/setting_device_actions.js", import.meta.url), "utf8");

function switchFixture(initial, fail = false) {
  const writes = [], errors = [], prompts = [];
  let resolveDialog, change;
  const input = {
    checked: initial, disabled: false,
    closest: () => ({ dataset: { param: "OpenpilotEnabledToggle" } }),
    addEventListener: (_, listener) => { change = listener; },
  };
  const context = vm.createContext({
    getUIText: (_, fallback) => fallback,
    appConfirm: (message, options) => {
      prompts.push({ message, options });
      return new Promise(resolve => { resolveDialog = resolve; });
    },
    setParam: async (name, value) => {
      writes.push([name, value]);
      if (fail) throw new Error("offline");
    },
    showAppToast: message => errors.push(message),
  });
  vm.runInContext(source, context);
  context.bindDeviceToggleRows({ querySelectorAll: () => [input] });
  return {
    input, writes, errors, prompts,
    tap() {
      if (!input.disabled) input.checked = !input.checked;
      return change({ target: input });
    },
    answer: value => resolveDialog(value),
  };
}

test("turning off waits for confirmation every time and ignores repeated taps", async () => {
  const ui = switchFixture(true);
  let action = ui.tap();
  assert.equal(ui.input.checked, true);
  assert.equal(ui.input.disabled, true);
  await ui.tap();
  assert.equal(ui.prompts.length, 1);
  assert.deepEqual(ui.writes, []);
  ui.answer(false);
  await action;
  assert.deepEqual(ui.writes, []);
  assert.equal(ui.input.checked, true);
  assert.equal(ui.input.disabled, false);

  action = ui.tap();
  assert.equal(ui.prompts.length, 2);
  ui.answer(true);
  await action;
  assert.deepEqual(ui.writes, [["OpenpilotEnabledToggle", 0]]);
  assert.equal(ui.input.checked, false);
  await ui.tap();
  assert.equal(ui.prompts.length, 2);
  assert.equal(ui.input.checked, true);
  assert.deepEqual(ui.writes.at(-1), ["OpenpilotEnabledToggle", 1]);
});

test("an unacknowledged disable keeps the switch on and available to retry", async () => {
  const ui = switchFixture(true, true);
  const action = ui.tap();
  ui.answer(true);
  await action;
  assert.equal(ui.input.checked, true);
  assert.equal(ui.input.disabled, false);
  assert.deepEqual(ui.errors, ["offline"]);
});
