import {ANIMALS} from './object_classes.js';
// Original closed sedan mesh. Dimensions and styling are illustrative, never inferred.
export function drawVehicleMesh(ctx,project,{view=project.view||[-8,0,6],ego=true,body=null,lamps={},outline=null}={}){
  const faces=[];
  const paint=ego&&/^#[0-9a-f]{6}$/i.test(body?.paint||'')?body.paint:null;
  const coatings=new Set(['#a7b2be','#b9c4ce','#cbd4dc','#d3dce4','#dce3ea','#c8d2dc','#aebbc8','#9baab9','#c7d2de','#d9e1e9','#eaf0f5','#f1f5f9','#f6f8fb','#e5ebf1','#cfdae4','#bdcad7','#dce4ec','#edf2f7','#e1e6ec','#c5d1dd','#e4ebf2','#c4ced9','#b5c0cb']);
  const tint=color=>!paint?color:'#'+[1,3,5].map(i=>Math.round(parseInt(paint.slice(i,i+2),16)*(.65+.35*parseInt(color.slice(i,i+2),16)/255)).toString(16).padStart(2,'0')).join('');
  const scale=body?.scale||[1,1,1],roofShape=body?.roof||[-.65,.65,1.42];
  const transform=p=>p.map((v,i)=>v*scale[i]);
  const face=(points,color)=>{points=points.map(transform);const coated=!!paint&&coatings.has(color);faces.push({points,color:coated?tint(color):color,coated,depth:points.reduce((sum,p)=>sum+p.reduce((n,v,i)=>n+v*view[i],0),0)/points.length});};
  const ring=(z,length,width)=>[[-length,-width,z],[length,-width,z],[length,width,z],[-length,width,z]];
  const roundedRing=(z,length,width,cut)=>[[-length,-width+cut,z],[-length+cut,-width,z],[length-cut,-width,z],[length,-width+cut,z],[length,width-cut,z],[length-cut,width,z],[-length+cut,width,z],[-length,width-cut,z]];
  const lower=roundedRing(.26,2.10,.84,.22),shoulder=roundedRing(.61,2.18,.94,.22),belt=roundedRing(.82,2.04,.90,.24),style=body?.style||'sedan';
  const suv=['sorento','sportage','carnival','ev9','ev3','ev5','niro','seltos','tucson','santafe','kona','palisade','staria','custin','venue','inster','mufasa'].includes(style),rear=suv?-1.85:['ev6','ioniq5'].includes(style)?-1.65:-1.22;
  for(let i=0;i<8;i++){
    const j=(i+1)%8;
    face([lower[i],lower[j],shoulder[j],shoulder[i]],(ego?['#a7b2be','#b9c4ce','#cbd4dc','#d3dce4','#dce3ea','#c8d2dc','#aebbc8','#9baab9']:['#7d8a98','#8794a2','#94a1af','#a6b1bc','#b2bdc8','#9daab6','#8c9aaa','#81909e'])[i]);
    face([shoulder[i],shoulder[j],belt[j],belt[i]],(ego?['#c7d2de','#d9e1e9','#eaf0f5','#f1f5f9','#f6f8fb','#e5ebf1','#cfdae4','#bdcad7']:['#a3b0be','#b1bdc9','#b8c4d0','#c4cdd5','#c8d1d9','#bdc7d1','#a5b4c2','#96a6b5'])[i]);
  }
  face([[-2.04,-.66,.82],[rear,-.80,.89],[rear,.80,.89],[-2.04,.66,.82]],'#dce4ec');
  for(const side of [-1,1]){
    const hood=[[1.35,.82,.89],[1.65,.85,.88],[1.89,.79,.85],[2.04,.66,.82]];
    for(let i=1;i<hood.length;i++){
      const [a,wa,za]=hood[i-1],[b,wb,zb]=hood[i];
      face([[a,0,za+.035],[b,0,zb+.035],[b,side*wb,zb],[a,side*wa,za]],'#edf2f7');
    }
    face([[rear,side*.8,.89],[1.35,side*.8,.89],[1.80,side*.90,.82],[-1.80,side*.90,.82]],'#dce4ec');
  }
  const [back,frontRoof,peak]=roofShape;
  // Taper the glazing at the hatch and bonnet. A shallow crown catches light as the camera orbits.
  const cabinSections=[[rear,.80,.89],[(rear+back)/2,.755,(peak+.89)/2+.05],[back,.67,peak-.035],
    [(back+frontRoof)/2,.685,peak],[frontRoof,.66,peak-.045],[(frontRoof+1.35)/2,.75,(peak+.89)/2+.035],[1.35,.80,.89]];
  for(let i=1;i<cabinSections.length;i++){
    const [a,wa,za]=cabinSections[i-1],[b,wb,zb]=cabinSections[i],roofBand=i===3||i===4;
    const glazing=roofBand?(ego?'#e1e6ec':'#9ba8b6'):(i<3?'#344454':'#455869');
    for(const side of [-1,1]){
      face([[a,0,za+.032],[b,0,zb+.032],[b,side*wb,zb],[a,side*wa,za]],glazing);
      face([[a,side*wa,za],[b,side*wb,zb],[b,side*.82,.89],[a,side*.82,.89]],'#455869');
    }
  }
  // Roof edge rails, rear spoiler and divided glazing avoid a plain box silhouette.
  for(const side of [-1,1]){
    face([[rear,side*.82,.89],[roofShape[0],side*.69,roofShape[2]],[roofShape[0]+.07,side*.69,roofShape[2]],[rear+.07,side*.82,.89]],'#c5d1dd');
    face([[1.28,side*.82,.91],[roofShape[1]-.06,side*.69,roofShape[2]],[roofShape[1],side*.69,roofShape[2]],[1.35,side*.82,.89]],'#e4ebf2');
    if(suv)face([[roofShape[0]+.08,side*.65,roofShape[2]+.035],[roofShape[1]-.18,side*.65,roofShape[2]+.035],[roofShape[1]-.18,side*.69,roofShape[2]+.055],[roofShape[0]+.08,side*.69,roofShape[2]+.055]],'#7c8e9f');
  }
  if(ego)face([[rear-.15,-.84,.94],[rear+.15,-.84,.98],[rear+.15,.84,.98],[rear-.15,.84,.94]],'#a7b7c7');
  if(ego&&['ev6','ev9','sportage'].includes(style)){
    const glass=[[back+.06,.43,.012],[back+.20,.57,.045],[(back+frontRoof)/2,.59,.065],[frontRoof-.19,.54,.042],[frontRoof-.05,.42,.009]];
    for(let i=1;i<glass.length;i++){
      const [a,wa,za]=glass[i-1],[b,wb,zb]=glass[i];
      for(const side of [-1,1]){
        face([[a,0,peak+za+.025],[b,0,peak+zb+.025],[b,side*wb,peak+zb],[a,side*wa,peak+za]],i<3?'#242d35':'#33404b');
      }
    }
  }
  for(const side of [-1,1]){
    face([[-1.25,side*.835,.82],[1.4,side*.835,.82],[1.35,side*.82,.91],[-1.22,side*.82,.91]],'#c4ced9');
    face([[-.08,side*.77,.9],[.04,side*.77,.9],[.04,side*.69,1.42],[-.08,side*.69,1.42]],'#9eacb9');
    // Lower sill, two door seams, flush handles and mirrors add readable depth.
    face([[-1.85,side*.905,.30],[1.8,side*.905,.30],[1.7,side*.935,.39],[-1.75,side*.935,.39]],'#5a6470');
    for(const x of [-.1,1.15])face([[x,side*.943,.39],[x+.012,side*.943,.39],[x+.012,side*.943,.8],[x,side*.943,.8]],'#8c99a6');
    for(const x of [-.85,.65])face([[x-.14,side*.946,.72],[x+.14,side*.946,.72],[x+.14,side*.946,.75],[x-.14,side*.946,.75]],'#738393');
    face([[.95,side*.82,.91],[1.18,side*.82,.91],[1.15,side*1.08,.97],[.9,side*1.08,.97]],'#9aa7b5');
    for(const x of [-1.4,1.35]){
      face(Array.from({length:20},(_,i)=>{const a=i*Math.PI/10;return[x+Math.cos(a)*.36,side*.96,.36+Math.sin(a)*.36];}),'#252d36');
      for(let i=0;i<20;i++){const a=i*Math.PI/10,b=(i+1)*Math.PI/10;face([[x+Math.cos(a)*.36,side*.86,.36+Math.sin(a)*.36],[x+Math.cos(b)*.36,side*.86,.36+Math.sin(b)*.36],[x+Math.cos(b)*.36,side*.96,.36+Math.sin(b)*.36],[x+Math.cos(a)*.36,side*.96,.36+Math.sin(a)*.36]],'#252d36');}
      face(Array.from({length:16},(_,i)=>{const a=i*Math.PI/8;return[x+Math.cos(a)*.22,side*.97,.36+Math.sin(a)*.22];}),'#9aa7b5');
      for(let spoke=0;spoke<5;spoke++){const a=spoke*Math.PI*.4;face([[x,side*.975,.36],[x+Math.cos(a)*.21,side*.975,.36+Math.sin(a)*.21],[x+Math.cos(a+.22)*.21,side*.975,.36+Math.sin(a+.22)*.21]],'#dce3eb');}
    }
  }
  const brake=ego&&lamps.brake===true,red=brake?'#ff343d':'#912f3b';
  const tail=(y0,y1,z0,z1,color)=>face([[-2.19,y0,z0],[-2.19,y1,z0],[-2.10,y1,z1],[-2.10,y0,z1]],color);
  const front=(y0,y1,z0,z1,color)=>face([[2.19,y0,z0],[2.19,y1,z0],[2.10,y1,z1],[2.10,y0,z1]],color);
  if(ego){
    tail(-.27,.27,.37,.51,'#53616d');front(-.65,.65,.36,.50,['ev6','ev9'].includes(style)?'#687786':'#303f4b');
    tail(-.35,.35,.83,.88,'#b5c0cb');
  }
  if(style==='ev6'){
    for(let i=0;i<16;i++){const y=-.84+i*.105,z=.69+.12*(1-(y/.9)**2);tail(y,y+.105,z,z+.045,red);}tail(-.9,-.7,.62,.76,red);tail(.7,.9,.62,.76,red);
  }else if(['sorento','carnival','ev9','ev3','ev5','palisade','staria'].includes(style)){
    for(const side of [-1,1])for(const offset of [0,.13])tail(side*(.7+offset)-.035,side*(.7+offset)+.035,.46,.82,red);
    if(style!=='sorento')tail(-.82,.82,.78,.82,red);
  }else if(['sportage','tucson','niro','seltos','custin','kona','k5','ioniq6','mufasa'].includes(style)){
    tail(-.82,.82,.72,.75,red);for(const side of [-1,1])tail(side*.72-.1,side*.72+.1,.59,.74,red);
  }else if(style==='santafe'){
    for(const side of [-1,1])for(const y of [side*.55,side*.82])tail(y-.04,y+.04,.46,.74,red);tail(-.86,.86,.58,.62,red);
  }else if(style==='ioniq5'){
    for(const side of [-1,1])for(let x=0;x<5;x++)tail(side*.53+(x-2)*.065-.023,side*.53+(x-2)*.065+.023,.64,.70,red);
  }else for(const y of [-.68,.68])tail(y-.18,y+.18,.59,.7,red);
  if(ego)face([[roofShape[0]-.01,-.27,roofShape[2]],[roofShape[0]-.01,.27,roofShape[2]],[roofShape[0]-.01,.27,roofShape[2]+.035],[roofShape[0]-.01,-.27,roofShape[2]+.035]],red);
  for(const side of [-1,1]){
    const y=side*.68;
    front(y-.18,y+.18,.59,.7,ego?(lamps.lowBeam||lamps.highBeam?'#f4f9ff':'#4a5663'):'#4a5663');
    if(ego&&['ev9','ev3','ev5','sportage','sorento','carnival','palisade'].includes(style))front(y-.04,y+.04,.45,.81,lamps.lowBeam||lamps.highBeam?'#f4f9ff':'#4a5663');
    if(ego&&style==='ioniq5')for(let p=0;p<4;p++)front(y-.12+p*.065,y-.075+p*.065,.62,.68,lamps.lowBeam||lamps.highBeam?'#f4f9ff':'#4a5663');
    if(ego&&['kona','staria','santafe'].includes(style))front(-.82,.82,.79,.815,lamps.lowBeam||lamps.highBeam?'#f4f9ff':'#4a5663');
    const amber=ego&&(side<0?lamps.left:lamps.right)===true?'#ffb126':'#65513b';
    if(ego){tail(y-.13,y+.13,.51,.57,amber);front(y-.13,y+.13,.53,.58,amber);face([[.9,side*1.085,.94],[1.13,side*1.085,.94],[1.13,side*1.085,.97],[.9,side*1.085,.97]],amber);}
  }
  const shadow=ring(.02,2.3,1.02).map(p=>project(...transform(p)));ctx.save();
  if(shadow.every(Boolean)){ctx.beginPath();shadow.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fillStyle='#50607020';ctx.fill();}
  for(const f of faces.sort((a,b)=>a.depth-b.depth)){
    const p=f.points.map(v=>project(...v));if(p.some(v=>!v))continue;
    ctx.beginPath();p.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fillStyle=f.color;
    if(ego&&(f.coated||['#f6f8fb','#e5ebf1','#cfdae4','#e1e6ec','#34414e','#344454','#455869'].includes(f.color))){
      const ys=p.map(v=>v[1]),g=ctx.createLinearGradient?.(0,Math.min(...ys),0,Math.max(...ys)+1);
      if(g?.addColorStop){g.addColorStop(0,f.color);g.addColorStop(1,['#34414e','#344454','#455869'].includes(f.color)?'#101b29':'#a5b2c0');ctx.fillStyle=g;}
    }
    const illuminated=f.color==='#ff343d'||f.color==='#ffb126'||f.color==='#f4f9ff';if(illuminated){ctx.shadowColor=f.color;ctx.shadowBlur=5;}ctx.fill();if(illuminated)ctx.shadowBlur=0;
    if(outline){ctx.strokeStyle=outline;ctx.lineWidth=.8;ctx.stroke();}
  }
  ctx.restore();
}


// Object classes come from the existing detector. Size/heading are illustrative.
export function drawDetectedMesh(ctx,project,object){
  const {x,y,kind}=object;
  if(!Number.isFinite(x)||!Number.isFinite(y))return;
  const p=(dx,dy,z)=>project(x+dx,y+dy,z);
  if(project.view)p.view=[project.view[0]-x,project.view[1]-y,project.view[2]];
  const poly=(points,color)=>{const a=points.map(v=>p(...v));if(a.some(v=>!v))return;ctx.beginPath();a.forEach((v,i)=>i?ctx.lineTo(...v):ctx.moveTo(...v));ctx.closePath();ctx.fillStyle=color;ctx.fill();};
  const box=(cx,cy,z,l,w,h,color)=>{
    poly([[cx-l,cy-w,z],[cx-l,cy+w,z],[cx-l,cy+w,z+h],[cx-l,cy-w,z+h]],'#7b8895');
    poly([[cx-l,cy+w,z],[cx+l,cy+w,z],[cx+l,cy+w,z+h],[cx-l,cy+w,z+h]],color);
    poly([[cx-l,cy-w,z+h],[cx+l,cy-w,z+h],[cx+l,cy+w,z+h],[cx-l,cy+w,z+h]],'#c4cdd5');
  };
  const disc=(cx,z,r,color)=>{const center=p(cx,0,z),edge=p(cx,0,z+r);if(!center||!edge)return;ctx.beginPath();ctx.arc(center[0],center[1],Math.max(1,Math.hypot(center[0]-edge[0],center[1]-edge[1])),0,Math.PI*2);ctx.fillStyle=color;ctx.fill();};
  if(kind==='barrier'){box(0,0,.03,.9,.22,.8,'#ce785a');return;}
  if(kind==='drum'){
    for(let i=0;i<12;i++){
      const a=Math.PI*i/6,b=Math.PI*(i+1)/6,side=(angle,z)=>[.34*Math.cos(angle),.34*Math.sin(angle),z];
      for(const [lo,hi,color] of [[0,.42,'#d7963d'],[.42,.62,'#dfdfdb'],[.62,.92,'#d7963d']])poly([side(a,lo),side(b,lo),side(b,hi),side(a,hi)],color);
    }
    return;
  }
  if(kind==='traffic cone'){
    box(0,0,.01,.3,.3,.05,'#626f7c');
    poly([[-.23,-.23,.06],[.23,-.23,.06],[0,0,.8]],'#ef9d55');
    poly([[.23,-.23,.06],[.23,.23,.06],[0,0,.8]],'#da7b36');
    poly([[.23,.23,.06],[-.23,.23,.06],[0,0,.8]],'#ef914b');
    poly([[-.23,.23,.06],[-.23,-.23,.06],[0,0,.8]],'#f0a365');
    poly([[-.15,.15,.32],[-.15,-.15,.32],[-.1,-.1,.48],[-.1,.1,.48]],'#f6f6ef');return;
  }
  if(kind==='car'){drawVehicleMesh(ctx,p,{ego:true,body:{paint:object.pathFocus?'#659fd7':'#a8a9ac'}});return;}
  if(ANIMALS.includes(kind)){
    const scale=({cat:.45,dog:.65,horse:1.2,sheep:.8,cow:1.2,elephant:2.3,bear:1.1,zebra:1.2,giraffe:1.5})[kind];
    const color=kind==='zebra'?'#b6c1cb':kind==='bear'?'#697c8d':'#93a7b8';
    box(0,0,.65*scale,.65*scale,.23*scale,.42*scale,color);
    for(const dx of [-.45,.45])for(const dy of [-.18,.18])box(dx*scale,dy*scale,.05*scale,.065*scale,.065*scale,.62*scale,'#768b9c');
    const neck=kind==='giraffe'?1.5:kind==='horse'||kind==='zebra'?.55:.2;
    box(.52*scale,0,.85*scale,.12*scale,.14*scale,neck*scale,color);
    box(.7*scale,0,(.9+neck)*scale,.23*scale,.17*scale,.24*scale,'#aab9c5');
    if(kind==='elephant')box(.92*scale,0,.35*scale,.08*scale,.1*scale,.85*scale,'#8298aa');
    if(kind==='zebra')for(const dx of [-.45,-.15,.15,.45])box(dx*scale,.235*scale,.7*scale,.03*scale,.012*scale,.33*scale,'#596e80');
    return;
  }
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
