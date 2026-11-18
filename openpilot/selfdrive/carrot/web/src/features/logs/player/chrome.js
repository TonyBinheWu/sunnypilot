// One idle timer owns both transport rows, avoiding competing touch timers.
export function bindPlayerChrome(frame, player) {
  let revealOnly=false,held=false,timer=null;
  const target=frame.ownerDocument?.defaultView||globalThis;
  const clear=()=>{if(timer!==null)target.clearTimeout(timer);timer=null;};
  const blocked=()=>held||player.paused||player.ended||frame.classList.contains('is-media-scrubbing')||frame.querySelector('input:focus,select:focus,[role=menu]:focus-within,.plyr__menu__container:not([hidden])');
  const hide=()=>{clear();if(!blocked())frame.classList.add('is-player-idle');};
  const arm=()=>{clear();if(!player.paused&&!player.ended)timer=target.setTimeout(()=>{timer=null;if(blocked())arm();else hide();},2000);};
  const show=()=>{frame.classList.remove('is-player-idle');arm();};
  const down=e=>{revealOnly=frame.classList.contains('is-player-idle')&&!e.target.closest('button,input,select,a');held=true;if(revealOnly){e.preventDefault?.();e.stopPropagation?.();player.toggleControls?.(true);}show();};
  const up=()=>{held=false;arm();};
  const click=e=>{if(revealOnly){revealOnly=false;e.preventDefault();e.stopImmediatePropagation();player.toggleControls?.(true);}};
  frame.addEventListener('pointerdown',down,true);frame.addEventListener('click',click,true);
  const listeners=[['pointerup',up,true],['pointercancel',up,true],['pointermove',show,false],['focusin',show,false],['focusout',arm,false]];
  for(const [name,fn,capture]of listeners)frame.addEventListener(name,fn,capture);
  const events=[['controlshidden',hide],['controlsshown',show],['play',show],['pause',show],['ended',show]];
  for(const [name,fn]of events)player.on(name,fn);
  arm();
  return ()=>{clear();frame.classList.remove('is-player-idle');frame.removeEventListener('pointerdown',down,true);frame.removeEventListener('click',click,true);for(const [name,fn,capture]of listeners)frame.removeEventListener(name,fn,capture);for(const [name,fn]of events)player.off?.(name,fn);};
}
