// Original, unbranded display assets. Rebuild with node scripts/build_road_models.mjs.
import * as T from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {writeFile} from 'node:fs/promises';

// GLTFExporter uses the browser FileReader interface for the final binary Blob.
globalThis.FileReader = class {
  async readAsArrayBuffer(blob) { this.result=await blob.arrayBuffer(); this.onloadend(); }
};

const paint='#b8bdc1', glass='#40515c', tire='#25282c', rim='#a7aeb2', trim='#50585d';
const styles = {
  sedan:[4.55,1.82,1.47], suv:[4.78,1.92,1.77], mpv:[5.00,1.94,1.89],
  pickup:[5.35,1.98,1.85], truck:[7.30,2.45,3.35], bus:[10.6,2.49,3.08]
};
const material=new T.MeshStandardMaterial({vertexColors:true,roughness:.47,metalness:.12,side:T.DoubleSide});

function model(name,lod) {
  const parts=[], segments=[20,12,8][lod], pi=Math.PI;
  function piece(g,color,forward,left,up,rotate=null) {
    if(rotate)g.applyMatrix4(rotate);
    g.translate(left,up,forward);
    g.deleteAttribute('uv');
    g.clearGroups();
    const rgb=new T.Color(color).toArray().map(n=>Math.round(255*n));
    const data=new Uint8Array(3*g.attributes.position.count);
    for(let i=0;i<data.length;i+=3)data.set(rgb,i);
    g.setAttribute('color',new T.Uint8BufferAttribute(data,3,true));
    parts.push(g);
  }
  function box(f,l,u,length,width,height,color) {
    piece(new T.BoxGeometry(width,height,length),color,f,l,u);
  }
  function oval(f,l,u,length,width,height,color) {
    const g=new T.SphereGeometry(1,segments,Math.max(4,segments/2));
    piece(g.scale(width/2,height/2,length/2),color,f,l,u);
  }
  function cylinder(f,l,u,top,bottom,height,color,wheel=false) {
    const g=new T.CylinderGeometry(top,bottom,height,segments);
    piece(g,color,f,l,u,wheel?new T.Matrix4().makeRotationZ(pi/2):null);
  }
  function rod(a,b,r,color) {
    const point=([f,l,u])=>new T.Vector3(l,u,f);
    const v=point(b).sub(point(a)),mid=a.map((n,i)=>(n+b[i])/2);
    const rot=new T.Matrix4().makeRotationFromQuaternion(new T.Quaternion().setFromUnitVectors(new T.Vector3(0,1,0),v.clone().normalize()));
    piece(new T.CylinderGeometry(r,r,v.length(),lod===0?8:5),color,...mid,rot);
  }
  // Horizontal superellipse rings form a crowned body, swept glass and rounded roof.
  function shell(rings,color,roundness=.42) {
    const pos=[],idx=[],count=segments*2;
    for(const [u,f,len,width] of rings)for(let i=0;i<count;i++){
      const a=2*pi*i/count;
      const shape=n=>Math.sign(n)*Math.abs(n)**roundness;
      pos.push(width/2*shape(Math.sin(a)),u,f+len/2*shape(Math.cos(a)));
    }
    for(let j=0;j<rings.length-1;j++)for(let i=0;i<count;i++){
      const a=j*count+i,b=j*count+(i+1)%count;
      idx.push(a,b,b+count,a,b+count,a+count);
    }
    const last=count*(rings.length-1);
    for(let i=1;i<count-1;i++)idx.push(0,i+1,i,last,last+i,last+i+1);
    const g=new T.BufferGeometry();
    g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();
    piece(g,color,0,0,0);
  }
  function wheel(f,l,r,width) {
    cylinder(f,l,r,r,r,width,tire,true);
    for(const side of [-1,1]){
      const edge=l+side*(width/2+.008);
      cylinder(f,edge,r,r*.66,r*.66,.016,rim,true);
      if(lod===0){
        cylinder(f,edge+side*.012,r,r*.50,r*.50,.012,trim,true);
        for(let k=0;k<5;k++){
          const a=2*pi*k/5;
          rod([f,edge+side*.024,r],[f+Math.cos(a)*r*.51,edge+side*.024,r+Math.sin(a)*r*.51],.018,rim);
        }
      }
    }
  }
  if(Object.hasOwn(styles,name)){
    const [L,W,H]=styles[name],large=name==='truck'||name==='bus';
    const radius=large?.46:name==='pickup'?.40:.34, belt=large?.95:H*.57;
    shell([[radius*.57,0,L*.91,W*.88],[belt*.70,0,L,W],[belt,0,L*.99,W*.97],[belt+.075,0,L*.91,W*.93]],paint);
    if(name==='truck'){
      const cab=L*.285,front=(L-cab)/2;
      shell([[belt,front,cab,W*.96],[2.40,front-.13,cab*.88,W*.92],[2.57,front-.14,cab*.85,W*.91]],glass,.23);
      box(front-.13,0,2.55,cab*.84,W*.92,.09,paint);
      box(-cab/2-.07,0,(H+belt)/2,L-cab-.24,W*.98,H-belt,'#c7cbce');
      if(lod===0)for(const side of [-1,1])for(let f=-L*.44;f<L*.16;f+=.22)box(f,side*W*.491,(H+belt)/2,.022,.018,H-belt-.08,'#aeb6ba');
    }else if(name==='bus'){
      shell([[belt,0,L*.99,W],[1.28,0,L*.99,W],[H-.10,0,L*.97,W*.98],[H,0,L*.95,W*.94]],paint,.2);
      shell([[1.53,0,L*.994,W*1.004],[H-.35,0,L*.984,W]],glass,.24);
      for(const side of [-1,1])for(let f=-L*.41;f<L*.46;f+=lod===2?L/4:L/8)box(f,side*W*.501,(H+1.18)/2,.063,.025,H-1.88,trim);
      box(0,0,belt+.04,L*.98,W+.025,.16,'#668192');
      if(lod===0)box(-1.5,0,H+.055,2.1,1.22,.11,rim);
    }else{
      const pickup=name==='pickup',van=name==='mpv',fast=name==='sedan';
      const cf=pickup?L*.115:van?-.02:-L*.06, cab=L*(pickup?.51:van?.89:fast?.72:.83);
      shell([[belt+.035,cf,cab,W*.91],[H*.76,cf-.04,cab*.91,W*.87],[H*.96,cf-.13,cab*(fast?.57:.78),W*.74]],glass);
      shell([[H*.95,cf-.13,cab*(fast?.59:.80),W*.76],[H,cf-.12,cab*(fast?.55:.77),W*.71]],paint);
      if(pickup){
        box(-L*.33,0,belt+.08,L*.28,W*.79,.06,trim);
        for(const s of [-1,1])box(-L*.33,s*W*.43,belt+.16,L*.3,.10,.23,paint);
        box(-L*.474,0,belt+.16,.10,W*.90,.22,paint);
      }
      for(const side of [-1,1]){
        if(lod<2){
          rod([cf,side*W*.455,belt+.06],[cf-.04,side*W*.38,H*.95],.038,trim);
          oval(cf+cab*.35,side*W*.51,belt+.17,.24,.16,.12,paint);
        }
        if(lod===0){
          for(const offset of [-.18,.16])box(cf+offset*cab,side*W*.496,belt*.86,.17,.022,.032,trim);
          box(0,side*W*.49,belt*.49,L*.69,.035,.047,rim);
        }
      }
    }
    for(const side of [-1,1]){
      for(const f of [-L*.30,L*.29])wheel(f,side*(W/2-.085),radius,large?.24:.20);
      box(-L*.493,side*W*.32,belt*.86,.055,W*.22,.10,'#9f3838');
      box(L*.491,side*W*.32,belt*.87,.055,W*.24,.085,'#dfe6e6');
    }
    if(lod<2)box(-L*.502,0,belt*.60,.025,W*.23,.125,trim);
  }else if(name==='motorcycle'||name==='bicycle'){
    const moto=name==='motorcycle',r=moto?.28:.32;
    for(const f of [-.64,.64]){
      if(moto)wheel(f,0,r,.14);
      else {
        const g=new T.TorusGeometry(r-.025,.028,6,segments).rotateY(pi/2);
        piece(g,tire,f,0,r);
        if(lod<2)for(let k=0;k<6;k++){const a=k*pi/6;rod([f-r*Math.cos(a),0,r-r*Math.sin(a)],[f+r*Math.cos(a),0,r+r*Math.sin(a)],.009,rim);}
      }
    }
    rod([-.64,0,r],[-.15,0,.88],.045,trim);rod([-.64,0,r],[.12,0,.33],.045,rim);
    rod([.12,0,.33],[.46,0,.89],.045,trim);rod([.46,0,.89],[-.15,0,.88],.037,rim);
    rod([.64,0,r],[.43,0,1.07],.043,trim);rod([.43,-.25,1.07],[.43,.25,1.07],.035,trim);
    oval(-.18,0,.91,moto?.78:.29,moto?.34:.17,.12,tire);
    if(moto){oval(.06,0,.58,.89,.38,.47,paint);oval(.46,0,.8,.33,.40,.54,paint);}
  }else if(name==='person'){
    oval(0,0,1.57,.24,.23,.28,'#a6a8a6');
    oval(0,0,1.12,.29,.47,.66,'#8998a2');
    for(const side of [-1,1]){
      rod([0,side*.12,.86],[side*.08,side*.11,.47],.095,trim);
      rod([side*.08,side*.11,.47],[side*.13,side*.12,.09],.065,trim);
      oval(side*.13+.045,side*.12,.08,.24,.15,.135,tire);
      rod([0,side*.2,1.32],[-side*.09,side*.29,.94],.065,'#82919a');
    }
  }else if(name==='cone'){
    box(0,0,.045,.48,.48,.09,trim);
    cylinder(0,0,.39,.037,.19,.63,'#ed802c');cylinder(0,0,.415,.10,.128,.115,'#e8e8de');
  }else if(name==='barrier'){
    shell([[.02,0,1.85,.53],[.22,0,1.82,.53],[.48,0,1.74,.29],[.88,0,1.72,.27]],'#d77453',.25);
    if(lod<2)for(const f of [-.52,0,.52])box(f,.145,.66,.15,.016,.13,'#e8ddc4');
  }else if(name==='drum'){
    cylinder(0,0,.47,.36,.34,.90,'#db9637');cylinder(0,0,.55,.36,.36,.19,'#dedfd8');
    cylinder(0,0,.93,.37,.37,.045,trim);
  }
  const geometry=mergeGeometries(parts);
  const mesh=new T.Mesh(geometry,material);
  mesh.name=name+'_lod'+lod;
  return mesh;
}

const types=[...Object.keys(styles),'motorcycle','bicycle','person','cone','barrier','drum'];
const scenes=types.flatMap(name=>[0,1,2].map(lod=>{
  const scene=new T.Scene();scene.name=name+'_'+lod;scene.add(model(name,lod));return scene;
}));
const output=await new GLTFExporter().parseAsync(scenes,{binary:true});
await writeFile(new URL('../assets/road-models-v1.glb',import.meta.url),new Uint8Array(output));
