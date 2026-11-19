import test from 'node:test';
import assert from 'node:assert/strict';
import {observedLamps} from '../src/features/drive/contents/vision/signal_lamps.js';
import {createSignalHistory} from '../src/features/drive/contents/vision/signal_history.js';

const colors={red:[236,13,18],yellow:[242,182,28],green:[16,233,87]};
const rgb=(color,shape='color')=>({color,shape});
function picture(bulbs,{width=144,height=45,background=16}={}){
  const rgba=new Uint8ClampedArray(width*height*4).fill(background);
  for(const {x,color,direction} of bulbs){
    for(let y=0;y<height;y++)for(let j=0;j<width;j++){
      const dx=j-x,dy=y-(height-1)/2;
      let lit=Math.hypot(dx,dy)<10;
      if(direction){
        const rot={left:Math.PI/2,right:-Math.PI/2,up:0,down:Math.PI}[direction];
        const u=dx*Math.cos(rot)-dy*Math.sin(rot),v=dx*Math.sin(rot)+dy*Math.cos(rot);
        lit=(Math.abs(u)<=2&&v>=-10&&v<=13)||(Math.abs(v+12-Math.abs(u))<2.4&&Math.abs(u)<12&&v<=1);
      }
      if(lit)rgba.set(colors[color],(y*width+j)*4);
    }
  }
  return observedLamps(rgba,width,height);
}
for(const color of Object.keys(colors)){
  test('read illuminated '+color+' from actual crop pixels',()=>{
    assert.deepEqual(picture([{x:68,color}]),[rgb(color)]);
  });
}
for(const dir of ['left','right','up','down']){
  test('red and a simultaneous green '+dir+' arrow retain their independent meanings',()=>{
    assert.deepEqual(picture([{x:20,color:'red'},{x:108,color:'green',direction:dir}]),
      [rgb('red'),rgb('green',dir)]);
  });
}
test('two green arrows on one head remain independent',()=>{
  assert.deepEqual(picture([{x:66,color:'green',direction:'up'},{x:112,color:'green',direction:'right'}]),
    [rgb('green','up'),rgb('green','right')]);
});
test('blank, glare, clipped lamps, three-colored reflections and tiny crops abstain',()=>{
  assert.deepEqual(picture([]),[]);assert.deepEqual(picture([],{background:249}),[]);
  assert.deepEqual(picture([{x:0,color:'red'}]),[]);
  assert.deepEqual(picture([{x:20,color:'red'},{x:68,color:'yellow'},{x:113,color:'green'}]),[]);
  assert.deepEqual(picture([{x:3,color:'red'}],{width:7,height:5}),[]);
});
const left=[.05,.12,.11,.09],right=[.42,.12,.11,.09];
const head=(box,color)=>({box,lamps:color?[rgb(color)]:[]});
test('confirm per physical head, reorder, and withdraw old green on the first changed frame',()=>{
  const h=createSignalHistory();
  assert.deepEqual(h.confirm([head(left,'green'),head(right,'red')],0),[null,null]);
  assert.deepEqual(h.confirm([head(right,'red'),head(left,'green')],300),[[rgb('red')],[rgb('green')]]);
  assert.deepEqual(h.confirm([head(left,'yellow'),head(right,null)],600),[null,null]);
  assert.deepEqual(h.confirm([head(left,'yellow')],900),[[rgb('yellow')]]);
  assert.deepEqual(h.confirm([],950),[]);
  assert.deepEqual(h.confirm([head(left,'yellow')],1000),[null]);
});
test('ambiguous matches, repeat timestamps, stream resets and old evidence cannot confirm a lamp',()=>{
  const h=createSignalHistory();
  h.confirm([head(left,'red')],200);
  assert.deepEqual(h.confirm([head(left,'red')],200),[null]);
  assert.deepEqual(h.confirm([head(left,'red'),head(left,'red')],500),[null,null]);
  assert.deepEqual(h.confirm([head(left,'red')],750),[null]);
  assert.deepEqual(h.confirm([head(left,'red')],2000),[null]);
  h.clear();assert.deepEqual(h.confirm([head(left,'red')],2250),[null]);
});

test('local contrast recovers a shaded lens but two contradictory circles abstain',()=>{
  const w=96,h=44,pixels=new Uint8ClampedArray(w*h*4).fill(212);
  for(let y=12;y<=32;y++)for(let x=13;x<=70;x++){
    const lit=(x-30)**2+(y-22)**2<=36;
    pixels.set(lit?[33,89,54]:[57,55,53],4*(y*w+x));
  }
  assert.deepEqual(observedLamps(pixels,w,h),[rgb('green')]);
  assert.deepEqual(picture([{x:20,color:'red'},{x:112,color:'green'}]),[]);
});
