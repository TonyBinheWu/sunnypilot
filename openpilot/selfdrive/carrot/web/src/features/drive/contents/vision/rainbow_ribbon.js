export const RAINBOW_COLORS = Object.freeze(['#f15c66','#ffad55','#ffe773','#79e5a1','#63cafa','#a18af5','#e88cdb'].map(hex=>Object.freeze({r:parseInt(hex.slice(1,3),16),g:parseInt(hex.slice(3,5),16),b:parseInt(hex.slice(5,7),16)})));
// Feed the existing GPU polygon batch, without adding a camera overlay timer.
export function drawRainbowRibbon(geometry,ribbon,rgba) {
  if(!Array.isArray(ribbon?.left)||ribbon.left.length<2||ribbon.left.length!==ribbon.right?.length)return false;
  for(let i=0;i<RAINBOW_COLORS.length;i++){
    const polygon=geometry.buildBandPolygon(ribbon.left,ribbon.right,i/7,(i+1)/7);
    if(polygon?.length>=3)geometry.drawPolygon(polygon,rgba(RAINBOW_COLORS[i],.55),'',0);
  }
  return true;
}
