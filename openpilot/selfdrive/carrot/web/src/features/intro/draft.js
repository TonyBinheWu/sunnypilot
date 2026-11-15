export function setupBody(ctx) {
  return {revision:ctx.baseline.revision,lang:ctx.lang,car:ctx.car,hda:ctx.hda,preset:ctx.preset};
}
export function setupChanges(ctx) {
  const before=ctx.baseline,desired={CarSelected3:ctx.car};
  if(ctx.hda!==null)desired.CanfdHDA2=ctx.hda;
  if(ctx.preset)Object.assign(desired,before.presets[ctx.preset]);
  const rows=Object.entries(desired).filter(([key,value])=>String(before.values[key]??'')!==String(value))
    .map(([key,value])=>({key,title:before.titles?.[key]?.[ctx.lang]||key,before:before.values[key],after:value}));
  if(ctx.lang!==before.lang)rows.push({key:'web_language',title:'web_language',before:before.lang||'auto',after:ctx.lang});
  return rows;
}
