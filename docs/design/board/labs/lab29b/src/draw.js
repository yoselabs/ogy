// ===== drawing: three levels of detail by scale, routed edges, labels placed in free space =====
const stage=document.getElementById('stage'),vp=document.getElementById('vp');
let scale=0.5,tx=0,ty=0,sel=null,selBd=null,selRow=null;
const LEVELS=[['map',0,0.75],['flow',0.75,1.35],['detail',1.35,9]];
const levelOf=s=>s<0.75?'map':s<1.35?'flow':'detail';
const sg=(x,y,inner,attrs='')=>`<g ${attrs} transform="translate(${x},${y}) scale(${1/scale})">${inner}</g>`;
function frameSvg(b,lv,dim){const W=b.w*scale,H=b.h*scale,col=b.col,auto=autoFrame(b);
 let o=`<rect class="f" width="${W}" height="${H}" rx="16" fill="#fff" stroke="${col}" stroke-width="2"${auto?' stroke-dasharray="3 7" stroke-linecap="round"':''}/>`+(auto?`<rect width="${W}" height="${H}" rx="16" fill="url(#hatch)" pointer-events="none"/>`:'')+`<rect width="${W}" height="${H}" rx="16" fill="${col}" fill-opacity=".04" pointer-events="none"/>`;
 if(lv==='map')o+=workflowMap(b,W,H);
 else{o+=frameHead(b,W,HEAD0*scale,lv);o+=workflowBody(b,W,HEAD0*scale,lv).svg}
 let g=`<g class="blk frame${dim?' dim':''}${sel===b.id?' hl':''}" data-id="${esc(b.id)}">`+sg(b.x,b.y,o);
 if(lv!=='map'){for(const sid of b.steps){const S=scr[sid];
   g+=lv==='flow'?sg(b.x+S.lx,b.y+S.ly,flowSlot(S,b,scale),`class="slot" data-sid="${esc(sid)}"`):`<g class="slot" transform="translate(${b.x},${b.y})">${detailSlot(S,b)}</g>`}
  for(const e of b.iedges||[])g+=`<path class="iedge" d="${pathD(e.pts,6)}" marker-end="url(#aro)" vector-effect="non-scaling-stroke"/><circle class="idot" cx="${e.pts[0][0]}" cy="${e.pts[0][1]}" r="${3/scale}"/>`}
 return g+'</g>'}
function noteSvg(b,lv,dim){const W=b.w*scale,H=b.h*scale;const fn=VIEWS[b.n.kind].any;
 return `<g class="blk note${dim?' dim':''}${sel===b.id?' hl':''}" data-id="${esc(b.id)}"><rect class="nb" x="${b.x}" y="${b.y}" width="${b.w}" height="${b.h}" rx="${8/scale}" fill="${b.fill}" style="stroke:${b.col};stroke-width:1.5px" vector-effect="non-scaling-stroke"/>`+sg(b.x,b.y,fn(b,W,H))+'</g>'}
// ---- labels: beside an edge in free space, never on it; dropped when no free spot ----
function placeLabels(){const L=[];const rects=blocks.map(b=>({x:b.x,y:b.y,w:b.w,h:b.h}));const segs=[];
 for(const u of bundles)for(let i=0;i<u.pts.length-1;i++)segs.push({a:u.pts[i],b:u.pts[i+1]});
 const m=3/scale,hit=(r,q)=>r.x<q.x+q.w&&r.x+r.w>q.x&&r.y<q.y+q.h&&r.y+r.h>q.y;
 const segRect=s=>({x:Math.min(s.a[0],s.b[0])-m,y:Math.min(s.a[1],s.b[1])-m,w:Math.abs(s.a[0]-s.b[0])+2*m,h:Math.abs(s.a[1]-s.b[1])+2*m});
 const sr=segs.map(segRect);const placed=[];
 for(const u of bundles){const wpx=tw(u.label,T11,500)+10,hpx=17,w=wpx/scale,h=hpx/scale;let done=false;
  const sorted=u.pts.slice(0,-1).map((p,i)=>({p,q:u.pts[i+1],len:Math.hypot(u.pts[i+1][0]-p[0],u.pts[i+1][1]-p[1])})).sort((p,q)=>q.len-p.len);
  outer:for(const s of sorted){const horiz=s.p[1]===s.q[1];for(const t of [.5,.3,.7,.15,.85]){for(const side of [-1,1]){
    const mx=s.p[0]+(s.q[0]-s.p[0])*t,my=s.p[1]+(s.q[1]-s.p[1])*t,off=(6+hpx/2)/scale;
    const cx=horiz?mx:mx+side*(off+wpx/2/scale-hpx/2/scale),cy=horiz?my+side*off:my;const r={x:cx-w/2,y:cy-h/2,w,h};
    if(horiz?(r.x<Math.min(s.p[0],s.q[0])||r.x+r.w>Math.max(s.p[0],s.q[0])):(r.y<Math.min(s.p[1],s.q[1])||r.y+r.h>Math.max(s.p[1],s.q[1])))continue;
    if(rects.some(b=>hit(r,b))||sr.some(q=>hit(r,q))||placed.some(q=>hit(r,q)))continue;
    placed.push(r);L.push({u,cx,cy,wpx,hpx});break outer}}}}
 return L}
function edgeSvg(u,lab){const on=sel&&(u.a===sel||u.b===sel)||selBd===u.id;const dim=(sel||selBd)&&!on;
 const mk=u.cls==='call'||u.cls==='cover'?'arp':'ar';const p=pathD(u.pts,10);
 return `<g class="edgeg${on?' hl':''}${dim?' dim2':''}" data-bd="${u.id}"><path class="edge ${u.cls}" d="${p}" marker-end="url(#${on?'ara':mk})" vector-effect="non-scaling-stroke"/><circle class="dot" cx="${u.pts[0][0]}" cy="${u.pts[0][1]}" r="${3.5/scale}"/><path class="edge-hit" d="${p}" vector-effect="non-scaling-stroke"/></g>`}
function draw(){const lv=levelOf(scale);document.getElementById('stage').dataset.lv=lv;
 const related=new Set();if(sel){related.add(sel);for(const u of bundles){if(u.a===sel)related.add(u.b);if(u.b===sel)related.add(u.a)}}
 if(selBd){const u=bundles.find(x=>x.id===selBd);if(u){related.add(u.a);related.add(u.b)}}
 let o='';for(const b of blocks){const dim=(sel||selBd)&&!related.has(b.id);o+=b.type==='frame'?frameSvg(b,lv,dim):noteSvg(b,lv,dim)}
 let e='';for(const u of bundles)e+=edgeSvg(u);
 let lab='';for(const l of placeLabels()){const u=l.u,on=sel&&(u.a===sel||u.b===sel)||selBd===u.id;
  lab+=`<g class="elab${on?' hl':''}" data-bd="${u.id}">`+sg(l.cx,l.cy,`<rect x="${-l.wpx/2}" y="${-l.hpx/2}" width="${l.wpx}" height="${l.hpx}" rx="5" class="elab-bg"/><text x="0" y="4" text-anchor="middle" class="el" style="font-size:${T11}px">${esc(u.label)}</text>`)+'</g>'}
 vp.innerHTML=o+e+lab;apply();lvUi();}
function apply(){vp.setAttribute('transform',`translate(${tx},${ty}) scale(${scale})`);for(const m of document.querySelectorAll('marker[markerUnits=userSpaceOnUse]')){m.setAttribute('markerWidth',12/scale);m.setAttribute('markerHeight',12/scale)}}
let _raf=0;const redraw=()=>{if(_raf)return;_raf=requestAnimationFrame(()=>{_raf=0;draw()})};
const worldBounds=l=>{let x0=Math.min(...l.map(b=>b.x)),y0=Math.min(...l.map(b=>b.y)),x1=Math.max(...l.map(b=>b.x+b.w)),y1=Math.max(...l.map(b=>b.y+b.h));const ids=new Set(l.map(b=>b.id));for(const u of bundles)if(ids.has(u.a)&&ids.has(u.b))for(const p of u.pts){x0=Math.min(x0,p[0]-24);x1=Math.max(x1,p[0]+24);y0=Math.min(y0,p[1]-24);y1=Math.max(y1,p[1]+24)}return{x0,y0,x1,y1}};
function fitTo(list,pad=60){const r=worldBounds(list),w=stage.clientWidth,h=stage.clientHeight-70;const s=Math.min(3,Math.max(0.05,Math.min((w-pad*2)/(r.x1-r.x0),(h-pad*2)/(r.y1-r.y0))));
 scale=s;tx=(w-(r.x1-r.x0)*s)/2-r.x0*s;ty=70+(h-(r.y1-r.y0)*s)/2-r.y0*s}
function zoomAt(ns,px,py){ns=Math.min(3,Math.max(0.05,ns));const wx=(px-tx)/scale,wy=(py-ty)/scale;scale=ns;tx=px-wx*ns;ty=py-wy*ns}
