// ===== step slots: flow level (screen-space text in the slot) and detail level (the lab 28 sketch screen, world-space) =====
const pillBg=(id,x,y,px)=>`<rect class="pb" x="${x-3}" y="${y-1}" width="${mnW(id,px)+6}" height="${px+5}" rx="${(px+5)/2}" fill="#fff" stroke="#c6ccda"/>`+mnSvg(id,x,y+1,{px});
function pillRow(ids,x,y,maxX,px,label,back){let o='';let cx=x;if(label){o+=`<text class="pl" x="${cx}" y="${y+px}" style="font-size:${px}px;font-weight:600">${esc(label)}</text>`;cx+=tw(label,px,600)+6}
 for(const id of ids){const w=mnW(id,px)+12;if(cx+w>maxX&&cx>x+10){break}o+=pillBg(id,cx+3,y,px);cx+=w}return o}
function badgeSvg(bd,x,y){const op=bd.op,del=op==='delete',cr=bd.ops.includes('create');const col=del?'#c92a2a':cr?'#2f9e44':'#4a5163';
 let o=`<g class="badge op-${op}" data-op="${op}" data-target="${esc(bd.target)}"><rect class="bd" x="${x}" y="${y}" width="${bd.w}" height="${bd.h}" rx="5" fill="${del?'#fdeceb':'#fff'}" stroke="${del?'#e0736b':'#c9ced9'}"/>`;
 if(cr)o+=`<path d="M${x+5},${y}h-1a4,4 0 0 0 -4,4v${bd.h-8}a4,4 0 0 0 4,4h1z" transform="translate(4,0)" fill="#2f9e44" />`;
 if(bd.fields.length)o+=`<path d="M${x+1},${y+17.5}h${bd.w-2}" stroke="${del?'#e0736b':'#dfe3ec'}" stroke-width=".8"/>`;o+=ic(BADGE_ICON[op],x+9,y+3.5,11,col)+mnSvg(bd.target,x+24,y+4,{px:BPX,color:del?'#8f1d1d':undefined});
 if(bd.ops.length>1)o+=ic('arrow',x+bd.w-17,y+3.5,11,'#4a5163');
 for(const r of bd.rows){const f=r.f,yy=y+r.y;
  if(f.label){o+=`<text x="${x+12}" y="${yy+BPX}" style="font-size:${BPX}px;font-weight:500;fill:#4a5163">${esc(human(f.label))}</text>`;let cx=x+r.nw+22,vy=yy,vx=cx;if(r.two){vx=x+12;vy=yy+11}else vx=cx;
   for(const id of f.from||[]){o+=mnSvg(id,vx,vy,{px:BPX});vx+=mnW(id,BPX)+3;o+=ic('arrow',vx,vy,9,'#6b7285');vx+=12}o+=mnSvg(f.to,vx,vy,{px:BPX})}
  else{o+=mnSvg(f.id,x+12,yy,{px:BPX});if(f.value!==undefined&&f.value!==null){const vtx=`<text class="val" x="${r.two?x+14:x+bd.w-8}" y="${yy+BPX+(r.two?11:0)}" ${r.two?'':'text-anchor="end"'} style="font-size:${BPX}px;font-weight:500;fill:#2b2f3a">${esc(f.value)}</text>`;o+=vtx}}}
 return o+'</g>'}
function detailSlot(S,f){const x=S.lx,y=S.ly;const o=[];
 if(S.end){const bad=S.n.result==='failure';return `<g data-sid="${esc(S.id)}" class="scr ${bad?'no':'ok'}"><rect class="w" x="${x}" y="${y}" width="${SW}" height="${S.h}" rx="9"/>${ic(bad?'no':'ok',x+8,y+8,15,bad?'#c92a2a':'#2f9e44')}${S.tl.map((t,i)=>`<text x="${x+29}" y="${y+19+i*12.5}" style="font-size:10.5px;font-weight:500">${esc(t)}</text>`).join('')}</g>`}
 return `<g data-sid="${esc(S.id)}" class="scr">${stepFull(S,x,y,S.compact)}</g>`}
function stepFull(S,x,y,light){const sys=!S.actors.length;let s=`<rect class="w" x="${x}" y="${y}" width="${SW}" height="${S.h}" rx="9"${light?' style="fill:#f4f5f9;stroke:#cfd4e0"':''}/>`;
 if(!light){s+=`<rect class="bar" x="${x+.6}" y="${y+.6}" width="${SW-1.2}" height="15" rx="7"/><circle cx="${x+8}" cy="${y+8}" r="2.2" fill="#e08a8a"/><circle cx="${x+15}" cy="${y+8}" r="2.2" fill="#e8c26a"/><circle cx="${x+22}" cy="${y+8}" r="2.2" fill="#8fd19e"/>`;
  s+=S.ifc[0]?mnSvg(S.ifc[0].id,x+30,y+3.5,{px:8.6}):`<text class="ti" x="${x+30}" y="${y+11}" style="font-size:8.6px">${sys?'no screen: the product works':'no screen'}</text>`;
  s+=S.calls?'':sys?`<text x="${x+9}" y="${y+31}" style="font-size:9.4px;fill:#6b7285">The product works on its own</text>`:S.actors.map((id,i)=>mnSvg(id,x+9+i*80,y+21,{px:9.4})).join('')}
 else s+=ic('gate',x+8,y+6,12,'#6b7285');
 s+=S.tl.map((t,i)=>`<text x="${x+(light?26:9)}" y="${y+(light?17:S.ty+4)+i*12.5}" style="font-size:10.5px;font-weight:500;fill:#2b2f3a">${esc(t)}</text>`).join('');
 if(S.inv&&S.inv.length){const iy=y+S.iy0;s+=`<rect x="${x+8}" y="${iy-6}" width="${SW-16}" height="${S.inv.length*10.5+6}" rx="4" fill="#f1f3f8"/>`+S.inv.map((t,i)=>`<text x="${x+12}" y="${iy+4+i*10.5}" style="font-family:${MONO};font-size:8.6px;fill:#444">${esc(t)}</text>`).join('')}
 for(const f of S.fields){const fy=y+f.y;s+=`<g class="fld">`+mnSvg(f.a.id,x+9,fy+4,{px:8.6});const cx=x+90,cw=SW-90-9;
  if(f.mode==='out'){s+=`<text x="${cx}" y="${fy+13}" style="fill:#98a0b3;font-size:9px">${f.ty==='flag'?'yes':f.ty==='number'?'42':f.ty==='date'||f.ty==='datetime'?'2026-11-21':'· · ·'}</text></g>`;continue}
  s+=`<rect x="${cx}" y="${fy+1}" width="${cw}" height="16" rx="3.5" fill="#fff" stroke="#b8bfce"/><text x="${cx+5}" y="${fy+12.5}" style="fill:#98a0b3;font-size:9px">${({flag:'yes / no',number:'0',money:'0.00',date:'yyyy-mm-dd',datetime:'date, time',duration:'0h 00m',enum:'Choose…',ref:'Pick one…'})[f.ty]||'Type here…'}</text></g>`}
 if(S.calls&&N[S.calls]){const cy=y+S.callY;s+=`<g class="call"><rect x="${x+8}" y="${cy}" width="${SW-16}" height="${S.callH}" rx="5"/><text x="${x+13}" y="${cy+14.5}" style="font-size:9px;font-weight:700">calls</text>${mnSvg(S.calls,x+45,cy+5,{px:9.4})}${ic('transition',x+SW-28,cy+6,10,'#4b2a7a')}</g><text x="${x+9}" y="${cy+S.callH+13}" style="font-size:8.8px;font-weight:700;fill:#6b7285">covers ends</text>`}
 for(const bt of S.bt){if(bt.hidden)continue;const r=bt.r,by=y+bt.y;const cls=r.kind==='timeout'?'tmo':sys?'sys':N[S.actors[0]]?.nature==='ai'?'aib':'';const kx=x+(r.kind==='timeout'?26:14);
  s+=`<g class="b ${cls}" data-row="${esc(r.id)}"><rect x="${x+8}" y="${by}" width="${INW}" height="${bt.h}" rx="5"/>${r.kind==='timeout'?ic('timer',x+11,by+4,11,'#6a4f00'):''}<text class="case-keyword" x="${kx}" y="${by+13}" style="font-size:10.5px;font-weight:700">${esc(r.keyword||'')}</text>`;
  let ty=by+13;for(const t of bt.L){ty+=11;s+=`<text x="${kx}" y="${ty}" style="font-size:9.2px">${esc(t)}</text>`}
  let cy2=ty+3;
  if(bt.reads.length){s+=pillRow(bt.reads,x+14,cy2,x+8+INW-6,8.6,'when');cy2+=14}
  if(bt.cov.length){s+=pillRow(bt.cov,x+14,cy2,x+8+INW-6,8.6,S.calls?'':'covers ends');cy2+=14}
  for(const bd of bt.badges){s+=badgeSvg(bd,x+15,cy2);cy2+=bd.h+3}
  if(bt.perf.length){s+=pillRow(bt.perf,x+14,cy2,x+8+INW-6,8.6,'performs');cy2+=14}
  s+='</g>'}
 return s}
// ---- flow level: same slot rectangle, text in screen px; what does not fit is dropped, lowest priority first ----
function flowSlot(S,f,sc){const W=SW*sc,H=S.h*sc;let o='';
 if(S.end){const bad=S.n.result==='failure';const L=lines(cap(S.n.says),W-38,12,500);const need=L.length*15+14;o+=`<rect x="0" y="0" width="${W}" height="${H}" rx="9" fill="${bad?'#fdeceb':'#e8f7ee'}" stroke="${bad?'#e0736b':'#5bbb83'}"/>`+ic(bad?'no':'ok',9,9,16,bad?'#c92a2a':'#2f9e44');
  if(need<=H)o+=L.map((t,i)=>T(t,32,22+i*15,{px:12,wt:500,fill:bad?'#6b1f1a':'#14532d'})).join('');return o}
 o+=`<rect x="0" y="0" width="${W}" height="${H}" rx="9" fill="#fff" stroke="#c9ced9"/>`;let y=8;
 const L=lines(cap(S.n.says),W-20,12,500);
 if(L.length*15+12<=H){o+=L.map((t,i)=>T(t,10,y+12+i*15,{px:12,wt:500,fill:'#2b2f3a'})).join('');y+=L.length*15+8}
 if(S.calls&&N[S.calls]&&H-y>=22){o+=`<g class="call"><rect x="6" y="${y}" width="${W-12}" height="20" rx="5" fill="#f1e6ff" stroke="#c9a6f5"/>${T('calls',11,y+14,{px:T11,wt:700,fill:'#4b2a7a'})}${mnSvg(S.calls,11+tw('calls',T11,700)+8,y+4,{px:T11})}</g>`;y+=26}
 else if(S.actors.length&&H-y>=22&&mnW(S.actors[0],T11)<W-16){o+=mnSvg(S.actors[0],10,y+4,{px:T11});y+=22}
 for(const bt of S.bt){if(bt.hidden||H-y<19)continue;const r=bt.r;const cls=r.kind==='timeout'?'#fff3d6':!S.actors.length?'#eceef3':'#2b5fd9',fg=!S.actors.length||r.kind==='timeout'?'#2b2f3a':'#fff';
  const kw=r.keyword||'';const ro=`<g class="row-flow" data-row="${esc(r.id)}"><rect x="6" y="${y}" width="${W-12}" height="19" rx="5" fill="${cls}"/>${T(kw,12,y+14,{px:T11,wt:700,fill:fg})}`;
  let ex=12+tw(kw,T11,700)+8;let ico='';for(const bd of bt.badges){if(ex+16>W-10)break;ico+=ic(BADGE_ICON[bd.op],ex,y+4,12,fg);ex+=16}
  o+=ro+ico+'</g>';y+=22}
 return o}
