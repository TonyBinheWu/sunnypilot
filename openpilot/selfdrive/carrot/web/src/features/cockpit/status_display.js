const clock=new Intl.DateTimeFormat('zh-TW',{timeZone:'Asia/Taipei',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',second:'2-digit',hourCycle:'h23'});
export function cockpitClock(date=new Date()){return Number.isFinite(date.getTime())?clock.format(date):'日期時間無法取得';}
export function assistStates(data={}){
 return ['latActive','longActive'].map((key,i)=>({axis:i?'縱向':'橫向',state:typeof data[key]!=='boolean'?'unknown':data[key]?'active':'inactive',text:typeof data[key]!=='boolean'?'無資料':data[key]?'介入中':'未介入'}));
}
