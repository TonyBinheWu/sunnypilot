export async function openSetupGuide() {
  const target=globalThis,text=(key,fallback)=>target.getUIText?.(key,fallback)||fallback;
  try{
    const response=await target.fetch('/api/intro/reconfigure',{cache:'no-store'});
    const state=await response.json();
    if(!response.ok||state.ok!==true)throw new Error(state.error||'vehicle_unavailable');
    if(typeof target.CarrotIntroShell?.open!=='function')throw new Error('unavailable');
    target.CarrotIntroShell.open({reconfigure:state});
  }catch(error){
    const message=['park_required','moving','controls_active','controls_unavailable','vehicle_unavailable'].includes(error.message)
      ?text('setup_again_park','Park and disengage, or switch off the vehicle, then try again. Fresh device state is required.')
      :text('setup_again_unavailable','Could not open setup. Update the vehicle and reopen this page.');
    await target.appAlert?.(message,{title:text('setup_again_title','Run setup again')});
  }
}
