"use strict";

const API = "/api/device/forced_offroad";
let lastStatus = null;
let busy = false;
let timer = null;
const FALLBACK = {
  title: "Force offroad (Park only)", on: "On", off: "Off",
  help: "Park, stop and disengage assistance to change this switch. Driving processes stop. Leaving Park or losing vehicle data cancels the mode. Resets after restart.",
  vehicle_unavailable: "Fresh vehicle data is required.", park_required: "Only available in P gear.",
  moving: "Stop the vehicle before changing this switch.", controls_unavailable: "Waiting for assistance status.",
  controls_active: "Disengage steering and cruise assistance first.", pending: "Switching mode...",
  active: "Forced offroad is active.", normal: "Normal automatic mode.", boolean_required: "Invalid switch value.",
};

function text(key) {
  return typeof getUIText === "function" ? getUIText(`forced_offroad_${key}`, FALLBACK[key] || FALLBACK.vehicle_unavailable)
    : FALLBACK[key] || FALLBACK.vehicle_unavailable;
}

export function canToggle(status) {
  return status?.ok === true && typeof status.requested === "boolean" && typeof status.active === "boolean"
    && status.can_toggle === true && status.pending === false;
}

function render() {
  const button = document.getElementById("btnForcedOffroad");
  const detail = document.getElementById("forcedOffroadDetail");
  if (!button || !detail) return;
  const checked = lastStatus?.requested === true;
  button.textContent = `${text("title")}: ${text(checked ? "on" : "off")}`;
  button.setAttribute("aria-checked", String(checked));
  button.disabled = busy || !canToggle(lastStatus);
  const reason = lastStatus?.reason || (lastStatus?.active ? "active" : "normal");
  detail.textContent = `${text(reason)} ${text("help")}`;
}

async function refresh() {
  try {
    const response = await fetch(API, { cache: "no-store", credentials: "same-origin" });
    if (!response.ok) throw new Error("status unavailable");
    lastStatus = await response.json();
  } catch {
    lastStatus = { ok: false, reason: "vehicle_unavailable" };
  }
  render();
  clearTimeout(timer);
  timer = setTimeout(refresh, document.hidden ? 3000 : 500);
}

async function change() {
  if (busy || !canToggle(lastStatus)) return;
  busy = true;
  render();
  try {
    const response = await fetch(API, { method: "POST", credentials: "same-origin",
      headers: { "Content-Type": "application/json" }, body: JSON.stringify({ enabled: !lastStatus.requested }) });
    const result = await response.json();
    if (!response.ok || result.ok !== true) throw new Error(result.error || "vehicle_unavailable");
    lastStatus = result;
  } catch (error) {
    if (typeof globalThis.showAppToast === "function") globalThis.showAppToast(text(error.message), { tone: "error" });
  } finally {
    busy = false;
    await refresh();
  }
}

function init() {
  const button = document.getElementById("btnForcedOffroad");
  if (!button || button.dataset.bound === "1") return;
  button.dataset.bound = "1";
  button.addEventListener("click", change);
  refresh();
}

globalThis.CarrotForcedOffroad = Object.freeze({ init, render });
