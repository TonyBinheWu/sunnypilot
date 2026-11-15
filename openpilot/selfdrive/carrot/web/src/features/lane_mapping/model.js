export const MAX_PROJECT_BYTES=8*1024*1024;
const id=value=>typeof value==='string'&&/^[A-Za-z0-9_.-]{1,80}$/.test(value);
const num=(value,max=100000)=>typeof value==='number'&&Number.isFinite(value)&&Math.abs(value)<=max;

export function validateProject(value){
  if(!value||value.schema!=='carrot-lane-map/v1'||value.ground_truth!==false||value.control_eligible!==false||value.pose_verified!==false)throw Error('invalid');
  if(!id(value.frame?.id)||value.frame.axes!=='ENU'||value.frame.units!=='m')throw Error('frame');
  if(!/^[a-f0-9]{64}$/.test(value.revision)||!Array.isArray(value.cells)||value.cells.length>25000)throw Error('limit');
  if(!value.trips||typeof value.trips!=='object'||Array.isArray(value.trips)||Object.keys(value.trips).length>64)throw Error('trips');
  const trips=Object.entries(value.trips).map(([key,trip])=>{
    if(!id(key)||!id(trip?.vehicle_id)||!id(trip?.calibration_id)||!['vio_optimized','rtk_fused','surveyed','synthetic'].includes(trip.source))throw Error('trip');
    return [key,{vehicle_id:trip.vehicle_id,calibration_id:trip.calibration_id,source:trip.source}];
  });
  const tripIds=new Set(trips.map(([key])=>key)),seen=new Set();
  const cells=value.cells.map(cell=>{
    if(!cell||typeof cell.id!=='string'||!/^(-?\d+,){2}-?\d+$/.test(cell.id)||cell.id.length>40||seen.has(cell.id))throw Error('cell');
    seen.add(cell.id);
    if(!Array.isArray(cell.xyz)||cell.xyz.length!==3||!cell.xyz.every(v=>num(v)))throw Error('point');
    if(!Array.isArray(cell.trip_ids)||cell.trip_ids.length>64||!cell.trip_ids.length||new Set(cell.trip_ids).size!==cell.trip_ids.length||cell.trip_ids.some(t=>!tripIds.has(t)))throw Error('support');
    if(!num(cell.dispersion_m,100)||cell.dispersion_m<0||!num(cell.input_bound_m,100)||cell.input_bound_m<0||!Number.isInteger(cell.vehicle_count)||cell.vehicle_count<1||cell.vehicle_count>64)throw Error('quality');
    return {id:cell.id,xyz:[...cell.xyz],trip_ids:[...cell.trip_ids],dispersion_m:cell.dispersion_m,input_bound_m:cell.input_bound_m,vehicle_count:cell.vehicle_count};
  });
  const changes={};
  for(const key of ['added_cells','unobserved_cells','shifted_cells']){
    const list=value.changes?.[key];
    if(!Array.isArray(list)||list.length>25000||list.some(v=>typeof v!=='string'||v.length>40||!/^(-?\d+,){2}-?\d+$/.test(v)))throw Error('changes');
    changes[key]=[...list];
  }
  return {schema:value.schema,revision:value.revision,frame:{...value.frame},ground_truth:false,control_eligible:false,pose_verified:false,
    trips:Object.fromEntries(trips),cells,changes,parent_revision:typeof value.parent_revision==='string'?value.parent_revision.slice(0,64):null};
}

export function visibleCells(project,enabled,minTrips=1){
  return project.cells.filter(cell=>cell.trip_ids.filter(t=>enabled.has(t)).length>=minTrips);
}

export function projectPoints(cells,{width,height,yaw=0,pitch=Math.PI/2,zoom=1,pan=[0,0]}){
  if(!cells.length)return [];
  const bounds=[0,1,2].map(i=>[Math.min(...cells.map(c=>c.xyz[i])),Math.max(...cells.map(c=>c.xyz[i]))]);
  const centre=bounds.map(([a,b])=>(a+b)/2);
  const span=Math.max(10,...bounds.map(([a,b])=>b-a));
  const scale=Math.min(width,height)*.8/span*zoom;
  return cells.map(cell=>{
    const [x,y,z]=cell.xyz.map((v,i)=>v-centre[i]);
    const right=x*Math.cos(yaw)-y*Math.sin(yaw),front=x*Math.sin(yaw)+y*Math.cos(yaw);
    return {cell,x:width/2+right*scale+pan[0],y:height/2-(front*Math.sin(pitch)+z*Math.cos(pitch))*scale+pan[1]};
  });
}

export function sampleProject(){
  const cells=[];
  for(let y=0;y<80;y++)for(const side of [-1.8,1.8]){
    const x=side+.001*y*y;
    cells.push({id:`${Math.floor(x)},${y},0`,xyz:[x,y,.003*y],trip_ids:['demo-a','demo-b'],vehicle_count:2,dispersion_m:.08,input_bound_m:.6});
  }
  return validateProject({schema:'carrot-lane-map/v1',revision:'0'.repeat(64),frame:{id:'synthetic-demo',axes:'ENU',units:'m'},
    ground_truth:false,control_eligible:false,pose_verified:false,trips:Object.fromEntries(['demo-a','demo-b'].map(t=>[t,{vehicle_id:t,calibration_id:'synthetic',source:'synthetic'}])),
    cells,changes:{added_cells:[],unobserved_cells:[],shifted_cells:[]}});
}
