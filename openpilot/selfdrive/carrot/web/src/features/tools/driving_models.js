const EN = {
  title: "sunnypilot driving model selector", small: "Small model · built-in GPU", large: "Large model · eGPU",
  primary: "Primary model after reboot", auto: "Prefer external large model", internal: "Internal small model",
  scene: "C3X / C4 device display", legacy: "Use device layout", dynamic: "Dynamic 3D", camera: "Camera", perception: "Model perception 3D",
  help: "Both model choices are saved separately. First use downloads and verifies the model. Restart the parked device to apply.",
  parked: "Turn the ignition off to change these settings.", boot: "Selected for this boot", loading: "Loading models…",
  unavailable: "Cannot load the model list. Checking the connection…", preparing: "Preparing model…",
  failed: "Preparation failed. Check the connection and free space, then select the model again.",
  load_failed: "Model failed to load this boot", saved: "Saved for next boot", jetson: "Jetson model",
  vla: "PhysicalAI-reason-VLA 4B · Recorded-drive comparison",
  vla_observer: "PhysicalAI-reason-VLA 4B · C4 Chestnut observation",
  off: "Off",
  observe: "Compare with the built-in primary model",
  observe_help: "Select the internal primary and reboot. First use verifies a 2.95 GB download. The VLA compares decisions on matching frames. Vehicle control stays with the primary model.",
  idle: "Waiting for a session",
  waiting: "Waiting for healthy, aligned inputs",
  loading_vla: "Loading VLA weights",
  inferencing: "Running inference",
  expired: "Result expired",
  result: "Received an aligned observation",
  too_slow: "Stopped after three late results",
  usb_unavailable: "Chestnut connection or power unavailable",
  worker_failed: "GPU worker unavailable or timed out",
  primary_guard: "Stopped to protect primary inference",
  primary_owns_gpu: "Select the internal primary and reboot",
  session: "Session totals · accepted / late",
  latency: "Last completed inference, camera to result",
  last_comparison: "Last accepted stop comparison",
  both_stop: "Both models indicated stop",
  only_vla_stop: "Only the VLA indicated stop",
  only_primary_stop: "Only the primary indicated stop",
  inconclusive: "No comparable stop decision",
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

export function renderModelConnectionError(root) {
  root.hidden = false;
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
  const signature = JSON.stringify([state, library.selected, t("title")]);
  if (root.dataset.signature === signature) return;
  root.dataset.signature = signature;
  root.replaceChildren(element("h3", t("title")), element("p", t("help")));
  const name = id => models.find(model => model.id === id)?.name || id;
  root.append(element("p", t("boot") + " · " + [name(state.boot.small), name(state.boot.large), t(state.boot.primary)].join(" / ")));
  if (!state.offroad) root.append(element("p", t("parked")));
  function addSelect(field, value, groups) {
    const label = element("label", t(field));
    const select = document.createElement("select");
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
        list.append(option);
      }
    }
    select.value = value ?? "";
    select.addEventListener("change", async () => {
      if (writing) return;
      writing = true;
      for (const input of root.querySelectorAll("select")) input.disabled = true;
      try {
        const value = field === "scene" ? Number(select.value) : select.value;
        const reply = await postJson("/api/driving-models/selection", {field, value});
        if (reply.job) latest = {...latest, selector: {...latest.selector, job: reply.job}};
      } catch (error) {
        if (typeof showAppToast === "function") showAppToast(error.message || String(error), {tone: "error"});
      } finally {
        await globalThis.CarrotEgpuModel?.refresh();
        writing = false;
        delete root.dataset.signature;
        await renderDrivingLibrary(root, latest);
      }
    });
    label.append(select);
    root.append(label);
  }
  for (const size of ["small", "large"]) {
    const groups = ["carrot-wip", "sunnypilot"].map(source => [source, models.filter(m => m.source === source && m.size === size)
      .map(m => {
        const original = library.models.find(item => item.id === m.id);
        return [m.id, original?.noo ? m.name + " · NOO" : m.name];
      })]);
    addSelect(size, state.next[size], groups);
  }
  addSelect("primary", state.next.primary, [["", [["internal", t("internal")], ["auto", t("auto")]]]]);
  addSelect("scene", state.scene, [["", ["legacy", "dynamic", "camera", "perception"].map((label, i) => [i - 1, t(label)])]]);
  if (state.job?.state && (state.job.state !== "saved" || [state.next.small, state.next.large].includes(state.job.model))) {
    const note = element("p", name(state.job.model) + " · " + t(state.job.state));
    note.setAttribute("role", "status");
    root.append(note);
  }
  for (const key of state.failed || []) root.append(element("p", t("load_failed") + " · " + name(key)));
  if (state.internal_build_failed) root.append(element("p", t("load_failed") + " · " + t("small")));
  if (library.selected && library.selected !== state.next.large) root.append(element("p", t("jetson") + " · " + name(library.selected)));
  const observer = state.vla_observer;
  if (!observer) {
    root.append(element("p", t("vla")));
    return;
  }
  addSelect("vla_observer", observer.enabled ? "on" : "off", [["", [["off", t("off")], ["on", t("observe")]]]]);
  root.append(element("p", t("observe_help")));
  if (observer.enabled) {
    const status = observer.last_error || observer.state || "idle";
    root.append(element("p", t(status === "loading" ? "loading_vla" : status)));
    const stats = observer.session;
    if (stats) {
      root.append(element("p", t("session") + " · " + stats.accepted + " / " + stats.expired));
      if (Number.isFinite(stats.last_ms)) root.append(element("p", t("latency") + " · " + stats.last_ms + " ms"));
      if (stats.last_comparison) root.append(element("p", t("last_comparison") + " · " + t(stats.last_comparison)));
    }
  }
}
