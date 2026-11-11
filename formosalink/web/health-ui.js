// Device health rendering. Null/stale readings stay unknown, including zero SOC.
export function healthValue(value,unit=''){return typeof value==='number'&&Number.isFinite(value)?`${value}${unit}`:'—';}
export function temperatureList(value){return Array.isArray(value)&&value.length?value.map(v=>healthValue(v,' °C')).join(' / '):'—';}
const expanded=new Set();
export function deviceHealth(container,{devices,t,el,date,onOpen}){
 const grid=el('div',undefined,'health-grid');container.append(grid);
 for(const d of devices.filter(x=>x.state==='paired')){
  const info=d.health||{},valid=d.health_fresh&&info.health_valid,card=el('article',undefined,'workspace-card health-card');
  const heading=el('div',undefined,'health-card-heading'),name=el('h2',d.name),open=el('button',t('deviceSettings'),'workspace-save');open.type='button';open.addEventListener('click',()=>onOpen(d));const title=el('div');title.append(name,el('small',t(valid?'connected':d.health_fresh?'stale':'offline'),'workspace-muted'));heading.append(title,open);card.append(heading);
  card.append(el('p',[info.device_model||info.hardware||'FormosaPilot',info.vehicle_brand,info.vehicle_platform].filter(Boolean).join(' · '),'workspace-muted'));
  const dl=el('dl',undefined,'device-details');
  const field=(title,value)=>dl.append(el('dt',t(title)),el('dd',value));
  field('info_vehicle_vin',info.vehicle_vin||'—');
  field('vehicleSoc',d.health_fresh&&info.soc_status==='available'?healthValue(info.vehicle_soc_percent,' %'):t(!d.health_fresh?'stale':info.soc_status==='unsupported'?'socUnsupported':'unknown'));
  field('cpu',valid?temperatureList(info.cpu_temperatures):'—');field('gpu',valid?temperatureList(info.gpu_temperatures):'—');field('deviceTemperature',valid?healthValue(info.max_temp_c,' °C'):'—');
  const gpuStatus=!valid?'unknown':info.egpu_status||'unknown';
  field('egpu',gpuStatus==='available'?healthValue(info.egpu_temp_c,' °C'):t('egpu_'+gpuStatus));
  if(gpuStatus==='available')field('egpuMemory',healthValue(info.egpu_memory_temp_c,' °C'));
  card.append(dl);
  const sensors=el('details',undefined,'health-sensors');sensors.open=expanded.has(d.id);sensors.addEventListener('toggle',()=>{if(sensors.open)expanded.add(d.id);else expanded.delete(d.id);});sensors.append(el('summary',t('allSensors')));const list=el('dl',undefined,'device-details');
  for(const key of ['memory_temp_c','dsp_temp_c','intake_temp_c','exhaust_temp_c','gnss_temp_c','bottom_soc_temp_c','pmic_temperatures','modem_temperatures'])list.append(el('dt',t('info_'+key)),el('dd',valid&&info[key]!=null&&(!Array.isArray(info[key])||info[key].some(v=>typeof v==='number'))?(Array.isArray(info[key])?temperatureList(info[key]):healthValue(info[key],' °C')):t('sensorUnavailable')));
  (info.thermal_names||[]).forEach((name,index)=>list.append(el('dt',name),el('dd',valid?healthValue(info.thermal_values?.[index],' °C'):'—')));
  sensors.append(list);card.append(sensors,el('p',`${t('received')} ${date(d.health_received_at)}`,'workspace-muted'));grid.append(card);
 }
 if(!grid.childElementCount)grid.append(el('p',t('noDevices'),'workspace-empty'));
}
