/* Display only. The exact navRoute is copied read-only; mapsd/model stay untouched. */
'use strict';
(() => {
  const coordinate = (lat, lng) => Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 85.05112878 && Math.abs(lng) <= 180 ? [lat,lng] : null;
  function normalize(view) {
    const position=view?.position, point=coordinate(position?.lat,position?.lng);
    const raw=Array.isArray(view?.coordinates)&&view.coordinates.length<=4096?view.coordinates:[];
    const route=raw.map(p=>Array.isArray(p)?coordinate(p[1],p[0]):null);
    const step=view?.instruction;
    const instruction=Number(view?.route_id)>0&&point&&step&&[step.distance,step.remaining_m,step.remaining_s].every(n=>Number.isFinite(n)&&n>=0&&n<=1e8)?{...step,text:String(step.text||'').slice(0,256),modifier:String(step.modifier||'').slice(0,40)}:null;
    return {point,route:route.every(Boolean)&&Number(view?.route_id)>0?route:[],instruction};
  }
  function start({tr,isVisible}) {
    const host=document.getElementById('osmMap'),status=document.getElementById('mapStatus');
    const followButton=document.getElementById('mapFollow');
    const maneuver=document.getElementById('mapManeuver'),trip=document.getElementById('mapTrip');
    const distance=n=>n>=1000?`${(n/1000).toFixed(1)} km`:`${Math.round(n)} m`;
    function instruction(value){
      maneuver.hidden=trip.hidden=!value;if(!value)return;
      const arrows={'left':'←','slight left':'↖','sharp left':'↙','right':'→','slight right':'↗','sharp right':'↘','uturn':'↶'};
      document.getElementById('mapTurn').textContent=`${arrows[value.modifier]||'↑'} ${distance(value.distance)}`;
      document.getElementById('mapRoad').textContent=value.text;
      document.getElementById('mapRemaining').textContent=`${distance(value.remaining_m)} · ${Math.ceil(value.remaining_s/60)} ${tr('분','min')}`;
    }
    document.getElementById('map').hidden=true;
    document.getElementById('mapAttribution').innerHTML='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · <a href="https://www.openstreetmap.org/fixthemap">'+tr('지도 오류 신고','Report a map issue')+'</a> · <a href="https://download.geofabrik.de/asia/taiwan.html">Geofabrik</a>';
    let map,route,marker,destination,selected=null,follow=true,lastPoint=null,busy=false,stopped=false,firstFix=true,timer,tileUrl,nextConfigRead=0;
    let baseLayer=null,baseKey=null;
    const offline=globalThis.CarrotOfflineMap?.start({tr,onChange:syncBasemap});
    let parkingLayers=[],parkingAt=0,parkingBusy=false;
    async function refreshParking(){
      if(parkingBusy||Date.now()<parkingAt||!visible()||!map)return;parkingBusy=true;parkingAt=Date.now()+10000;
      const controller=new AbortController(),deadline=setTimeout(()=>controller.abort(),9000);
      try{const response=await fetch('/api/navigation/parking',{cache:'no-store',signal:controller.signal});if(!response.ok)throw Error();const value=await response.json();
        parkingLayers.forEach(layer=>map.removeLayer(layer));parkingLayers=[];
        if(visible()&&value.status==='ready')for(const area of (value.areas||[]).slice(0,80)){
          if(!Array.isArray(area.points)||area.points.length>300||!area.points.every(p=>Array.isArray(p)&&coordinate(p[0],p[1])))continue;
          const layer=globalThis.L.polygon(area.points,{color:'#b98924',weight:2,fillOpacity:.07});
          layer.bindTooltip(tr('지도에 표시된 주차 구획 · 빈자리 미확인','Mapped parking area / space · availability unknown'));layer.addTo(map);parkingLayers.push(layer);
        }
      }catch{parkingLayers.forEach(layer=>map.removeLayer(layer));parkingLayers=[];}
      finally{clearTimeout(deadline);parkingBusy=false;}
    }
    async function configure(){
      if(tileUrl||Date.now()<nextConfigRead)return;
      nextConfigRead=Date.now()+5000;const controller=new AbortController(),deadline=setTimeout(()=>controller.abort(),8000);
      try{const response=await fetch('/api/navigation/config',{cache:'no-store',signal:controller.signal});if(!response.ok)throw Error();const value=await response.json();await offline?.refresh();
        const url=value.osm_tile_url||'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
        if(url!=='https://tile.openstreetmap.org/{z}/{x}/{y}.png'&&!(url.startsWith('/')&&!url.startsWith('//')))throw Error();tileUrl=url;
      }catch{status.textContent=tr('지도를 불러올 수 없습니다. 페이지를 다시 여세요.','Unable to load the map. Reopen this page.');status.hidden=false;}
      finally{clearTimeout(deadline);}
    }
    const message=text=>{status.textContent=text;status.hidden=!text;};
    const visible=()=>{
      if(document.hidden||!isVisible())return false;
      try{const frame=window.frameElement;if(frame&&(getComputedStyle(frame).visibility==='hidden'||getComputedStyle(frame).display==='none'))return false;}catch{}
      return true;
    };
    function syncBasemap(){
      if(!map)return;
      const info=offline?.info(),point=map.getCenter?.(),bounds=info?.bounds;
      const useLocal=point&&bounds&&point.lat>=bounds[1]&&point.lat<=bounds[3]&&point.lng>=bounds[0]&&point.lng<=bounds[2];
      const key=useLocal?'local:'+info.version:'online';
      if(key===baseKey)return;
      if(baseLayer)map.removeLayer(baseLayer);
      baseKey=key;host.dataset.basemap=useLocal?'offline':'online';
      if(useLocal)baseLayer=offline.layer(globalThis.L);
      else baseLayer=globalThis.L.tileLayer(tileUrl,{maxZoom:19,keepBuffer:0,updateWhenIdle:true,referrerPolicy:'strict-origin-when-cross-origin'});
      baseLayer.on('tileerror',()=>message(useLocal?tr('오프라인 지도 파일을 확인하세요.','Unable to read offline tiles. Check the installed map.'):tr('OSM 지도를 받지 못했습니다. 연결을 확인하세요.','OSM tiles are unavailable. Check the connection.'))).addTo(map);
    }
    function ensureMap(){
      if(map)return true;if(!tileUrl)return false;
      const L=globalThis.L;
      if(!L){message(tr('지도를 불러올 수 없습니다. 페이지를 다시 여세요.','Unable to load the map. Reopen this page.'));return false;}
      host.hidden=false;
      map=L.map(host,{zoomControl:false,attributionControl:false}).setView([23.8,120.95],7);
      L.control.zoom({position:'topright',zoomInTitle:tr('확대','Zoom in'),zoomOutTitle:tr('축소','Zoom out')}).addTo(map);
      syncBasemap();
      map.on('moveend',syncBasemap);
      route=L.polyline([],{color:'#087bff',weight:6,opacity:.9}).addTo(map);
      map.on('dragstart',()=>{follow=false;followButton.hidden=false;});
      followButton.textContent=tr('현재 위치로','Current position');
      followButton.onclick=()=>{follow=true;followButton.hidden=true;if(lastPoint)map.setView(lastPoint,map.getZoom(),{animate:false});};
      if(typeof ResizeObserver==='function')new ResizeObserver(()=>map.invalidateSize({pan:false})).observe(host);
      return true;
    }
    function showDestination(){
      if(!map)return;
      if(destination){map.removeLayer(destination);destination=null;}
      const p=selected&&coordinate(selected.latitude,selected.longitude);
      if(p){destination=globalThis.L.circleMarker(p,{radius:8,color:'#fff',weight:3,fillColor:'#e54843',fillOpacity:1}).addTo(map);if(!lastPoint)map.setView(p,16,{animate:false});}
    }
    function setDestination(place){selected=place||null;if(visible()&&ensureMap())showDestination();}
    async function refresh(){
      if(stopped)return;
      if(visible()){await configure();refreshParking();}
      if(stopped)return;
      if(!busy&&visible()&&ensureMap()){
        busy=true;const controller=new AbortController(),deadline=setTimeout(()=>controller.abort(),8000);
        try{
          const response=await fetch('/api/navigation/route_view',{cache:'no-store',signal:controller.signal});
          if(!response.ok)throw Error();const view=normalize(await response.json());
          if(visible()){
          route.setLatLngs(view.route);lastPoint=view.point;instruction(view.instruction);
          if(marker){map.removeLayer(marker);marker=null;}
          if(view.point){marker=globalThis.L.circleMarker(view.point,{radius:9,color:'#fff',weight:3,fillColor:'#087bff',fillOpacity:1}).addTo(map);if(follow){map.setView(view.point,firstFix?Math.max(map.getZoom(),16):map.getZoom(),{animate:false});firstFix=false;}}
          showDestination();message(view.point||selected?'':tr('현재 GPS 위치를 기다리는 중입니다.','Waiting for a current GPS position.'));
          }
        }catch{route?.setLatLngs([]);instruction(null);if(marker){map.removeLayer(marker);marker=null;}lastPoint=null;message(tr('차량과 연결할 수 없습니다.','Unable to read map status. Check your connection to the vehicle.'));}
        finally{clearTimeout(deadline);busy=false;}
      }
      if(!stopped)timer=setTimeout(refresh,1000);
    }
    refresh();
    window.addEventListener('pagehide',()=>{stopped=true;clearTimeout(timer);offline?.stop();},{once:true});
    return {setDestination,normalize};
  }
  globalThis.CarrotNavigationOsm=Object.freeze({start,normalize});
})();
