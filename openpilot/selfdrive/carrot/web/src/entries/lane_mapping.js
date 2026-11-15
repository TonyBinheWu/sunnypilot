import {MAX_PROJECT_BYTES,validateProject,visibleCells,projectPoints,sampleProject} from '../features/lane_mapping/model.js';
import {messages} from '../features/lane_mapping/messages.js';

const $=id=>document.getElementById(id);
let text=messages(document.documentElement.lang),project=null,enabled=new Set(),minTrips=1;
let selected=null,points=[],reviews={},zoom=1,yaw=0,pitch=Math.PI/2,pan=[0,0],synthetic=false;
let pending=null;
const canvas=$('scene'),ctx=canvas.getContext('2d');
function localize(lang){
  text=messages(lang);document.documentElement.lang=lang||'zh-TW';document.title=text.title;
  document.querySelectorAll('[data-text]').forEach(el=>{el.textContent=text[el.dataset.text]||el.dataset.text;});
  $('yaw').setAttribute('aria-label',text.yaw);$('file').setAttribute('aria-label',text.local);$('paste').setAttribute('aria-label',text.paste);
  $('scene').setAttribute('aria-label',text.title);$('support').setAttribute('aria-label',text.support);
  for(const id of ['zoomIn','zoomOut'])$(id).setAttribute('aria-label',text[id]);
  $('catalog').setAttribute('aria-label',text.catalogLabel);
  update();
}
function clearView(){zoom=1;yaw=0;pitch=Math.PI/2;pan=[0,0];$('yaw').value=0;}
function load(value,isSynthetic=false,confirmed=false){
  const next=validateProject(value);
  if(Object.keys(reviews).length&&!confirmed){pending=[value,isSynthetic];$('replaceConfirm').hidden=false;return;}
  pending=null;$('replaceConfirm').hidden=true;
  project=next;synthetic=isSynthetic||Object.values(next.trips).every(t=>t.source==='synthetic');
  enabled=new Set(Object.keys(next.trips));selected=null;reviews={};$('reviewJson').hidden=true;clearView();
  $('error').textContent='';$('tripList').replaceChildren();
  for(const [id,trip] of Object.entries(project.trips)){
    const label=document.createElement('label'),check=document.createElement('input');check.type='checkbox';check.checked=true;
    check.onchange=()=>{check.checked?enabled.add(id):enabled.delete(id);selected=null;update();};
    label.append(check,document.createTextNode(`${id} · ${trip.vehicle_id} · ${trip.source}`));$('tripList').append(label);
  }
  update();
}
function draw(){
  const rect=canvas.getBoundingClientRect(),width=rect.width,height=rect.height,dpr=Math.min(2,devicePixelRatio||1);
  canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.fillStyle='#121d2b';ctx.fillRect(0,0,width,height);
  ctx.strokeStyle='#263649';ctx.lineWidth=1;
  for(let x=width/2%40;x<width;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,height);ctx.stroke();}
  for(let y=height/2%40;y<height;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(width,y);ctx.stroke();}
  if(!project){points=[];return;}
  const cells=visibleCells(project,enabled,minTrips),changed=new Set([...project.changes.added_cells,...project.changes.shifted_cells]);
  points=projectPoints(cells,{width,height,yaw,pitch,zoom,pan});
  for(const p of points){
    if(p.x<0||p.y<0||p.x>width||p.y>height)continue;
    ctx.fillStyle=changed.has(p.cell.id)?'#f08cce':p.cell.dispersion_m>.4?'#f5b462':p.cell.trip_ids.filter(t=>enabled.has(t)).length>1?'#7ce6ad':'#64d7f0';
    const size=p.cell.id===selected?8:Math.max(2,Math.min(5,zoom*2));ctx.fillRect(p.x-size/2,p.y-size/2,size,size);
    if(reviews[p.cell.id]){ctx.strokeStyle=reviews[p.cell.id].status==='exclude'?'#ff8080':'white';ctx.strokeRect(p.x-5,p.y-5,10,10);}
  }
  $('count').textContent=String(cells.length);
}
function update(){
  $('projectInfo').textContent=project?`${text.revision}: ${project.revision.slice(0,16)} · ${text.frame}: ${project.frame.id} (ENU, m)`:'—';
  $('sourceNote').textContent=project?text[synthetic?'synthetic':'real']:text.empty;
  $('changeCounts').textContent=project?`${text.changed}: ${project.changes.added_cells.length} / ${project.changes.unobserved_cells.length} / ${project.changes.shifted_cells.length}`:'—';
  const cell=project?.cells.find(c=>c.id===selected);$('selection').hidden=!cell;
  if(cell){
    $('cellInfo').textContent=`${text.selected}: ${cell.id}\nE / N / U: ${cell.xyz.join(' / ')} m\n${text.dispersion}: ${cell.dispersion_m} m\n${text.bound}: ${cell.input_bound_m} m\n${text.vehicles}: ${cell.vehicle_count}\n${text.trips}: ${cell.trip_ids.join(', ')}`;
    $('note').value=reviews[cell.id]?.note||'';
    $('reviewState').textContent=reviews[cell.id]?text[{keep:'accept',exclude:'reject',inspect:'inspect'}[reviews[cell.id].status]]:'';
  }
  draw();
}
function fail(){ $('error').textContent=text.error; }
async function importText(raw){
  try{if(new TextEncoder().encode(raw).length>MAX_PROJECT_BYTES)throw Error('size');load(JSON.parse(raw));}catch{fail();}
}
$('file').onchange=async()=>{const file=$('file').files[0];if(!file)return;try{if(file.size>MAX_PROJECT_BYTES)throw Error('size');await importText(await file.text());}catch{fail();}$('file').value='';};
$('import').onclick=()=>{void importText($('paste').value);};
$('demo').onclick=()=>load(sampleProject(),true);
$('replace').onclick=()=>{if(pending)load(...pending,true);};
$('keep').onclick=()=>{pending=null;$('replaceConfirm').hidden=true;};
$('top').onclick=()=>{pitch=Math.PI/2;draw();};$('three').onclick=()=>{pitch=Math.PI/4;draw();};
$('zoomIn').onclick=()=>{zoom=Math.min(10,zoom*1.3);draw();};$('zoomOut').onclick=()=>{zoom=Math.max(.2,zoom/1.3);draw();};
$('reset').onclick=()=>{clearView();draw();};$('yaw').oninput=()=>{yaw=Number($('yaw').value)*Math.PI/180;draw();};
$('support').onchange=()=>{minTrips=Number($('support').value);selected=null;update();};
let drag=null;
canvas.onpointerdown=e=>{if(e.button!==0)return;drag={x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,moved:false};canvas.setPointerCapture(e.pointerId);};
canvas.onpointermove=e=>{if(!drag)return;pan[0]+=e.clientX-drag.x;pan[1]+=e.clientY-drag.y;drag.moved||=Math.hypot(e.clientX-drag.startX,e.clientY-drag.startY)>6;drag.x=e.clientX;drag.y=e.clientY;draw();};
canvas.onpointerup=e=>{
  if(!drag)return;
  if(!drag.moved){const rect=canvas.getBoundingClientRect(),x=e.clientX-rect.left,y=e.clientY-rect.top;
    const nearest=points.reduce((a,p)=>{const d=Math.hypot(p.x-x,p.y-y);return d<(a?.d??14)?{p,d}:a;},null);selected=nearest?.p.cell.id||null;update();}
  drag=null;
};canvas.onpointercancel=()=>{drag=null;};
for(const [button,status] of [['accept','keep'],['reject','exclude'],['inspect','inspect']])$(button).onclick=()=>{
  if(!selected)return;reviews[selected]={status,note:$('note').value.slice(0,160)};update();
};
$('note').oninput=()=>{if(selected&&reviews[selected])reviews[selected].note=$('note').value.slice(0,160);};
$('reviews').onclick=()=>{
  if(!project)return;
  const result={schema:'carrot-lane-reviews/v1',map_revision:project.revision,ground_truth:false,control_eligible:false,reviews};
  const raw=JSON.stringify(result,null,2);$('reviewJson').value=raw;$('reviewJson').hidden=false;
  const url=URL.createObjectURL(new Blob([raw],{type:'application/json'}));
  const a=document.createElement('a');a.href=url;a.download=`lane-reviews-${project.revision.slice(0,12)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);
};
async function catalog(){
  try{
    const response=await fetch('/api/lane-mapping/projects',{cache:'no-store'});if(!response.ok)throw Error('catalog');
    const value=await response.json();if(!Array.isArray(value.projects)||value.projects.length>32)throw Error('catalog');
    for(const name of value.projects){if(typeof name!=='string'||!/^[A-Za-z0-9_.-]{1,80}$/.test(name))continue;
      const option=document.createElement('option');option.value=name;option.textContent=name;$('catalog').append(option);}
    $('open').disabled=!$('catalog').options.length;
  }catch{$('open').disabled=true;}
}
$('open').onclick=async()=>{
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);$('open').disabled=true;
  try{
    const response=await fetch(`/api/lane-mapping/projects/${encodeURIComponent($('catalog').value)}`,{cache:'no-store',signal:controller.signal});
    if(!response.ok)throw Error('http');
    const reader=response.body.getReader(),decoder=new TextDecoder();let size=0,raw='';
    try{while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>MAX_PROJECT_BYTES)throw Error('size');raw+=decoder.decode(value,{stream:true});}raw+=decoder.decode();}
    finally{await reader.cancel().catch(()=>{});}
    await importText(raw);
  }catch{fail();}finally{clearTimeout(timer);$('open').disabled=false;}
};
new ResizeObserver(draw).observe(canvas);
localize(document.documentElement.lang);void catalog();
fetch('/api/web_settings',{cache:'no-store'}).then(r=>r.ok?r.json():null).then(v=>{if(v?.settings?.web_language)localize(v.settings.web_language);}).catch(()=>{});
window.addEventListener('beforeunload',e=>{if(Object.keys(reviews).length){e.preventDefault();e.returnValue='';}});
