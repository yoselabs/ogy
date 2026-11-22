export const OVERLAP = String.raw`(()=>{const BLOCK="[data-local-id]";            // the build's top-level node selector
const EDGE="#vp path, #vp polyline, #vp line";  // the build's edge layer; must not match icons
const R=e=>e.getBoundingClientRect();
const vis=r=>r.width>2&&r.height>2&&r.right>0&&r.bottom>0&&r.left<innerWidth&&r.top<innerHeight;
const hit=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>2&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2;
const blocks=[...document.querySelectorAll(BLOCK)].filter(e=>!e.parentElement.closest(BLOCK)).map(e=>[e,R(e)]).filter(x=>vis(x[1]));
let bb=0;for(let i=0;i<blocks.length;i++)for(let j=i+1;j<blocks.length;j++){if(hit(blocks[i][1],blocks[j][1]))bb++}
const texts=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
for(let n;(n=w.nextNode());){if(!n.nodeValue.trim()||!n.parentElement.closest(BLOCK))continue;const g=document.createRange();g.selectNodeContents(n);for(const r of g.getClientRects())if(vis(r))texts.push(r)}
const edges=[...document.querySelectorAll(EDGE)].filter(p=>!p.closest(BLOCK)&&!p.closest("defs")&&!p.closest("svg svg"));
const pts=[];for(const p of edges){const L=p.getTotalLength?p.getTotalLength():0;if(!L)continue;const m=p.getScreenCTM();
 for(let d=0;d<=L;d+=3){const q=p.getPointAtLength(d);pts.push([q.x*m.a+q.y*m.c+m.e,q.x*m.b+q.y*m.d+m.f])}}
let rt=0;for(const t of texts){if(pts.some(s=>s[0]>t.left&&s[0]<t.right&&s[1]>t.top+1&&s[1]<t.bottom-1))rt++}
let rb=0;for(const b of blocks){const r=b[1];if(pts.some(s=>s[0]>r.left+6&&s[0]<r.right-6&&s[1]>r.top+6&&s[1]<r.bottom-6))rb++}
const labels=[...document.querySelectorAll(".route-label")].map(R).filter(vis);
let lb=0;for(const l of labels)if(blocks.some(b=>hit(l,b[1])))lb++;
return "blocks="+blocks.length+" edges="+edges.length+" blockOverlaps="+bb+" textRunsCrossedByEdge="+rt+"/"+texts.length+" blocksEnteredByEdge="+rb+"/"+blocks.length+" labelsOnBlocks="+lb+"/"+labels.length})()`;

export const TEXT = `(() => {
  const sizes = [...document.querySelectorAll('body, body *')]
    .filter(e => [...e.childNodes].some(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim()))
    .filter(e => !e.closest('script, style, template'))
    .map(e => parseFloat(getComputedStyle(e).fontSize));
  return { min: sizes.length ? Math.min(...sizes) : null,
    max: sizes.length ? Math.max(...sizes) : null, distinct: new Set(sizes).size };
})()`;

export const VIEWER_WORDS = `(() => {
  const clone = document.body.cloneNode(true);
  clone.querySelectorAll('[data-authored]').forEach(e => e.remove());
  return clone.innerText;
})()`;
