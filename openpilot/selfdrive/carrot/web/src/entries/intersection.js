import {createDrivingScene3D} from '../features/drive/contents/vision/hud/scene_3d.js';
import {paintedVehicle} from '../features/cockpit/vehicle_paint.js';
import {VEHICLE_SKINS} from '../features/cockpit/vehicle.js';
import {createObjectTracker} from '../features/drive/contents/vision/hud/object_tracker.js';
import {intersectionSignals} from '../features/cockpit/intersection_signals.js';
const signals=intersectionSignals(document);
const stage=document.querySelector('main'),scene=createDrivingScene3D(document,window,{scenery:signals.group});
stage.append(scene.canvas);
const x=[0,2,4,8,12,14,15,16,18,20,23,25,27,29,30,33,40,50,65,82];
const widening=[0,0,0,0,0,.2,1,3,18,18,18,15,3,.7,.2,0,0,0,0,0];
const path=(offset,edge=0)=>({x,y:x.map((v,i)=>offset+(edge?widening[i]*edge:0))});
const lane=(y)=>({x:[0,5,12,15,NaN,30,35,42,55,80],y:Array(10).fill(y)});
const model={roadEdges:[path(-6.8,-1),path(6.5,1)],laneLines:[lane(-5.2),lane(-1.95),lane(1.9),lane(5.35)],laneLineProbs:[.9,.98,.97,.85]};
const skin=paintedVehicle(VEHICLE_SKINS.generic,'white');

let yaw=0, distance=9,night=false,t=0,previous=performance.now(),moving=true;
const tracker=createObjectTracker(),motion={speed:0,yaw:0};
let last=-600;
function observe(s){
  const observations=[];
  const car=(x,y,h)=>observations.push({kind:'car',x,y,heading:h,probability:.96});
  car(7,-3.5,Math.PI);
  car(46,-3.3,Math.PI);
  // Waiting traffic belongs only to the explicitly labelled intersection demo.
  for(const [x,y] of [[3.4,3.65],[11.5,3.65],[34,1.0],[42,1.0],[50,1.0],[38,4.5],[46,4.5]])car(x,y,0);
  for(let n=-1;n<=Math.ceil(s/9)+1;n++){
    const u=s-n*9;
    const crossY=.7+4.4*u;
    if(Math.abs(crossY)<=19)car(22,crossY,Math.PI/2);
    const opposite=13-4.8*u;
    if(Math.abs(opposite)<=19)car(28,opposite,-Math.PI/2);
  }
  for(let n=-1;n<=Math.ceil(s/17)+1;n++){
    const u=s+1.45-n*17, radius=4.5, rate=.72, angle=Math.min(Math.PI/2,Math.max(0,u*rate));
    const x=14+radius*(1-Math.cos(angle))+Math.max(0,u-Math.PI/(2*rate))*radius*rate;
    const y=-3.8+radius*Math.sin(angle)+Math.min(0,u)*radius*rate;
    if(Math.abs(y)<19&&x<66)car(x,y,Math.PI/2-angle);
  }
  const foot=-6+(((s+3)%15+15)%15)*.75;
  if(foot<5)observations.push({kind:'person',x:32,y:foot,heading:Math.PI/2,probability:.94});
  return observations;
}
function tracksAt(ms){
  while(last+200<=ms){last+=200;tracker.ingest('vision',{stamp:last,objects:observe(last/1000)},last,motion);}
  return tracker.sample(ms,motion);
}
function draw(now){
  const w=stage.clientWidth,h=stage.clientHeight;
  if(moving&&!document.hidden)t+=Math.min(.20,(now-previous)/1000);previous=now;
  signals.update(t);
  const tracks=tracksAt(t*1000);
  scene.render(w,h,{model,tracks,paint:[11,24,10,11]},{skin,night,view:{yaw,pitch:25,distance}});
  const stats=scene.snapshot();if(stats.backend==='canvas-fallback')stage.setAttribute('aria-label','此裝置無法開啟 3D 顯示');
  stage.dataset.ready=stats.backend;stage.dataset.ego=stats.egoModel;stage.dataset.library=stats.modelLibrary;stage.dataset.lod=JSON.stringify(stats.lodCounts);frame=requestAnimationFrame(draw);
}
let frame=0;
window.addEventListener('pagehide',event=>{cancelAnimationFrame(frame);if(!event.persisted){scene.destroy();signals.dispose();}});
window.addEventListener('pageshow',event=>{if(event.persisted){previous=performance.now();frame=requestAnimationFrame(draw);}});
let touch=null;stage.onpointerdown=e=>{touch=e.clientX;stage.setPointerCapture(e.pointerId);};
stage.onpointermove=e=>{if(touch!==null){yaw+=(e.clientX-touch)*.25;touch=e.clientX;}};
stage.onpointerup=stage.onpointercancel=()=>{touch=null;};
document.querySelector('#mode').onclick=e=>{night=!night;e.target.textContent=night?'切換日間':'切換夜間';};
document.querySelector('#play').onclick=e=>{moving=!moving;e.target.textContent=moving?'暫停':'播放';};
stage.onwheel=e=>{e.preventDefault();distance=Math.max(6,Math.min(24,distance*Math.exp(e.deltaY*.002)));};
document.querySelector('#play').textContent=moving?'暫停':'播放';
document.querySelector('#reset').onclick=()=>{yaw=0;distance=9;};
frame=requestAnimationFrame(draw);
