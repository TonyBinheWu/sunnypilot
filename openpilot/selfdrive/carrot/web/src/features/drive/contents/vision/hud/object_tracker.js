// Display-only tracks in metres, x forward and y right. Each source owns its clock and IDs.
const finite = Number.isFinite;
const clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
const wrap = angle => Math.atan2(Math.sin(angle), Math.cos(angle));
const TTL = 1200, MAX_TRACKS = 64, REJECT = 100;

// Minimum-cost one-to-one assignment. Every row can instead choose an empty slot.
function assign(costs, count) {
  const rows = costs.length, cols = count + rows;
  const u = new Float64Array(rows+1), v = new Float64Array(cols+1);
  const owner = new Int16Array(cols+1), prev = new Int16Array(cols+1);
  for (let i=1; i<=rows; i++) {
    owner[0]=i;
    const distance=new Float64Array(cols+1).fill(Infinity), used=new Uint8Array(cols+1);
    let j=0;
    do {
      used[j]=1;
      const row=owner[j]; let step=Infinity, next=0;
      for (let k=1; k<=cols; k++) if (!used[k]) {
        const cost=(k<=count?costs[row-1][k-1]:1)-u[row]-v[k];
        if (cost<distance[k]) {distance[k]=cost; prev[k]=j;}
        if (distance[k]<step) {step=distance[k]; next=k;}
      }
      for(let k=0;k<=cols;k++) {
        if(used[k]) {u[owner[k]]+=step; v[k]-=step;}
        else distance[k]-=step;
      }
      j=next;
    } while(owner[j]);
    do {const k=prev[j]; owner[j]=owner[k]; j=k;} while(j);
  }
  const matches=new Map();
  for(let j=1;j<=count;j++) if(owner[j] && costs[owner[j]-1][j-1]<1) matches.set(owner[j]-1,j-1);
  return matches;
}

function project(t, at, motion) {
  const dt=clamp((at-t.at)/1000,0,TTL/1000);
  const angle=(motion.yaw??0)*dt, c=Math.cos(angle), s=Math.sin(angle);
  // Transfer the last relative velocity to the new ego frame. Compensate measured ego acceleration.
  const x=t.x+(t.vx+(finite(t.ego)&&finite(motion.speed)?(t.ego-motion.speed)*.5:0))*dt, y=t.y+t.vy*dt;
  return {x:c*x+s*y,y:c*y-s*x, heading:t.heading===null?null:wrap(t.heading-angle)};
}

function displayPose(t,at,motion,period) {
  const age=Math.max(0,at-t.at), delay=t.missedAt??Math.max(140,period*1.2);
  // Confirmed samples interpolate between observations. Only a marked prediction
  // may extrapolate beyond the filtered measurement.
  const ahead=t.phase==='predicted'?Math.max(0,age-delay):0;
  const p=project(t,t.at+ahead,motion);
  const blend=t.easing?clamp(1-age/t.easing,0,1):0;
  return {x:p.x+t.ex*blend,y:p.y+t.ey*blend,heading:p.heading===null?null:wrap(p.heading+t.eh*blend)};
}

function association(t, p, o, at) {
  if (o.kind!==t.obs.kind || (t.native!==null && o.trackId!=null && t.native!==o.trackId)) return REJECT;
  const dt=(at-t.at)/1000, dx=o.x-p.x, dy=o.y-p.y;
  const known=t.native!==null && t.native===o.trackId;
  const xGate=1.6+.055*p.x+dt*(t.hits===1?25:9), yGate=.85+.015*p.x+dt*(t.hits===1?4:2.8);
  const pos=(dx/xGate)**2+(dy/yGate)**2;
  if(pos>=1 || (finite(o.vRel)&&Math.abs(o.vRel-t.vx)>13)) return REJECT;
  const dv=finite(o.vRel)?Math.min(1,Math.abs(o.vRel-t.vx)/8):0;
  const dir=finite(o.heading)&&finite(p.heading)?Math.abs(wrap(o.heading-p.heading))/Math.PI:0;
  return .84*pos+.09*dv+.04*dir+.03*(1-(o.probability??.5))-(known?.3:0);
}

export function createObjectTracker() {
  const streams=new Map(), totals={created:0,lost:0,removed:0};
  let serial=0;
  function drop(name) {
    const stream=streams.get(name);
    if(stream) {for(const t of stream.tracks.values())if(t.phase==='confirmed'||t.phase==='predicted')totals.lost++;
      totals.removed+=stream.tracks.size; streams.delete(name);}
  }
  function advance(s,at) {
    for(const [id,t] of s.tracks) {
      const age=at-t.at;
      const limit=Math.min(TTL,Math.max(400,s.period*2.45));
      if(age>TTL) {
        if(t.hits>1 && t.phase!=='lost') totals.lost++;
        t.phase='removed';s.tracks.delete(id);totals.removed++;continue;
      }
      if(t.hits===1) continue;
      if(age>limit) {
        if(t.phase!=='lost') totals.lost++;
        t.phase='lost';
      } else if(t.missed || age>Math.max(140,s.period*1.2)) t.phase='predicted';
    }
  }
  function ingest(name,{stamp,epoch=0,objects,geometry=null},now,motion={}) {
    if(!finite(stamp)||stamp>now||now-stamp>TTL) return;
    let s=streams.get(name);
    if(!s||s.epoch!==epoch) {
      drop(name);
      s={epoch,stamp:null,period:name==='radar'?100:350,frames:0,latency:null,tracks:new Map()};
      streams.set(name,s);
    }
    if(s.stamp!==null && stamp<=s.stamp) return;
    if(s.stamp!==null) {
      const gap=stamp-s.stamp;
      s.period=clamp(s.frames===1?gap:s.period*.65+gap*.35,16,1100);
    }
    s.frames++;s.stamp=stamp;s.latency=now-stamp;s.geometry=geometry;
    advance(s,stamp);
    const obs=(objects||[]).filter(o=>o && finite(o.x)&&finite(o.y)&&o.x>0&&o.x<=75&&Math.abs(o.y)<=20).slice(0,32);
    const tracks=[...s.tracks.values()],pred=tracks.map(t=>project(t,stamp,motion));
    const costs=tracks.map((t,i)=>obs.map(o=>association(t,pred[i],o,stamp)));
    // A first side-on crossing can travel several metres between camera frames.
    // Relax the lateral gate only for a unique pair with no regular association.
    if(name!=='radar' && finite(motion.speed) && Math.abs(motion.speed)<3){
      const openRows=costs.map(row=>row.every(n=>n>=1));
      const openCols=obs.map((_,j)=>costs.every(row=>row[j]>=1));
      const counts=new Map(),pairs=new Map();
      tracks.forEach((t,i)=>{
        const dt=(stamp-t.at)/1000;
        if(!openRows[i]||t.hits!==1||dt<=0||dt>.5||!['car','bus','truck','motorcycle','bicycle'].includes(t.obs.kind))return;
        const candidates=[];
        obs.forEach((o,j)=>{
          if(!openCols[j]||o.kind!==t.obs.kind||!(o.probability>=.65)||!(t.obs.probability>=.65))return;
          if(Math.abs(o.x-pred[i].x)>1.2||Math.abs(o.y-pred[i].y)>Math.min(6,.45+16*dt))return;
          candidates.push(j);counts.set(j,(counts.get(j)??0)+1);
        });
        if(candidates.length===1)pairs.set(i,candidates[0]);
      });
      for(const [i,j] of pairs)if(counts.get(j)===1)costs[i][j]=.95;
    }
    const matches=assign(costs,obs.length);
    const used=new Set(matches.values());
    tracks.forEach((t,i)=>{
      if(!matches.has(i)) {t.missed=true;t.missedAt??=Math.min(stamp-t.at,Math.max(140,s.period*1.2));return;}
      const o=obs[matches.get(i)], p=pred[i], dt=(stamp-t.at)/1000;
      const dx=o.x-p.x, dy=o.y-p.y;
      const prior=displayPose(t,stamp,motion,s.period);
      const gain=t.hits===1?.82:clamp(.5+dt*.55,.52,.88);
      const angle=(motion.yaw??0)*dt,c=Math.cos(angle),sin=Math.sin(angle);
      // Estimate target velocity from two observations after compensating for ego rotation.
      const measuredX=(c*o.x-sin*o.y-t.x)/dt, measuredY=(sin*o.x+c*o.y-t.y)/dt;
      const beta=t.hits===1?.85:clamp(.3+dt*.4,.32,.65);
      t.vx=finite(o.vRel)?o.vRel:t.vx+beta*(clamp(measuredX,-55,55)-t.vx);
      t.vy+=beta*(clamp(measuredY,-15,15)-t.vy);
      const lastHeading=p.heading;
      let heading=finite(o.heading)?o.heading:null;
      if(heading===null && finite(motion.speed)&&finite(motion.yaw)&&Math.hypot(t.vx+motion.speed,t.vy)>2 && o.kind!=='traffic cone')
        heading=Math.atan2(t.vy,t.vx+motion.speed);
      t.heading=heading===null?lastHeading:lastHeading===null?heading:wrap(lastHeading+beta*wrap(heading-lastHeading));
      // Ease innovations over a brief real-time window, without delaying the association state.
      t.easing=t.hits===1||t.phase==='lost'?0:Math.min(450,dt*1000);
      t.ex=prior.x-(p.x+gain*dx);t.ey=prior.y-(p.y+gain*dy);
      t.eh=finite(prior.heading)&&finite(t.heading)?wrap(prior.heading-t.heading):0;t.missedAt=null;
      t.x=p.x+gain*dx;t.y=p.y+gain*dy;t.at=stamp;t.obs=o;t.hits++;t.missed=false;
      t.ego=motion.speed;t.native=o.trackId??t.native;t.phase='confirmed';
    });
    obs.forEach((o,i)=>{
      if(used.has(i)||s.tracks.size>=MAX_TRACKS)return;
      const id=++serial;
      s.tracks.set(id,{id,native:o.trackId??null,obs:o,x:o.x,y:o.y,vx:o.vRel??0,vy:0,ego:motion.speed,
        heading:finite(o.heading)?o.heading:null,at:stamp,hits:1,phase:'tentative',missed:false,easing:0,ex:0,ey:0,eh:0});
      totals.created++;
    });
  }
  function sample(now,motion={}) {
    const out=[];
    for(const s of streams.values()) {
      advance(s,now);
      for(const [id,t] of s.tracks) {
        if(t.phase==='tentative'||t.phase==='lost')continue;
        const {x,y,heading}=displayPose(t,now,motion,s.period);
        const bound=t.phase==='predicted'?project(t,now,motion):{x,y};
        if(bound.x<=0||bound.x>75||Math.abs(bound.y)>20||(s.geometry&&!inCameraView(s.geometry,bound.x,bound.y))) {
          t.phase='removed';s.tracks.delete(id);totals.removed++;continue;
        }
        out.push({...t.obs,id:'track-'+id,trackingId:id,state:t.phase,x,y,heading,
          vx:t.vx,vy:t.vy,measurementAt:t.at});
      }
    }
    return out;
  }
  function snapshot(now) {
    const tracks=[], sources={};
    for(const [name,s] of streams) {
      sources[name]={fps:s.frames>=2 && now-s.stamp<TTL?1000/s.period:null,latencyMs:s.latency,ageMs:now-s.stamp};
      for(const t of s.tracks.values())tracks.push({id:t.id,source:name,kind:t.obs.kind,state:t.phase,confidence:t.obs.probability??null,ageMs:now-t.at,
        x:t.x,y:t.y,vx:t.vx,vy:t.vy,heading:t.heading,positionMethod:t.obs.positionMethod??t.obs.origin});
    }
    return {...totals,active:tracks.filter(t=>['confirmed','predicted'].includes(t.state)).length,tracks,sources};
  }
  return {ingest,drop,sample,snapshot,reset(){for(const k of streams.keys())drop(k);},
    get pending(){for(const s of streams.values())if(s.tracks.size)return true;return false;}};
}

// Inverse of groundPoint: project a ground contact back into the calibrated ROAD image.
function inCameraView(g,x,y) {
  const [r,p,yaw]=g.rpy, cr=Math.cos(r),sr=Math.sin(r),cp=Math.cos(p),sp=Math.sin(p),cy=Math.cos(yaw),sy=Math.sin(yaw);
  const z=g.heightM, a=cy*cp*x+(cy*sp*sr-sy*cr)*y+(cy*sp*cr+sy*sr)*z;
  const b=sy*cp*x+(sy*sp*sr+cy*cr)*y+(sy*sp*cr-cy*sr)*z, d=-sp*x+cp*sr*y+cp*cr*z;
  if(a<=0)return false;
  const u=g.width/2+g.fx*b/a, v=g.height/2+g.fy*d/a;
  return u>=0&&u<=g.width&&v>=0&&v<=g.height;
}
