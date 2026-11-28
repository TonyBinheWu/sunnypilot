const EN = {
  title: "sunnypilot driving model selector", small: "Small model · built-in GPU", large: "Large model · eGPU",
  primary: "Primary model after reboot", auto: "Prefer external large model", internal: "Internal small model",
  scene: "C3X / C4 device display", legacy: "Use device layout", dynamic: "Dynamic 3D", camera: "Camera", perception: "Model perception 3D",
  help: "Both model choices are saved separately. First use downloads and verifies the model. Restart the parked device to apply.",
  parked: "Turn the ignition off to change these settings.", boot: "Selected for this boot", loading: "Loading models…",
  unavailable: "Cannot load the model list. Checking the connection…", preparing: "Preparing model…",
  connecting: "Connecting", downloading: "Downloading", verifying: "Verifying file", installing: "Installing",
  receiving: "received",
  failed: "Preparation failed. Check the connection and free space, then select the model again.",
  load_failed: "Model failed to load this boot", saved: "Saved for next boot", jetson: "Jetson model",
  lat2v_forced_offroad: "Forced offroad is active. Turn the ignition off.",
  lat2v_engaged: "Disengage assistance and turn the ignition off.",
  lat2v_offroad: "Wait for ignition-off offroad mode.",
  lat2v_unsaved: "Preparation stopped before the choice was saved.",
  lat2v_retry: "Prepare lat2v again",
  lat2v_unsupported: "Requires a comma four",
  lat2v_queued: "Queued for download",
  lat2v_waiting_offroad: "Queued · waiting for ignition off",
  lat2v_preparing: "Preparing model on C4",
  lat2v_retry_download: "Download interrupted · will retry",
  lat2v_waiting_egpu: "Downloaded · waiting for powered 5 Gbps Chestnut",
  lat2v_verifying_gpu: "Verifying on eGPU",
  lat2v_failed: "Verification failed",
};
const t = key => typeof getUIText === "function" ? getUIText("driving_models_" + key, EN[key]) : EN[key];
function element(tag, value) {
  const node = document.createElement(tag);
  node.textContent = value;
  return node;
}

let catalogRequest;
let latest;
let writing = false;
let version = 0;
const transferViews = new WeakMap();

function transferView(root, model) {
  const box = element("div", "");
  box.className = "model-transfer";
  const label = element("strong", "");
  label.setAttribute("role", "status");
  const file = element("small", "");
  const track = element("div", "");
  track.className = "progress";
  track.setAttribute("role", "progressbar");
  track.setAttribute("aria-label", model);
  const bar = element("div", "");
  const amount = element("small", "");
  track.append(bar);
  box.append(label, file, track, amount);
  root.append(box);
  transferViews.set(root, {label, file, track, bar, amount});
}

function updateTransfer(root, job, model, disconnected) {
  const view = transferViews.get(root);
  if (!view) return;
  const p = job?.progress;
  const downloading = !disconnected && p?.phase === "downloading";
  const known = downloading && Number.isFinite(p.total) && p.total > 0;
  const percent = known ? Math.max(0, Math.min(100, Math.floor(100 * p.received / p.total))) : null;
  const mib = bytes => (bytes / 1048576).toLocaleString(undefined, {maximumFractionDigits: 1}) + " MiB";
  const phase = disconnected ? "unavailable" : p?.phase || "preparing";
  const title = model + " · " + t(phase);
  if (view.label.textContent !== title) view.label.textContent = title;
  view.file.hidden = !p?.file || p.file === model;
  view.file.textContent = p?.file || "";
  view.bar.className = "progress-bar" + (known ? "" : " is-indeterminate");
  view.bar.style.width = known ? percent + "%" : "";
  if (known) view.track.setAttribute("aria-valuenow", String(percent));
  else view.track.removeAttribute("aria-valuenow");
  view.amount.hidden = !downloading;
  view.amount.textContent = downloading ? (known ? percent + "% · " + mib(p.received) + " / " + mib(p.total) : mib(p.received) + " " + t("receiving")) : "";
}

export function renderModelConnectionError(root) {
  root.hidden = false;
  delete root.dataset.signature;
  transferViews.delete(root);
  root.replaceChildren(element("h3", t("title")), element("p", t("unavailable")));
}

export async function renderDrivingLibrary(root, library) {
  latest = library;
  const current = ++version;
  if (writing) return;
  if (!catalogRequest) {
    root.replaceChildren(element("h3", t("title")), element("p", t("loading")));
    catalogRequest = getJson("/api/driving-models/catalog").then(result => {
      if (!Array.isArray(result.models) || !result.models.length) throw Error("Empty model catalog");
      return result.models;
    });
  }
  let models;
  try {
    models = await catalogRequest;
  } catch {
    if (current === version) {
      catalogRequest = null;
      renderModelConnectionError(root);
    }
    return;
  }
  if (current !== version || writing) return;
  const state = library.selector;
  const job = state.job;
  const install = state.lat2v_install || {};
  const transfer = job?.state === "preparing" ? job :
    install.state === "preparing" ? {model: "lat2v", progress: install.progress} : null;
  const name = id => models.find(model => model.id === id)?.name || id;
  const signature = JSON.stringify([{...state, lat2v_install: [install.state, install.detail],
    job: [job?.state, job?.model, job?.park_block, job?.detail]}, library.selected, t("title")]);
  if (root.dataset.signature === signature) {
    updateTransfer(root, transfer, name(transfer?.model), state.connection_lost);
    return;
  }
  transferViews.delete(root);
  root.dataset.signature = signature;
  root.replaceChildren(element("h3", t("title")), element("p", t("help")));
  if (transfer) {
    transferView(root, name(transfer.model));
    updateTransfer(root, transfer, name(transfer.model), state.connection_lost);
  }
  const boot = element("p", t("boot") + " · " + [name(state.boot.small), name(state.boot.large), t(state.boot.primary)].join(" / "));
  boot.className = "model-boot";
  root.append(boot);
  if (!state.offroad) root.append(element("p", t("parked")));
  const lat2vBlock = state.lat2v_park_block;
  const canQueue = state.lat2v_supported !== false && (!lat2vBlock || (state.lat2v_supported && lat2vBlock === "forced_offroad"));
  if (!install.state && lat2vBlock && (state.offroad || lat2vBlock !== "offroad") && !state.connection_lost)
    root.append(element("p", name("lat2v") + " · " + t("lat2v_" + lat2vBlock)));
  if (install.state) {
    const note = element("p", [name("lat2v"), t("lat2v_" + install.state), install.detail].filter(Boolean).join(" · "));
    note.setAttribute("role", "status");
    root.append(note);
  } else if (state.next.large === "lat2v" && state.boot.large !== "lat2v" && job?.model !== "lat2v") {
    root.append(element("p", name("lat2v") + " · " + t("saved")));
  }

  async function submit(field, value) {
    if (writing || !state.offroad || (value === "lat2v" && !canQueue)) return;
    writing = true;
    for (const input of root.querySelectorAll("select")) input.disabled = true;
    try {
      const reply = await postJson("/api/driving-models/selection", {field, value});
      if (reply.lat2v_install) latest = {...latest, selector: {...latest.selector, lat2v_install: reply.lat2v_install, job: {}}};
      else if (reply.job) latest = {...latest, selector: {...latest.selector, job: reply.job}};
    } catch (error) {
      const reason = error.payload?.park_block;
      if (typeof showAppToast === "function") showAppToast(reason ? t("lat2v_" + reason) : error.message || String(error), {tone: "error"});
    } finally {
      await globalThis.CarrotEgpuModel?.refresh();
      writing = false;
      delete root.dataset.signature;
      await renderDrivingLibrary(root, latest);
    }
  }
  function addSelect(field, value, groups) {
    const label = element("label", t(field));
    const select = document.createElement("select");
    select.className = "form-select";
    select.disabled = !state.offroad || state.job?.state === "preparing" || (field === "scene" && value == null);
    select.dataset.field = field;
    for (const [group, options] of groups) {
      const list = group ? document.createElement("optgroup") : select;
      if (group) {
        list.label = group + " (" + options.length + ")";
        select.append(list);
      }
      for (const [id, title] of options) {
        const option = element("option", title);
        option.value = id;
        if (id === "lat2v" && !canQueue) {
          option.disabled = true;
          if (state.lat2v_supported === false) option.textContent += " · " + t("lat2v_unsupported");
        }
        list.append(option);
      }
    }
    select.value = value ?? "";
    select.addEventListener("change", () => submit(field, field === "scene" ? Number(select.value) : select.value));
    label.append(select);
    root.append(label);
  }
  for (const size of ["small", "large"]) {
    const groups = ["carrot-wip", "sunnypilot"].map(source => [source, models.filter(m => m.source === source && m.size === size)
      .map(m => {
        const original = library.models.find(item => item.id === m.id);
        return [m.id, original?.noo ? m.name + " · NOO" : m.name];
      })]);
    addSelect(size, size === "large" && install.state ? "lat2v" : state.next[size], groups);
  }
  addSelect("primary", state.next.primary, [["", [["internal", t("internal")], ["auto", t("auto")]]]]);
  addSelect("scene", state.scene, [["", ["legacy", "dynamic", "camera", "perception"].map((label, i) => [i - 1, t(label)])]]);
  if (job?.state === "failed" || (job?.state === "saved" && [state.next.small, state.next.large].includes(job.model))) {
    const detail = job.park_block ? t("lat2v_unsaved") : job.detail || t(job.state);
    const note = element("p", name(job.model) + " · " + detail);
    note.setAttribute("role", "status");
    root.append(note);
  }
  if (job?.state !== "preparing" && (install.state === "failed" ||
      (!install.state && ((job?.model === "lat2v" && job.state === "failed") || state.next.large === "lat2v")))) {
    const retry = element("button", t("lat2v_retry"));
    retry.type = "button";
    retry.className = "btn btn-secondary";
    retry.disabled = !state.offroad || !canQueue;
    retry.addEventListener("click", () => submit("large", "lat2v"));
    root.append(retry);
  }
  for (const key of state.failed || []) root.append(element("p", t("load_failed") + " · " + name(key)));
  if (state.internal_build_failed) root.append(element("p", t("load_failed") + " · " + t("small")));
  if (library.selected && library.selected !== state.next.large) root.append(element("p", t("jetson") + " · " + name(library.selected)));
}
