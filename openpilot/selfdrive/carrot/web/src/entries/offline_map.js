import {vectorLayer} from '../features/cockpit/offline_vector_tiles.js';

function start({tr,onChange}){
  const button=document.getElementById('downloadOfflineMap'),label=document.getElementById('offlineMapStatus');
  const picker=document.getElementById('offlineCountry');
  const codes={taiwan:'TW','south-korea':'KR',andorra:'AD',luxembourg:'LU'};
  const names=new Intl.DisplayNames([document.documentElement.lang||navigator.language],{type:'region'});
  const name=id=>codes[id]?names.of(codes[id]):id;
  const countryLabel=document.getElementById('offlineCountryLabel');
  if(countryLabel)countryLabel.textContent=tr('오프라인 지도 국가','Offline map country');
  let info=null,loading=false,poll=null,closed=false,lastKey='',request=null;
  async function refresh(install=false){
    if(!button||!label||loading||closed)return;
    loading=true;clearTimeout(poll);
    request=new AbortController();const deadline=setTimeout(()=>request.abort(),10000);
    try{
      if(install){button.disabled=true;label.textContent=tr('다운로드 중','Downloading…');}
      const response=await fetch('/api/navigation/offline',{signal:request.signal,...(install?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({country:picker?.value||'taiwan'})}:{cache:'no-store'})});
      if(!response.ok)throw Error();
      const s=await response.json();if(closed)return;
      const busy=s.stage==='downloading'||s.stage==='verifying';button.disabled=busy;
      info=s.installed||null;
      if(picker){
        if(!picker.options.length){
          for(const id of s.countries||['taiwan'])picker.add(new Option(name(id),id));
          picker.value=info?.country||'taiwan';
        }
        picker.disabled=busy;
      }
      const mib=n=>(n/1048576).toFixed(0)+' MiB';
      const installed=info?name(info.country||'taiwan')+' · '+mib(info.bytes)+' · '+new Date(info.installedAt).toLocaleDateString():'';
      const messages={invalid:tr('지도 파일 손상. 다시 다운로드하세요.','Map file damaged. Download again.'),space:tr('저장 공간이 부족합니다.','Insufficient storage.'),failed:tr('다운로드 실패. 다시 시도하세요.','Download failed. Try again.'),verifying:tr('지도 확인 중','Verifying the map…')};
      label.textContent=[s.stage==='downloading'?tr('다운로드 중','Downloading…')+' '+mib(s.received)+(s.total?' / '+mib(s.total):''):messages[s.stage],installed].filter(Boolean).join(' · ')||tr('국가를 선택하세요.','Select a country to store its map on the device.');
      button.textContent=tr('지도 다운로드 또는 선택','Download or select map');
      const key=info?.version||'';if(key!==lastKey){lastKey=key;onChange();}
      if(busy)poll=setTimeout(()=>refresh(),1200);
    }catch{if(!closed){button.disabled=false;label.textContent=tr('장치 연결을 확인하세요.','Check the connection to the device.');poll=setTimeout(()=>refresh(),5000);}}
    finally{clearTimeout(deadline);request=null;loading=false;}
  }
  if(button)button.onclick=()=>refresh(true);
  const details=document.getElementById('mapConfig');
  details?.addEventListener('toggle',()=>{if(details.open)void refresh();});
  function stop(){closed=true;clearTimeout(poll);request?.abort();}
  return {refresh,stop,info:()=>info,layer(L){return vectorLayer(L,info);}};
}
globalThis.CarrotOfflineMap={start};
