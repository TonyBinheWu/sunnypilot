"use strict";
// Compatibility for cached old pages. No SDK, key or network calls.
(() => {
  const message = "Google 地圖已停用，請重新載入以使用 Mapbox／OpenStreetMap。Google maps are retired; reload to use Mapbox / OpenStreetMap.";
  const unavailable = async () => { throw new Error(message); };
  globalThis.CarrotNavigationGoogle = Object.freeze({
    create: () => ({showMap:unavailable,search:unavailable,resolveFavorite:unavailable,updateRoute(){},recenter(){}}),
    reference(){throw new Error(message);},
  });
})();
