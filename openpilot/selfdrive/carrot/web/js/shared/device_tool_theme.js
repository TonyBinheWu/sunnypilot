"use strict";
try {
  document.documentElement.dataset.managerTheme = localStorage.getItem("carrot_manager_theme") || "light";
} catch {}
