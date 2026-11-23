// ===== ui: camera, one tooltip, selection card, relations panel, levels =====
const tip=document.getElementById('tip'),card=document.getElementById('card'),relEl=document.getElementById('rel');
const HINT={realizes:'ontology: a capability realizes a goal; a workflow realizes a capability',for:'ontology: a goal is for actors',actor:'ontology: the actor of a step',calls:'ontology: a step calls a workflow; the callee runs whole, then the caller carries on by cases',covers_ends:'ontology: a case of the calling step covers ends of the callee',event:'ontology: a transition of an entity starts the workflow',shows:'ontology: an interface shows an entity'};
const OPWORD={create:'creates the thing',write:'writes fields of the thing',delete:'deletes the thing',tell:'tells an actor',transition:'moves the thing to another state'};
const entryHtml=(id,{rows=true,pinned=false}={})=>{const n=N[id];if(!n)return'';const c=kindColor(n);
 let h=`<div class="hh"><span class="hi" style="background:${c}"><svg viewBox="0 0 16 16" class="ic" style="color:#fff">${ICON[kindIcon(n)]}</svg></span><span class="ht">${esc(title(n))}</span><span class="hk" style="color:${c}">${esc(n.kind)}</span></div>`;
 if(n.says)h+=`<p class="says">${esc(n.says)}</p>`;
 if(!n.title&&pinned)h+=`<p class="hint">Hint: every kind takes a title in the ontology; this entry has none yet, so its key is shown humanized.</p>`;
 if(rows){const sec=(w,ids)=>{ids=[...new Set(ids)].filter(i=>N[i]);return ids.length?`<div class="sec"><label>${esc(w)}</label><div class="chs">${ids.map(mnHtml).join('')}</div></div>`:''};
  const b=blockOf(id)===id;
  if(n.kind==='goal')h+=sec('for',to(id,'for'))+sec('← realizes',from(id,'realizes'));
  if(n.kind==='capability')h+=sec('realizes',to(id,'realizes'))+sec('← realizes',from(id,'realizes'));
  if(n.kind==='actor')h+=sec('← for',from(id,'for'))+sec('← actor',from(id,'actor').map(s=>wfOf(N[s])?.id));
  if(n.kind==='workflow')h+=sec('realizes',to(id,'realizes'))+sec('calls',kidsOf(id,['step']).flatMap(s=>to(s.id,'calls')))+sec('← calls',from(id,'calls').map(s=>wfOf(N[s])?.id))+sec('event',to(id,'event'));
  if(n.kind==='entity')h+=sec('fields',kidsOf(id,['attribute']).map(a=>a.id))+sec('states',kidsOf(id,['state']).map(a=>a.id))+sec('transitions',kidsOf(id,['transition']).map(a=>a.id));
  if(n.kind==='transition'){h+=sec('from',to(id,'from'))+sec('to',to(id,'to'));const f=D.nodes.filter(x=>(x.fx||[]).some(f=>f.onid===id)).map(x=>wfOf(x)?.id);h+=f.length?sec('← transition',f):'<p class="hint">No effect fires this transition.</p>'}}
 return h}
const bundleHtml=u=>`<div class="hh"><span class="ht">${esc(u.label)}</span><span class="hk">${u.cls==='effect'?'effect':'relation'}</span></div><div class="sec"><div class="chs">${mnHtml(u.a)}<span class="ar">→</span>${mnHtml(u.b)}</div></div>`+u.items.map(i=>`<div class="it">${mnHtml(i.s)}<span class="fw">${esc(fieldWord(i.f))}</span>${mnHtml(i.t)}</div>`).join('')+`<p class="hint">${esc(u.items[0].f in HINT?HINT[u.items[0].f]:(OPWORD[u.items[0].f]?'ontology effect: '+OPWORD[u.items[0].f]:''))}</p>`;
function showTip(html,e){tip.innerHTML=html;tip.style.display='block';const r=tip.getBoundingClientRect();let x=e.clientX+16,y=e.clientY+16;if(x+r.width>innerWidth-8)x=e.clientX-r.width-16;if(y+r.height>innerHeight-8)y=Math.max(8,innerHeight-r.height-8);tip.style.left=x+'px';tip.style.top=y+'px'}
const hideTip=()=>{tip.style.display='none'};
stage.addEventListener('mousemove',e=>{if(pan&&pan.moved){hideTip();return}
 const t=e.target;let h='';
 const call=t.closest?.('.call');const bd=t.closest?.('[data-bd]');const en=t.closest?.('[data-entry]');const bg=t.closest?.('.badge');
 if(call&&!t.closest?.('[data-entry]'))h=`<div class="hh"><span class="ht">calls</span><span class="hk">step</span></div><p>The callee runs whole, then this step carries on by the cases below, one for each end of the callee (ontology: calls, then covers ends).</p>`;
 else if(bg)h=`<div class="hh"><span class="ht">${esc(OPWORD[bg.dataset.op]||bg.dataset.op)}</span><span class="hk">effect</span></div><div class="sec"><div class="chs">${mnHtml(bg.dataset.target)}</div></div>`;
 else if(en)h=entryHtml(en.dataset.entry);
 else if(bd){const u=bundles.find(x=>x.id===bd.dataset.bd);if(u)h=bundleHtml(u)}
 if(h)showTip(h,e);else hideTip()});
stage.addEventListener('mouseleave',hideTip);
// ---- selection ----
function select(id,bdId){sel=id||null;selBd=bdId||null;draw();showCard()}
function showCard(){if(selBd){const u=bundles.find(x=>x.id===selBd);card.innerHTML='<button class="close">×</button>'+(u?bundleHtml(u):'');card.style.display='block'}
 else if(sel){card.innerHTML='<button class="close">×</button>'+entryHtml(sel,{pinned:true})+blockRelHtml(sel);card.style.display='block'}else card.style.display='none'}
function blockRelHtml(id){const us=bundles.filter(u=>u.a===id||u.b===id);if(!us.length)return'';return '<div class="sec"><label>relations</label>'+us.map(u=>`<div class="it" data-bdgo="${u.id}">${mnHtml(u.a)}<span class="fw">${esc(u.label)}</span>${mnHtml(u.b)}</div>`).join('')+'</div>'}
card.addEventListener('click',e=>{if(e.target.closest('.close')){select(null);return}const g=e.target.closest('[data-goto]');if(g){goBlock(g.dataset.goto);return}const r=e.target.closest('[data-bdgo]');if(r)focusBundle(r.dataset.bdgo)});
function goBlock(id){const bid=blockOf(id)||id;if(!B[bid])return;const b=B[bid];select(bid);const w=stage.clientWidth,h=stage.clientHeight;const s=Math.max(scale,Math.min(1.0,(h-160)/b.h));const ns=Math.min(3,Math.max(scale,Math.min(w*0.8/b.w,(h-140)/b.h)));scale=Math.min(ns,1.6);tx=w/2-(b.x+b.w/2)*scale;ty=h/2+30-(b.y+b.h/2)*scale;draw()}
function focusBundle(id){const u=bundles.find(x=>x.id===id);if(!u)return;sel=null;selBd=id;fitTo([B[u.a],B[u.b]],120);draw();showCard()}
// ---- relations panel (lab 29 idea): every relation, grouped by the ontology's own word ----
function relPanel(){const facts=[];for(const u of bundles)for(const i of u.items)facts.push({u,i});const by={};for(const f of facts)(by[f.u.cls==='effect'?fieldWord(f.i.f):fieldWord(f.i.f)]??=[]).push(f);
 const open=relEl.querySelector('details')?.open;
 relEl.innerHTML=`<details${open?' open':''}><summary>Relations · ${facts.length}</summary><div class="rb">`+Object.entries(by).sort().map(([w,l])=>`<div class="rg"><label>${esc(w)} · ${l.length}</label>`+l.map(f=>`<div class="it" data-bdgo="${f.u.id}">${mnHtml(f.i.s)}<span class="fw">${esc(w)}</span>${mnHtml(f.i.t)}</div>`).join('')+'</div>').join('')+'</div></details>'}
relEl.addEventListener('click',e=>{const g=e.target.closest('[data-goto]');const r=e.target.closest('[data-bdgo]');if(g&&!e.target.closest('summary')){goBlock(g.dataset.goto);return}if(r)focusBundle(r.dataset.bdgo)});
// ---- levels ----
const REP={map:0.5,flow:1.0,detail:1.7};
function lvUi(){const lv=levelOf(scale);for(const b of document.querySelectorAll('[data-lv]'))b.classList.toggle('on',b.dataset.lv===lv);document.getElementById('zoom').textContent=Math.round(scale*100)+'%'}
function setLevel(l){const w=stage.clientWidth,h=stage.clientHeight;const cx=sel&&B[sel]?B[sel].x+B[sel].w/2:(w/2-tx)/scale,cy=sel&&B[sel]?B[sel].y+B[sel].h/2:(h/2-ty)/scale;scale=REP[l];tx=w/2-cx*scale;ty=h/2-cy*scale;draw()}
document.getElementById('top').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;if(b.dataset.lv)setLevel(b.dataset.lv);if(b.id==='fit'){fitTo(blocks);draw()}if(b.id==='helpb')document.getElementById('help').style.display='flex'});
// ---- input: drag pans, wheel and pinch zoom, click selects ----
let pan=null;
stage.addEventListener('mousedown',e=>{if(e.button!==0&&e.button!==1)return;pan={x:e.clientX,y:e.clientY,tx,ty,moved:false,target:e.target};if(e.button===1)e.preventDefault()});
addEventListener('mousemove',e=>{if(!pan)return;const dx=e.clientX-pan.x,dy=e.clientY-pan.y;if(!pan.moved&&Math.hypot(dx,dy)>4){pan.moved=true;stage.classList.add('pan')}if(pan.moved){tx=pan.tx+dx;ty=pan.ty+dy;apply()}});
addEventListener('mouseup',e=>{stage.classList.remove('pan');if(!pan)return;const p=pan;pan=null;if(p.moved)return;
 const t=p.target;const g=t.closest?.('[data-goto]');if(g){goBlock(g.dataset.goto);return}
 const eg=t.closest?.('[data-bd]');if(eg){const u=bundles.find(x=>x.id===eg.dataset.bd);if(u)focusBundle(u.id);return}
 const bl=t.closest?.('.blk');if(bl)select(bl.dataset.id);else select(null)});
stage.addEventListener('wheel',e=>{e.preventDefault();hideTip();const r=stage.getBoundingClientRect();if(e.shiftKey&&!e.ctrlKey){tx-=e.deltaY||e.deltaX;apply();return}
 zoomAt(scale*Math.exp(-e.deltaY*(e.ctrlKey?0.012:0.0016)),e.clientX-r.left,e.clientY-r.top);redraw()},{passive:false});
addEventListener('keydown',e=>{if(e.key==='Escape'){select(null);document.getElementById('help').style.display='none'}if(e.key==='0'||e.key==='f'){fitTo(blocks);draw()}});
addEventListener('resize',()=>{fitTo(blocks);draw()});
document.getElementById('help').addEventListener('click',()=>{document.getElementById('help').style.display='none'});
// ---- boot ----
layoutWorld();routeAll();relPanel();fitTo(blocks);draw();
window.LAB={get scale(){return scale},get tx(){return tx},get ty(){return ty},get level(){return levelOf(scale)},blocks,bundles,B,scr,N,select,setScale(s,wx,wy){const w=stage.clientWidth,h=stage.clientHeight;scale=s;tx=w/2-wx*s;ty=h/2-wy*s;draw()},fit(){fitTo(blocks);draw()},focus:goBlock,get sel(){return sel},draw};
