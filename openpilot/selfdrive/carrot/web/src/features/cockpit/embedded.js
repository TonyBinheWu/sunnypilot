const installed=new WeakSet();
// Reuse the actual setting controls and their guards. Only disclose their
// existing full description on demand; never duplicate setters or omit text.
export function installCockpitHelp(doc){
  if(installed.has(doc)||!doc.defaultView?.MutationObserver)return;
  installed.add(doc);
  const wrap=()=>{
    const heading=doc.getElementById?.('itemsTitle');if(heading?.textContent==='項')heading.textContent='控制與設定';
    for(const description of doc.querySelectorAll('.setting .descr')){
      if(description.closest('.cockpit-help'))continue;
      const details=doc.createElement('details'),summary=doc.createElement('summary');
      details.className='cockpit-help';summary.textContent='功能說明';
      // The regular setting row also opens a context panel on click. Keep the
      // native details toggle from launching that second operation.
      summary.addEventListener?.('click',event=>event.stopPropagation());
      description.before(details);details.append(summary,description);
    }
  };
  new doc.defaultView.MutationObserver(wrap).observe(doc.body,{childList:true,subtree:true});
  wrap();
}
