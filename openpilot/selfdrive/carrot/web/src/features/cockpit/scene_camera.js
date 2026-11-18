// Presentation only: orbit a fixed vehicle pivot and fit its complete envelope.
const finite=Number.isFinite,clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function sceneCamera(width,height,view={}){
 const w=finite(width)&&width>0?width:1,h=finite(height)&&height>0?height:1,aspect=w/h;
 const yaw=(finite(view?.yaw)?view.yaw:0)*Math.PI/180,pitch=clamp(finite(view?.pitch)?view.pitch:25,18,60)*Math.PI/180;
 const scale=Array.isArray(view?.skinScale)&&view.skinScale.length===3&&view.skinScale.every(n=>finite(n)&&n>.5&&n<2)?view.skinScale:[1.25,1.15,1.55];
 const pivot=[0,0,.78*scale[2]],anchor=clamp((finite(view?.anchorY)?view.anchorY:.80)-.20,.56,.65);
 const fov=Math.max(50,Math.min(100,2*Math.atan(Math.tan(Math.PI/8)/Math.max(.25,aspect))*180/Math.PI));
 const tan=Math.tan(fov*Math.PI/360),theta=pitch-Math.atan((anchor*2-1)*tan);
 const cy=Math.cos(yaw),sy=Math.sin(yaw),ct=Math.cos(theta),st=Math.sin(theta);
 const forward=[ct*cy,-ct*sy,-st],right=[-sy,-cy,0],up=[st*cy,-st*sy,ct];
 let range=clamp(finite(view?.distance)?view.distance:9,5,26)*.80,position;
 const depth=(p)=>p.reduce((n,v,i)=>n+v*forward[i],0);
 const extents=[2.42*scale[0],1.16*scale[1],1.66*scale[2]];
 for(let attempt=0;attempt<40;attempt++){
  position=[-range*Math.cos(pitch)*cy,range*Math.cos(pitch)*sy,pivot[2]+range*Math.sin(pitch)];
  let fits=true;
  for(const x of [-extents[0],extents[0]])for(const y of [-extents[1],extents[1]])for(const z of [0,extents[2]]){
   const p=[x-position[0],y-position[1],z-position[2]],d=depth(p);
   const px=p.reduce((n,v,i)=>n+v*right[i],0)/(d*tan*aspect),py=p.reduce((n,v,i)=>n+v*up[i],0)/(d*tan);
   if(d<=.1||Math.abs(px)>.90||Math.abs(py)>.84)fits=false;
  }
  if(fits)break;range*=1.09;
 }
 return {position,target:position.map((p,i)=>p+forward[i]*20),pivot,aspect,fov,range,forward,right,up};
}
export function sceneProjection(width,height,view){
 const spec=sceneCamera(width,height,view),tan=Math.tan(spec.fov*Math.PI/360);
 const transform=(x,y,z)=>[x-spec.position[0],-y-spec.position[1],z-spec.position[2]];
 const dot=(p,v)=>p.reduce((sum,n,i)=>sum+n*v[i],0);
 const project=(x,y,z=0)=>{const p=transform(x,y,z),d=dot(p,spec.forward);return d>.1?[width/2+dot(p,spec.right)/(d*tan*spec.aspect)*width/2,height/2-dot(p,spec.up)/(d*tan)*height/2]:null;};
 project.view=[spec.position[0],-spec.position[1],spec.position[2]];
 project.depth=(x,y,z=0)=>dot(transform(x,y,z),spec.forward);
 return project;
}
