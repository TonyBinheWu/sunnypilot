// BEV research layer. Local-only fetch, no network calls to a tile provider.
export function researchMap(target) {
  let lines=[],expires=0,next=0,pending=false,generation=0,revision=0;
  return {
    read(active, now) {
      if (!active) {
        if(lines.length||pending||next){generation++;lines=[];next=expires=0;}
        return {lines:[],revision};
      }
      if (!pending && now>=next && target.fetch) {
        pending=true;const tag=generation;next=now+2000;
        target.fetch('/api/research/road-scenes/context',{cache:'no-store'}).then(res=>res.ok?res.json():null).then(data=>{
          if (tag!==generation)return;
          const at=target.performance?.now?.()??Date.now();
          lines=data?.enabled&&Array.isArray(data.lines)&&at-now<800?data.lines:[];
          expires=now+900;next=now+(data?.enabled?500:30000);revision++;
        }).catch(()=>{if(tag===generation){lines=[];next=now+30000;revision++;}}).finally(()=>{pending=false;});
      }
      if(lines.length && now>=expires){lines=[];revision++;}
      return {lines,revision};
    },
  };
}
