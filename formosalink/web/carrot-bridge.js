/* Per-tab routing: two devices never share a mutable "selected device" cookie. */
(() => {
  "use strict";
  const script = document.currentScript;
  const prefix = new URL(script.src).pathname.replace(/__formosa_bridge\.js$/, "");
  const map = (value) => {
    if (typeof value !== "string" && !(value instanceof URL)) return value;
    if (String(value).startsWith("#")) return value;
    const url = new URL(value, location.href);
    if (url.origin === location.origin || url.protocol === "wss:" && location.protocol === "https:" && url.host === location.host
        || url.protocol === "ws:" && location.protocol === "http:" && url.host === location.host) {
      if (!url.pathname.startsWith(prefix)) url.pathname = prefix + url.pathname.replace(/^\//, "");
    }
    return url.href;
  };
  const cssUrls = value => typeof value === "string" ? value.replace(/url\(\s*(["']?)([^)"']+)\1\s*\)/g,
    (_, quote, url) => `url(${quote}${map(url.trim())}${quote})`) : value;
  if (window.FontFace) {
    const Face = window.FontFace;
    window.FontFace = class extends Face { constructor(name, source, descriptors) { super(name, cssUrls(source), descriptors); } };
  }
  if (window.CSSStyleDeclaration) {
    const styleSet = CSSStyleDeclaration.prototype.setProperty;
    CSSStyleDeclaration.prototype.setProperty = function (name, value, priority) { return styleSet.call(this, name, cssUrls(value), priority); };
    for (const name of ["cssText", "background", "backgroundImage", "maskImage"]) {
      const descriptor = Object.getOwnPropertyDescriptor(CSSStyleDeclaration.prototype, name);
      if (descriptor?.set && descriptor.configurable) Object.defineProperty(CSSStyleDeclaration.prototype, name,
        { ...descriptor, set(value) { descriptor.set.call(this, cssUrls(value)); } });
    }
  }
  globalThis.FormosaCarrotRemote = Object.freeze({ prefix, url: map });
  const fetchOriginal = window.fetch.bind(window);
  window.fetch = (input, options) => fetchOriginal(input instanceof Request ? new Request(map(input.url), input) : map(input), options);
  for (const name of ["Worker", "SharedWorker"]) {
    const Native = window[name];
    if (Native) window[name] = class extends Native { constructor(url, options) { super(map(url), options); } };
  }
  const Socket = window.WebSocket;
  window.WebSocket = class extends Socket {
    constructor(url, protocols) { super(map(url), protocols); }
  };
  if (window.EventSource) {
    const Source = window.EventSource;
    window.EventSource = class extends Source {
      constructor(url, options) { super(map(url), options); }
    };
  }
  const xhrOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function (method, url, ...args) { return xhrOpen.call(this, method, map(url), ...args); };
  if (navigator.sendBeacon) {
    const beacon = navigator.sendBeacon.bind(navigator);
    navigator.sendBeacon = (url, data) => beacon(map(url), data);
  }
  if (window.Audio) {
    const NativeAudio = window.Audio;
    window.Audio = function (url) { return new NativeAudio(url == null ? url : map(url)); };
    window.Audio.prototype = NativeAudio.prototype;
    Object.setPrototypeOf(window.Audio, NativeAudio);
  }
  const open = window.open.bind(window);
  window.open = (url, ...args) => open(map(url), ...args);
  for (const name of ["pushState", "replaceState"]) {
    const original = history[name].bind(history);
    history[name] = (state, unused, url) => original(state, unused, url == null ? url : map(url));
  }
  const attribute = Element.prototype.setAttribute;
  Element.prototype.setAttribute = function (name, value) {
    return attribute.call(this, name, /^(src|href|poster|action)$/i.test(name) ? map(value) : value);
  };
  for (const [type, names] of [[HTMLImageElement, ["src"]], [HTMLScriptElement, ["src"]],
    [HTMLLinkElement, ["href"]], [HTMLAnchorElement, ["href"]], [HTMLMediaElement, ["src", "poster"]],
    [HTMLSourceElement, ["src"]], [HTMLFormElement, ["action"]]]) {
    for (const name of names) {
      const descriptor = Object.getOwnPropertyDescriptor(type.prototype, name);
      if (!descriptor?.set || !descriptor.configurable) continue;
      Object.defineProperty(type.prototype, name, { ...descriptor, set(value) { descriptor.set.call(this, map(value)); } });
    }
  }
  // Device-local preferences must not overwrite the portal or another device's settings.
  for (const name of ["localStorage", "sessionStorage"]) {
    try {
      const original = window[name], namespace = "formosa-carrot:" + prefix + ":";
      const keys = () => Array.from({ length: original.length }, (_, index) => original.key(index)).filter(key => key?.startsWith(namespace));
      const isolated = {
        getItem: key => original.getItem(namespace + key), setItem: (key, value) => original.setItem(namespace + key, value),
        removeItem: key => original.removeItem(namespace + key), clear: () => keys().forEach(key => original.removeItem(key)),
        key: index => keys()[index]?.slice(namespace.length) ?? null, get length() { return keys().length; },
      };
      Object.defineProperty(window, name, { configurable: true, value: isolated });
    } catch (_) { /* private browsing may disable storage */ }
  }
})();
