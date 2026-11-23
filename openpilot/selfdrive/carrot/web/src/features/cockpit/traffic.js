const faultFlags = ['canError', 'radarFault', 'wrongConfig', 'radarUnavailableTemporary'];

function fresh(sample, stamp, now) {
  return sample && !sample._sourceInvalid && Number.isFinite(stamp) && now >= stamp && now - stamp <= 500;
}

function near(a, b) {
  return Math.abs(a.x - b.x) < 2 && Math.abs(a.y - b.y) < 1.2;
}

// Match the bounds, axes and observation priority of C4 reality_scene.vehicle_points.
export function cockpitTraffic(model, radar, stamps, now, tracks = [], car = null) {
  const vehicles = [];
  function add(id, x, y, rearRadar=false) {
    if (!Number.isFinite(x) || !Number.isFinite(y) || (rearRadar ? x < -26 || x >= 0 : x < 1 || x > 110) || Math.abs(y) > 18) return;
    const point = {id, x, y, kind: 'unknown', nativeVehicleMarker: true, ...(rearRadar ? {rearRadar:true} : {})};
    if (!vehicles.some(other => near(point, other))) vehicles.push(point);
  }
  if (fresh(car, stamps.carState, now) && car.canValid && !car.canTimeout) {
    for (const [prefix, sign] of [['displayRearLeft', -1], ['displayRearRight', 1]]) {
      const d=car[prefix+'Distance'], y=car[prefix+'Lateral'];
      if (d>0 && d<=26 && y>0 && y<=13) add(prefix,-d,sign*y,true);
    }
  }
  if (fresh(radar, stamps.radarState, now) && !faultFlags.some(flag => radar.radarErrors?.[flag])) {
    function addLead(id, lead) {
      if (lead?.status === true && Number.isFinite(lead.yRel)) add(id, lead.dRel, -lead.yRel, lead.radar===true && lead.dRel<0);
    }
    for (const slot of ['leadOne', 'leadTwo']) addLead(slot, radar[slot]);
    for (const slot of ['leadsCenter', 'leadsLeft', 'leadsRight']) {
      (radar[slot] || []).slice(0, 24).forEach((lead, index) => addLead(slot + index, lead));
    }
  }
  if (fresh(model, stamps.modelV2, now)) {
    (model.leadsV3 || []).forEach((lead, index) => {
      if (lead?.prob > 0.5) add('model' + index, lead.x?.[0], lead.y?.[0]);
    });
  }
  const observations = tracks.filter(t => !['native_lead_reference', 'driving_model_lead'].includes(t.origin));
  const classified = observations.filter(t => ['car','bus','truck','motorcycle','bicycle'].includes(t.kind) && t.state === 'confirmed');
  const remaining = vehicles.filter(v => !classified.some(t => near(t, v)));
  const visible = observations.filter(t => t.state !== 'predicted' || !remaining.some(v => near(t, v)));
  return [...visible, ...remaining].sort((a, b) => b.x - a.x);
}
