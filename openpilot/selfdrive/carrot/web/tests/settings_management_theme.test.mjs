import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { pathToFileURL } from "node:url";
import { promisify } from "node:util";

const web = new URL("../", import.meta.url);
const chrome = [
  process.env.CHROME_BIN, "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  join(process.env.ProgramFiles || "", "Google/Chrome/Application/chrome.exe"),
  join(process.env["ProgramFiles(x86)"] || "", "Microsoft/Edge/Application/msedge.exe"),
].find(path => path && existsSync(path));

// Run inside Chromium. Painting the computed colors includes color-mix() and
// translucent state backgrounds in the measurement.
function measure() {
  const root = document.documentElement;
  const canvas = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
  function paint(color) {
    canvas.fillStyle = color;
    canvas.fillRect(0, 0, 1, 1);
  }
  function luminance() {
    const rgb = [...canvas.getImageData(0, 0, 1, 1).data].slice(0, 3).map(byte => {
      const channel = byte / 255;
      return channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4;
    });
    return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2];
  }
  function contrast(element) {
    const layers = [];
    for (let e = element; e; e = e.parentElement) layers.unshift(getComputedStyle(e).backgroundColor);
    paint("white");
    layers.forEach(paint);
    const bg = luminance();
    paint(getComputedStyle(element).color);
    const fg = luminance();
    return (Math.max(bg, fg) + .05) / (Math.min(bg, fg) + .05);
  }
  function sheet() { return getComputedStyle(document.querySelector(".app-dialog__sheet")).backgroundColor; }
  const original = sheet();
  const results = {};
  root.classList.add("carrot-manager");
  for (const theme of ["light", "dark"]) {
    root.dataset.managerTheme = theme;
    for (const page of ["overview", "tools", "setting", "logs", "car", "branch"]) {
      root.dataset.page = document.body.dataset.page = page;
      results[theme + "/" + page] = {
        scheme: getComputedStyle(document.querySelector("select")).colorScheme,
        contrasts: Object.fromEntries([...document.querySelectorAll("[data-probe]")]
          .map(el => [el.dataset.probe, contrast(el)])),
      };
    }
  }
  root.dataset.managerTheme = "light";
  root.dataset.page = document.body.dataset.page = "carrot";
  const driving = sheet();
  root.dataset.page = document.body.dataset.page = "setting";
  root.classList.remove("carrot-manager");
  document.querySelector("output").textContent = JSON.stringify({ results, original, driving, embedded: sheet() });
}

test("management popup colors resolve together across page and theme changes", { skip: !chrome && "Chromium unavailable" }, async () => {
  const index = await readFile(new URL("index.html", web), "utf8");
  const styles = [...index.matchAll(/<link rel="stylesheet" href="\/([^"]+)"/g)]
    .map(([, href]) => '<link rel="stylesheet" href="' + new URL(href, web).href + '">').join("\n");
  const dir = await mkdtemp(join(tmpdir(), "carrot-popup-"));
  try {
    const file = join(dir, "theme.html");
    await writeFile(file, '<!doctype html><meta charset="UTF-8">' + styles + `
      <body class="carrot-flat"><div class="app-dialog is-open"><div class="app-dialog__sheet">
        <strong class="app-dialog__title" data-probe="title">Language</strong>
        <span class="app-dialog__body" data-probe="body">Current language</span>
        <div class="app-dialog__choices app-dialog__choices--list">
          <button class="btn app-dialog__choiceBtn app-dialog__choiceBtn--action" data-probe="choice">English</button>
          <button class="btn app-dialog__choiceBtn app-dialog__choiceBtn--action is-current" data-probe="selected">繁體中文</button>
        </div><input class="input-text" value="Input" data-probe="input">
        <span class="app-dialog__inputError" data-probe="error">Error</span>
        <button id="appDialogConfirm" class="smallBtn btn--filled" data-probe="confirm">OK</button>
      </div></div><div class="ui-dropdown-menu__panel"><button class="ui-dropdown-menu__item" data-probe="menu">Menu</button></div>
      <div id="pageTools"><div class="model-library"><select class="form-select" data-probe="model"><option>Model</option></select></div>
        <div class="egpu-model-card" data-state="compiled"><span class="egpu-model-card__state" data-probe="ready">Ready</span></div>
        <div class="egpu-model-card" data-state="error"><span class="egpu-model-card__state" data-probe="failed">Failed</span></div></div>
      <output></output><script>(${measure.toString()})()</script>`);
    const { stdout } = await promisify(execFile)(chrome, [
      "--headless", "--disable-gpu", "--disable-extensions", "--no-first-run", "--dump-dom",
      "--user-data-dir=" + join(dir, "profile"), pathToFileURL(file).href,
    ], { timeout: 30_000, windowsHide: true });
    const { results, original, driving, embedded } = JSON.parse(stdout.match(/<output>([^<]+)<\/output>/)[1]);
    for (const [location, { scheme, contrasts }] of Object.entries(results)) {
      assert.equal(scheme, location.split("/")[0], location);
      for (const [role, ratio] of Object.entries(contrasts)) assert.ok(ratio >= 4.5, location + " " + role + " " + ratio);
    }
    assert.equal(driving, original);
    assert.equal(embedded, original);
  } finally {
    await rm(dir, { recursive: true, force: true, maxRetries: 3, retryDelay: 100 });
  }
});
