const point = p => Array.isArray(p) && Number.isFinite(p[0]) && Math.abs(p[0]) <= 90 && Number.isFinite(p[1]) && Math.abs(p[1]) <= 180;

export function tripRecords(raw) {
  if (!Array.isArray(raw)) return [];
  return raw.slice(-12).flatMap(item => {
    try {
      const r = JSON.parse(item);
      if (typeof r.route !== 'string' || !Number.isFinite(r.start) || !Number.isFinite(r.last) || r.last < r.start ||
          !Number.isFinite(r.m) || r.m < 0 || !Array.isArray(r.points)) return [];
      return [{...r, points: r.points.slice(0, 64).filter(point)}];
    } catch { return []; }
  }).reverse();
}

// Fit a north-up local track. Unwrap longitude across the date line.
export function plotPoints(points, w, h) {
  if (!points.length) return [];
  const [lat, lon] = points[0];
  const xy = points.map(([y,x]) => [(((x-lon+540)%360)-180)*Math.cos(lat*Math.PI/180), lat-y]);
  const xs = xy.map(p=>p[0]), ys = xy.map(p=>p[1]);
  const xmin = Math.min(...xs), ymin = Math.min(...ys), dx = Math.max(...xs)-xmin, dy = Math.max(...ys)-ymin;
  const scale = Math.min((w-32)/Math.max(dx,.0001),(h-32)/Math.max(dy,.0001));
  return xy.map(([x,y])=>[(w-dx*scale)/2+(x-xmin)*scale,(h-dy*scale)/2+(y-ymin)*scale]);
}

export function driveView(root, {el,t}) {
  const box = el('section', undefined, 'trip-panel');
  root.append(box);
  let selected = null, previous = null;
  function update(info, fresh) {
    const marker = JSON.stringify([t('tripTitle'),fresh,info?.trip_sharing,info?.trip_fix,info?.trip_history]);
    if (marker===previous) return;
    previous=marker;
    const focused = box.contains(document.activeElement) ? document.activeElement?.dataset?.tripField : null;
    box.replaceChildren(el('h3',t('tripTitle')));
    if (info?.trip_sharing !== true) {
      box.append(el('p',t(info?.trip_sharing===false?'tripOptIn':fresh?'tripUpgrade':'settingsOffline')));
      selected=null;
      return;
    }
    const trips = tripRecords(info.trip_history);
    const live = fresh && point(info.trip_fix);
    const lastFix = trips.find(r=>point(r.last_fix))?.last_fix;
    const fix = live ? info.trip_fix : lastFix;
    const fmt = time => new Date(time*1000).toLocaleString(document.documentElement.lang || undefined);
    if(!fresh)box.append(el('p',t('tripOffline'),'workspace-muted'));
    box.append(el('h4',t(live?'tripLocation':'tripLastFix')));
    if (point(fix)) {
      box.append(el('p',fix[0].toFixed(5)+', '+fix[1].toFixed(5)+' · ±'+fix[2]+' m'));
      if(!live && Number.isFinite(fix[3]))box.append(el('p',fmt(fix[3])));
      const link = el('a',t('tripOpenMap'));
      link.href = 'https://www.openstreetmap.org/?mlat='+fix[0]+'&mlon='+fix[1]+'#map=17/'+fix[0]+'/'+fix[1];
      link.target='_blank'; link.rel='noopener noreferrer'; link.dataset.tripField='map';
      box.append(link);
    } else box.append(el('p',t('tripNoFix')));
    box.append(el('h4',t('tripRecent')));
    if (!trips.length) { box.append(el('p',t('tripEmpty'))); return; }
    const choice=el('select'), summary=el('p'), track=el('canvas');
    choice.dataset.tripField='route';choice.setAttribute('aria-label',t('tripRecent'));
    for (const trip of trips) { const o=el('option',fmt(trip.start));o.value=trip.route;choice.append(o); }
    choice.value=trips.some(r=>r.route===selected)?selected:trips[0].route;
    track.width=520;track.height=210;track.setAttribute('aria-label',t('tripTrack'));
    box.append(choice,summary,track);
    function show() {
      const r=trips.find(v=>v.route===choice.value) || trips[0];
      const distance=r.distance_known===false?t('tripDistanceUnknown'):(r.m/1000).toFixed(1)+' km';
      summary.textContent=fmt(r.start)+' – '+fmt(r.last)+' · '+((r.last-r.start)/60).toFixed(0)+' min · '+distance;
      track.hidden=!r.points.length;
      if (track.hidden) return;
      const ctx=track.getContext('2d'), pts=plotPoints(r.points,track.width,track.height);
      ctx.fillStyle='#14232d';ctx.fillRect(0,0,track.width,track.height);
      ctx.strokeStyle='#61d0da';ctx.lineWidth=3;ctx.beginPath();
      pts.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke();
      for (const [p,c] of [[pts[0],'#8ee7be'],[pts.at(-1),'#ffbd72']]) {
        ctx.beginPath();ctx.fillStyle=c;ctx.arc(...p,5,0,Math.PI*2);ctx.fill();
      }
    }
    choice.addEventListener('change',()=>{selected=choice.value;show();});
    show();
    if(focused)box.querySelector('[data-trip-field="'+focused+'"]')?.focus({preventScroll:true});
  }
  return {update};
}

export function hudText(hud,t) {
  if (!hud) return '';
  return [Number.isFinite(hud.speed_kph)?Math.round(hud.speed_kph)+' km/h':'',
          typeof hud.engaged==='boolean'?t(hud.engaged?'hudActive':'hudInactive'):''].filter(Boolean).join(' · ');
}
