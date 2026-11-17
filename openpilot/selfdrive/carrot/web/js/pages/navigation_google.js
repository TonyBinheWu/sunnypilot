/* Google is presentation/search only. Route geometry comes from mapsd/navRoute.
 * No Google routes, geocoding API, tile scraping, autocomplete or fetchFields.
 * Places UI Kit attribution remains visible in the original components.
 */
"use strict";
(() => {
  function coordinates(location) {
    const lat = typeof location?.lat === 'function' ? location.lat() : location?.lat;
    const lng = typeof location?.lng === 'function' ? location.lng() : location?.lng;
    if (typeof lat !== 'number' || typeof lng !== 'number' || !Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat)>85.05112878 || Math.abs(lng)>180) return null;
    return {lat,lng};
  }
  function reference(place, name) {
    if (!/^[A-Za-z0-9_-]{1,256}$/.test(place?.google_place_id || '')) throw Error('無效的 Google 地點。');
    // The name is user-entered. Do not persist Google's coordinates/address.
    return {provider:'google',google_place_id:place.google_place_id,name};
  }
  function create({doc=document,target=window,key='',language='zh-TW',onError=()=>{}}={}) {
    let loading=null,map=null,line=null,point=null,follow=true,routeId=null,position=null;
    let placesLoading=null;
    const sdk=()=>loading ||= new Promise((resolve,reject)=>{
      if (!/^[A-Za-z0-9_-]{20,128}$/.test(key)) {reject(Error('請先設定 Google 瀏覽器金鑰，並啟用 Maps JavaScript API 與 Places UI Kit API。'));return;}
      const script=doc.createElement('script'),callback='__carrotGoogleMapsReady';
      target.gm_authFailure=()=>onError(Error('Google 金鑰驗證失敗。請檢查帳單、已啟用 API 與 HTTP 來源限制；修正後重新載入頁面。'));
      const timer=target.setTimeout(()=>fail(),20000);
      const fail=()=>{target.clearTimeout(timer);delete target[callback];script.remove();reject(Error('Google 地圖載入失敗。請檢查金鑰、API、帳單、HTTP 來源限制與網路，修正後重新載入頁面。'));};
      target[callback]=()=>{target.clearTimeout(timer);delete target[callback];resolve(target.google.maps);};
      script.onerror=fail;script.async=true;
      const params=new URLSearchParams({key,v:'weekly',loading:'async',language,region:'TW',callback});
      script.src='https://maps.googleapis.com/maps/api/js?'+params;doc.head.append(script);
    });
    const places=()=>placesLoading ||= sdk().then(async g=>{await g.importLibrary('places');return g;});
    async function showMap(host) {
      if (map) return map;
      const g=await sdk();await g.importLibrary('maps');
      map=new g.Map(host,{center:{lat:23.7,lng:121},zoom:7,mapTypeId:'roadmap',mapTypeControl:true,streetViewControl:false,fullscreenControl:false,clickableIcons:false});
      line=new g.Polyline({map,strokeColor:'#1679e8',strokeOpacity:.9,strokeWeight:6});
      point=new g.Circle({map,radius:5,fillColor:'#1679e8',fillOpacity:1,strokeColor:'#fff',strokeWeight:2});
      map.addListener('dragstart',()=>{follow=false;});
      return map;
    }
    function updateRoute(value) {
      if(!map)return;
      const path=(value?.coordinates||[]).map(p=>Array.isArray(p)&&p.length===2?coordinates({lat:p[1],lng:p[0]}):null);
      const valid=path.length>=2&&path.length<=4096&&path.every(Boolean);
      line.setPath(valid?path:[]);
      position=coordinates(value?.position);point.setVisible(Boolean(position));if(position)point.setCenter(position);
      if(valid&&value.route_id!==routeId){routeId=value.route_id;const bounds=new target.google.maps.LatLngBounds();for(const p of path)bounds.extend(p);map.fitBounds(bounds,32);}
      if(!valid)routeId=null;
      if(position&&follow){map.panTo(position);if(map.getZoom()<14)map.setZoom(16);}
    }
    function waitFor(component,read,begin){
      return new Promise((resolve,reject)=>{
        const clean=()=>{target.clearTimeout(timer);component.removeEventListener('gmp-load',loaded);component.removeEventListener('gmp-error',failed);};
        const loaded=()=>{try{const result=read();clean();resolve(result);}catch(e){clean();reject(e);}};
        const failed=()=>{clean();reject(Error('Google 查詢失敗。請檢查 API 額度、金鑰限制與網路後再試。'));};
        const timer=target.setTimeout(failed,15000);component.addEventListener('gmp-load',loaded);component.addEventListener('gmp-error',failed);
        begin();
      });
    }
    async function search(query,host,onSelect) {
      await places();host.replaceChildren();
      const component=doc.createElement('gmp-place-search'),request=doc.createElement('gmp-place-text-search-request');
      component.setAttribute('selectable','');request.setAttribute('max-result-count','5');
      component.append(doc.createElement('gmp-place-standard-content'),request);
      let selected=false;
      component.addEventListener('gmp-select',e=>{
        const p=coordinates(e.place?.location);if(!p||selected)return;selected=true;
        void Promise.resolve(onSelect({latitude:p.lat,longitude:p.lng,place_name:query,provider:'google',google_place_id:e.place.id})).catch(onError).finally(()=>{selected=false;});
      });
      host.append(component);
      return waitFor(component,()=>component.places.length,()=>{request.textQuery=query;});
    }
    async function resolveFavorite(saved,host) {
      reference(saved,saved.name);await places();host.replaceChildren();
      const component=doc.createElement('gmp-place-details-compact'),request=doc.createElement('gmp-place-details-place-request');
      component.append(doc.createElement('gmp-place-standard-content'),request);host.append(component);
      return waitFor(component,()=>{
        const p=coordinates(component.place?.location);if(!p)throw Error('Google 地點已無可用座標，請重新搜尋。');
        return {latitude:p.lat,longitude:p.lng,place_name:saved.name,provider:'google',google_place_id:saved.google_place_id};
      },()=>{request.place=saved.google_place_id;});
    }
    return {showMap,updateRoute,search,resolveFavorite,recenter(){follow=true;if(position){map?.panTo(position);map?.setZoom(16);}}};
  }
  globalThis.CarrotNavigationGoogle={create,coordinates,reference};
})();
