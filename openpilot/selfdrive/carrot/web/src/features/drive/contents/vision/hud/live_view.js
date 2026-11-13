import { el, setText } from "./dom.js";
import { createLiveFrameHealth } from "./live_health.js";

export function liveViewData(data, { stale = false, metric = true } = {}) {
  const value = (number) => !stale && Number.isFinite(number) ? String(number) : "—";
  return {
    speed: value(data?.speed), max: value(data?.setSpeed), limit: value(data?.speedLimit),
    unit: metric ? "km/h" : "mph",
    state: stale ? "vision_live_stale" : data?.lfaActive === true ? "vision_live_lateral" : "vision_live_monitor",
  };
}

// A presentation of the existing HUD payload, not another camera/data session.
export function createLiveView(doc, target, actions) {
  const text = (key) => target.getUIText?.(key) || key;
  const root = el(doc, "div", { class: "clive" });
  const rail = el(doc, "nav", { class: "clive-rail", attrs: { "aria-label": "Carrot Vision" } });
  const brand = el(doc, "strong", { class: "clive-brand", text: "CARROT" });
  const labels = [];
  function button(key, action, parent = rail) {
    const node = el(doc, "button", { attrs: { type: "button" } });
    node.addEventListener("click", (event) => { event.stopPropagation(); return action(); });
    labels.push([node, key]); parent.appendChild(node);
    return node;
  }
  rail.appendChild(brand);
  button("vision_live_classic", actions.classic);
  const fullscreenButton = button(null, async () => {
    try {
      const ok = await target.ToggleCarrotFullscreen?.({ quiet: false });
      if (ok === false) target.showAppToast?.(text("vision_live_fullscreen_hint"), { tone: "error" });
    } catch { target.showAppToast?.(text("vision_live_fullscreen_hint"), { tone: "error" }); }
    render();
  });
  let detailed = false, speedVisible = true, toolsVisible = true;
  const detailsButton = button("vision_live_details", () => {
    detailed = !detailed; details.hidden = !detailed;
    detailsButton.setAttribute("aria-expanded", String(detailed));
    render();
  });
  detailsButton.setAttribute("aria-expanded", "false");
  const speedButton = button(null, () => { speedVisible = !speedVisible; render(); });
  let saving = false;
  const displayButton = button(null, async () => {
    if (saving || typeof target.setWebSettingByKey !== "function") return;
    const modes = ["fit", "normal", "crop"];
    const current = target.CarrotWebSettingsState?.vision_display_mode || "normal";
    saving = true; render();
    try { await target.setWebSettingByKey("vision_display_mode", modes[(modes.indexOf(current) + 1) % modes.length]); }
    catch { target.showAppToast?.(text("vision_live_save_failed"), { tone: "error" }); }
    finally { saving = false; render(); }
  });
  const toolsButton = button(null, () => toggleTools(), root);
  toolsButton.className = "clive-tools-toggle";
  function toggleTools() {
    toolsVisible = !toolsVisible;
    rail.hidden = !toolsVisible;
    root.classList.toggle("tools-collapsed", !toolsVisible);
    toolsButton.setAttribute("aria-expanded", String(toolsVisible));
    if (!toolsVisible) {
      detailed = false; details.hidden = true; detailsButton.setAttribute("aria-expanded", "false");
      toolsButton.focus?.();
    }
    render();
    return true;
  }
  const cluster = el(doc, "div", { class: "clive-cluster" });
  const maxLabel = el(doc, "small"); labels.push([maxLabel, "vision_live_set_speed"]);
  const max = el(doc, "b");
  const speed = el(doc, "b", { class: "clive-speed" });
  const unit = el(doc, "small");
  const limitLabel = el(doc, "small"); labels.push([limitLabel, "vision_live_limit"]);
  const limit = el(doc, "b", { class: "clive-limit" });
  cluster.append(
    el(doc, "div", { class: "clive-cell" }, [maxLabel, max]),
    el(doc, "div", { class: "clive-dial" }, [speed, unit]),
    el(doc, "div", { class: "clive-cell" }, [limitLabel, limit]),
  );
  const state = el(doc, "div", { class: "clive-state", attrs: { role: "status" } });
  const healthLabel = el(doc, "div", { class: "clive-health", attrs: { role: "status" } });
  const vehicleDetail = el(doc, "div", { class: "clive-vehicle-detail" });
  const streamDetail = el(doc, "div", { class: "clive-stream-detail" });
  const details = el(doc, "section", { class: "clive-details" }, [vehicleDetail, streamDetail]);
  details.hidden = true;
  root.append(rail, cluster, state, healthLabel, details);
  let last = {}, isMetric = true, lastUpdate = null, active = false, unsubscribe = null;
  const now = () => target.performance?.now?.() ?? Date.now();
  const health = createLiveFrameHealth();
  function subscribe() {
    if (active && !unsubscribe && target.DriveVisionPresentedFrames?.subscribe) {
      unsubscribe = target.DriveVisionPresentedFrames.subscribe(frame => health.observe(frame, now()));
    }
  }
  function setActive(value) {
    const next = Boolean(value);
    if (active !== next) {
      active = next; health.reset();
      if (!active) { unsubscribe?.(); unsubscribe = null; }
    }
    subscribe();
  }
  function render() {
    if (root.hidden) return;
    subscribe();
    const replay = target.CarrotVisionReplay?.status?.()?.active === true;
    const stale = lastUpdate == null || (!replay && now() - lastUpdate > 2000);
    const model = liveViewData(last, { stale, metric: isMetric });
    const stream = health.snapshot({ now: now(), wallNow: Date.now(), replay, perf: target.CarrotRtcPerf });
    setText(speed, model.speed); setText(max, model.max); setText(limit, model.limit); setText(unit, model.unit);
    setText(state, text(model.state));
    setText(healthLabel, text(`vision_live_stream_${stream.state}`));
    healthLabel.setAttribute("data-state", stream.state);
    root.classList.toggle("is-stale", stale);
    cluster.hidden = !speedVisible;
    speedButton.setAttribute("aria-pressed", String(speedVisible));
    toolsButton.setAttribute("aria-expanded", String(toolsVisible));
    setText(speedButton, text(speedVisible ? "vision_live_hide_speed" : "vision_live_show_speed"));
    setText(toolsButton, text(toolsVisible ? "vision_live_hide_tools" : "vision_live_show_tools"));
    setText(fullscreenButton, text(doc.fullscreenElement ? "vision_live_exit_fullscreen" : "vision_live_fullscreen"));
    const display = target.CarrotWebSettingsState?.vision_display_mode || "normal";
    setText(displayButton, `${text("vision_live_framing")}: ${text(`display_${display}`)}`);
    displayButton.disabled = saving || typeof target.setWebSettingByKey !== "function";
    labels.forEach(([node, key]) => { if (key) setText(node, text(key)); });
    const val = (v) => stale || v == null ? "—" : String(v);
    setText(vehicleDetail, `${text("vision_live_gear")}: ${val(last.gear)} · ${text("vision_live_gap")}: ${val(last.gap)} · ${text("vision_live_temperature")}: ${val(last.cpuTemp)} °C`);
    const number = (v, digits = 0) => v == null ? "—" : v.toFixed(digits);
    setText(streamDetail, `${text("vision_live_stream_stats")}: ${stream.resolution} · ${number(stream.fps)} fps · RTT ${number(stream.rttMs)} ms · ${number(stream.bitrateMbps, 2)} Mbps`);
  }
  return {
    root, render, setActive, toggleTools,
    update(data, payload) { last = data; isMetric = payload.isMetric !== false; lastUpdate = now(); render(); },
    reset() { last = {}; lastUpdate = null; health.reset(); render(); },
  };
}

export const LIVE_VIEW_CSS = `
.clive{display:none;position:absolute;inset:0;z-index:1;font-family:system-ui,sans-serif;color:#fff;font-weight:600}
.chud.is-live-view .clive{display:block}
.chud.is-live-view .chud-zone:not(.chud-zone--tc),.chud.is-live-view .chud-corner{display:none}
.chud.is-live-view::before{background:linear-gradient(#05090b70,transparent);height:20%}
.clive-rail{position:absolute;left:8px;top:8px;bottom:8px;width:76px;overflow-y:auto;display:flex;flex-direction:column;align-items:stretch;gap:10px;padding:12px 6px;box-sizing:border-box;border:1px solid #ffffff20;border-radius:16px;background:#0b121be8;pointer-events:auto}
.clive-brand{font-size:12px;color:#50dfc1;text-align:center;margin:6px 0 16px;letter-spacing:1px}
.clive-rail button{min-height:44px;border:1px solid #ffffff24;border-radius:10px;color:#e9f8f5;background:#ffffff09;font:inherit;font-size:12px;cursor:pointer;padding:6px 2px;touch-action:manipulation}
.clive-rail button:focus-visible,.clive-tools-toggle:focus-visible{outline:3px solid #50dfc1;outline-offset:2px}
.clive-rail button{flex-shrink:0}
.clive-tools-toggle{position:absolute;right:8px;top:8px;min-width:96px;min-height:44px;pointer-events:auto;border:1px solid #ffffff40;border-radius:12px;padding:8px 12px;color:#effffa;background:#0b121bf0;font:600 12px system-ui;cursor:pointer;touch-action:manipulation}
.clive.tools-collapsed .clive-cluster{left:50%;max-width:calc(100% - 24px)}
.clive.tools-collapsed .clive-state,.clive.tools-collapsed .clive-health{left:8px}
.clive-health{position:absolute;left:98px;top:46px;max-width:calc(100% - 220px);padding:5px 10px;border:1px solid #ffffff20;border-radius:8px;color:#b8ced7;background:#0b121be8;font-size:11px}
.clive-health[data-state=playing]{color:#50dfc1}.clive-health[data-state=stalled],.clive-health[data-state=reconnecting]{color:#ffc46b}
.clive-stream-detail{margin-top:8px;border-top:1px solid #ffffff28;padding-top:8px;font-variant-numeric:tabular-nums}
.clive-rail button:disabled{opacity:.5;cursor:wait}
.clive-cluster{position:absolute;bottom:14px;left:calc(50% + 38px);transform:translateX(-50%);display:flex;align-items:center;gap:20px;padding:12px 24px;border:1px solid #ffffff24;border-radius:24px;background:#0b121bef;box-shadow:0 6px 28px #0006;font-variant-numeric:tabular-nums;max-width:calc(100% - 110px);box-sizing:border-box}
.clive-cell{display:flex;align-items:center;flex-direction:column;gap:7px;min-width:40px}.clive-cell small{font-size:11px;color:#a9bfca;white-space:nowrap}.clive-cell b{font-size:25px}
.clive-dial{display:flex;flex-direction:column;align-items:center;justify-content:center;width:100px;height:85px;border:4px solid #50dfc1;border-bottom-color:transparent;border-radius:60px 60px 20px 20px;box-sizing:border-box;padding-top:8px}
.clive-dial .clive-speed{font-size:40px;line-height:1;letter-spacing:-1px}.clive-dial small{font-size:11px;color:#b2c7d0;margin-top:5px}
.clive-cell .clive-limit{background:#fff;color:#10161c;border:3px solid #e25d5d;border-radius:50%;width:44px;height:44px;line-height:44px;text-align:center;font-size:23px;box-sizing:content-box}
.clive-state{position:absolute;left:98px;top:14px;border-radius:8px;padding:7px 11px;background:#0b121be8;color:#50dfc1;font-size:12px}
.clive-details{position:absolute;left:98px;top:84px;overflow:auto;max-height:calc(100% - 100px);max-width:calc(100% - 120px);padding:10px;border:1px solid #ffffff24;border-radius:10px;background:#0b121bef;font-size:12px;line-height:1.5}
.clive.is-stale .clive-state{color:#ffc46b}.clive.is-stale .clive-dial{border-color:#62717b;border-bottom-color:transparent}
@container chud (max-width:540px){
 .clive-rail{top:auto;bottom:8px;left:8px;right:8px;width:auto;height:104px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;padding:4px;align-items:stretch;border-radius:12px}
 .clive-brand{display:none}.clive-rail button{min-height:44px;font-size:11px;padding:4px;line-height:1.2}
 .clive-cluster{bottom:124px;left:50%;gap:14px;padding:9px 16px;max-width:calc(100% - 16px)}
 .clive.tools-collapsed .clive-cluster{bottom:14px}
 .clive-state{left:8px;top:8px;max-width:calc(100% - 140px)}.clive-health{left:8px;top:46px;max-width:calc(100% - 32px)}
 .clive-details{left:8px;top:84px;max-width:calc(100% - 36px)}
 .clive-dial{width:88px;height:78px}.clive-dial .clive-speed{font-size:36px}
}
@container chud (max-width:540px) and (max-height:270px){.clive-rail{display:flex;overflow-x:auto;height:52px;gap:4px}.clive-rail button{min-width:84px}.clive-cluster{bottom:70px;padding:5px 12px;gap:10px}.clive-dial{height:64px;width:78px}.clive-dial .clive-speed{font-size:30px}}
@container chud (min-width:541px) and (max-height:270px){.clive-cluster{bottom:6px;padding:4px 14px;gap:12px}.clive-dial{height:62px;width:80px}.clive-dial .clive-speed{font-size:29px}.clive-rail{gap:4px;padding:4px}.clive-brand{margin:0 0 3px}.clive-rail button{min-height:44px}}
`;
