// The map is rendered locally from the owner's server-side OSM extract.
const strings={
  'zh-TW':['道路環境研究','開始分享','停止分享','停止並清除資料','下載道路場景','關閉','等待車機傳回場景','車道線','道路邊緣','前方目標','附近 OSM 路段','已收集','筆','已停止','分享中','確認刪除這台車的道路研究資料？','影像分類','台灣圖資未安裝','最近收到','尚無可靠方位'],
  en:['Road scene research','Start sharing','Stop sharing','Stop and erase','Download road scenes','Close','Waiting for vehicle scenes','Lane lines','Road edges','Front targets','Nearby OSM segments','Collected','samples','Stopped','Sharing','Erase road research data for this device?','Image detections','OSM index unavailable','Last received','Heading unavailable'],
  ja:['道路環境研究','共有開始','共有停止','停止して削除','道路場面を保存','閉じる','車両の場面を待機中','車線','道路端','前方物体','周辺OSM道路','収集済み','件','停止中','共有中','この車両の道路研究データを削除しますか？','画像認識','OSM索引なし','最終受信','方位不明'],
};
export const sceneTitle=lang=>(strings[lang]||strings.en)[0];
export function drawScene(canvas, item, roads, history=[]) {
  const ctx=canvas.getContext('2d'), w=canvas.width,h=canvas.height;
  ctx.fillStyle='#101923';ctx.fillRect(0,0,w,h);
  if(!item)return;
  const s=item.scene,f=s.fix,scale=Math.min(w/100,h/90);
  const project=([x,y,z=0])=>[w*.5+y*scale,h*.88-x*scale*.86-z*scale*.45];
  function line(points,color,width,offset=0) {
    ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();
    points.forEach(([x,y,z],i)=>{const p=project([x,y+offset,z]);if(i)ctx.lineTo(...p);else ctx.moveTo(...p);});
    ctx.stroke();
  }
  if(f&&Number.isFinite(f.heading)) {
    const angle=f.heading*Math.PI/180, c=Math.cos(angle),t=Math.sin(angle);
    for(const road of roads){
      const local=road.lonlat.map(([lon,lat])=>{
        const e=(lon-f.lon)*111320*Math.cos(f.lat*Math.PI/180),n=(lat-f.lat)*111320;
        return [n*c+e*t,e*c-n*t,0];
      });
      line(local,'#41556a',4);
    }
  }
  for(const observation of history)line(observation.xy,'#59677a',1);
  for(const l of s.lines) {
    const color=l.kind==='edge'?'#eb846c':Math.floor(l.oem/10)===2?'#ffd047':'#f7f8fa';
    line(l.xyz,color,1.8);
    if(l.oem!==null&&l.oem%10===4)line(l.xyz,color,1.8,l.index===1?-.38:.38);
  }
  for(const xy of s.targets){const [x,y]=project(xy);ctx.strokeStyle='#91bdd1';ctx.strokeRect(x-2,y-2,4,4);}
  for(const packet of s.camera){
    if(packet.eof!==s.eof||packet.frame!==s.frame)continue;
    for(const o of packet.objects)if(o.xy){const [x,y]=project(o.xy);ctx.fillStyle='#68cfa9';ctx.fillRect(x-3,y-3,6,6);}
  }
  const [x,y]=project([0,0]);ctx.fillStyle='#519bff';ctx.fillRect(x-4,y-6,8,12);
}

export async function roadSceneDialog(device,api,language) {
  const l=strings[language]||strings.en, path='/devices/'+encodeURIComponent(device.id)+'/road-scenes';
  const dialog=document.createElement('dialog'), title=document.createElement('h2'), status=document.createElement('p');
  const notice=document.createElement('p'), canvas=document.createElement('canvas'), legend=document.createElement('p');
  const actions=document.createElement('div'), link=document.createElement('a');
  title.textContent=l[0];canvas.width=680;canvas.height=340;canvas.className='research-scene';
  canvas.setAttribute('aria-label',l[0]);link.href='/api/v1'+path+'/download';link.textContent=l[4];
  dialog.append(title,notice,status,canvas,legend,actions,link);
  let data=await api(path),closed=false,timer;
  const buttons=[];
  function render() {
    notice.textContent=data.notice[language]||data.notice.en;
    const item=data.items.at(-1), scene=item?.scene;
    status.textContent=[l[data.enabled?14:13],l[11]+' '+data.count+' '+l[12],
      item?l[18]+' '+new Date(item.received*1000).toLocaleString():l[6]].join(' · ');
    legend.textContent=scene?[l[7]+' '+scene.lines.filter(l=>l.kind==='lane').length,l[8]+' '+scene.lines.filter(l=>l.kind==='edge').length,
      l[9]+' '+scene.targets.length,l[16]+' '+scene.camera.reduce((n,p)=>n+p.objects.length,0),
      data.osm_index?l[10]+' '+data.osm.length:l[17],scene.fix?.heading==null?l[19]:'',data.osm_attribution].filter(Boolean).join(' · '):'';
    drawScene(canvas,item,data.osm,data.history);link.hidden=!data.count;
    buttons[0].disabled=data.enabled;buttons[1].disabled=!data.enabled;
  }
  async function refresh() {data=await api(path);if(!closed)render();}
  for(const [i,action] of [[1,'enable'],[2,'disable'],[3,'erase'],[5,'close']]) {
    const b=document.createElement('button');b.type='button';b.textContent=l[i];actions.append(b);buttons.push(b);
    b.onclick=async()=>{
      if(action==='close'){dialog.close();return;}
      if(action==='erase'&&!confirm(l[15]))return;
      b.disabled=true;
      try{await api(path,{action,schema:data.schema,revision:data.revision});await refresh();}
      catch(e){status.textContent=e.reason||l[6];}
      finally{if(!closed){buttons[2].disabled=false;}}
    };
  }
  const tick=async()=>{try{await refresh();}catch{status.textContent=l[6];}if(!closed)timer=setTimeout(tick,5000);};
  dialog.addEventListener('close',()=>{closed=true;clearTimeout(timer);dialog.remove();},{once:true});
  document.body.append(dialog);render();dialog.showModal();timer=setTimeout(tick,5000);
}
