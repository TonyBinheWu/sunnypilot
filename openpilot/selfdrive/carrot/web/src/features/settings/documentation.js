import {
  createPublishedSettingDocumentationClient,
  PUBLISHED_SETTINGS_INDEX_URL,
} from "./published_documentation.js";

export const TRADITIONAL_SETTINGS_INDEX_URL = "/docs/settings/Settings-Catalog.json";

const DOC_LANGUAGES = new Set(["ko", "en", "zh", "zh-tw"]);
export const SETTING_DOCUMENTATION_INDEX_URL = PUBLISHED_SETTINGS_INDEX_URL;

export function normalizeSettingDocLanguage(value) {
  const language = String(value || "").trim().toLowerCase();
  return DOC_LANGUAGES.has(language) ? language : "en";
}

export function resolveSettingDocumentationIndexUrl(language) {
  return normalizeSettingDocLanguage(language) === "zh-tw" ? TRADITIONAL_SETTINGS_INDEX_URL : SETTING_DOCUMENTATION_INDEX_URL;
}

export function createSettingDocumentationClient(options = {}) {
  const indexUrl = String(options.indexUrl || PUBLISHED_SETTINGS_INDEX_URL);
  const client = createPublishedSettingDocumentationClient({
    fetchImpl: options.fetchImpl,
    storage: options.storage,
    now: options.now,
    indexUrl,
    indexTtlMs: options.indexTtlMs,
    requestTimeoutMs: options.requestTimeoutMs,
    maxIndexBytes: options.maxIndexBytes,
    maxPageBytes: options.maxPageBytes,
    maxMemoryPages: options.maxMemoryPages,
    maxStorageBytes: options.maxStorageBytes,
    clock: options.clock,
  });

  // An explicit upstream index must never override the Traditional reference.
  const traditionalIndexUrl = String(options.traditionalIndexUrl || TRADITIONAL_SETTINGS_INDEX_URL);
  const traditionalClient = createPublishedSettingDocumentationClient({
    ...options,
    indexUrl: traditionalIndexUrl,
    storageKey: "carrot.settings.traditional-docs.v1",
  });

  let activeClient = client;
  let activeIndexUrl = indexUrl;

  function load(name, language, ...args) {
    const selected = normalizeSettingDocLanguage(language) === "zh-tw" ? traditionalClient : client;
    activeClient = selected;
    activeIndexUrl = selected === client ? indexUrl : traditionalIndexUrl;
    return selected.load(name, language, ...args);
  }

  function clear() {
    client.clear();
    if (traditionalClient !== client) traditionalClient.clear();
  }

  function diagnostics() {
    return {
      ...activeClient.diagnostics(),
      channel: "wiki",
      indexUrl: activeIndexUrl,
    };
  }

  return Object.freeze({ load, clear, diagnostics });
}
