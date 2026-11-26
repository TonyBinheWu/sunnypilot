import { drawCockpitVehicle, resolveVehicleSkin } from "../cockpit/vehicle.js";

async function get(path, signal) {
  const response = await fetch(path, { cache: "no-store", signal });
  if (!response.ok) throw new Error(String(response.status));
  return response.json();
}

const percent = n => Number.isFinite(n) ? Math.round(n) + "%" : "—";
const metrics = ["cpu", "gpu", "memory", "temperature"];

export function installOverview(doc, translate) {
  const byId = id => doc.getElementById(id);
  const cells = metrics.map(key => {
    const box = doc.createElement("div"), name = doc.createElement("span"), value = doc.createElement("strong");
    name.dataset.managerText = key;
    value.textContent = "—";
    const history = doc.createElement("canvas");
    history.width = 240;
    history.height = 40;
    history.setAttribute("aria-hidden", "true");
    box.append(name, value, history);
    byId("managerMetrics").append(box);
    return {value, history, samples:[]};
  });
  let generation = 0, timer, active, abort;
  function paintCar(values) {
    const canvas = byId("managerVehicle"), ctx = canvas.getContext("2d");
    if (!ctx) return;
    const skin = resolveVehicleSkin(values);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawCockpitVehicle(ctx, (x, y, z) => [260 + 76*x - 44*y, 150 - 12*x - 23*y - 65*z], {skin, view:[-3.8,-6.6,3.04]});
  }
  function renderResources(data) {
    const cores = (data?.cores || []).filter(Number.isFinite);
    const cpu = cores.length ? cores.reduce((a,b) => a+b, 0) / cores.length : null;
    const memory = data?.memory;
    const temperature = (data?.temps || []).map(pair => pair[1]).filter(Number.isFinite);
    const memPercent = memory?.total > 0 && Number.isFinite(memory.free) ? (1-memory.free/memory.total)*100 : memory?.percent;
    const values = [percent(cpu), percent(data?.gpu), percent(memPercent), temperature.length ? Math.round(Math.max(...temperature)) + " °C" : "—"];
    const samples = [cpu, data?.gpu, memPercent, temperature.length ? Math.max(...temperature) : null];
    cells.forEach(({value, history, samples: series}, i) => {
      value.textContent = values[i];
      const ctx = history.getContext("2d");
      if (!ctx) return;
      ctx.clearRect(0, 0, history.width, history.height);
      if (!Number.isFinite(samples[i])) { series.length = 0; return; }
      series.push(samples[i]);
      if (series.length > 24) series.shift();
      const low = Math.min(...series) - 3, span = Math.max(...series) + 3 - low;
      ctx.beginPath();
      series.forEach((n, j) => {
        const x = 238 - (series.length - 1 - j) * 10, y = 36 - (n - low) / span * 32;
        if (j) ctx.lineTo(x, y); else ctx.moveTo(x - 1, y);
        if (!j) ctx.lineTo(x, y);
      });
      ctx.strokeStyle = ["#bd572d","#507990","#538367","#ad704b"][i];
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }
  function renderTrips(segments) {
    const list = byId("managerTrips");
    list.replaceChildren();
    if (!segments?.length) {
      const note = doc.createElement("span");
      note.dataset.managerText = segments ? "logsEmpty" : "offline";
      note.textContent = translate(note.dataset.managerText);
      list.append(note);
      return;
    }
    for (const segment of segments) {
      const row = doc.createElement("button");
      row.type = "button";
      row.addEventListener("click", () => {
        window.showPage("logs", true);
        const route = segment.replace(/--\d+$/, "");
        window.CarrotLogsRuntime.dashcam.openPlayer(route, segment);
      });
      row.textContent = segment;
      list.append(row);
    }
  }
  function renderModel(model, catalog) {
    const library = model?.library;
    const boot = library?.selector?.boot;
    const name = id => catalog?.models?.find(m => m.id === id)?.name || library?.models?.find(m => m.id === id)?.name || id;
    byId("managerModel").textContent = boot
      ? [name(boot.small), name(boot.large)].filter(Boolean).join(" / ") || "—"
      : name(library?.effective) || "—";
  }
  function stop() {
    generation++;
    active = false;
    clearTimeout(timer);
    abort?.abort();
    abort = null;
  }
  async function sample(initial, version) {
    if (!active || version !== generation) return;
    const controller = new AbortController();
    abort = controller;
    const signal = controller.signal;
    const deadline = setTimeout(() => controller.abort(), 4500);
    async function read(path, render) {
      let data;
      try { data = await get(path, signal); } catch { data = null; }
      if (version === generation) render(data);
    }
    const reads = [read("/api/tools/resources", renderResources)];
    if (initial) {
      reads.push(read("/api/params_bulk?names=CarName,CarSelected3,GitBranch,DeviceType", result => {
        const values = result?.values || {};
        byId("managerCar").textContent = resolveVehicleSkin(values).identity || "—";
        byId("managerBranch").textContent = values.GitBranch || "—";
        byId("managerDevice").textContent = ({tici:"C3",tizi:"C3X",mici:"C4"})[values.DeviceType] || values.DeviceType || "—";
        paintCar(values);
      }), read("/api/dashcam/recent?limit=2", result => renderTrips(result?.segments)));
      const modelReads = ["/api/egpu/model", "/api/driving-models/catalog"].map(path => get(path, signal).catch(() => null));
      reads.push(Promise.all(modelReads).then(([model, catalog]) => {
        if (version === generation) renderModel(model, catalog);
      }));
    }
    try { await Promise.all(reads); }
    finally {
      clearTimeout(deadline);
      if (version === generation && active) timer = setTimeout(() => sample(false, version), 5000);
    }
  }
  function sync() {
    const visible = !doc.hidden && doc.documentElement.dataset.page === "overview";
    if (!visible) { if (active) stop(); return; }
    if (active) return;
    active = true;
    renderResources(null);
    for (const id of ["managerCar", "managerBranch", "managerDevice", "managerModel"]) byId(id).textContent = "—";
    byId("managerTrips").replaceChildren();
    paintCar({});
    void sample(true, ++generation);
  }
  doc.addEventListener("visibilitychange", sync);
  window.addEventListener("carrot:pagechange", sync);
  window.addEventListener("pageshow", sync);
  window.addEventListener("pagehide", stop);
}
