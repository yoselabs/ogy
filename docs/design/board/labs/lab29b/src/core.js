// ===== core: names, icons, one identity renderer =====
// ONE thing has ONE name and ONE style. Every mention of an entry (board, panel, card, badge) goes through mnSvg/mnHtml.
// Names: the entry's `title` when the ontology has one (every kind takes `title`), else the key humanized. Never raw keys.
const MONO='ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', SANS='system-ui, sans-serif';
const cv=document.createElement('canvas').getContext('2d');
Object.assign(ICON,{plus:'<path d="M8 3v10M3 8h10"/>',pen:'<path d="M3 13l.7-3L11 2.7 13.3 5 6 12.3z"/>',bin:'<path d="M3.5 4.5h9M6 4.5V3h4v1.5M4.5 4.5l.6 9h5.8l.6-9"/>',send:'<path d="M2 8l12-5.5-4.5 11-2-4.5z"/>',arrow:'<path d="M2.5 8h10M9 4.5L12.5 8 9 11.5"/>',back:'<path d="M13.5 8h-10M7 4.5L3.5 8 7 11.5"/>',start:'<circle cx="8" cy="8" r="3.4" fill="currentColor"/>',warn:'<path d="M8 2L14.5 13.5h-13zM8 6.5v3M8 11.6h.01"/>'});
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const human=k=>{const t=String(k??'');return t.replace(/[-_]/g,' ').replace(/^./,c=>c.toUpperCase())};
const cap=s=>{s=String(s);return /^[a-z]/.test(s)?s[0].toUpperCase()+s.slice(1):s};
const PAL=['#e8590c','#2f9e44','#1c7ed6','#c2255c','#7048e8','#d9480f','#0ca678'];
// kind -> icon, colour, word. The kind word is the ontology's own word (lowercase), drawn small in the corner.
const KC={goal:'#806900',capability:'#a65300',workflow:'#7048b8',entity:'#1d4f7a',actor:'#9c3675',step:'#526783',end:'#2f7d4a',state:'#1d4f7a',transition:'#7048b8',attribute:'#526783',case:'#526783',choice:'#526783',timeout:'#6a4f00',interface:'#3b5b8c',handler:'#526783',quantity:'#526783',enum:'#8a5a00',dependency:'#526783',setting:'#526783'};
const KI={workflow:'call',entity:'doc',goal:'goal',capability:'cap',step:'gear',state:'tag',transition:'swap',attribute:'doc',case:'gate',choice:'gate',timeout:'timer',interface:'web',handler:'gear',quantity:'hash',enum:'list',dependency:'plug',setting:'gear',end:'ok',rule:'list'};
function kindIcon(n){if(n.kind==='actor')return n.nature==='ai'?'ai':n.nature==='program'?'robot':'person';if(n.kind==='end')return n.result==='failure'?'no':'ok';if(n.kind==='interface')return FORMIC[n.form]||'web';return KI[n.kind]||'doc'}
const kindColor=n=>n.kind==='end'?(n.result==='failure'?'#c92a2a':'#2f7d4a'):(KC[n.kind]||'#526783');
const title=n=>n.title||human(n.key);
// ---- text measure (screen px) ----
function tw(t,px,wt=500,mono=false){cv.font=`${wt} ${px}px ${mono?MONO:SANS}`;return cv.measureText(t).width}
function lines(text,width,px=11,wt=400,mono=false){cv.font=`${wt} ${px}px ${mono?MONO:SANS}`;const out=[];
 for(const para of String(text).split('\n')){let cur='';for(let w of para.split(/\s+/).filter(Boolean)){
  while(cv.measureText(w).width>width&&w.length>1){let k=w.length-1;while(k>1&&cv.measureText(w.slice(0,k)).width>width)k--;if(cur){out.push(cur);cur=''}out.push(w.slice(0,k));w=w.slice(k)}
  const t=cur?cur+' '+w:w;if(cv.measureText(t).width>width&&cur){out.push(cur);cur=w}else cur=t}out.push(cur)}return out.length?out:['']}
// ---- the identity renderer ----
// SVG: a link-looking name with its kind icon. Width is known before drawing so callers can place or drop it; it is never truncated.
const mnW=(id,px=11)=>{const n=N[id];return n?Math.ceil(tw(title(n),px,600))+px+6:0};
function mnSvg(id,x,y,{px=11,color}={}){const n=N[id];if(!n)return'';const c=color||kindColor(n);
 return `<g class="mn k-${n.kind}" data-entry="${esc(id)}" data-goto="${esc(id)}">${ic(kindIcon(n),x,y,px+1,c)}<text class="mt" x="${x+px+5}" y="${y+px-0.5}" style="font-size:${px}px;fill:${c}">${esc(title(n))}</text></g>`}
function mnHtml(id){const n=N[id];if(!n)return'';const c=kindColor(n);
 return `<span class="mn k-${n.kind}" data-entry="${esc(id)}" data-goto="${esc(id)}" style="color:${c}"><svg viewBox="0 0 16 16" class="ic" style="color:${c}">${ICON[kindIcon(n)]}</svg><span class="mt">${esc(title(n))}</span></span>`}
// ontology field words (the only relation words on the board). Underscores read as spaces; nothing is invented.
const FIELD={realizes:'realizes',for:'for',actor:'actor',calls:'calls',covers_ends:'covers ends',event:'event',schedule:'schedule',start:'start',serves:'serves',performs:'performs',offers:'offers',shows:'shows',then:'then',create:'create',write:'write',delete:'delete',tell:'tell',transition:'transition',to:'to',from:'from'};
const fieldWord=f=>FIELD[f]||String(f).replace(/_/g,' ');
