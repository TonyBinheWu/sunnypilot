const primarySections = [
  ["deviceGroup", "hdd-network", ["/task-manager.html", "/remote-screen.html", "btnDeviceInfo", "btnToolsCarSelect", "btnToolsLanguage", "btnToolsWebSettings", "btnToolsBluetooth", "btnSetupAgain"]],
  ["navigation", "signpost-split", ["/navigation", "laneMappingLink", "btnSteeringLearning", "/guide.zh-TW.html"]],
  ["diagnostics", "activity", ["btnSelfDiagnostics", "btnRecordingQuota", "btnTrainingData", "btnToolsAssistant"]],
];
const icons = {
  "/task-manager.html": "activity", "/remote-screen.html": "display", "/navigation": "map", "/guide.zh-TW.html": "book",
  laneMappingLink: "signpost-split", btnToolsCarSelect: "car-front", btnToolsLanguage: "translate", btnToolsWebSettings: "sliders",
  btnSetupAgain: "magic", btnSelfDiagnostics: "heart-pulse", btnDeviceInfo: "info-circle", btnToolsBluetooth: "bluetooth",
  btnSteeringLearning: "speedometer2", btnRecordingQuota: "device-hdd", btnTrainingData: "shield-check", btnToolsAssistant: "chat-dots",
};

export function arrangeTools(doc, translate) {
  const page = doc.getElementById("pageTools");
  const stack = page.querySelector(".tools-scroll-stack");
  const primary = doc.getElementById("toolsPrimaryActions");
  const sections = new Map();
  const make = (tag, className) => {
    const node = doc.createElement(tag);
    node.className = className;
    return node;
  };
  function label(tag, key, className = "") {
    const node = make(tag, className);
    node.dataset.managerText = key;
    return node;
  }
  function icon(name) {
    const node = make("i", "manager-icon manager-icon-" + name);
    node.setAttribute("aria-hidden", "true");
    return node;
  }
  function section(key, glyph, heading = true) {
    const node = make("section", "directory-section");
    if (heading) {
      const title = make("h2", "directory-heading");
      title.append(icon(glyph), label("span", key));
      node.append(title);
    }
    sections.set(key, node);
    stack.append(node);
    return node;
  }
  function pageButton(grid, key, dest, glyph) {
    const button = label("button", key, "btn manager-icon-" + glyph);
    button.type = "button";
    button.dataset.managerPage = dest;
    grid.append(button);
  }

  const guide = page.querySelector('a[href="/guide.zh-TW.html"]');
  const guideWrapper = guide.parentElement;
  const links = new Map([...primary.children, guide].map(n => [n.id || n.getAttribute("href"), n]));
  for (const [key, glyph, ids] of primarySections) {
    const panel = section(key, glyph);
    const grid = key === "deviceGroup" ? primary : make("div", "");
    grid.classList.add("directory-grid");
    panel.append(grid);
    for (const id of ids) {
      const item = links.get(id);
      if (!item) continue;
      item.classList.add("manager-icon-" + icons[id]);
      grid.append(item);
    }
    if (key === "diagnostics") {
      pageButton(grid, "openLogs", "logs", "clock-history");
      panel.append(doc.getElementById("selfDiagnosticsNotice"));
    }
  }
  guideWrapper.remove();

  const modelPanel = section("models", "boxes");
  const details = make("details", "directory-model");
  details.append(label("summary", "modelStatus"), doc.getElementById("externalModelLibrary"), doc.getElementById("egpuModelCard"));
  modelPanel.append(details);
  for (const [group, key, glyph] of [["git","git","git"], ["system","system","motherboard"], ["settings","backup","archive"]]) {
    const element = page.querySelector('[data-tools-group="' + group + '"]');
    element.querySelector(".tools-group__toggle").prepend(icon(glyph));
    section(key, glyph, false).append(element);
  }
  for (const rule of stack.querySelectorAll(":scope > hr.divider")) rule.remove();

  const consolePanel = section("console", "terminal");
  consolePanel.append(doc.getElementById("toolsMeta"), page.querySelector(".tools-console-dock"));
  const consoleLinks = make("div", "directory-grid");
  pageButton(consoleLinks, "openTerminal", "terminal", "terminal");
  consolePanel.append(consoleLinks);

  const labels = {
    gitCommandsTitle: "git", userSystemTitle: "system", userSettingsTitle: "backup",
    btnGitSync: "gitSync", btnGitReset: "gitReset", btnGitLog: "gitLog", btnGitBranch: "gitBranch", btnGitResetRepo: "gitRepo",
    btnResetCalib: "calib", btnSendTmuxLog: "tmux", btnSendTmuxServerLog: "sendLog", btnDeleteVideos: "videos",
    btnDeleteLogs: "logsDelete", btnRebuildAll: "rebuild", btnReboot: "reboot",
  };
  for (const [id, key] of Object.entries(labels)) doc.getElementById(id).dataset.managerText = key;
  doc.querySelector("#btnGitPull > span:first-child").dataset.managerText = "gitPull";

  const search = make("input", "directory-search");
  search.type = "search";
  const tabs = make("div", "directory-tabs");
  tabs.setAttribute("role", "group");
  const filters = make("div", "directory-filter");
  const empty = label("p", "noMatch", "directory-empty");
  empty.setAttribute("role", "status");
  filters.append(search, tabs);
  stack.prepend(filters, empty);
  let category = "all";
  function filter() {
    const term = search.value.trim().toLowerCase();
    let count = 0;
    for (const [key, panel] of sections) {
      const buttons = [...panel.querySelectorAll(".directory-grid > .btn,.tools-group__bodyInner > button:not([hidden])")];
      const matched = buttons.filter(b => [b.textContent, b.id, b.title].join(" ").toLowerCase().includes(term));
      panel.hidden = (category !== "all" && category !== key) ||
        Boolean(term && !matched.length && !(translate(key) + " " + panel.textContent).toLowerCase().includes(term));
      if (!panel.hidden) count++;
      for (const button of buttons) button.classList.toggle("directory-filtered", Boolean(term && matched.length && !matched.includes(button)));
      // Search reveals matching controls without changing the user's saved expand/collapse preference.
      const searching = Boolean(term && !panel.hidden);
      panel.classList.toggle("directory-searching", searching);
      const group = panel.querySelector("[data-tools-group]");
      if (group) group.querySelector(".tools-group__toggle").setAttribute("aria-expanded", String(searching || group.classList.contains("is-open")));
    }
    empty.hidden = count > 0;
    for (const b of tabs.children) b.setAttribute("aria-pressed", String(category === b.value));
  }
  function select(key) {
    category = key;
    search.value = "";
    filter();
    if (key === "models") details.open = true;
    if (key !== "all") page.scrollTop = 0;
  }
  for (const key of ["all", ...sections.keys()]) {
    const b = label("button", key, "directory-tab");
    b.type = "button";
    b.value = key;
    b.addEventListener("click", () => select(key));
    tabs.append(b);
  }
  search.addEventListener("input", () => { category = "all"; filter(); });
  return {
    select,
    refresh() {
      search.placeholder = translate("search");
      search.setAttribute("aria-label", search.placeholder);
      tabs.setAttribute("aria-label", translate("toolTitle"));
      filter();
    },
  };
}
