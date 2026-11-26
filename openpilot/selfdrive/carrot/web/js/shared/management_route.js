"use strict";

// Shared by the first-paint hint and the full page controller.
(() => {
  if (window.top !== window || window.FormosaCarrotRemote || location.search ||
      /CarrotWebAndroid|CarrotAssistPhone/i.test(navigator.userAgent)) return;

  const pages = new Map([["home","overview"], ["vision","carrot"], ["settings","setting"], ["tools","tools"], ["logs","logs"], ["terminal","terminal"]]);
  const hashes = new Map([...pages].map(([hash, page]) => [page, hash]));
  function startPage() {
    const direct = pages.get(location.hash.slice(1));
    if (direct) return direct;
    const setting = window.__CARROT_BOOTSTRAP__?.webSettings?.start_page || "last";
    if (setting !== "last") return undefined;
    try {
      if (!localStorage.getItem("carrot_web_last_page") || localStorage.getItem("carrot_manager_last_overview") === "true") return "overview";
    } catch { return "overview"; }
    return undefined;
  }
  window.CarrotManagementRoute = Object.freeze({
    startPage,
    pageUrl(page) { return hashes.has(page) ? "#" + hashes.get(page) : undefined; },
  });
})();
