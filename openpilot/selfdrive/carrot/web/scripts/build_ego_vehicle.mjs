// Original unbranded CUV, in metres. glTF axes: +Z forward, +X left, +Y up.
import * as T from 'three';
import {GLTFExporter} from 'three/addons/exporters/GLTFExporter.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {writeFile} from 'node:fs/promises';

globalThis.FileReader=class {async readAsArrayBuffer(blob){this.result=await blob.arrayBuffer();this.onloadend();}};
const scene=new T.Scene();
const materials={};
for(const [name,color,metalness,roughness] of [
  ['Paint','#eef0f2',.45,.28],['Glass','#253039',.3,.18],['Trim','#26282a',.08,.7],
  ['Alloy','#a6aeb3',.65,.32],['RearLens','#681e25',.15,.26],
  ['IndicatorLeft','#56391c',.1,.3],['IndicatorRight','#56391c',.1,.3],['Headlamp','#b0c8d1',.18,.22]
]){
  materials[name]=new T.MeshStandardMaterial({name,color,metalness,roughness,side:T.DoubleSide});
}
for(const level of [0,1,2]){
  const root=new T.Group();root.name='CUV_LOD'+level;scene.add(root);
  const sides=[48,24,12][level],round=n=>Math.sign(n)*Math.abs(n)**.48;
  const groups=new Map();
  function part(material,geometry,x=0,y=0,z=0){
    geometry.translate(x,y,z);geometry.deleteAttribute('uv');
    const g=geometry.index?geometry.toNonIndexed():geometry;
    if(!groups.has(material))groups.set(material,[]);
    groups.get(material).push(g);
  }
  function shell(material,rings){
    const pos=[],idx=[];
    for(const [y,w,long,z] of rings)for(let i=0;i<sides;i++){
      const a=2*Math.PI*i/sides;
      pos.push(w*.5*round(Math.sin(a)),y,z+long*.5*round(Math.cos(a)));
    }
    for(let j=1;j<rings.length;j++)for(let i=0;i<sides;i++){
      const a=(j-1)*sides+i,b=(j-1)*sides+(i+1)%sides;idx.push(a,b,b+sides,a,b+sides,a+sides);
    }
    const last=(rings.length-1)*sides;
    for(let i=1;i<sides-1;i++)idx.push(0,i+1,i,last,last+i,last+i+1);
    const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setIndex(idx);g.computeVertexNormals();part(material,g);
  }
  function bar(material,x,y,z,w,h,d){part(material,new T.BoxGeometry(w,h,d),x,y,z);}
  shell('Trim',[[.26,1.67,4.26,0],[.39,1.82,4.62,0],[.52,1.88,4.63,0]]);
  shell('Paint',[[.44,1.84,4.55,0],[.66,1.90,4.65,0],[.87,1.86,4.49,-.02],[.99,1.78,4.17,-.1]]);
  shell('Glass',[[.96,1.78,3.45,-.31],[1.26,1.67,2.97,-.33],[1.54,1.44,2.16,-.4]]);
  shell('Paint',[[1.51,1.48,2.24,-.41],[1.59,1.43,2.18,-.43],[1.62,1.25,1.90,-.43]]);
  bar('RearLens',0,.84,-2.25,1.58,.056,.085);
  for(const side of [-1,1]){
    const indicator=side===1?'IndicatorLeft':'IndicatorRight';
    bar(indicator,side*.77,.85,-2.18,.18,.064,.19);
    bar(indicator,side*.80,.81,2.14,.11,.042,.18);
    bar('Headlamp',side*.62,.81,2.21,.39,.053,.12);
    if(level<2){
      bar('Trim',side*.90,.46,-.02,.09,.10,2.21);
      bar('Trim',side*.808,1.25,-.21,.059,.47,.10);
      part('Paint',new T.SphereGeometry(1,12,6).scale(.135,.065,.105),side*.96,1.09,.72);
      if(level===0)for(const z of [-.64,.58])bar('Alloy',side*.916,.90,z,.032,.033,.16);
    }
    for(const front of [false,true]){
      const pivot=new T.Group(),wheel=new T.Group();pivot.name=(front?'Front':'Rear')+(side===1?'Left':'Right')+'_'+level;
      pivot.position.set(side*.845,.34,front?1.42:-1.39);pivot.add(wheel);root.add(pivot);
      const radial=[24,16,8][level];
      function disk(mat,r,width,x){
        const mesh=new T.Mesh(new T.CylinderGeometry(r,r,width,radial).rotateZ(Math.PI/2),materials[mat]);
        mesh.position.x=x;wheel.add(mesh);
      }
      disk('Trim',.34,.22,0);disk('Alloy',.234,.012,side*.112);
      if(level<2){
        disk('Trim',.195,.014,side*.119);
        const spokes=[];for(let i=0;i<(level===0?8:5);i++){
          const a=i*2*Math.PI/(level===0?8:5);spokes.push(new T.BoxGeometry(.016,.18,.035).translate(0,.095,0).rotateX(a));
        }
        const mesh=new T.Mesh(mergeGeometries(spokes),materials.Alloy);mesh.position.x=side*.13;wheel.add(mesh);
      }
    }
  }
  if(level<2){bar('Trim',0,.47,2.291,1.22,.115,.035);bar('Trim',0,.52,-2.285,.56,.13,.042);}
  for(const [key,geometries] of groups)root.add(new T.Mesh(mergeGeometries(geometries),materials[key]));
}
const glb=await new GLTFExporter().parseAsync(scene,{binary:true});
await writeFile(new URL('../assets/ego-cuv-v1.glb',import.meta.url),new Uint8Array(glb));
