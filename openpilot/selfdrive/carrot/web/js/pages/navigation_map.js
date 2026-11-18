"use strict";
(() => {
  const $ = (id) => document.getElementById(id);
  let preferred = navigator.language || "en";
  try { preferred = localStorage.getItem("language") || preferred; } catch (_) { /* private browsing */ }
  const language = preferred.toLowerCase().replaceAll("_", "-");
  const traditional = /^zh-(tw|hk|mo|hant|cht)(-|$)/.test(language);
  const tr = (k, e) => traditional ? (globalThis.CarrotNavigationZhTw[e] || e) : language.startsWith("ko") ? k : e;
  let viewVisible=true;
  if(typeof IntersectionObserver==='function')new IntersectionObserver(entries=>{viewVisible=entries[0]?.isIntersecting===true;}).observe(document.querySelector('main'));
  document.documentElement.lang = traditional ? "zh-Hant" : language.startsWith("ko") ? "ko" : "en";
  $("title").textContent = tr("Carrot 내비게이션", "Carrot Navigation");
  $("searchTitle").textContent = tr("목적지 검색", "Find a destination");
  $("search").textContent = tr("검색", "Search");
  $("clear").textContent = tr("현재 내비게이션 종료", "End current navigation");
  $("note").textContent = tr("키 등록 후 목적지를 검색하고 선택하세요. 선택한 위치는 현재 주행 세션에만 사용되며, 주행이 끝나거나 장치가 재시작되면 지워집니다. 경로 지도는 주행 화면이 켜져 있고 현재 위치와 안내 경로가 있을 때 표시됩니다. 외부 내비 안내가 우선이며, 연결이 끝나면 현재 주행의 Mapbox 목적지를 사용합니다.", "After saving your Public key, search for and select a destination. The selected place is used only for the current drive and is cleared when the drive ends or the device restarts. The route map needs the driving screen, a current position and route guidance. External navigation takes priority; the current drive's Mapbox destination resumes after it disconnects.");
  $('mapConfigTitle').textContent=tr('지도와 검색 소스','Map sources and search');
  $('mapSourceNote').textContent=tr('표시 지도는 OpenStreetMap, 검색과 경로 및 모델 지도는 기존 Mapbox를 사용합니다.','The display uses OpenStreetMap. Search, routes and model maps retain the existing Mapbox pipeline.');
  const osm=globalThis.CarrotNavigationOsm?.start({tr,isVisible:()=>viewVisible});
  async function api(path, options) {
    let response, value;
    const controller=typeof AbortController==='function'?new AbortController():null;
    const deadline=controller?setTimeout(()=>controller.abort(),10000):null;
    try {
      response = await fetch(`/api/navigation/${path}`, {...options, cache:"no-store",...(controller?{signal:controller.signal}:{})});
      value = await response.json();
    } catch (_) { throw new Error(tr("서버에 연결할 수 없습니다. 연결을 확인하고 다시 시도하세요.", "Unable to reach the server. Check your connection and try again.")); }
    finally {if(deadline!==null)clearTimeout(deadline);}
    if (!response.ok) {
      const error = value.error?.startsWith("Mapbox search failed") ? "Mapbox search is unavailable." : value.error;
      throw new Error(tr(error, error) || `HTTP ${response.status}`);
    }
    return value;
  }
  let mapReady = false;
  let currentPlace = null, savedPlaces = [], editingId = null, deletePending = null;
  let savingEditor = false, searchVersion = 0, currentSearchQuery = '';
  let destinationBusy=false,destinationReadBusy=false,destinationRevision=0,destinationKnown=false,destinationError='',lastDestinationRead=-Infinity;
  const labels = {
    favoritesTitle: ['즐겨찾기', 'Favorites'], addFavorite: ['즐겨찾기 추가', 'Add favorite'],
    saveCurrent: ['현재 검색어 저장', 'Save current search'], nameLabel: ['이름', 'Name'],
    addressLabel: ['저장할 주소 또는 검색어', 'Address or search text to save'],
    saveFavorite: ['저장', 'Save'], cancelFavorite: ['취소', 'Cancel'], retryFavorites: ['다시 시도', 'Retry'],
    searchRegionLabel: ['검색 범위', 'Search region'],
  };
  for (const [id, words] of Object.entries(labels)) $(id).textContent = tr(...words);
  $('searchRegion').value = traditional && !/^zh-(hk|mo)/.test(language) ? 'tw' : '';
  $('searchRegion').options[0].textContent = tr('대만', 'Taiwan');
  $('searchRegion').options[1].textContent = tr('전 세계', 'Worldwide');
  $('favoritesNote').textContent = tr('이름과 직접 입력한 주소만 저장합니다. 즐겨찾기를 누르면 검색 결과에서 위치를 선택한 후 안내를 시작합니다.', 'Save a name and your own address text. Tap a favorite, then select a search result to navigate.');
  $('storageNote').textContent = tr('저장과 편집은 주소 API를 호출하지 않습니다. 안내할 때만 임시 검색을 사용합니다. 무료 한도 초과 시 요금이 발생할 수 있습니다. 영구 지오코딩은 사용하지 않습니다.', 'Saving and editing do not call an address API. Temporary search runs only when navigating. Usage above the free allowance may be billed. Permanent geocoding is disabled.');
  $('favoriteSearch').hidden = true;
  const endLabel=$('clear').textContent;
  function destinationAction(){
    $('clear').textContent=destinationKnown?endLabel:tr('목적지 다시 확인','Refresh navigation state');
    $('clear').disabled=destinationBusy||destinationReadBusy||(destinationKnown&&!currentPlace);
    $('endOnMap').hidden=!destinationKnown||!currentPlace;$('endOnMap').disabled=$('clear').disabled;$('endOnMap').textContent=endLabel;
  }
  function current(value) {
    currentPlace = value.destination || null;
    mapReady = value.map_ready === true;
    osm?.setDestination(currentPlace);
    destinationKnown=true;destinationError='';
    $('current').textContent = currentPlace?.place_name || tr('현재 목적지 없음', 'No current destination');
    $('saveCurrent').disabled = !currentPlace;
    destinationAction();
  }
  async function readDestination(){
    if(destinationReadBusy||destinationBusy)return;
    destinationReadBusy=true;destinationAction();lastDestinationRead=Date.now();const revision=destinationRevision;
    try{const value=await api('destination');if(revision===destinationRevision&&!destinationBusy)current(value);}
    catch(error){if(revision===destinationRevision){destinationKnown=false;destinationError=error.message;$('current').textContent=destinationError;}}
    finally{destinationReadBusy=false;destinationAction();}
  }
  async function changeDestination(method,place){
    if(destinationBusy)throw Error(tr('내비게이션 요청 처리 중입니다. 잠시 기다리세요.','A navigation request is already in progress.'));
    destinationBusy=true;destinationRevision++;destinationError='';$('clear').disabled=true;
    try{const value=await api('destination',{method,...(place?{headers:{'Content-Type':'application/json'},body:JSON.stringify(place)}:{})});current(value);}
    catch(error){destinationKnown=false;destinationError=error.message;throw error;}
    finally{destinationBusy=false;destinationAction();}
  }
  async function endNavigation(){
    if(destinationBusy||destinationReadBusy)throw Error(tr('내비게이션 요청 처리 중입니다. 잠시 기다리세요.','A navigation request is already in progress.'));
    if(!destinationKnown)throw Error(tr('목적지를 다시 확인하세요.','Read the navigation state again before ending navigation.'));
    if(!currentPlace)return {ended:false};
    await changeDestination('DELETE');currentSearchQuery='';
    $('status').textContent=tr('이 페이지의 내비게이션을 종료했습니다. 외부 내비게이션은 해당 앱에서 종료하세요.','Navigation from this page has ended. End external navigation in its source app.');
    return {ended:true};
  }
  globalThis.CarrotNavigationView=Object.freeze({
    snapshot:()=>({known:destinationKnown,mapReady:destinationKnown && mapReady,busy:destinationBusy||destinationReadBusy,active:destinationKnown&&!!currentPlace,label:currentPlace?.place_name||'',error:destinationError}),
    refresh:readDestination,end:endNavigation,
    refreshIfDue:()=>{if(Date.now()-lastDestinationRead>=5000)return readDestination();},
  });
  $('clear').disabled=true;readDestination();
  function button(text, action) {
    const element = document.createElement('button'); element.type = 'button'; element.textContent = text;
    element.addEventListener('click', async () => {
      element.disabled = true;
      try { await action(); } catch (error) { $('status').textContent = error.message; }
      finally { element.disabled = false; }
    });
    return element;
  }
  async function navigate(place, query) {
    await changeDestination('POST',place);
    currentSearchQuery = query;
    globalThis.dispatchEvent?.(new Event('carrot-navigation-started'));
    $('status').textContent = tr('현재 주행 목적지로 설정했습니다. GPS와 지도 수신을 기다립니다.', 'Destination set for this drive. Waiting for GPS and map data.');
  }
  function quality(place) {
    if (place.feature_type && place.feature_type !== 'address')
      return tr('도로 또는 지역 결과: 정확한 문패 위치가 아닐 수 있습니다.', 'Road or area result: this may not be an exact street address.');
    if (['low','medium'].includes(place.match_confidence) || ['interpolated','approximate'].includes(place.accuracy))
      return tr('추정 위치: 번지와 지도 위치를 확인하세요.', 'Approximate location: check the street number and map position.');
    return tr('문패와 실제 진입 위치를 확인한 후 선택하세요.', 'Check the street address and actual entrance before selecting.');
  }
  function renderResults(places, query) {
    $('results').replaceChildren();
    for (const place of places) {
      const row = document.createElement('li'), note = document.createElement('small');
      note.textContent = quality(place);row.append(button(place.place_name, () => navigate(place, query)),note);
      // Only the user's query is persisted, never temporary returned coordinates
      // or a returned standardized address, even from this shortcut.
      row.append(button(tr('검색어를 즐겨찾기에 저장', 'Save search text to favorites'), () => openEditor(null, {query})));
      $('results').append(row);
    }
  }
  async function runSearch(query) {
    query = String(query || '').trim();
    if (query.length < 2 || query.length > 200) { $('status').textContent=tr('2–200자를 입력하세요.', 'Enter 2–200 characters.');return; }
    const version = ++searchVersion;$('query').value = query;$('search').disabled = true;$('results').replaceChildren();
    $('status').textContent = tr('검색 중…', 'Searching…');
    const suffix = `&country=${encodeURIComponent($('searchRegion').value)}&language=${traditional?'zh-Hant':language.startsWith('ko')?'ko':'en'}`;
    try {
      const value = await api(`search?q=${encodeURIComponent(query)}${suffix}`);
      if (version !== searchVersion) return;
      const places=value.results;
      if(places.length===1&&places[0].feature_type==='address'&&['exact','high'].includes(places[0].match_confidence)&&!['interpolated','approximate'].includes(places[0].accuracy)){
        await navigate(places[0],query);return true;
      }
      renderResults(places, query);
      $('status').textContent = value.results.length ? tr('결과를 선택하면 안내를 시작합니다.', 'Select a result to start navigation.') : tr('검색 결과 없음', 'No results.');
    } catch (error) { if (version === searchVersion) $('status').textContent = error.message; }
    finally { if (version === searchVersion) $('search').disabled = false; }
  }
  $('form').addEventListener('submit', async event => {event.preventDefault();await runSearch($('query').value);});
  $('searchRegion').addEventListener('change',()=>{searchVersion++;$('search').disabled=false;$('results').replaceChildren();$('status').textContent=tr('범위 변경 후 다시 검색하세요.','Search again after changing region.');});
  $('endOnMap').addEventListener('click',async()=>{try{await endNavigation();}catch(error){$('status').textContent=error.message;}});
  $('clear').addEventListener('click', async () => {
    try { if(!destinationKnown){await readDestination();return;}await endNavigation(); }
    catch (error) { $('status').textContent = error.message; }
  });
  function renderFavorites(value) {
    if (!Array.isArray(value.favorites)) throw new Error(tr('즐겨찾기를 불러올 수 없습니다.', 'Favorites are unavailable.'));
    savedPlaces = value.favorites;$('favorites').replaceChildren();$('retryFavorites').hidden = true;
    $('favoritesStatus').textContent = savedPlaces.length ? '' : tr('즐겨찾기가 없습니다. 주소를 입력하여 추가하세요.', 'No favorites yet. Add your address text.');
    for (const place of savedPlaces) {
      const row = document.createElement('li');row.className = 'favorite-row';
      const go = button(place.name, async () => {
        if (place.provider === 'google') {openEditor(place.id,place);$('status').textContent=tr('이 즐겨찾기에 주소나 검색어를 입력하세요.', 'Enter an address or search text for this legacy favorite.');return;}
        const request=await api(`favorites/${encodeURIComponent(place.id)}/query`);
        if(request.requires_selection!==true||typeof request.query!=='string')throw Error(tr('내비게이션을 새로 고침하세요.', 'Reload navigation.'));
        const started=await runSearch(request.query);if(!started){$('query').focus();$('results').scrollIntoView?.({block:'nearest'});}
      });go.className = 'go';
      const address = document.createElement('small');address.textContent=place.query||place.place_name||tr('주소 입력 필요', 'Address text needed');
      const actions = document.createElement('div');actions.className = 'actions';
      actions.append(button(tr('편집', 'Edit'),()=>openEditor(place.id,place)));
      actions.append(button(deletePending===place.id?tr('삭제 확인','Confirm delete'):tr('삭제','Delete'),async()=>{
        if(deletePending!==place.id){deletePending=place.id;renderFavorites({favorites:savedPlaces});return;}
        renderFavorites(await api(`favorites/${encodeURIComponent(place.id)}`,{method:'DELETE'}));deletePending=null;
      }));
      if(deletePending===place.id)actions.append(button(tr('취소','Cancel'),()=>{deletePending=null;renderFavorites({favorites:savedPlaces});}));
      row.append(go,address,actions);$('favorites').append(row);
    }
  }
  async function loadFavorites(){try{renderFavorites(await api('favorites'));}catch(error){$('favoritesStatus').textContent=error.message;$('retryFavorites').hidden=false;}}
  function syncEditor(){const q=$('favoriteQuery').value.trim(),name=$('favoriteName').value.trim();$('saveFavorite').disabled=savingEditor||q.length<2||q.length>200||!name||name.length>80;}
  function openEditor(id,place){
    if(savingEditor)return;editingId=id;$('favoriteForm').hidden=false;
    $('editorTitle').textContent=id?tr('즐겨찾기 편집','Edit favorite'):tr('즐겨찾기 추가','Add favorite');
    const query=place?.query||place?.place_name||'';
    $('favoriteName').value=place?.name||query.slice(0,80);$('favoriteQuery').value=query;$('favoriteQuery').required=true;$('favoriteResults').replaceChildren();
    $('editorStatus').textContent=tr('직접 입력한 주소나 검색어를 저장합니다. 위치는 안내할 때 선택하세요.', 'Save your own address or search text. Select a location when navigating.');
    syncEditor();$('favoriteName').focus();
  }
  $('addFavorite').addEventListener('click',()=>openEditor(null,null));
  $('saveCurrent').addEventListener('click',()=>openEditor(null,{query:currentSearchQuery}));
  $('cancelFavorite').addEventListener('click',()=>{if(!savingEditor)$('favoriteForm').hidden=true;});
  $('favoriteQuery').addEventListener('input',syncEditor);$('favoriteName').addEventListener('input',syncEditor);
  $('favoriteForm').addEventListener('submit',async event=>{
    event.preventDefault();if(savingEditor)return;
    const name=$('favoriteName').value.trim(),query=$('favoriteQuery').value.trim();
    if(!name||name.length>80||query.length<2||query.length>200){syncEditor();return;}
    savingEditor=true;syncEditor();$('cancelFavorite').disabled=true;$('favoriteName').disabled=true;$('favoriteQuery').disabled=true;
    try{
      renderFavorites(await api(editingId?`favorites/${encodeURIComponent(editingId)}`:'favorites',{method:editingId?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({provider:'query',name,query})}));
      $('favoriteForm').hidden=true;$('status').textContent=tr('즐겨찾기를 저장했습니다.','Favorite saved.');
    }catch(error){$('editorStatus').textContent=error.message;}
    finally{savingEditor=false;$('cancelFavorite').disabled=false;$('favoriteName').disabled=false;$('favoriteQuery').disabled=false;syncEditor();}
  });
  $('retryFavorites').addEventListener('click',loadFavorites);loadFavorites();
  let imageUrl;
  function waiting(message) {
    $("map").hidden = true; $("map").removeAttribute("src");
    if (imageUrl) URL.revokeObjectURL(imageUrl); imageUrl = undefined;
    $("mapStatus").hidden = false; $("mapStatus").textContent = message;
  }
  waiting(tr("현재 위치와 목적지를 확인하고 있습니다.", "Checking position and destination."));
  async function refresh() {
    if (!document.hidden && viewVisible) {
      if(Date.now()-lastDestinationRead>=5000)void readDestination();
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
    setTimeout(refresh, 500);
  }
  if(!osm)refresh();
})();
