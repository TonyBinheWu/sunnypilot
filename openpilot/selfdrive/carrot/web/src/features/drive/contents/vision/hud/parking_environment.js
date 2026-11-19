// Parking distances describe the position of an observation in its source frame.
// Paint, flat ground, uncertain depth intervals and predicted tracks are never obstacles.
const finite = Number.isFinite;
const degrees = 180 / Math.PI;
const reach = 12;
export const PARKING_VIEW = Object.freeze({parking:true, yaw:0, pitch:30, distance:13});

export function parkingObservation({tracks=[], environment, environmentMotion}={}) {
  let nearest = null;
  function consider(x, y, source, markerX=x, cellIndex=-1) {
    if (!finite(x) || !finite(y) || x <= 0) return;
    const distance = Math.hypot(x, y);
    if (distance > reach || (nearest && distance >= nearest.distance)) return;
    nearest = {x:markerX, y, source, cellIndex, distance, bearing:Math.atan2(y,x)*degrees,
      color:distance <= 4 ? '#ef584d' : distance <= 8 ? '#e7a326' : '#7895ab'};
  }
  for (const track of tracks || []) {
    if (track.state !== 'confirmed' || ['crosswalk','stop line','traffic light'].includes(track.kind)) continue;
    if (!finite(track.x) || !finite(track.y)) continue;
    // radarState and the model lead use a bumper reference. Return them to the
    // camera reference used by ground projection and occupancy before comparing.
    if (['driving_model_lead','native_lead_reference','radar_contact'].includes(track.origin)) {
      consider(track.x+1.52, track.y, 'target', track.x);
    } else if (track.positionMethod === 'flat_ground_projection' || track.origin === 'calibrated_camera') {
      consider(track.x, track.y, 'target');
    }
  }
  const dx=environmentMotion?.x??0, dy=environmentMotion?.y??0, yaw=environmentMotion?.angle??0;
  const c=Math.cos(yaw), s=Math.sin(yaw);
  for (let i=0; i+2<(environment?.length||0); i+=3) {
    const x=environment[i], y=environment[i+1], z=environment[i+2];
    if (!finite(z) || z<.5 || z>2.5) continue;
    const movedX=c*x-s*y+dx;
    consider(movedX, s*x+c*y+dy, 'surface', movedX, i);
  }
  if (nearest?.source==='surface') nearest.shape=verticalSupport(environment,nearest.cellIndex);
  return nearest;
}

// Describe only observed morphology. Adjacent 1 m cells must each have two
// vertically stacked samples before a horizontal run can count as a facade.
function verticalSupport(points, index) {
  const columns=new Map();
  for (let i=0;i+2<points.length;i+=3) {
    const x=points[i], y=points[i+1], z=points[i+2];
    if (!Number.isInteger(z) || z<1 || z>5) continue;
    const key=x+','+y;
    columns.set(key,(columns.get(key)||0) | (1<<z));
  }
  const x=points[index], y=points[index+1];
  const upright=(x,y)=>{const mask=columns.get(x+','+y)||0;return !!(mask & (mask>>1));};
  if (!upright(x,y)) return 'surface';
  let adjacent=false;
  for (const [dx,dy] of [[1,0],[0,1],[1,1],[1,-1]]) {
    let run=1;
    for (const side of [-1,1]) {
      for (let step=1;step<=3 && upright(x+side*step*dx,y+side*step*dy);step++) run++;
    }
    if (run>=4) return 'wall';
    if (run>1) adjacent=true;
  }
  return adjacent?'surface':'column';
}

// Device orientation in NED composed with device-from-calibrated-vehicle.
// Use the gravity direction only; roll and pitch do not require geographic heading.
export function parkingAttitude(overlay, stamps, now) {
  const fresh=(key)=>finite(stamps?.[key]) && now>=stamps[key] && now-stamps[key]<1000;
  const pose=overlay?.livePose, calib=overlay?.liveCalibration, v=pose?.orientationNED;
  if (!fresh('livePose') || !fresh('liveCalibration') || pose?._sourceInvalid || calib?._sourceInvalid ||
      !pose?.sensorsOK || !pose.inputsOK || !pose.posenetOK || !v?.valid || ![1,'calibrated'].includes(calib?.calStatus)) return null;
  if (![v.x,v.y,v.xStd,v.yStd].every(finite) || [v.xStd,v.yStd].some(sd=>sd<0||sd>.1) ||
      calib.rpyCalib?.length!==3 || !calib.rpyCalib.every(finite)) return null;
  const [r,p,h]=calib.rpyCalib;
  const gx=-Math.sin(v.y), gy=Math.sin(v.x)*Math.cos(v.y), gz=Math.cos(v.x)*Math.cos(v.y);
  const hx=gx*Math.cos(h)+gy*Math.sin(h), hy=-gx*Math.sin(h)+gy*Math.cos(h);
  const x=hx*Math.cos(p)-gz*Math.sin(p), z=hx*Math.sin(p)+gz*Math.cos(p);
  const roll=Math.atan2(hy*Math.cos(r)+z*Math.sin(r), z*Math.cos(r)-hy*Math.sin(r));
  const pitch=Math.asin(Math.max(-1,Math.min(1,-x)));
  return Math.abs(roll)<=Math.PI/4 && Math.abs(pitch)<=Math.PI/4 ? {roll,pitch} : null;
}

// Short ticks ahead of the front wheels show the measured steering direction.
export function parkingWheelTicks(angle, scale) {
  if(!finite(angle) || Math.abs(angle)>60)return [];
  const radians=-angle/degrees, x=1.5*(scale?.[0]??1), width=.95*(scale?.[1]??1);
  return [-width,width].map(y=>[x+.35*Math.cos(radians),y+.35*Math.sin(radians),
    x+1.45*Math.cos(radians),y+1.45*Math.sin(radians)]);
}

export function parkingDistanceText(cue) {
  return '≈ '+Math.round(cue.distance)+' m';
}

// Apply the same right-side-down / nose-up convention as the WebGL ego pivot.
export function inclinedProjection(project, attitude) {
  if (!attitude) return project;
  const {roll,pitch}=attitude, cr=Math.cos(roll), sr=Math.sin(roll), cp=Math.cos(pitch), sp=Math.sin(pitch);
  const tilt=(x,y,z)=>{const up=z*cr-y*sr;return [x*cp-up*sp,y*cr+z*sr,x*sp+up*cp];};
  const adjusted=(x,y,z=0)=>project(...tilt(x,y,z));
  adjusted.view=project.view;
  if (project.depth) adjusted.depth=(x,y,z=0)=>project.depth(...tilt(x,y,z));
  return adjusted;
}
