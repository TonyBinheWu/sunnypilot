export function themePreference(storage){try{const v=storage?.getItem('formosalink-theme');return ['light','dark','system'].includes(v)?v:'system';}catch{return 'system';}}
export function initTheme(t){
 let storage;try{storage=localStorage;}catch{}let mode=themePreference(storage);const system=matchMedia('(prefers-color-scheme: dark)');
 function apply(){document.documentElement.dataset.theme=mode==='system'?(system.matches?'dark':'light'):mode;for(const b of document.querySelectorAll('[data-theme-toggle]')){b.textContent=t('theme_'+mode);b.title=t('themeHelp');b.setAttribute('aria-label',t('themeHelp')+' · '+t('theme_'+mode));}}
 document.querySelectorAll('[data-theme-toggle]').forEach(b=>b.addEventListener('click',()=>{mode=mode==='system'?'light':mode==='light'?'dark':'system';try{localStorage.setItem('formosalink-theme',mode);}catch{}apply();}));
 system.addEventListener('change',apply);addEventListener('storage',event=>{if(event.key==='formosalink-theme'){mode=themePreference(storage);apply();}});apply();return apply;
}
