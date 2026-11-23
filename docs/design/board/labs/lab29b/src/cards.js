// ===== views: one registry of renderable views, keyed by kind and context. An entry never draws itself. =====
// context: 'map' | 'flow' | 'detail' for board blocks (screen-space, richness gated by the pixels the block has), 'mention', 'hover'.
// Text is always >= 11 screen px; what does not fit is dropped (lower priority first), never shrunk and never truncated.
const T11=11;
const gray='#6b7285',ink='#302a20';
const T=(s,x,y,{px=12,wt=400,fill=ink,anchor,ls,cls,extra=''}={})=>`<text${cls?` class="${cls}"`:''} x="${x}" y="${y}"${anchor?` text-anchor="${anchor}"`:''} style="font-size:${px}px;font-weight:${wt};fill:${fill}${ls?`;letter-spacing:${ls}`:''}" ${extra}>${esc(s)}</text>`;
const KINDWORD=k=>k;// the ontology's own kind word, lowercase
// chips that wrap; returns {svg,y} (y is the bottom). A chip is an entry id; a chip that cannot fit a whole row goes to the next row.
function chips(ids,x,y,maxX,px=T11,gap=10,rowH=17){let cx=x,cy=y,o='';for(const id of ids){const w=mnW(id,px);if(w>maxX-x)continue;if(cx>x&&cx+w>maxX){cx=x;cy+=rowH}o+=mnSvg(id,cx,cy-px+1,{px});cx+=w+gap}return{svg:o,y:cy+rowH}}
// a relation row: ontology word + direction mark, then the entries. inbound=true shows the arrow back (this entry is the object).
// The row is dropped whole when its first entry cannot fit: a name is never cut.
function relRow(word,inbound,ids,x,y,W,pad=12){ids=[...new Set(ids)].filter(id=>N[id]);if(!ids.length)return{svg:'',y};
 const lab=tw(word,T11,500)+16;const o=`<g class="rel-w">${ic(inbound?'back':'arrow',x,y-T11,T11+1,gray)}${T(word,x+T11+4,y-1,{px:T11,wt:500,fill:gray})}</g>`;
 const maxX=W-pad;const fits=ids.filter(id=>mnW(id,T11)<=maxX-x-lab-4);
 if(fits.length){const r=chips(fits,x+lab+4,y,maxX);return{svg:o+r.svg,y:Math.max(r.y,y+17)}}
 const fits2=ids.filter(id=>mnW(id,T11)<=maxX-x-8);if(!fits2.length)return{svg:'',y};
 const r=chips(fits2,x+8,y+17,maxX);return{svg:o+r.svg,y:r.y}}
function head(b,W,H,{light=false}={}){const n=b.n;const col=kindColor(n);const word=KINDWORD(n.kind);const kw=tw(word.toUpperCase(),T11,600)+(word.length)*0.6;
 const showWord=W>=170;const avail=W-14-22-(showWord?kw+16:6);const L=lines(title(n),Math.max(60,avail),14,700);const ls=L.slice(0,3);
 let o=ic(kindIcon(n),12,11,16,col)+ls.map((t,i)=>T(t,34,25+i*17,{px:14,wt:700,fill:ink})).join('');
 if(showWord)o+=T(word.toUpperCase(),W-12,22,{px:T11,wt:600,fill:col+'cc',anchor:'end',ls:'.06em',cls:'kw'});
 return{svg:o,y:12+ls.length*17+10}}
function says(text,x,y,W,H,maxLines=3,px=12){if(!text)return{svg:'',y};const L=lines(text,W-x-12,px,500);const room=Math.floor((H-y-6)/(px+4));const n=Math.min(maxLines,room,L.length);if(n<1)return{svg:'',y};
 const seg=L.slice(0,n);if(n<L.length)return{svg:'',y};// never cut a sentence: all of it or none
 return{svg:seg.map((t,i)=>T(t,x,y+i*(px+4),{px,wt:500,fill:'#3a3328'})).join(''),y:y+seg.length*(px+4)+4}}
function marker(b,W,H){const col=kindColor(b.n);return ic(kindIcon(b.n),W/2-9,H/2-9,18,col)}
// ---- goal, capability, actor: mini views by attention priority ----
function noteCard(b,W,H){const n=b.n;let o='';if(W<112||H<50)return marker(b,W,H);
 const h=head(b,W,H);o+=h.svg;let y=h.y+4;
 const sy=says(n.says,14,y+8,W,H,H>110?3:2);o+=sy.svg;if(sy.svg)y=sy.y+4;
 const room=()=>H-y-8>=17;
 const rel=(word,inb,ids)=>{if(!ids.length||!room())return;const r=relRow(word,inb,ids,14,y+13,W);if(r.y<=H-4){o+=r.svg;y=r.y+2}};
 if(n.kind==='goal'){rel('for',false,to(n.id,'for'));rel('realizes',true,from(n.id,'realizes'))}
 if(n.kind==='capability'){rel('realizes',false,to(n.id,'realizes'));rel('realizes',true,from(n.id,'realizes'))}
 if(n.kind==='actor'){if(room()){o+=`<g class="nature">${ic(kindIcon(n),14,y+3,12,gray)}${T(n.nature,30,y+13,{px:T11,wt:500,fill:gray})}</g>`;y+=20}
  rel('for',true,from(n.id,'for'));rel('actor',true,[...new Set(from(n.id,'actor').map(s=>wfOf(N[s])?.id))]);
  rel('tell',true,[...new Set(D.nodes.filter(x=>(x.fx||[]).some(f=>f.do==='tell'&&f.onid===n.id)).map(x=>wfOf(x)?.id))])}
 return o}
// ---- entity: fields, lifecycle as a graph, who creates/changes it ----
function lifecycle(ent,x,y,W,maxH){const states=kidsOf(ent,['state']),trs=kidsOf(ent,['transition']);if(!states.length&&!trs.length)return{svg:'',y};
 const order=[],seen=new Set(),q=trs.filter(t=>!to(t.id,'from').length).map(t=>to(t.id,'to')[0]);q.push(...states.filter(s=>!trs.some(t=>to(t.id,'to')[0]===s.id)).map(s=>s.id));
 const walk=()=>{while(q.length){const id=q.shift();if(!id||!N[id]||seen.has(id))continue;seen.add(id);order.push(id);for(const t of trs)if(to(t.id,'from').includes(id))q.push(to(t.id,'to')[0])}};walk();for(const s of states){q.push(s.id);walk()}
 const initial=trs.find(t=>!to(t.id,'from').length);const nodes=[];let cx=x;const rowY=y+18;
 if(initial){nodes.push({start:true,x:cx,w:14});cx+=14+44}
 for(const id of order){const w=mnW(id,T11)+16;nodes.push({id,x:cx,w});cx+=w+44}
 const total=cx-44-x;if(total>W)return{svg:'',y};
 let o='',pos={};for(const nd of nodes){if(nd.start){o+=`<circle cx="${nd.x+7}" cy="${rowY+11}" r="6" fill="#1d4f7a"/>`;pos.start=nd}else{pos[nd.id]=nd;o+=`<rect class="st-pill" x="${nd.x}" y="${rowY}" width="${nd.w}" height="22" rx="11"/>`+mnSvg(nd.id,nd.x+8,rowY+5,{px:T11})}}
 const lab=[];let yy=rowY+11;
 for(const t of trs){const f=to(t.id,'from'),tgt=to(t.id,'to')[0];const a=f.length?pos[f[0]]:pos.start,b=pos[tgt];if(!a||!b)continue;const ax=a.x+a.w,bx=b.x;
  if(bx>ax){o+=`<path class="st-arrow" d="M${ax+2},${yy}L${bx-3},${yy}" marker-end="url(#ar)"/>`;o+=T(title(t),(ax+bx)/2,yy-8,{px:T11,wt:600,fill:'#7048b8',anchor:'middle'})}}
 let y2=rowY+30;
 // who handles each transition: workflows are links in the workflow style, states are pills: never the same look
 for(const t of trs){const firers=[...new Set(D.nodes.filter(n=>(n.fx||[]).some(f=>f.onid===t.id)).map(n=>wfOf(n)?.id).filter(Boolean))],evs=from(t.id,'event');
  if(y2+19>y+maxH)break;o+=T(title(t),x,y2+12,{px:T11,wt:600,fill:'#7048b8'});const tx0=x+tw(title(t),T11,600)+14;let first=true;
  for(const [word,ids] of [['transition',firers],['event',evs]]){if(!ids.length)continue;const r=relRow(word,true,ids,tx0,y2+12,x+W,0);o+=r.svg;y2=r.y}
  if(!firers.length){o+=`<g class="gap">${ic('warn',tx0,y2,12,'#c92a2a')}${T('no effect fires it',tx0+16,y2+11,{px:T11,wt:500,fill:'#c92a2a'})}</g>`;y2+=19}}
 return{svg:o,y:Math.max(y2,rowY+30)+4}}
function entityCard(b,W,H){const n=b.n;let o='';if(W<112||H<50)return marker(b,W,H);
 const h=head(b,W,H);o+=h.svg;let y=h.y+4;const sy=says(n.says,14,y+8,W,H,2);o+=sy.svg;if(sy.svg)y=sy.y+4;
 const at=kidsOf(n.id,['attribute']),st=kidsOf(n.id,['state']),tr=kidsOf(n.id,['transition']);
 const count=[at.length&&`${at.length} fields`,st.length&&`${st.length} states`,tr.length&&`${tr.length} transitions`].filter(Boolean).join(' · ');
 if(H-y>=at.length*18+34){for(const a of at){const ty=a.atype||(a.of&&N[a.of]?mnTitle(a.of):'text');o+=mnSvg(a.id,14,y+3,{px:T11});if(mnW(a.id,T11)+tw(ty,T11,500)+44<W)o+=T(ty,W-12,y+14,{px:T11,wt:500,fill:gray,anchor:'end'});y+=18}y+=6}
 else if(count&&H-y>=22){o+=T(count,14,y+14,{px:T11,wt:500,fill:gray});y+=22}
 if(H-y>=104){const l=lifecycle(n.id,14,y,W-28,H-y-6);if(l.svg){o+=`<g class="lifecycle">${l.svg}</g>`;y=l.y}}
 const rel=(word,ids)=>{if(!ids.length||H-y<22)return;const r=relRow(word,true,ids,14,y+13,W);if(r.y<=H-2){o+=r.svg;y=r.y+2}};
 for(const op of ['create','write','delete','tell']){const ids=[...new Set(D.nodes.filter(x=>(x.fx||[]).some(f=>f.do===op&&(f.onid===n.id||N[f.onid]?.parent===n.id))).map(x=>wfOf(x)?.id).filter(Boolean))];rel(op,ids)}
 rel('shows',[...new Set(E.filter(e=>e.f==='shows'&&e.t===n.id).map(e=>e.s))]);
 return o}
const mnTitle=id=>title(N[id]);
// ---- workflow: header (all levels), summary body (map level) ----
function startChip(b,x,y,maxW){const st=b.starter;if(st.none)return{svg:`<g class="starter">${ic('gear',x+8,y+3,12,'#555')}${T('nothing starts this yet',x+26,y+13,{px:T11,wt:500,fill:'#444'})}</g>`,w:tw('nothing starts this yet',T11,500)+34,y:y+22};
 const ids=st.ids||[st.id];const w0=ids.reduce((s,id)=>s+mnW(id,T11)+6,0)+tw(st.lead,T11,500)+34;if(w0>maxW)return{svg:'',w:0,y};
 let cx=x+8;let o=ic(st.icon,cx,y+3,12,'#555');cx+=18;o+=T(st.lead,cx,y+13,{px:T11,wt:500,fill:'#444'});cx+=tw(st.lead,T11,500)+6;for(const id of ids){o+=mnSvg(id,cx,y+4,{px:T11});cx+=mnW(id,T11)+6}
 return{svg:`<rect x="${x}" y="${y}" width="${cx-x+4}" height="19" rx="9.5" fill="#0001" stroke="#c9ced9"/>`+o,w:cx-x+4,y:y+22}}
const autoFrame=b=>b.starter.icon==='gear'||b.starter.icon==='timer';
function frameHead(b,W,H,lv){const col=b.col;let o='';const bandH=32;
 o+=`<path d="M0,16a16,16 0 0 1 16,-16h${W-32}a16,16 0 0 1 16,16v${bandH-16}h-${W}z" fill="${col}"/>`;
 const word='workflow',kw=tw(word.toUpperCase(),T11,600)+8,avail=W-14-34-kw-14;const t=title(b.n),fits=tw(t,14,700)<=avail;
 o+=ic('call',12,9,15,'#fff')+(fits?T(t,34,22,{px:14,wt:700,fill:'#fff'}):'');
 if(W>=170)o+=T(word.toUpperCase(),W-12,21,{px:T11,wt:600,fill:'#ffffffcc',anchor:'end',ls:'.06em',cls:'kw'});
 if(!fits){const L=lines(t,W-60,14,700);o+=L.slice(0,2).map((s,i)=>T(s,34,22+i*0,{px:14,wt:700,fill:'#fff'})).join('')}
 return o}
function workflowBody(b,W,H,lv){let o='',y=bandH0;
 const sy=says(b.n.says,14,y+14,W,H,2);o+=sy.svg;if(sy.svg)y=sy.y;
 const sc=startChip(b,14,y+2,W-28);if(sc.svg&&H-y>=26){o+=sc.svg;y=sc.y+4}
 return{svg:o,y}}
const bandH0=40;
function workflowMap(b,W,H){let o='';if(W<150||H<56)return `<rect width="${W}" height="${H}" rx="10" fill="${b.col}"/>`+ic('call',W/2-9,H/2-9,18,'#fff');
 o+=frameHead(b,W,H,'map');const w=workflowBody(b,W,H,'map');o+=w.svg;let y=w.y;const c=b.counts;
 if(H-y>=26){const txt=`${c.steps} steps · ${c.ends} ends`;o+=T(txt,14,y+16,{px:T11,wt:500,fill:gray});let cx=14+tw(txt,T11,500)+10;
  if(c.success)o+=ic('ok',cx,y+5,13,'#2f7d4a')+T(String(c.success),cx+16,y+16,{px:T11,wt:600,fill:'#2f7d4a'}),cx+=16+tw(String(c.success),T11,600)+8;
  if(c.failure)o+=ic('no',cx,y+5,13,'#c92a2a')+T(String(c.failure),cx+16,y+16,{px:T11,wt:600,fill:'#c92a2a'});y+=24}
 const rel=(word,inb,ids)=>{if(!ids.length||H-y<24)return;const r=relRow(word,inb,ids,14,y+14,W);if(r.y<=H-2){o+=r.svg;y=r.y+2}};
 rel('realizes',false,to(b.id,'realizes'));rel('calls',false,[...new Set(b.steps.flatMap(s=>to(s,'calls')))]);rel('calls',true,from(b.id,'calls').map(s=>wfOf(N[s]).id));
 return o}
// ---- registry ----
const VIEWS={
 workflow:{map:workflowMap,flow:null,detail:null},
 goal:{any:noteCard},capability:{any:noteCard},actor:{any:noteCard},entity:{any:entityCard}};
