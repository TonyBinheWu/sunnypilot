export function parseCoordinates(value){
 let text=value.trim();
 try{if(/^https?:\/\//i.test(text)){const url=new URL(text);const q=url.searchParams.get('q')||url.searchParams.get('query')||url.searchParams.get('ll');const at=url.pathname.match(/@(-?[\d.]+),(-?[\d.]+)/);const osm=url.hash.match(/map=\d+\/(-?[\d.]+)\/(-?[\d.]+)/);text=q||(at?at[1]+','+at[2]:osm?osm[1]+','+osm[2]:'');}}catch{return null;}
 const m=text.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);if(!m)return null;const latitude=Number(m[1]),longitude=Number(m[2]);return Math.abs(latitude)<=90&&Math.abs(longitude)<=180?{latitude,longitude}:null;
}
