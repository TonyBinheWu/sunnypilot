// Original closed sedan mesh. Dimensions and styling are illustrative, never inferred.
export function drawVehicleMesh(ctx,project,{view=[-8,0,6],ego=true}={}){
  const faces=[];
  const face=(points,color)=>faces.push({points,color,depth:points.reduce((sum,p)=>sum+p.reduce((n,v,i)=>n+v*view[i],0),0)/points.length});
  const ring=(z,length,width)=>[[-length,-width,z],[length,-width,z],[length,width,z],[-length,width,z]];
  const lower=ring(.26,2.18,.88),belt=ring(.82,2.08,.94);
  for(let i=0;i<4;i++)face([lower[i],lower[(i+1)%4],belt[(i+1)%4],belt[i]],(ego?['#adb8c4','#c9d1d9','#dbe1e7','#b9c3ce']:['#7d8a98','#94a1af','#b2bdc8','#8c9aaa'])[i]);
  face([[-2.08,-.94,.82],[-1.22,-.82,.89],[-1.22,.82,.89],[-2.08,.94,.82]],'#e2e7ec');
  face([[1.35,-.82,.89],[2.08,-.94,.82],[2.08,.94,.82],[1.35,.82,.89]],'#edf0f3');
  const cabin=[[-1.22,-.82,.89],[1.35,-.82,.89],[1.35,.82,.89],[-1.22,.82,.89]];
  const roof=[[-.65,-.69,1.42],[.65,-.69,1.42],[.65,.69,1.42],[-.65,.69,1.42]];
  for(let i=0;i<4;i++)face([cabin[i],cabin[(i+1)%4],roof[(i+1)%4],roof[i]],i%2?'#344454':'#455869');
  face(roof,ego?'#d5dce4':'#9ba8b6');
  for(const side of [-1,1]){
    face([[-1.25,side*.835,.82],[1.4,side*.835,.82],[1.35,side*.82,.91],[-1.22,side*.82,.91]],'#c4ced9');
    face([[-.08,side*.77,.9],[.04,side*.77,.9],[.04,side*.69,1.42],[-.08,side*.69,1.42]],'#9eacb9');
    for(const x of [-1.4,1.35]){
      face(Array.from({length:20},(_,i)=>{const a=i*Math.PI/10;return[x+Math.cos(a)*.36,side*.96,.36+Math.sin(a)*.36];}),'#252d36');
      face(Array.from({length:16},(_,i)=>{const a=i*Math.PI/8;return[x+Math.cos(a)*.22,side*.97,.36+Math.sin(a)*.22];}),'#9aa7b5');
    }
  }
  for(const y of [-.68,.68]){
    face([[-2.19,y-.18,.59],[-2.19,y+.18,.59],[-2.09,y+.18,.7],[-2.09,y-.18,.7]],'#d04b50');
    face([[2.19,y-.18,.59],[2.19,y+.18,.59],[2.09,y+.18,.7],[2.09,y-.18,.7]],'#f4fbff');
  }
  const shadow=ring(.02,2.3,1.02).map(p=>project(...p));ctx.save();
  if(shadow.every(Boolean)){ctx.beginPath();shadow.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fillStyle='#50607020';ctx.fill();}
  for(const f of faces.sort((a,b)=>a.depth-b.depth)){
    const p=f.points.map(v=>project(...v));if(p.some(v=>!v))continue;
    ctx.beginPath();p.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fillStyle=f.color;ctx.fill();
  }
  ctx.restore();
}


// Object classes come from the existing detector. Size/heading are illustrative.
export function drawDetectedMesh(ctx,project,object){
  const {x,y,kind}=object;
  if(!Number.isFinite(x)||!Number.isFinite(y))return;
  const p=(dx,dy,z)=>project(x+dx,y+dy,z);
  const poly=(points,color)=>{const a=points.map(v=>p(...v));if(a.some(v=>!v))return;ctx.beginPath();a.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fillStyle=color;ctx.fill();};
  const box=(cx,cy,z,l,w,h,color)=>{
    poly([[cx-l,cy-w,z],[cx-l,cy+w,z],[cx-l,cy+w,z+h],[cx-l,cy-w,z+h]],'#7b8895');
    poly([[cx-l,cy+w,z],[cx+l,cy+w,z],[cx+l,cy+w,z+h],[cx-l,cy+w,z+h]],color);
    poly([[cx-l,cy-w,z+h],[cx+l,cy-w,z+h],[cx+l,cy+w,z+h],[cx-l,cy+w,z+h]],'#c4cdd5');
  };
  const disc=(cx,z,r,color)=>{const center=p(cx,0,z),edge=p(cx,0,z+r);if(!center||!edge)return;ctx.beginPath();ctx.arc(center[0],center[1],Math.max(1,Math.hypot(center[0]-edge[0],center[1]-edge[1])),0,Math.PI*2);ctx.fillStyle=color;ctx.fill();};
  if(kind==='car'){drawVehicleMesh(ctx,p,{ego:false});return;}
  if(kind==='bus'||kind==='truck'){
    if(kind==='bus'){
      box(0,0,.3,4,1.05,2.35,'#a8b4c0');
      poly([[-3.8,1.06,1.25],[3.7,1.06,1.25],[3.7,1.06,2.35],[-3.8,1.06,2.35]],'#394c60');
      poly([[-4.01,-.88,1.2],[-4.01,.88,1.2],[-4.01,.88,2.3],[-4.01,-.88,2.3]],'#4b5d70');
    }else{
      box(-.9,0,.4,2.1,1.05,2.2,'#b4bec8');box(2.1,0,.35,.9,.98,1.5,'#95a5b6');
      poly([[2.2,-.8,1.85],[2.9,-.8,1.3],[2.9,.8,1.3],[2.2,.8,1.85]],'#3c5268');
    }
    for(const wx of [-2.8,2.6])box(wx,1.07,.15,.4,.1,.65,'#29343f');return;
  }
  if(kind==='person'){
    box(0,0,.62,.12,.23,.65,'#76899b');
    box(0,-.14,.08,.12,.08,.6,'#4d5e70');box(0,.14,.08,.12,.08,.6,'#566a7e');
    box(0,-.31,.65,.08,.065,.48,'#889aa9');box(0,.31,.65,.08,.065,.48,'#889aa9');disc(0,1.51,.17,'#a4b3bf');return;
  }
  if(kind==='motorcycle'||kind==='bicycle'){
    for(const wx of [-.68,.68])poly(Array.from({length:20},(_,i)=>{const a=i*Math.PI/10;return[wx+Math.cos(a)*.32,0,.34+Math.sin(a)*.32];}),'#344454');
    if(kind==='motorcycle')box(0,0,.38,.55,.23,.28,'#9aaabb');
    else poly([[-.68,0,.34],[.12,0,.74],[.68,0,.34],[-.2,0,.36]],'#8fabbf');
    box(-.12,0,.7,.24,.12,.07,'#43576b');box(.55,0,.6,.05,.24,.07,'#485e73');
  }
}
