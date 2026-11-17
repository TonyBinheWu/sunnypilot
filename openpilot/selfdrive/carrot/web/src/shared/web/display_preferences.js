// Scale text declarations, never the video, page geometry or map coordinates.
export function scaledFontSize(value) {
  const size = String(value || "").trim();
  if (!size || size.includes("--carrot-text-scale") || /(?:^|[^\w-])(?:inherit|initial|unset|revert)(?:$|\s)/.test(size)) return null;
  // Relative text inherits the already-scaled parent. Scaling em/% again would
  // multiply nested headings and buttons more than once.
  if (/(?:[\d.])(?:em|ex|ch|%)(?:\b|\s|\)|$)/.test(size)) return null;
  return `calc((${size}) * var(--carrot-text-scale, 1))`;
}

export function installDisplayPreferences(target = globalThis) {
  if (target.CarrotDisplayPreferences) return target.CarrotDisplayPreferences;
  const doc = target.document;
  if (!doc) return null;
  const seen = new WeakSet();
  function declaration(style) {
    if (!style || seen.has(style)) return;
    const size = scaledFontSize(style.getPropertyValue("font-size"));
    if (size) style.setProperty("font-size", size, style.getPropertyPriority("font-size"));
    seen.add(style);
  }
  function rules(list) {
    for (const rule of list || []) {
      // Keep the rem reference stable; individual text declarations scale once.
      if (rule.style && !/^(?:html|:root)$/.test(rule.selectorText || "")) declaration(rule.style);
      try { if (rule.cssRules) rules(rule.cssRules); } catch (_) {}
    }
  }
  function sheets() {
    for (const sheet of doc.styleSheets || []) {
      try { rules(sheet.cssRules); } catch (_) { /* Cross-origin styles remain owned by their provider. */ }
    }
  }
  function apply(settings = {}) {
    let cached = null;
    try { cached = target.localStorage?.getItem("carrot_web_text_scale"); } catch (_) {}
    const percent = Number(settings.web_text_scale ?? cached ?? 100);
    const safe = [80, 90, 100, 110, 125, 150, 175, 200].includes(percent) ? percent : 100;
    doc.documentElement.style.setProperty("--carrot-text-scale", String(safe / 100));
    doc.documentElement.dataset.textScale = String(safe);
    try { target.localStorage?.setItem("carrot_web_text_scale", String(safe)); } catch (_) {}
  }
  function inspect(node) {
    if (node?.nodeType !== 1) return;
    if (node.matches?.("style,link[rel=stylesheet]")) {
      sheets();
      node.addEventListener?.("load", sheets, { once: true });
    }
    declaration(node.style);
    for (const child of node.querySelectorAll?.("[style]") || []) declaration(child.style);
  }
  apply(target.__CARROT_BOOTSTRAP__?.webSettings);
  doc.addEventListener("DOMContentLoaded", () => { sheets(); inspect(doc.body); }, { once: true });
  doc.addEventListener("load", (event) => {
    if (event.target?.matches?.("link[rel=stylesheet]")) sheets();
  }, true);
  if (doc.readyState !== "loading") { sheets(); inspect(doc.body); }
  const observer = target.MutationObserver && new target.MutationObserver((records) => {
    for (const record of records) for (const node of record.addedNodes) inspect(node);
  });
  const observe = () => { if (doc.documentElement) observer?.observe(doc.documentElement, { childList: true, subtree: true }); };
  if (doc.documentElement) observe();
  else doc.addEventListener('DOMContentLoaded', observe, { once: true });
  const api = Object.freeze({ apply });
  target.CarrotDisplayPreferences = api;
  return api;
}
