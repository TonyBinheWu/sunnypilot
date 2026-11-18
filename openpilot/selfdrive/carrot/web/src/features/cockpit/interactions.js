// Keep original dialog forms and their cancellation/confirmation handlers.
export function installCockpitDialogHeaders(doc){
  for(const dialog of doc.querySelectorAll('dialog')){
    if(dialog.querySelector('.cockpit-dialog-head'))continue;
    const title=dialog.querySelector('h2'),form=dialog.querySelector('form[method="dialog"]');
    if(!title||!form)continue;
    title.id ||= `${dialog.id}Title`;
    dialog.setAttribute('aria-labelledby',title.id);
    const head=doc.createElement('header');head.className='cockpit-dialog-head';
    head.append(title,form);dialog.prepend(head);
  }
}

export function closeEmbeddedDialog(target){
  const doc=target?.document;if(!doc)return false;
  const app=doc.getElementById('appDialog');
  if(app&&!app.hidden){
    const cancel=doc.getElementById('appDialogCancel');
    // A pending operation owns its cancellation. Never turn Back into confirm.
    if(cancel&&!cancel.disabled)cancel.click();
    return true;
  }
  const dialog=doc.querySelector('dialog[open]');
  if(!dialog)return false;
  const event=new target.Event('cancel',{cancelable:true});
  if(dialog.dispatchEvent(event)&&dialog.open)dialog.close();
  return true;
}
