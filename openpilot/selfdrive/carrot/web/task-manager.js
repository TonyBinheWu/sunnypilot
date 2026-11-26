const el=id=>document.getElementById(id);
const pct=n=>Number.isFinite(n)?n.toFixed(1)+"%":"—";
const gib=n=>Number.isFinite(n)?(n/2**30).toFixed(2)+" GiB":"—";
const temp=n=>Number.isFinite(n)?n.toFixed(1)+" °C":"—";
const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!=null)e.textContent=text;if(cls)e.className=cls;return e};
const chip=text=>node("span",text,"chip");
function metric(name,val,note,fraction){
  const e=node("div",null,"metric");e.append(node("small",name),node("strong",val),node("small",note));
  if(Number.isFinite(fraction)){const bar=node("progress");bar.max=100;bar.value=fraction;e.append(bar)}return e;
}
let timer,controller,paused=false,current=null,library=null,libraryAt=0,loadingLibrary=false;
async function modelStatus(){
  if(loadingLibrary||Date.now()-libraryAt<30000)return;
  loadingLibrary=true;libraryAt=Date.now();
  const abort=new AbortController(),timeout=setTimeout(()=>abort.abort(),4000);
  try{const r=await fetch("/api/egpu/model",{cache:"no-store",signal:abort.signal});
    const model=r.ok?await r.json():null;library=model?.available?{name:model.display_name||model.model_id,compiled:model.compiled}:null;
  }catch{library=null}finally{clearTimeout(timeout);loadingLibrary=false}
}
function processRows(){const key=el("sort").value;
  el("procs").replaceChildren(...[...(current?.processes||[])].sort((a,b)=>(b[key]??-1)-(a[key]??-1)).map(p=>{
    const row=node("tr");for(const v of [p.name,p.pid,pct(p.cpu),gib(p.rss)])row.append(node("td",v));return row;
  }));
}
function paint(s){current=s;const cpus=s.cores.filter(Number.isFinite),cpu=cpus.length?cpus.reduce((a,b)=>a+b,0)/cpus.length:null;
  const capacity=(title,v)=>Number.isFinite(v.total)&&Number.isFinite(v.free)&&v.total>0
    ?metric(title,gib(v.total-v.free),"可用 "+gib(v.free)+" ／ 共 "+gib(v.total),100*(1-v.free/v.total))
    :metric(title,pct(v.percent),"使用率",v.percent);
  el("metrics").replaceChildren(metric("CPU",pct(cpu),"整機平均",cpu),metric("內建 GPU",pct(s.gpu),"硬體使用率",s.gpu),capacity("記憶體",s.memory),capacity("儲存空間",s.disk));
  el("cores").replaceChildren(...s.cores.map((n,i)=>chip("CPU "+i+" · "+pct(n))));if(!s.cores.length)el("cores").textContent="等待下一次取樣";
  el("temps").replaceChildren(...s.temps.map(([k,v])=>chip(k+" · "+temp(v))));if(!s.temps.length)el("temps").textContent="未取得溫度感測器";
  const g=s.egpu, box=el("external");box.replaceChildren(node("strong",g.bridge||g.cards.map(c=>c.name).join("、")||(g.workers.length?"GPU 工作程序運行中":"未偵測到外接 GPU")));
  if(library?.name)box.append(node("p","模型庫 · "+library.name+(library.compiled?" · 已編譯":"")));
  if(g.usb_mbps)box.append(node("p","USB 連線 "+g.usb_mbps+" Mbps"));
  for(const c of g.cards){box.append(node("p",c.name+" · GPU 使用 "+pct(c.busy)+" ／ 閒置 "+pct(Number.isFinite(c.busy)?100-c.busy:null)+" · 可用顯存 "+gib(c.free_bytes)+" ／ "+gib(c.total_bytes)));
    for(const [k,v] of c.temps)box.append(chip(k+" · "+temp(v)))}
  for(const w of g.workers){box.append(node("h3",w.model),node("p",w.arch+" · 推理程序忙碌 "+pct(w.worker_busy)+" ／ 空檔 "+pct(100-w.worker_busy)),
    node("p","可配置顯存 "+gib(w.free_bytes)+" ／ 實體總量 "+gib(w.total_bytes)))}
  for(const [k,v] of g.temps||[])box.append(chip(k+" · "+temp(v)));
  if(g.bridge&&!g.cards.length)box.append(node("p","晶片使用率未回報。推理程序忙碌時間包含運算、同步及傳輸。"));
  if((g.bridge||g.cards.length)&&!g.workers.length)box.append(node("p","目前沒有新鮮的模型執行回報。"));
  const rate=v=>Number.isFinite(v)?(v/2**20).toFixed(2)+" MiB/s":"—";
  el("metrics").append(metric("網路接收",rate(s.io?.rx),"傳送 "+rate(s.io?.tx)),metric("磁碟讀取",rate(s.io?.read),"寫入 "+rate(s.io?.write)));processRows();
}
function clear(){current=null;for(const id of ["metrics","cores","external","temps","procs"])el(id).replaceChildren()}
async function poll(){if(paused||document.hidden||controller)return;
  void modelStatus();const c=new AbortController();controller=c;const deadline=setTimeout(()=>c.abort(),4500);
  try{const r=await fetch("/api/tools/resources",{cache:"no-store",signal:c.signal});if(!r.ok)throw Error();const s=await r.json();if(controller!==c)return;
    paint(s);el("status").textContent=(s.preview?"車機唯讀預覽 · 現行版本僅提供部分欄位 · ":"即時 · ")+new Date().toLocaleTimeString()+" · 每 2 秒更新"}
  catch{if(controller===c){clear();el("status").textContent="車機資料中斷，正在重新連線"}}
  finally{clearTimeout(deadline);if(controller===c){controller=null;timer=setTimeout(poll,2000)}}
}
function reset(){clearTimeout(timer);controller?.abort();controller=null;if(!paused&&!document.hidden)poll()}
el("pause").onclick=()=>{paused=!paused;el("pause").textContent=paused?"繼續更新":"暫停更新";if(paused)el("status").textContent="已暫停 · 顯示最後一次取樣";reset()};
el("sort").onchange=processRows;document.addEventListener("visibilitychange",reset);window.addEventListener("pagehide",()=>{paused=true;reset()});poll();
