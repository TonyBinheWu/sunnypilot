import { arrangeTools } from "./tools.js";
import { installOverview } from "./overview.js";

function install() {
  const doc = document;
  const root = doc.documentElement;
  const route = window.CarrotManagementRoute;
  const translate = key => window.getUIText("manager_" + key, key);
  const byId = id => doc.getElementById(id);
  const directory = arrangeTools(doc, translate);
  const overview = byId("btnOverview");
  const themeButtons = [];

  for (const page of [byId("pageOverview"), byId("pageTools")]) {
    const header = doc.createElement("header");
    header.className = "manager-heading";
    const heading = page === byId("pageOverview") ? byId("overviewTitle") : doc.createElement("h1");
    if (!heading.id) heading.dataset.managerText = "toolTitle";
    const toggle = doc.createElement("button");
    toggle.type = "button";
    themeButtons.push(toggle);
    header.append(heading, toggle);
    page.prepend(header);
    toggle.addEventListener("click", () => {
      root.dataset.managerTheme = root.dataset.managerTheme === "dark" ? "light" : "dark";
      try { localStorage.setItem("carrot_manager_theme", root.dataset.managerTheme); } catch {}
      updateText();
    });
  }

  function updateText() {
    for (const el of doc.querySelectorAll("[data-manager-text]")) el.textContent = translate(el.dataset.managerText);
    for (const b of themeButtons) {
      b.className = "manager-theme manager-icon manager-icon-" + (root.dataset.managerTheme === "dark" ? "sun" : "moon");
      b.setAttribute("aria-label", translate("theme"));
      b.title = translate("theme");
    }
    directory.refresh();
  }
  function remember(page) {
    overview.classList.toggle("active", page === "overview");
    if (page === "overview") overview.setAttribute("aria-current", "page");
    else overview.removeAttribute("aria-current");
    if (route.pageUrl(page)) {
      try { localStorage.setItem("carrot_manager_last_overview", String(page === "overview")); } catch {}
    }
  }
  function navigate(page) {
    const models = page === "models";
    if (models) page = "tools";
    if (!route.pageUrl(page)) return;
    window.showPage(page, true);
    if (models) directory.select("models");
  }

  root.classList.add("carrot-manager");
  try { root.dataset.managerTheme = localStorage.getItem("carrot_manager_theme") || "light"; }
  catch { root.dataset.managerTheme = "light"; }
  overview.hidden = false;
  doc.querySelector(".manager-brand").hidden = false;
  overview.addEventListener("click", () => navigate("overview"));
  doc.addEventListener("click", event => {
    const target = event.target.closest("[data-manager-page]");
    if (target) navigate(target.dataset.managerPage);
  });
  window.addEventListener("carrot:languagechange", updateText);
  window.addEventListener("load", updateText, {once: true});
  window.addEventListener("carrot:pagechange", event => remember(event.detail.page));
  installOverview(doc, translate);
  window.CarrotManagement = route;
  updateText();
}

// Embedded cockpit panels, the native companion and special-purpose links own their navigation and viewport.
if (window.CarrotManagementRoute && document.getElementById("pageOverview") && document.getElementById("pageTools")) install();
