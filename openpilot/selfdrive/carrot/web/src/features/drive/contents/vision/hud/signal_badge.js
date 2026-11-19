import {el} from './dom.js';
import {SIGNAL_GLYPHS} from '../signal_history.js';

export function describeSignal(head,text,reader){
  const lamps=(head.signalState||[]).map(l=>({
    color:l.color,label:SIGNAL_GLYPHS[l.shape]+' '+text('signal_'+l.color,l.color)
  }));
  const label=lamps.length?lamps.map(l=>l.label).join(' · '):
    text(reader==='unavailable'?'signal_unavailable':'scene_kind_traffic_light','Traffic light (state unknown)');
  return {lamps,label};
}

export function signalBadge(doc,{lamps,label}){
  const badge=el(doc,'span',{class:'tesla-image-object signal-observation',attrs:{'aria-label':label}});
  badge.dataset.kind='signal';badge.dataset.classification='traffic light';
  for(const lamp of lamps){
    const chip=el(doc,'span',{class:'signal-lamp',text:lamp.label});
    chip.dataset.color=lamp.color;badge.appendChild(chip);
  }
  if(!lamps.length)badge.appendChild(el(doc,'span',{text:label}));
  return badge;
}
