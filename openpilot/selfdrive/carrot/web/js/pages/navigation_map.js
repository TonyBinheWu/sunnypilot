"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let preferred = navigator.language || "en";
  try { preferred = localStorage.getItem("language") || preferred; } catch (_) { /* private browsing */ }
  const language = preferred.toLowerCase().replaceAll("_", "-");
  const traditional = /^zh-(tw|hk|mo|hant|cht)(-|$)/.test(language);
  const tr = (k, e) => traditional ? (globalThis.CarrotNavigationZhTw[e] || e) : language.startsWith("ko") ? k : e;
  const navText = (tw, en) => traditional ? tw : en;
  let mapProvider = 'mapbox', googleView = null, googleShown = false, googleBusy = false, googleBroken = false, viewVisible = true;
  let configuration;
  document.documentElement.lang = traditional ? "zh-Hant" : language.startsWith("ko") ? "ko" : "en";
  $("title").textContent = tr("Carrot 내비게이션", "Carrot Navigation");
  $("searchTitle").textContent = tr("목적지 검색", "Find a destination");
  $("search").textContent = tr("검색", "Search");
  $("clear").textContent = tr("현재 내비게이션 종료", "End current navigation");
  $("note").textContent = tr("키 등록 후 목적지를 검색하고 선택하세요. 선택한 위치는 현재 주행 세션에만 사용되며, 주행이 끝나거나 장치가 재시작되면 지워집니다. 경로 지도는 주행 화면이 켜져 있고 현재 위치와 안내 경로가 있을 때 표시됩니다. 외부 내비 안내가 우선이며, 연결이 끝나면 현재 주행의 Mapbox 목적지를 사용합니다.", "After saving your Public key, search for and select a destination. The selected place is used only for the current drive and is cleared when the drive ends or the device restarts. The route map needs the driving screen, a current position and route guidance. External navigation takes priority; the current drive's Mapbox destination resumes after it disconnects.");
  async function api(path, options) {
    let response, value;
    try {
      response = await fetch(`/api/navigation/${path}`, {...options, cache:"no-store"});
      value = await response.json();
    } catch (_) { throw new Error(tr("서버에 연결할 수 없습니다. 연결을 확인하고 다시 시도하세요.", "Unable to reach the server. Check your connection and try again.")); }
    if (!response.ok) {
      const error = value.error?.startsWith("Mapbox search failed") ? "Mapbox search is unavailable." : value.error;
      throw new Error(tr(error, error) || `HTTP ${response.status}`);
    }
    return value;
  }
  let currentPlace = null, savedPlaces = [], editingId = null, editorPlace = null, deletePending = null;
  let config = {provider:'mapbox',google_key:''};
  function google() { return googleView ||= globalThis.CarrotNavigationGoogle.create({key:config.google_key,language:traditional?'zh-TW':language.startsWith('ko')?'ko':'en',onError:e=>{$("status").textContent=e.message;if(e.message.includes('金鑰驗證')){googleBroken=true;googleShown=false;$("googleMap").hidden=true;$("mapStatus").textContent=e.message;}}}); }
  function useConfiguration(value) {
    config=value;mapProvider=value.provider==='google'?'google':'mapbox';
    $("mapProvider").value=mapProvider;$("googleKey").value=value.google_key||'';
    $("loadGoogle").hidden=mapProvider!=='google';$("mapAttribution").hidden=mapProvider==='google';$("routeAttribution").hidden=mapProvider!=='google';
    if(mapProvider==='google')waiting(navText('按「載入 Google 地圖」才會載入圖層；搜尋可獨立使用。路徑及模型圖資仍為 Mapbox。','Press Load Google map to load its layers. Search works independently. Routing and model map data remain Mapbox.'));
  }
  if(!traditional){
    for(const [id,text] of Object.entries({mapConfigTitle:'Map and search source',providerLabel:'Display / search',googleKeyLabel:'Google browser API key',saveMapConfig:'Save map source',loadGoogle:'Load Google map',recenterGoogle:'Recenter on vehicle',routeAttribution:'Route: Mapbox · Display map and search: Google',googleBudgetNote:'Maps load only on request; searches run only on submit, without autocomplete. Enable billing, Maps JavaScript API and Places UI Kit API; restrict referrers and quotas. Standard Google Maps terms exclude embedded vehicle systems; an applicable agreement is required for in-vehicle use.'}))$(id).textContent=text;
  }
  $("mapProvider").setAttribute('aria-label',navText('顯示與搜尋來源','Display and search source'));
  $("googleKey").setAttribute('aria-label',navText('Google 瀏覽器金鑰','Google browser API key'));
  configuration=api('config').then(useConfiguration).catch(()=>{$("mapConfigStatus").textContent=navText('無法讀取地圖來源，沿用 Mapbox。請確認車機已更新。','Unable to read map configuration. Using Mapbox. Check the device version.');});
  $("saveMapConfig").onclick=async()=>{
    $("saveMapConfig").disabled=true;
    try{
      const updates={navigation_map_provider:$("mapProvider").value,navigation_google_key:$("googleKey").value.trim()};
      if(updates.navigation_google_key&&!/^[A-Za-z0-9_-]{20,128}$/.test(updates.navigation_google_key))throw Error(navText('金鑰格式不正確。','Invalid key format.'));
      if(updates.navigation_map_provider==='google'&&!updates.navigation_google_key)throw Error(navText('請先輸入受來源限制的 Google 瀏覽器金鑰。','Enter a referrer-restricted Google browser key first.'));
      const response=await fetch('/api/web_settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(updates)});
      const result=await response.json();if(!response.ok||result.settings?.navigation_map_provider!==updates.navigation_map_provider||result.settings?.navigation_google_key!==updates.navigation_google_key)throw Error(navText('儲存未確認，請重新讀取。','Save was not confirmed. Reload and check.'));
      // Explicit reload creates a clean SDK/key context. Never silently retry a
      // billable search or create another map after a configuration change.
      location.reload();
    }catch(e){$("mapConfigStatus").textContent=e.message;}
    finally{$("saveMapConfig").disabled=false;}
  };
  $("loadGoogle").onclick=async()=>{
    if(googleBusy||googleShown)return;googleBusy=true;$("loadGoogle").disabled=true;
    try{$("googleMap").hidden=false;await google().showMap($("googleMap"));googleShown=true;$("loadGoogle").hidden=true;$("recenterGoogle").hidden=false;$("mapStatus").classList.add('google-status');}
    catch(e){$("googleMap").hidden=true;$("mapStatus").textContent=e.message;}
    finally{googleBusy=false;$("loadGoogle").disabled=false;}
  };
  $("recenterGoogle").onclick=()=>googleView?.recenter();
  if(typeof IntersectionObserver==='function')new IntersectionObserver(entries=>{viewVisible=entries[0]?.isIntersecting===true;}).observe(document.querySelector('main'));
  let searchingEditor = false, savingEditor = false, editorVersion = 0;
  const labels = {
    favoritesTitle: ["즐겨찾기", "Favorites"], addFavorite: ["즐겨찾기 추가", "Add favorite"],
    saveCurrent: ["현재 목적지 저장", "Save current destination"], nameLabel: ["이름", "Name"],
    addressLabel: ["주소 또는 장소", "Address or place"], favoriteSearch: ["주소 검색", "Search address"],
    saveFavorite: ["저장", "Save"], cancelFavorite: ["취소", "Cancel"], retryFavorites: ["다시 시도", "Retry"],
  };
  for (const [id, words] of Object.entries(labels)) $(id).textContent = tr(...words);
  $("favoritesNote").textContent = tr("즐겨찾기는 차량에 저장되어 앱과 웹에서 함께 사용합니다. 이름을 누르면 바로 목적지로 설정합니다.", "Favorites are saved on this vehicle and shared by the app and web. Tap a name to navigate.");
  $("storageNote").textContent = tr("주소 저장 검색은 Mapbox 영구 지오코딩을 사용합니다. 계정에서 지원해야 하며 Mapbox 요금이 적용됩니다. 이름만 수정할 때는 다시 검색하지 않아도 됩니다.", "Saving an address uses Mapbox permanent geocoding. Your account must support it and Mapbox charges apply. Renaming an existing favorite does not require another search.");
  function current(value) {
    currentPlace = value.destination || null;
    $("current").textContent = currentPlace?.place_name || tr("현재 목적지 없음", "No current destination");
    $("saveCurrent").disabled = !currentPlace;
  }
  function button(text, action) {
    const element = document.createElement("button"); element.type = "button"; element.textContent = text;
    element.addEventListener("click", async () => {
      element.disabled = true;
      try { await action(); } catch (error) { $("status").textContent = error.message; }
      finally { element.disabled = false; }
    });
    return element;
  }
  async function navigate(path, place) {
    const response=await api(path, { method: "POST", headers: {"Content-Type":"application/json"}, ...(place ? {body:JSON.stringify(place)} : {}) });
    current(place?.provider==='google'?{...response,destination:{...response.destination,provider:'google',google_place_id:place.google_place_id}}:response);
    $("status").textContent = tr("현재 주행 목적지로 설정했습니다. GPS와 지도 수신을 기다립니다.", "Destination set for this drive. Waiting for GPS and map data.");
  }
  function renderResults(places, target, choose) {
    target.replaceChildren();
    for (const place of places) {
      const row = document.createElement("li");
      row.append(button(place.place_name, () => choose(place)));
      if (target === $("results")) row.append(button(tr("즐겨찾기 저장", "Save to favorites"), () => openEditor(null, place)));
      target.append(row);
    }
  }
  $("form").addEventListener("submit", async (event) => {
    event.preventDefault(); $("search").disabled = true; $("results").replaceChildren();
    $("status").textContent = tr("검색 중…", "Searching…");
    try {
      await configuration;
      if(mapProvider==='google'){
        $("googleResults").hidden=false;
        const count=await google().search($("query").value.trim(),$("googleResults"),place=>navigate('destination',place));
        $("status").textContent=count?navText('請選擇 Google 搜尋結果，路徑由 Mapbox 規劃。','Choose a Google result. Mapbox will plan the route.'):tr('검색 결과 없음','No results.');return;
      }
      $("googleResults").hidden=true;
      const value = await api(`search?q=${encodeURIComponent($("query").value.trim())}`);
      renderResults(value.results, $("results"), place => navigate("destination", place));
      $("status").textContent = value.results.length ? tr("목적지를 선택하세요.", "Select a destination.") : tr("검색 결과 없음", "No results.");
    } catch (error) { $("status").textContent = error.message; }
    finally { $("search").disabled = false; }
  });
  $("clear").addEventListener("click", async () => {
    $("clear").disabled = true;
    try { current(await api("destination", {method:"DELETE"})); $("status").textContent = tr("이 페이지의 내비게이션을 종료했습니다. 외부 내비게이션은 해당 앱에서 종료하세요.", "Navigation from this page has ended. End external navigation in its source app."); }
    catch (error) { $("status").textContent = error.message; }
    finally { $("clear").disabled = false; }
  });
  api("destination").then(current).catch((error) => { $("status").textContent = error.message; });
  function renderFavorites(value) {
    savedPlaces = value.favorites; $("favorites").replaceChildren(); $("retryFavorites").hidden = true;
    $("favoritesStatus").textContent = savedPlaces.length ? "" : tr("즐겨찾기가 없습니다. 주소를 검색하여 추가하세요.", "No favorites yet. Search for an address to add one.");
    for (const place of savedPlaces) {
      const row = document.createElement("li"); row.className = "favorite-row";
      const go = button(place.name, async () => {
        if(place.provider==='google'){
          await configuration;$("googleResults").hidden=false;
          await navigate('destination',await google().resolveFavorite(place,$("googleResults")));
        }else await navigate(`favorites/${encodeURIComponent(place.id)}/destination`);
      }); go.className = "go";
      const address = document.createElement("small"); address.textContent = place.provider==='google'?navText('Google 最愛 · 點選時更新座標','Google favorite · Refreshes coordinates when selected'):place.place_name;
      const actions = document.createElement("div"); actions.className = "actions";
      actions.append(button(tr("편집", "Edit"), () => openEditor(place.id, place)));
      actions.append(button(deletePending === place.id ? tr("삭제 확인", "Confirm delete") : tr("삭제", "Delete"), async () => {
        if (deletePending !== place.id) { deletePending = place.id; renderFavorites({favorites:savedPlaces}); return; }
        renderFavorites(await api(`favorites/${encodeURIComponent(place.id)}`, {method:"DELETE"})); deletePending = null;
      }));
      if (deletePending === place.id) actions.append(button(tr("취소", "Cancel"), () => { deletePending = null; renderFavorites({favorites:savedPlaces}); }));
      row.append(go, address, actions); $("favorites").append(row);
    }
  }
  async function loadFavorites() {
    try { renderFavorites(await api("favorites")); }
    catch (error) { $("favoritesStatus").textContent = error.message; $("retryFavorites").hidden = false; }
  }
  function syncEditor() { $("saveFavorite").disabled = !editorPlace || searchingEditor || savingEditor; }
  function openEditor(id, place) {
    if (savingEditor) return;
    editorVersion++; editingId = id; editorPlace = place && (id || place.permanent || place.provider==='google') ? {...place} : null;
    $("favoriteForm").hidden = false; $("editorTitle").textContent = id ? tr("즐겨찾기 편집", "Edit favorite") : tr("즐겨찾기 추가", "Add favorite");
    $("favoriteName").value = place?.name || place?.place_name?.slice(0,80) || "";
    $("favoriteQuery").value = place?.place_name || place?.name || ""; $("favoriteResults").replaceChildren();$("googleFavoriteResults").replaceChildren();$("googleFavoriteResults").hidden=true;
    $("favoriteQuery").required=place?.provider!=='google';
    if(place?.provider==='google')$("storageNote").textContent=navText('只儲存地點 ID 與你的命名；點選最愛會查詢最新座標，適用 Google Places UI Kit 查詢費用。','Only the place ID and your name are stored. Selecting it queries fresh coordinates; Google Places UI Kit charges apply.');
    $("editorStatus").textContent = editorPlace ? "" : tr("주소를 검색하고 저장할 위치를 선택하세요.", "Search the address and select the location to save.");
    syncEditor(); $("favoriteName").focus();
  }
  $("addFavorite").addEventListener("click", () => openEditor(null, null));
  $("saveCurrent").addEventListener("click", () => { if (currentPlace) openEditor(null, currentPlace); });
  $("cancelFavorite").addEventListener("click", () => { if (!savingEditor) { editorVersion++; $("favoriteForm").hidden = true; } });
  $("favoriteQuery").addEventListener("input", () => { editorVersion++; editorPlace = null; syncEditor(); });
  $("favoriteSearch").addEventListener("click", async () => {
    const query = $("favoriteQuery").value.trim(), version = editorVersion;
    if (query.length < 2 || query.length > 200 || searchingEditor) { $("editorStatus").textContent = tr("2–200자를 입력하세요.", "Enter 2–200 characters."); return; }
    searchingEditor = true; $("favoriteSearch").disabled = true; syncEditor();
    $("editorStatus").textContent = tr("검색 중…", "Searching…");
    try {
      await configuration;
      if(mapProvider==='google'){
        $("googleFavoriteResults").hidden=false;
        const count=await google().search(query,$("googleFavoriteResults"),place=>{
          if(version!==editorVersion)return;
          editorPlace=place;$("favoriteQuery").value=query;$("editorStatus").textContent=navText('地點已選取，請命名並儲存。','Place selected. Name it and save.');syncEditor();
        });
        if(version===editorVersion)$("editorStatus").textContent=count?navText('請選擇 Google 地點。','Choose a Google place.'):tr('검색 결과 없음','No results.');return;
      }
      $("googleFavoriteResults").hidden=true;
      const value = await api(`search?q=${encodeURIComponent(query)}&permanent=true`);
      if (version !== editorVersion) return;
      renderResults(value.results, $("favoriteResults"), place => {
        editorPlace = place; $("favoriteQuery").value = place.place_name; $("favoriteResults").replaceChildren();
        $("editorStatus").textContent = tr("주소를 선택했습니다. 이름을 확인하고 저장하세요.", "Address selected. Check the name and save."); syncEditor();
      });
      $("editorStatus").textContent = value.results.length ? tr("목적지를 선택하세요.", "Select a destination.") : tr("검색 결과 없음", "No results.");
    } catch (error) { if (version === editorVersion) $("editorStatus").textContent = error.message; }
    finally { searchingEditor = false; $("favoriteSearch").disabled = false; syncEditor(); }
  });
  $("favoriteForm").addEventListener("submit", async event => {
    event.preventDefault(); if (!editorPlace || savingEditor || searchingEditor) return;
    const name = $("favoriteName").value.trim();
    if (!name || name.length > 80) { $("editorStatus").textContent = tr("이름을 1–80자로 입력하세요.", "Enter a name of 1–80 characters."); return; }
    savingEditor = true; syncEditor(); $("cancelFavorite").disabled = true;
    $("favoriteName").disabled = true; $("favoriteQuery").disabled = true; $("favoriteSearch").disabled = true;
    try {
      renderFavorites(await api(editingId ? `favorites/${encodeURIComponent(editingId)}` : "favorites", {
        method:editingId ? "PUT" : "POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(editorPlace.provider==='google'?globalThis.CarrotNavigationGoogle.reference(editorPlace,name):{...editorPlace, name}),
      }));
      $("favoriteForm").hidden = true; $("status").textContent = tr("즐겨찾기를 저장했습니다.", "Favorite saved.");
    } catch (error) { $("editorStatus").textContent = error.message; }
    finally {
      savingEditor = false; $("cancelFavorite").disabled = false;
      $("favoriteName").disabled = false; $("favoriteQuery").disabled = false; $("favoriteSearch").disabled = false; syncEditor();
    }
  });
  $("retryFavorites").addEventListener("click", loadFavorites);
  loadFavorites();
  let imageUrl;
  function waiting(message) {
    $("map").hidden = true; $("map").removeAttribute("src");
    if (imageUrl) URL.revokeObjectURL(imageUrl); imageUrl = undefined;
    $("mapStatus").hidden = false; $("mapStatus").textContent = message;
  }
  waiting(tr("현재 위치와 목적지를 확인하고 있습니다.", "Checking position and destination."));
  async function refresh() {
    if (!document.hidden && viewVisible && mapProvider==='google') {
      if(googleShown&&!googleBroken){
        try{
          const value=await api('route_view');googleView.updateRoute(value);
          $("mapStatus").textContent=value.position?(value.coordinates?.length>=2?navText('Mapbox 原始路線 · Google 顯示圖層','Original Mapbox route · Google display layers'):navText('已有位置，等待 Mapbox 路線。','Position received. Waiting for a Mapbox route.')):navText('等待車機目前位置；過期路線已清除。','Waiting for the vehicle position; stale routes cleared.');
        }catch(_){googleView.updateRoute(null);$("mapStatus").textContent=navText('車機連線中斷，路線與位置已清除。','Device disconnected. Route and position cleared.');}
      }
    } else if (!document.hidden && viewVisible && mapProvider==='mapbox') {
      try {
        const response = await fetch("/api/navigation/map.png", {cache:"no-store"});
        if (response.status !== 200 && response.status !== 204) throw new Error("waiting");
        const reasons = {
          ready: tr("Nav 모델 지도 · 실시간 경로", "Nav model map · Live route"),
          tiles: tr("지도 데이터를 받지 못했습니다. Mapbox 키와 네트워크를 확인하세요.", "Map data unavailable. Check your Mapbox key and network."),
          route: tr("아래에서 목적지를 검색·선택하거나 외부 네비의 안내를 시작하세요. 키 등록만으로는 경로 지도가 표시되지 않습니다.", "Search for and select a destination below, or start external navigation guidance. Saving keys alone does not display a route map."),
          offroad: tr("차량의 주행 화면이 켜지면 경로 지도를 표시합니다. 먼저 아래에서 목적지를 선택하세요.", "The route map is available when the vehicle's driving screen is active. Select a destination below first."),
          waiting: tr("지도 서비스를 기다리는 중입니다. 목적지와 현재 위치를 확인하세요.", "Waiting for the map service. Check your destination and current position."),
          position: tr("현재 GPS 위치를 기다리는 중입니다.", "Waiting for a current GPS position."),
          instruction: tr("현재 경로의 안내를 기다리는 중입니다.", "Waiting for current route instructions."),
          route_position: tr("현재 위치가 안내 경로에서 벗어나 있습니다.", "Current position is away from the route."),
          slow: tr("지도 로딩 중입니다. 잠시 기다려 주세요.", "Loading map data. Please wait."),
        };
        const reason = response.headers.get("X-Nav-Map-Status");
        if (response.status === 200 && reason === "ready") {
          const next = URL.createObjectURL(await response.blob());
          $("map").src = next; if (imageUrl) URL.revokeObjectURL(imageUrl); imageUrl = next;
          $("map").hidden = false; $("mapStatus").hidden = true;
        } else {
          waiting(reasons[reason] || reasons.waiting);
        }
      } catch (_) { waiting(tr("지도 상태를 받지 못했습니다. 차량과의 연결을 확인하세요.", "Unable to read map status. Check your connection to the vehicle.")); }
    }
    setTimeout(refresh, mapProvider==='google'?1000:500);
  }
  refresh();
})();
