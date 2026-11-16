// Original generic sedan artwork; illustrative geometry, never a measured vehicle mesh.
export function drawCockpitVehicle(ctx,project){
  const face=(points,color)=>{const p=points.map(v=>project(...v));if(p.some(v=>!v))return;
    ctx.beginPath();p.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fillStyle=color;ctx.fill();};
  const center=project(0,0,0),edge=project(0,1,0);if(!center||!edge)return;
  const scale=Math.abs(edge[0]-center[0]);
  ctx.save();ctx.fillStyle='#48546224';ctx.beginPath();ctx.ellipse(center[0],center[1]+scale*.14,scale*1.15,scale*.42,0,0,Math.PI*2);ctx.fill();
  for(const x of [-1.35,1.3])for(const y of [-.94,.94]){
    const p=project(x,y,.28);if(!p)continue;ctx.fillStyle='#232a34';ctx.beginPath();ctx.ellipse(p[0],p[1],scale*.13,scale*.28,0,0,Math.PI*2);ctx.fill();
  }
  face([[-2.1,-.9,.25],[2.1,-.85,.25],[2.1,-.85,.76],[-1.9,-.94,.85]],'#a9b6c7');
  face([[-2.1,.9,.25],[2.1,.85,.25],[2.1,.85,.76],[-1.9,.94,.85]],'#c5d0dd');
  face([[-2.1,-.9,.25],[-2.1,.9,.25],[-1.9,.94,.85],[-1.9,-.94,.85]],'#c3cedb');
  face([[-1.9,-.94,.85],[-1.9,.94,.85],[2.1,.85,.76],[2.1,-.85,.76]],'#edf1f5');
  face([[-1.2,-.8,.85],[-1.2,.8,.85],[-.6,.7,1.3],[-.6,-.7,1.3]],'#3d4e62');
  face([[.85,-.7,1.3],[.85,.7,1.3],[1.55,.8,.82],[1.55,-.8,.82]],'#52677e');
  face([[-.6,-.7,1.3],[.85,-.7,1.3],[.85,.7,1.3],[-.6,.7,1.3]],'#f7f9fb');
  face([[-1.2,-.8,.85],[-.6,-.7,1.3],[.85,-.7,1.3],[1.55,-.8,.82]],'#718297');
  face([[-1.2,.8,.85],[-.6,.7,1.3],[.85,.7,1.3],[1.55,.8,.82]],'#8595a8');
  face([[-2.105,-.77,.59],[-2.105,.77,.59],[-2.06,.77,.66],[-2.06,-.77,.66]],'#d5535d');
  face([[-2.11,-.9,.27],[-2.11,.9,.27],[-2.11,.9,.35],[-2.11,-.9,.35]],'#57667a');
  face([[-2.12,-.25,.4],[-2.12,.25,.4],[-2.12,.25,.51],[-2.12,-.25,.51]],'#e5ebf0');
  ctx.restore();
}
