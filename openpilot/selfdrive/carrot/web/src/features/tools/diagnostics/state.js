export function classifyDiagnosticText(value) {
  const text=String(value||'').slice(0,800);
  if (/\bCAN\b/.test(text)||/\bcan(?:fd)?\s*(?:error|bus|timeout|錯誤|異常)|canfd|匯流排/i.test(text)) return 'can_invalid';
  if (/處理.*逾時|處理.*超時|processing|lagging|commissue/i.test(text)) return 'processing_delay';
  if (/麥克風|語音模型|microphone|speech|permission|權限/i.test(text)) return 'speech_setup';
  if (/nv?16|模型|egpu|model/i.test(text)) return 'model_error';
  if (/影像|鏡頭|vision|camera|串流/i.test(text)) return 'camera_error';
  if (/連線|websocket|network|fetch|timeout|離線|connect|wi-?fi/i.test(text)) return 'network_error';
  return null;
}

export function createDiagnosticErrors({clock=Date.now,limit=12}={}) {
  let rows=[];
  return {
    record(value={}) {
      const now=clock();
      let path='';
      try {path=new URL(String(value.url||''),'http://local.invalid').pathname.slice(0,120);}catch{}
      // Keep only known route shapes. Query strings, identities, bodies and raw
      // exception messages never enter the automatic report.
      if (!/^\/(api\/[a-z0-9_/-]+|js\/[a-z0-9_./-]+)$/i.test(path)) path='';
      if (path.startsWith('/api/device/diagnostics')) return false;
      const entry={time:now,kind:['request','script','vision','network'].includes(value.kind)?value.kind:'request',
        path,status:Number.isInteger(value.status)&&value.status>=0&&value.status<=599?value.status:0,
        code:/^[A-Z0-9_-]{1,64}$/i.test(value.code||'')?value.code:''};
      const last=rows.at(-1);
      if(last&&now-last.time<30000&&['kind','path','status','code'].every(key=>last[key]===entry[key])) return false;
      rows=rows.filter(row=>now-row.time<=900000).slice(-(limit-1));rows.push(entry);return true;
    },
    list(){rows=rows.filter(row=>clock()-row.time<=900000);return rows.map(row=>({...row}));},
  };
}
