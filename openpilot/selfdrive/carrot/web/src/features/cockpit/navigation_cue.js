export function navigationCue(nav, age){
  if(!nav || nav._sourceInvalid || !Number.isFinite(age) || age<0 || age>=2000 ||
     !(nav.nGoPosDist>0 && nav.xTurnInfo>0 && Number.isFinite(nav.xDistToTurn) && nav.xDistToTurn>=0)) return '';
  const arrow=({1:'←',2:'→',3:'↖',4:'↗',5:'⟳'})[nav.xTurnInfo]||'';
  const distance=nav.xDistToTurn<1000 ? nav.xDistToTurn+' m' : (nav.xDistToTurn/1000).toFixed(1)+' km';
  return [arrow,nav.szTBTMainText,distance].filter(Boolean).join(' ');
}
