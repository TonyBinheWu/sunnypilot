export const SIGNAL_GLYPHS={color:'●',up:'↑',up_right:'↗',right:'→',down_right:'↘',down:'↓',down_left:'↙',left:'←',up_left:'↖'};

function overlap(a,b){
  const w=Math.max(0,Math.min(a[0]+a[2],b[0]+b[2])-Math.max(a[0],b[0]));
  const h=Math.max(0,Math.min(a[1]+a[3],b[1]+b[3])-Math.max(a[1],b[1]));
  const area=w*h;
  return area/(a[2]*a[3]+b[2]*b[3]-area || 1);
}

export function createSignalHistory(){
  let prior=[],at=-Infinity;
  return {
    clear(){prior=[];at=-Infinity;},
    confirm(heads,stamp){
      const fresh=stamp>at&&stamp-at<=900;
      const matching=heads.map(h=>fresh?prior.filter(p=>overlap(p.box,h.box)>=.4):[]);
      const next=heads.map(h=>({box:h.box,key:h.lamps.map(l=>l.color+'/'+l.shape).sort().join(',')}));
      const confirmed=heads.map((head,i)=>{
        const p=matching[i][0];
        return p&&matching[i].length===1&&matching.filter(matches=>matches.includes(p)).length===1&&
          next[i].key===p.key&&head.lamps.length?head.lamps:null;
      });
      prior=next;at=stamp;
      return confirmed;
    }
  };
}
