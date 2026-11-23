// Perspective illustration for layout editing. All coordinates and traffic are simulated.
function drawRealityScene(canvas,w,h,v) {
  canvas.width=w; canvas.height=h;
  const ctx=canvas.getContext("2d"), night=v.scene_style===1;
  ctx.scale(w/1000,h/450);
  const bg=ctx.createLinearGradient(0,0,0,450);
  bg.addColorStop(0,night?"#17222e":"#c3d6e1");bg.addColorStop(.32,night?"#404d59":"#e8eded");
  bg.addColorStop(1,night?"#24313b":"#acb9c3");ctx.fillStyle=bg;ctx.fillRect(0,0,1000,450);
  const color=k=>"#"+v[k+"_color"].toString(16).padStart(6,"0");
  function face(points,paint) {
    ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fillStyle=paint;ctx.fill();
  }
  function layer(key,draw) {
    ctx.save();ctx.translate(v[key+"_x"]*10,v[key+"_y"]*4.5);
    draw(v[key+"_size"]/100,color(key));ctx.restore();
  }
  function project(x,z,y=0) {
    const scale=740/(z+8);
    return [435+(x+Math.min(z,90)**2*.00032)*scale,118+(4-y)*scale];
  }
  function strip(x,a,b,width,paint) {
    const left=[],right=[];
    for(let z=a;z<b;z+=2){left.push(project(x-width/2,z));right.push(project(x+width/2,z));}
    left.push(project(x-width/2,b));right.push(project(x+width/2,b));face(left.concat(right.reverse()),paint);
  }
  strip(0,-1,110,22,night?"#35424c":"#85939d");
  strip(0,-1,110,18,night?"#25303a":"#65747f");
  layer("path",(s,c)=>{ctx.globalAlpha=.55;strip(0,0,65,1.8*s,c);});
  layer("lane",(s,c)=>{
    for(const x of [-8.8,-5.3,-1.76,1.76,5.3,8.8]){
      if(Math.abs(x)>8)strip(x,-1,105,.12*s,c);
      else for(let z=0;z<100;z+=8)strip(x,z,z+4,.13*s,c);
    }
  });
  layer("vehicle",(s,c)=>{
    for(const [x,z] of [[0,48],[3.52,35],[-3.52,20],[0,12],[3.52,7],[0,1.3]]){
      const pt=(a,b,y)=>project(x+a*s,z+b*s,y*s);
      function panel(vertices,paint){face(vertices.map(p=>pt(...p)),paint);}
      panel([[-1.1,-.16,0],[1.12,-.16,0],[1.12,4.4,0],[-1.1,4.4,0]],"#15212b88");
      panel([[-.93,0,.22],[.93,0,.22],[.95,0,.85],[-.95,0,.85]],c);
      panel([[-.95,0,.85],[.95,0,.85],[.91,4.2,.8],[-.91,4.2,.8]],c);
      const side=x<0?1:-1;
      panel([[side*.93,0,.22],[side*.91,4.2,.22],[side*.91,4.2,.8],[side*.95,0,.85]],"#536271");
      panel([[-.84,.55,.85],[.84,.55,.85],[.7,1.35,1.48],[-.7,1.35,1.48]],"#23384b");
      panel([[side*.84,.55,.85],[side*.7,1.35,1.48],[side*.68,2.65,1.48],[side*.82,3.35,.82]],"#334a5a");
      panel([[-.7,1.35,1.48],[.7,1.35,1.48],[.68,2.65,1.48],[-.68,2.65,1.48]],c);
      for(const k of [-1,1])panel([[k*.89,-.01,.56],[k*.46,-.01,.56],[k*.47,-.01,.67],[k*.9,-.01,.68]],"#ff6567");
    }
  });
  layer("map",(s,c)=>{
    ctx.translate(805,128);ctx.scale(s*(Math.min(w*.31,h*.48)/w*1000/310),s*(Math.min(w*.31,h*.48)/h*450/184));
    ctx.beginPath();ctx.roundRect(-155,-92,310,184,12);ctx.clip();
    ctx.fillStyle=night?"#1a2a36":"#e4e9e6";ctx.fillRect(-155,-92,310,184);
    function line(points,paint,width){ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.strokeStyle=paint;ctx.lineWidth=width;ctx.lineJoin="round";ctx.stroke();}
    ctx.fillStyle=night?"#274339":"#bfd9c3";ctx.fillRect(35,20,75,46);
    for(let x=-200;x<200;x+=47)line([[x,-92],[x+43,92]],night?"#40525c":"#fff",4);
    for(let y=-110;y<120;y+=38)line([[-155,y],[155,y+15]],night?"#40525c":"#fff",5);
    line([[-12,98],[-29,30],[-40,-13],[44,-9],[29,-93]],c,9);
    face([[-25,14],[-36,43],[-25,38],[-14,43]],"#ffffff");
    ctx.fillStyle=night?"#e6edf1":"#26363e";ctx.font="bold 13px sans-serif";ctx.fillText("模擬導航",-140,-69);
  });
}
