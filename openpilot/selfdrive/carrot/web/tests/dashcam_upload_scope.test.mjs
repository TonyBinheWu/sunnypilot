import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";
import { dashcamUploadStats } from "../src/features/logs/upload_summary.js";

const source = await readFile(new URL("../src/features/logs/dashcam.js", import.meta.url), "utf8");
const uploadFunction = source.slice(source.indexOf("async function uploadDashcamSegments("), source.indexOf("async function uploadRecentDashcamSegments("));

test("completion dialog explains each receiver limit once, including failures outside the visible rows", () => {
  const render = source.slice(source.indexOf("function dashcamUploadResultHtml("), source.indexOf("async function showDashcamUploadResult("));
  const context = vm.createContext({
    dashcamUploadStats, DASHCAM_UPLOAD_RESULT_VISIBLE_LIMIT: 1,
    getUIText: (key) => key, escapeHtml: String, dashcamUploadSummaryLabel: (stats) => `bytes=${stats.bytes}`,
  });
  vm.runInContext(render, context);
  const results = ["upload_limit", "daily_upload_quota", "daily_upload_quota"].map((errorCode) => ({ ok: false, errorCode, totalSize: 100 }));
  results.push({ ok: true, totalSize: 24 });
  const html = context.dashcamUploadResultHtml({ results });
  assert.equal(html.match(/upload_daily_quota/g)?.length, 1);
  assert.equal(html.match(/upload_receiver_limit/g)?.length, 1);
  assert.match(html, /bytes=24</);
  assert.doesNotMatch(context.dashcamUploadResultHtml({ results: [{ ok: true }] }), /upload_daily_quota|upload_receiver_limit/);
});

async function runUpload(scope, confirm = true) {
  const requests = [];
  const summaries = [];
  const context = vm.createContext({
    dashcamUploadActiveJobId: null,
    getRememberedDashcamUploadJob: () => null,
    getUIText: (_key, fallback) => fallback,
    showAppToast: (message) => { throw new Error(message); },
    openAppDialog: async (options) => {
      assert.equal(options.choices[0].value, "default");
      assert.equal(options.choices[0].current, true);
      return scope;
    },
    appConfirm: async () => confirm,
    dashcamUploadConfirmHtml: (stats) => { summaries.push(stats); return "summary"; },
    dashcamUploadStats,
    postJson: async (url, body) => {
      requests.push({ url, ...body });
      if (url.endsWith("/summary")) return { summaries: [{
        segment: "route--0",
        files: [
          { name: "qcamera.ts", size: 10 }, { name: "rlog.zst", size: 20 },
          ...(body.includeAllFiles ? [{ name: "ecamera.hevc", size: 100 }, { name: "fcamera.hevc", size: 200 }] : []),
        ],
      }] };
      return { job_id: "job" };
    },
    rememberDashcamUploadJob() {},
    clearRememberedDashcamUploadJob() {},
    pollDashcamUploadJob: async () => ({ ok: true, uploaded: 1, total: 1, results: [] }),
    isDashcamUploadCanceledError: () => false,
  });
  vm.runInContext(uploadFunction, context);
  await context.uploadDashcamSegments(["route--0"], {
    showProgress: false, showResult: false, showSuccessToast: false,
  });
  return { requests, summaries };
}

for (const scope of ["default", "all"]) {
  test(`upload ${scope} uses the same scope for confirmation and transfer`, async () => {
    const { requests, summaries } = await runUpload(scope);
    assert.equal(requests.length, 2);
    assert.equal(requests[0].includeAllFiles, scope === "all");
    assert.equal(requests[1].includeAllFiles, scope === "all");
    assert.equal(summaries[0].files, scope === "all" ? 4 : 2);
    assert.equal(summaries[0].bytes, scope === "all" ? 330 : 30);
  });
}

test("canceling file selection sends no request", async () => {
  assert.equal((await runUpload(null)).requests.length, 0);
});

test("canceling size confirmation never starts an upload", async () => {
  const { requests } = await runUpload("all", false);
  assert.equal(requests.length, 1);
  assert.equal(requests[0].url, "/api/dashcam/upload/summary");
});
