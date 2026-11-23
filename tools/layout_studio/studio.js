"use strict";
const $ = s => document.querySelector(s);
const tabs = s => Array.from(document.querySelectorAll(s));
const sceneLayers = ["vehicle","lane","path","map"];
const names = {vehicle:"車輛模型",lane:"車道標線",path:"行駛軌跡",map:"導航地圖",device:"裝置", network:"網路", toggles:"功能開關", software:"軟體", firehose:"Firehose", developer:"開發者", egpu:"eGPU", language:"語言", pair:"配對", formosalink:"FormosaLink", hud:"儀表群組", speed:"目前車速", cruise:"巡航設定速度"};
function nativeLabel(key) {
  const translations = device==="c4" ? {firehose:"Firehose 資料分享",egpu:"外接 GPU"}
    : {toggles:"切換",firehose:"資料洪流",egpu:"外接 GPU",developer:"開發人員"};
  return translations[key] || names[key];
}
const panelData = {device:["裝置資訊","相機預覽","重新啟動"], network:["Wi-Fi","分享網路","進階設定"], toggles:["啟用 openpilot","實驗模式","車道偏離警示"], software:["軟體版本","檢查更新"], firehose:["Firehose 模式"], developer:["啟用 SSH","啟用 ADB"], egpu:["外接顯示卡","運算狀態"]};
const labels = {menu_font:"選單字級", menu_spacing:"間距", speed_font:"車速字級", cruise_font:"巡航字級"};
const dimensions = {c4:[536,240], c3x:[2160,1080]};
const icons = {egpu:"network", language:"toggles", formosalink:"pair"};
const savedKey = "formosa-native-studio-v1";
let device = "c4", view = "settings", selection = {c4:"toggles", c3x:"device"}, instrument = "speed";
let targets = {}, applied;
let exported, published, canPublish = false;
let base, draft, revision, limits, defaults, scale = 1, busy = false, railLeft = 0;
const clone = obj => JSON.parse(JSON.stringify(obj));
const layout = () => draft.devices[device];
const setStatus = msg => { $("#status").textContent = msg; };
function element(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}
function button(label, cls, action) {
  const btn = element("button", cls, label);
  btn.type = "button";
  btn.onclick = action;
  return btn;
}
function box(node, x, y, w, h) {
  Object.assign(node.style, {left:x+"px",top:y+"px",width:w+"px",height:h+"px"});
  return node;
}
function same(a,b) { return JSON.stringify(a) === JSON.stringify(b); }
function saveDraft() {
  const dirty = !same(draft,base);
  let saved = true;
  try { localStorage.setItem(savedKey,JSON.stringify({revision,profile:draft,device,view})); } catch { saved = false; }
  setStatus(dirty ? (saved ? "草稿已儲存在此瀏覽器" : "草稿僅保留在此頁面") : "目前顯示已輸出版面");
  if (!dirty && published) setStatus("已推送至 carrot-wip · "+published.slice(0,9));
  else if (!dirty && revision===exported) setStatus("已輸出到本機分支，等待推送");
  $("#export").disabled = busy || (!dirty && revision===exported);
  $("#apply").textContent="套用到 "+device.toUpperCase();
  $("#apply").disabled=busy || dirty || revision!==exported || !targets[device];
  $("#publish").hidden = !canPublish;
  $("#publish").disabled = busy || dirty || revision!==exported || Boolean(published) || (Object.keys(targets).length>0 && revision!==applied);
}
async function loadProfile(restore) {
  const response = await fetch("/api/layout",{cache:"no-store"});
  if (!response.ok) throw new Error("讀取版面失敗");
  const data = await response.json();
  applied=data.applied; targets=data.targets || {};
  canPublish = data.canPublish; exported = data.exported; published = data.published;
  base = data.profile; draft = clone(base); revision = data.revision; limits = data.limits; defaults = data.defaults;
  let warning = "";
  if (restore) {
    try {
      const stored = JSON.parse(localStorage.getItem(savedKey));
      if (stored?.revision===revision) for (const d of Object.keys(dimensions)) {
        const v=stored.profile?.devices?.[d];
        if(v && v.scene_style===undefined) Object.assign(v,Object.fromEntries(Object.entries(base.devices[d]).filter(([k])=>/^(scene|vehicle|lane|path|map)_/.test(k))));
      }
      if (stored && stored.revision === revision && valid(stored.profile)) {
        draft = stored.profile;
        if (stored.device in dimensions) device = stored.device;
        if (["settings","driving"].includes(stored.view)) view = stored.view;
      } else if (stored) warning = "分支檔案已有更新，已載入最新版面";
    } catch { warning = "已載入分支版面"; }
  }
  render(true); saveDraft();
  if (warning) setStatus(warning);
}
function valid(profile) {
  if (!profile || profile.version !== 1) return false;
  return Object.keys(dimensions).every(d => {
    const value = profile.devices?.[d], fields = limits[d];
    if (!value || !Array.isArray(value.order) || !same([...value.order].sort(),[...base.devices[d].order].sort())) return false;
    return Object.keys(fields).every(k => Number.isInteger(value[k]) && value[k]>=fields[k][0] && value[k]<=fields[k][1]);
  });
}
function sizePreview() {
  const [w,h] = dimensions[device], frame = $("#viewport"), screen = $("#screen");
  frame.style.aspectRatio = w+"/"+h;
  scale = frame.clientWidth / w;
  Object.assign(screen.style, {width:w+"px",height:h+"px",transform:"scale("+scale+")"});
}
function render(focusSelection=false) {
  for (const b of tabs("[data-device]")) b.setAttribute("aria-pressed",String(b.dataset.device===device));
  for (const b of tabs("[data-view]")) b.setAttribute("aria-pressed",String(b.dataset.view===view));
  $("#resolution").textContent = dimensions[device].join(" × ")+" px";
  renderStyles(); sizePreview(); renderScreen(focusSelection); renderList(); renderInspector();
}
function choose(key) {
  if (view==="settings") selection[device]=key; else instrument=key;
  render(true);
}
function renderList() {
  const menu = view==="settings", list = menu ? layout().order : [...(layout().scene_style ? sceneLayers : []),"hud","speed","cruise"];
  $("#structure-title").textContent = menu ? "選單排序" : "駕駛儀表";
  $("#count").textContent = list.length+" 項";
  const container=$("#structure"); container.replaceChildren();
  list.forEach((key,i) => {
    const active = key===(menu?selection[device]:instrument);
    const row=element("div","layer"+(active?" active":""));
    const select=button("", "select", ()=>choose(key));
    select.setAttribute("aria-pressed",String(active));
    select.append(element("small","",String(i+1).padStart(2,"0")),element("span","",names[key]));
    row.append(select);
    if (menu) {
      for (const [offset,mark,title] of [[-1,"↑","往前"],[1,"↓","往後"]]) {
        const move=button(mark,"move",()=>{
          const order=layout().order;
          [order[i],order[i+offset]]=[order[i+offset],order[i]];
          selection[device]=key; render(true); saveDraft();
          const next=document.getElementById(key+"-"+offset);
          (next.disabled ? next.parentElement.querySelector(".select") : next).focus({preventScroll:true});
        });
        move.title=names[key]+title; move.setAttribute("aria-label",move.title);
        move.id=key+"-"+offset; move.disabled=i+offset<0 || i+offset>=list.length;
        row.append(move);
      }
    }
    container.append(row);
  });
  if (!menu) container.append(button("互換車速與巡航左右位置","swap",()=>{
    const v=layout(), small=device==="c4";
    const speedCenter=small ? 18+$("#screen .speed").offsetWidth/2 : 100;
    const cruiseCenter=small ? 307*.76 : 270;
    const distance=cruiseCenter+v.cruise_x-speedCenter-v.speed_x;
    for(const [key,delta] of [["speed_x",distance],["cruise_x",-distance]]) {
      const [lo,hi]=limits[device][key];
      v[key]=Math.max(lo,Math.min(hi,v[key]+Math.round(delta)));
    }
    render();saveDraft();
  }));
}
const drivingStyles = [
  {name:"原廠配置"},
  {name:"大字車速", c4:{speed_font:88,cruise_font:30,hud_y:-6}, c3x:{speed_font:138,cruise_font:42,hud_y:-24}},
  {name:"精簡低位", c4:{speed_font:56,cruise_font:28,hud_y:4,speed_y:8}, c3x:{speed_font:86,cruise_font:38,speed_y:16}},
  {name:"巡航優先", c4:{cruise_x:-178,cruise_font:48,speed_x:154,speed_font:56}, c3x:{cruise_x:-168,cruise_font:72,speed_x:166,speed_font:84}},
  {name:"抬高儀表", c4:{hud_y:-22,hud_x:30,speed_font:68}, c3x:{hud_y:-100,hud_x:144,speed_font:108}},
];
const drivingKeys = ["speed_font","speed_x","speed_y","cruise_font","cruise_x","cruise_y","hud_x","hud_y"];
function renderStyles() {
  const scene = $("#scene-style");
  scene.parentElement.hidden = view !== "driving";
  scene.selectedIndex = layout().scene_style;
  scene.onchange = () => {
    layout().scene_style = scene.selectedIndex;
    instrument = layout().scene_style ? "vehicle" : "speed";
    render(); saveDraft();
  };
  if (!layout().scene_style && sceneLayers.includes(instrument)) instrument="speed";
  const picker = $("#drive-style");
  picker.parentElement.hidden = view !== "driving";
  if (view !== "driving") return;
  const values = style => Object.fromEntries(drivingKeys.map(key =>
    [key, style[device]?.[key] ?? defaults.devices[device][key]]));
  if (!picker.options.length) {
    picker.add(new Option("自訂配置","custom"));
    picker.options[0].disabled = true;
    drivingStyles.forEach((style,i) => picker.add(new Option(style.name,String(i))));
  }
  const match = drivingStyles.findIndex(style => Object.entries(values(style)).every(([key,value]) => layout()[key] === value));
  picker.value = match < 0 ? "custom" : String(match);
  picker.onchange = () => {
    Object.assign(layout(),values(drivingStyles[Number(picker.value)]));
    render(); saveDraft();
  };
}
function renderInspector() {
  const menu=view==="settings";
  $("#inspector-title").textContent = menu ? "選單樣式" : names[instrument];
  const layer = !menu && sceneLayers.includes(instrument);
  $("#inspector-title").nextElementSibling.textContent=layer ? "%" : "px";
  const keys=layer ? ["size","x","y","color"].map(field=>instrument+"_"+field) : menu ? ["menu_font","menu_spacing"] : (instrument==="hud" ? ["hud_x","hud_y"] : [instrument+"_font",instrument+"_x",instrument+"_y"]);
  const container=$("#inspector"); container.replaceChildren();
  for (const key of keys) {
    const row=element("div","pair");
    if (key.endsWith("_color")) {
      const label=element("label","",instrument==="map"?"導航路線顏色":"圖層顏色");
      const input=element("input");input.type="color";input.id=key;label.htmlFor=key;
      input.value="#"+layout()[key].toString(16).padStart(6,"0");
      input.oninput=()=>{layout()[key]=parseInt(input.value.slice(1),16);renderScreen();saveDraft();};
      row.append(label,input);container.append(row);continue;
    }
    const title=key.endsWith("_size") ? ({lane:"標線寬度",path:"軌跡寬度",vehicle:"模型大小",map:"地圖大小"})[instrument] : key==="menu_spacing" ? (device==="c4"?"卡片間距":"選單列高") : labels[key] || (key.endsWith("_x")?"水平位移":"垂直位移");
    const label=element("label","",title);
    const number=element("input"), range=element("input");
    number.type="number";range.type="range";label.htmlFor=number.id="num-"+key;
    range.id="range-"+key;range.setAttribute("aria-label",title);
    const [min,max]=limits[device][key];
    for (const input of [number,range]) Object.assign(input,{min,max,step:1,value:layout()[key]});
    function apply(value) {
      if (!Number.isFinite(value)) return;
      layout()[key]=Math.max(min,Math.min(max,Math.round(value)));
      number.value=range.value=layout()[key];renderScreen(false);renderStyles();saveDraft();
    }
    range.oninput=()=>apply(range.valueAsNumber);
    number.onchange=()=>Number.isFinite(number.valueAsNumber)?apply(number.valueAsNumber):(number.value=layout()[key]);
        row.append(label,number,range);
    if (!menu) {
      const adjust=element("div","fine-adjust");
      for (const [caption,change] of [["−1",-1],["+1",1],["還原",0]]) {
        const step=button(caption,"",()=>apply(change ? layout()[key]+change : defaults.devices[device][key]));
        step.setAttribute("aria-label",title+" "+caption);adjust.append(step);
      }
      row.append(adjust);
    }
    container.append(row);
  }
}
function renderMenu(screen,focusSelection) {
  const v=layout(), selected=selection[device];
  if (device==="c4") {
    const rail=element("div","rail"), track=element("div","rail-track");
    const gap=v.menu_spacing, pitch=402+gap;
    track.style.width=(40+pitch*v.order.length-gap)+"px";
    v.order.forEach((key,i)=>{
      const card=box(button("","native native-card",()=>choose(key)),20+i*pitch,30,402,180);
      const label=element("span","",nativeLabel(key));
      label.style.fontSize=(key==="formosalink"?Math.round(v.menu_font*.875):v.menu_font)*1.16+"px";
      if(key==="pair" || key==="formosalink") {
        card.classList.add("paired-card");
        card.append(element("small","sub-label",key==="pair"?"connect.comma.ai":"掃描 QR 配對"));
      }
      const img=element("img");img.alt="";img.src="/assets/"+(icons[key]||key)+".png";img.width=key==="pair"||key==="formosalink"?33:key==="network"||key==="egpu"?76:64;img.height=60;
      card.append(label,img);track.append(card);
    });
    rail.append(track); screen.append(rail);
    rail.scrollLeft=focusSelection ? v.order.indexOf(selected)*pitch : railLeft;
    railLeft=rail.scrollLeft;
    rail.onscroll=()=>{railLeft=rail.scrollLeft;};
    rail.onwheel=e=>{if (Math.abs(e.deltaY)>Math.abs(e.deltaX)) {e.preventDefault();rail.scrollLeft+=e.deltaY;}};
  } else {
    const content=box(element("div","native"),500,0,1660,1080);
    content.style.cssText+=";background:#292929;padding:75px 85px";
    (panelData[selected]||[]).forEach(name=>{
      const row=element("div","stock-row",name);row.style.height="145px";row.append(element("small","","›"));content.append(row);
    });
    screen.append(content);
    const sidebar=box(element("div","native big-menu"),0,0,500,1080);
    const close=box(element("span","native","×"),150,60,200,200);
    close.style.cssText+=";border-radius:50%;background:#292929;display:grid;place-items:center;font-size:100px";sidebar.append(close);
    v.order.forEach((key,i)=>{
      const tab=box(button(nativeLabel(key),"native"+(key===selected?" chosen":""),()=>choose(key)),50,300+i*v.menu_spacing,350,v.menu_spacing);
      tab.style.fontSize=v.menu_font*1.16+"px";sidebar.append(tab);
    });
    screen.append(sidebar);
  }
}
function drawRoad(canvas) {
  const [w,h]=dimensions[device];canvas.width=w;canvas.height=h;
  const ctx=canvas.getContext("2d");ctx.scale(w,h);
  const sky=ctx.createLinearGradient(0,0,0,.48);
  sky.addColorStop(0,"#536e83");sky.addColorStop(1,"#bbc9c5");ctx.fillStyle=sky;ctx.fillRect(0,0,1,1);
  function polygon(points,color) {ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fillStyle=color;ctx.fill();}
  polygon([[0,.4],[.12,.28],[.27,.41],[.38,.36],[.55,.44],[.76,.29],[.85,.36],[1,.22],[1,1],[0,1]],"#526d68");
  polygon([[0,.47],[.28,.41],[.45,.44],[.49,.45],[.69,.4],[1,.44],[1,1],[0,1]],"#45594d");
  polygon([[.47,.455],[.55,.455],[1,.82],[1,1],[0,1],[0,.84]],"#3c484e");
  polygon([[.505,.46],[.518,.46],[.65,1],[.375,1]],"#4f7976");
  for(const [end,mark] of [[-.2,"#f6d480"],[.28,"#f9f6eb"],[.76,"#f9f6eb"],[1.23,"#e7ece7"]]) {
    const center=.51; const at=z=>center+(end-center)*z;
    const segments=(end===.28||end===.76)?[[.01,.025],[.05,.08],[.12,.17],[.24,.33],[.44,.59],[.78,1]]:[[.015,1]];
    for(const [a,b] of segments) polygon([[at(a)-a*.005,.456+.544*a],[at(a)+a*.005,.456+.544*a],[at(b)+b*.005,.456+.544*b],[at(b)-b*.005,.456+.544*b]],mark);
  }
}
function renderDriving(screen) {
  const v=layout(), small=device==="c4", [w,h]=dimensions[device];
  const canvas=element("canvas","road");if(v.scene_style) drawRealityScene(canvas,w,h,v); else drawRoad(canvas);screen.append(canvas);
  if (v.scene_style) {
    const group=box(element("div","minimal-hud"),0,0,w,h);
    for (const [part,value,label,anchor] of [["speed","72","km/h",.035],["cruise","80","MAX",small?.24:.17]]) {
      const size=v[part+"_font"]*.66;
      const x=Math.max(3,Math.min(w-size*2,w*anchor+v.hud_x+v[part+"_x"]));
      const y=Math.max(2,Math.min(h-size*2,h*.045+v.hud_y+v[part+"_y"]));
      const block=element("div","minimal-reading "+part);
      block.dataset.part=part;
      Object.assign(block.style,{left:x+"px",top:y+"px",fontSize:size+"px",color:v.scene_style===1?"#eff5f8":"#142735"});
      block.append(element("span","",value),element("small","",label));
      group.append(block);
    }
    screen.append(group);
    return;
  }
  const pw=small?307:350, ph=small?115:150;
  const panel=box(element("div","instruments"),(small?10:40)+v.hud_x,h-(small?125:290)+v.hud_y,pw,ph);
  panel.dataset.part="hud";
  if(!small) {
    const back=box(element("div","native big-hud-bg"),20+v.hud_x,h-360+v.hud_y,475,355);
    back.dataset.part="hud";screen.append(back);
  }
  function reading(id,text,x,y,font,transform) {
    const n=element("span","reading "+id,text);
    Object.assign(n.style,{left:x+"px",top:y+"px",fontSize:font*1.16+"px",transform});
    if(id!=="fixed") n.dataset.part=id; panel.append(n);
  }
  reading("speed","72",(small?18:100)+v.speed_x,(small?ph*.48-2:116)+v.speed_y,v.speed_font,small?"translateY(-50%)":"translate(-50%,-100%)");
  reading("cruise","80",(small?pw*.76:270)+v.cruise_x,(small?ph*.33:81)+v.cruise_y,v.cruise_font,small?"translate(-50%,-50%)":"translate(-50%,-100%)");
  if(small) {
    reading("fixed","3",pw*.90,ph*.82,28,"translate(-50%,-50%)");
    const gear=box(element("span","native gear","D"),pw+12,ph*.50,44,54);
    panel.append(gear);
  }
  screen.append(panel);
}
function renderScreen(focusSelection=false) {
  const screen=$("#screen");screen.replaceChildren();
  if (view==="settings") renderMenu(screen,focusSelection); else renderDriving(screen);
}
let drag=null;
$("#screen").onpointerdown=e=>{
  const part=e.target.closest("[data-part]")?.dataset.part;
  if(!part || view!=="driving") return;
  instrument=part;renderList();renderInspector();
  drag={part,x:e.clientX,y:e.clientY,baseX:layout()[part+"_x"],baseY:layout()[part+"_y"]};
  $("#screen").setPointerCapture(e.pointerId);
};
$("#screen").onpointermove=e=>{
  if(!drag) return;
  for(const [axis,delta,start] of [["x",e.clientX-drag.x,drag.baseX],["y",e.clientY-drag.y,drag.baseY]]) {
    const key=drag.part+"_"+axis,[low,high]=limits[device][key];
    layout()[key]=Math.max(low,Math.min(high,Math.round(start+delta/scale)));
  }
  renderScreen();renderInspector();
};
function endDrag(){if(drag){drag=null;renderStyles();saveDraft();}}
$("#screen").onpointerup=endDrag;$("#screen").onpointercancel=endDrag;
for(const btn of tabs("[data-device]")) btn.onclick=()=>{if(!draft)return;device=btn.dataset.device;render(true);saveDraft();};
for(const btn of tabs("[data-view]")) btn.onclick=()=>{if(!draft)return;view=btn.dataset.view;render(true);saveDraft();};
new ResizeObserver(sizePreview).observe($("#viewport"));
function confirmAction(title,text,action) {
  const dialog=$("#confirm");$("#dialog-title").textContent=title;$("#dialog-text").textContent=text;
  dialog.returnValue="cancel";dialog.onclose=()=>{ if(dialog.returnValue==="ok") action(); };dialog.showModal();
}
$("#reset").onclick=()=>draft && confirmAction("還原 "+device.toUpperCase()+" 預設值？","這會取代此裝置兩個畫面的草稿。",()=>{
  draft.devices[device]=clone(defaults.devices[device]);render(true);saveDraft();
});
$("#reload").onclick=()=>confirmAction("載入已輸出版面？","目前的草稿將以分支檔案取代。",()=>loadProfile(false).catch(err=>setStatus(err.message)));
$("#export").onclick=async()=>{
  const profile=clone(draft);busy=true;$("#export").disabled=true;
  try {
    const res=await fetch("/api/export",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({revision,profile})});
    const data=await res.json();if(!res.ok) throw new Error(data.error || "輸出失敗");
    base=data.profile;revision=data.revision;exported=revision;published=null;busy=false;saveDraft();
    if(same(base,draft)) setStatus("已輸出到本機分支，等待推送");
  } catch(err) { busy=false;$("#export").disabled=false;setStatus(err.message); }
};
$("#apply").onclick=()=>confirmAction("套用到 "+device.toUpperCase()+"？",targets[device]+" 將於停車熄火狀態安裝已輸出的版面及介面程式，下次啟動車機介面時生效。",async()=>{
  if(busy || !same(base,draft) || revision!==exported) return;
  const selected=device;
  busy=true;saveDraft();setStatus("正在核對車機與套用版本…");
  try {
    const res=await fetch("/api/apply",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({device:selected,revision})});
    const data=await res.json();if(!res.ok) throw new Error(data.error);
    applied=revision;busy=false;saveDraft();setStatus(selected.toUpperCase()+" 已套用 "+data.commit.slice(0,9)+"，下次啟動介面生效");
  } catch(err){busy=false;saveDraft();setStatus("套用失敗 · "+err.message);}
});
$("#publish").onclick=()=>confirmAction("推送到 carrot-wip？","這會把已輸出的 C3X、C4 版面與本機分支的介面更新推送至 origin/carrot-wip。",async()=>{
  if (busy || !same(base,draft) || revision!==exported) return;
  busy=true;saveDraft();setStatus("正在推送並核對遠端版本…");
  try {
    const res=await fetch("/api/publish",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({revision})});
    const data=await res.json();if(!res.ok) throw new Error(data.error || "推送失敗");
    published=data.commit;busy=false;saveDraft();
  } catch(err) { busy=false;saveDraft();setStatus(err.message); }
});
loadProfile(true).catch(err=>setStatus("無法載入版面 · "+err.message));
