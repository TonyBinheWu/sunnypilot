import { installDisplayPreferences } from "../shared/web/display_preferences.js";

const display = installDisplayPreferences(window);
// Standalone navigation has no index-page bootstrap. Reuse the same saved
// preference, including when entered directly or through the Android host.
if (!window.__CARROT_BOOTSTRAP__?.webSettings) {
  fetch("/api/web_settings", { cache: "no-store" })
    .then(response => response.ok ? response.json() : null)
    .then(payload => { if (payload?.settings) display?.apply(payload.settings); })
    .catch(() => {});
}
