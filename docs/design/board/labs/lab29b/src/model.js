// ===== model: entries, steps as slots, effect badges, blocks, relation bundles =====
// Lab data: ogy's effect has no value field yet; the values below are a lab example to show the badge, not KB data.
{const r=D.nodes.find(n=>n.id==='product/lending/workflow/borrow/step/record/case/otherwise');if(r&&r.fx[0])r.fx[0].set={tool:'the tool asked for',renewals:'0'}}
const N={},topOf={};for(const n of D.nodes){if(n.kind==='area')continue;N[n.id]=n}
for(const id in N){let n=N[id];while(!n.top&&N[n.parent])n=N[n.parent];topOf[id]=n.id}
const E=D.edges.filter(e=>N[e.s]&&N[e.t]);const outE={},inE={};for(const e of E){(outE[e.s]??=[]).push(e);(inE[e.t]??=[]).push(e)}
const kidsOf=(id,ks)=>D.nodes.filter(n=>n.parent===id&&ks.includes(n.kind));
const to=(id,f)=>(outE[id]||[]).filter(e=>e.f===f).map(e=>e.t);
const from=(id,f)=>(inE[id]||[]).filter(e=>e.f===f).map(e=>e.s);
const wfOf=n=>{while(n&&n.kind!=='workflow')n=N[n.parent];return n};
const servers={};for(const e of E)if(e.f==='serves')(servers[e.t]??=[]).push(e.s);
const AREA_COL={};[...new Set(D.nodes.filter(n=>n.kind!=='area').map(n=>n.area))].sort().forEach((a,i)=>AREA_COL[a]=PAL[i%PAL.length]);
const SW=190,GX=64,GY=20,PAD=20,HEAD0=104;
// ---- effect badges: one badge per thing touched; fields listed top to bottom, with values when known ----
function fxBadges(r){const by=new Map();
 const get=(op,tid)=>{const k=op+'|'+tid;if(!by.has(k))by.set(k,{op,target:tid,fields:[],ops:[op]});return by.get(k)};
 for(const f of r.fx||[]){const t=N[f.onid];if(!t)continue;
  if(f.do==='tell'){get('tell',t.id);continue}
  if(f.do==='create'||f.do==='delete'){const b=get(f.do,t.id);if(f.do==='create')for(const a of kidsOf(t.id,['attribute']).filter(a=>!a.optional&&!a.derived))b.fields.push({id:a.id,value:f.set?.[a.key]});continue}
  if(f.do==='write'){const ent=t.kind==='attribute'?t.parent:t.id;const b=get('write',ent);b.fields.push({id:t.id,value:f.set?.[t.key]});continue}
  if(f.do==='transition'){const ent=t.parent,tgt=to(t.id,'to')[0],src=to(t.id,'from');const mate=by.get('create|'+ent);
   const fld={label:'state',from:src,to:tgt};if(mate){mate.fields.push(fld);mate.ops.push('transition')}else{const b=get('transition',ent);b.fields.push(fld)}}}
 return [...by.values()]}
const BADGE_ICON={create:'plus',write:'pen',delete:'bin',tell:'send',transition:'arrow'};
const BADGE_WORD={create:'create',write:'write',delete:'delete',tell:'tell',transition:'transition'};
const BPX=9;// world px of badge text; shown at detail level only (scale >= 1.35), so >= 12px on screen
function badgeLayout(bd,w){let h=19;bd.rows=[];
 for(const f of bd.fields){const nw=f.label?tw(human(f.label),BPX,500):mnW(f.id,BPX);let vw=0;
  if(f.label){vw=(f.from||[]).reduce((s,id)=>s+mnW(id,BPX)+14,0)+mnW(f.to,BPX)}else if(f.value!==undefined&&f.value!==null)vw=tw(String(f.value),BPX,500)+6;
  const two=nw+vw+22>w;bd.rows.push({f,y:h,two,nw});h+=two?24:13}
 bd.h=h+(bd.fields.length?3:1);bd.w=w;return bd}
// ---- steps as slots ----
function starterOf(w,start){const act=start?to(start,'actor')[0]:null;
 if(act){return{icon:kindIcon(N[act]),lead:'actor',id:act}}
 const sc=to(w.id,'schedule')[0];if(sc)return{icon:'timer',lead:'schedule',id:sc};
 const ev=to(w.id,'event')[0];if(ev)return{icon:'transition',lead:'event',id:ev};
 const by=[...new Set(E.filter(e=>e.f==='calls'&&e.t===w.id).map(e=>wfOf(N[e.s])?.id).filter(Boolean))];
 if(by.length)return{icon:'gear',lead:'calls',ids:by,back:true};return{icon:'gear',lead:'',none:true}}
// authored prose may name entries by key (max-loans); show them by name, like everywhere else
const KEYS=new Map(D.nodes.filter(n=>n.key&&/-/.test(n.key)&&n.kind!=='area').map(n=>[n.key,human(n.key).toLowerCase()]));
const prose=t=>String(t??'').replace(/\b[a-z0-9]+(?:-[a-z0-9]+)+\b/g,k=>KEYS.get(k)||k);
const clauses=t=>{t=String(t);if(t.length<90||!t.includes(', '))return t;return t.split(', ').map(c=>'• '+cap(c.replace(/^(or|and) /,''))).join('\n')};
function rowsOf(s){const rs=kidsOf(s.id,['choice','case','timeout']).map(r=>({id:r.id,kind:r.kind,key:r.key,keyword:r.kind==='timeout'?'Timeout':r.kind==='choice'?cap(r.label||human(r.key)):human(r.key),
  label:r.kind==='case'&&r.when?clauses(cap(prose(r.when))):r.kind==='timeout'?'Nothing happens in time':r.kind==='choice'&&r.when?'Only when: '+prose(r.when):'',
  then:to(r.id,'then'),fx:r.fx||[],covers:to(r.id,'covers_ends'),order:r.order??99,reads:(r.reads||[]).slice(0,3),perf:from(r.id,'performs')}));
 rs.sort((a,b)=>a.order-b.order);if(!rs.length){const t=to(s.id,'then');if(t.length)rs.push({id:s.id,kind:'then',keyword:'',label:'',then:t,fx:[],covers:[],order:0,reads:[],perf:[]})}return rs}
const scr={},B={};
const WF=D.nodes.filter(n=>n.kind==='workflow'&&kidsOf(n.id,['step']).length).sort((a,b)=>a.key.localeCompare(b.key));
const INW=SW-16;
for(const w of WF){const steps=kidsOf(w.id,['step']),ends=kidsOf(w.id,['end']),start=to(w.id,'start')[0];
 const rank={},rows={};for(const s of steps)rows[s.id]=rowsOf(s);
 if(start){rank[start]=0;const q=[start];while(q.length){const x=q.shift();for(const r of rows[x]||[])for(const t of r.then)if(rank[t]===undefined&&N[t]&&N[t].parent===w.id){rank[t]=rank[x]+1;q.push(t)}}}
 const mx=Math.max(0,...Object.values(rank));for(const e of ends)if(rank[e.id]===undefined)rank[e.id]=mx+1;for(const s of steps)if(rank[s.id]===undefined)rank[s.id]=0;
 const cols={},mine=[];
 for(const n of [...steps,...ends]){const isEnd=n.kind==='end';
  const S={id:n.id,n,frame:w.id,end:isEnd,rank:rank[n.id],rows:isEnd?[]:rows[n.id],actors:to(n.id,'actor'),ifc:(servers[n.id]||[]).map(i=>N[i]),calls:to(n.id,'calls')[0]};
  const tws=SW-18;let y;
  if(isEnd){S.tl=lines(cap(n.says),tws-26,10.5,500);y=14+S.tl.length*12.5+10;S.h=Math.max(y,58)}
  else{S.compact=!S.actors.length&&!S.calls&&!S.ifc.length;if(S.compact){S.tl=lines(cap(prose(n.says)),tws-26,10.5,500);S.ty=0;y=10+S.tl.length*12.5+2}else{y=22;S.tl=lines(cap(prose(n.says)),tws,10.5,500);S.ty=y+22;y=S.ty+S.tl.length*12.5+4}
   const inv=S.ifc.map(i=>i.invoked).find(Boolean);S.iy0=y;S.inv=inv?lines(inv,tws-10,8.6,400,true):[];if(S.inv.length)y+=S.inv.length*10.5+8;
   S.fields=[];const i0=S.ifc[0];if(i0){for(const [f,mode] of [['accepts','in'],['shows','out']])for(const t of to(i0.id,f)){const T=N[t];if(!T)continue;const list=T.kind==='attribute'?[T]:T.kind==='entity'?kidsOf(T.id,['attribute']).slice(0,4):[];for(const a of list){const ty=a.atype||(a.of&&N[a.of]?.kind==='enum'?'enum':a.of?'ref':'text');S.fields.push({a,mode,ty,h:19})}}
    for(const f of S.fields){f.y=y;y+=f.h+3}if(S.fields.length)y+=3}
   if(S.calls&&N[S.calls]){S.callY=y;S.callH=22;y+=S.callH+20}
   const lone=S.rows.length===1&&S.rows[0].kind==='then'&&!S.rows[0].fx.length;
   S.bt=S.rows.map(r=>{if(lone||r.kind==='then'&&!r.fx.length)return{r,y:0,h:0,hidden:true,badges:[]};
    const L=r.label?lines(r.label,INW-16-(r.kind==='timeout'?14:0),9.2,400):[];let h=7+13+L.length*11;
    const reads=r.reads.filter(id=>N[id]);if(reads.length)h+=14;
    const cov=r.covers.filter(id=>N[id]);if(cov.length)h+=14;
    const badges=fxBadges(r).map(b=>badgeLayout(b,INW-14));for(const b of badges)h+=b.h+3;
    const perf=r.perf.filter(id=>N[id]);if(perf.length)h+=14;
    const bt={r,L,y,h:h+3,badges,reads,cov,perf};y+=bt.h+4;return bt});
   S.h=y+6;for(const bq of S.bt)if(bq.hidden)bq.y=S.h/2}
  (cols[S.rank]??=[]).push(S);scr[n.id]=S;mine.push(n.id)}
 const colsN=Math.max(...Object.keys(cols).map(r=>+r+1));const fw=PAD*2+colsN*SW+(colsN-1)*GX;let fh=0;
 for(const r in cols){if(cols[r].every(S=>S.end)){const key=S=>{const v=[];for(const sid in scr){const T=scr[sid];if(T.frame!==w.id||T.end)continue;T.bt.forEach(b=>{if(b.r.then.includes(S.id))v.push(b.y+b.h/2)})}return v.length?v.reduce((a,b)=>a+b)/v.length:0};cols[r].sort((p,q)=>key(p)-key(q))}
  let y=HEAD0;for(const S of cols[r]){S.lx=PAD+(+r)*(SW+GX);S.ly=y;y+=S.h+GY}fh=Math.max(fh,y-GY)}
 B[w.id]={id:w.id,type:'frame',n:w,x:0,y:0,w:Math.max(fw,430),h:fh+PAD,col:AREA_COL[w.area],steps:mine,start,starter:starterOf(w,start),
  counts:{steps:steps.length,ends:ends.length,success:ends.filter(e=>e.result==='success').length,failure:ends.filter(e=>e.result==='failure').length}}}
// ---- note blocks (goal, capability, actor, entity): size is what the biggest level needs ----
const NOTE_FILL={goal:'#fff08a',capability:'#ffd27a',actor:'#f6d3e6',entity:'#eaf4fd'},NOTE_EDGE={goal:'#e0c800',capability:'#e8a43a',actor:'#d98ab8',entity:'#8ecbf5'};
const NOTE_SIZE={goal:[340,190],capability:[340,190],actor:[280,170],entity:[340,350]};
const blockOfCache={};
function blockOf(id){if(id in blockOfCache)return blockOfCache[id];let r=null;const n=N[id];if(n){const t=topOf[id],tn=N[t];
  if(B[t])r=t;else if(tn.kind==='interface'){const st=to(t,'serves')[0];r=st?blockOf(st):null}else if(tn.kind==='handler'){const rw=to(t,'performs')[0];r=rw?blockOf(rw):null}}
 return blockOfCache[id]=r}
function addNote(id){const t=topOf[id],n=N[t];if(!n||B[t]||!NOTE_FILL[n.kind])return;const [w,h]=NOTE_SIZE[n.kind];B[t]={id:t,type:'note',n,x:0,y:0,w,h,col:NOTE_EDGE[n.kind],fill:NOTE_FILL[n.kind]}}
// which entries get a block: everything a workflow or a card names
for(const w of WF){for(const t of to(w.id,'realizes'))addNote(t)}
for(const id in N)if(N[id].kind==='capability')for(const g of to(id,'realizes'))addNote(g);
for(const id in N)if(N[id].kind==='capability'||N[id].kind==='goal')addNote(id);
for(const sid in scr){const S=scr[sid];for(const a of S.actors)addNote(a);for(const r of S.rows){for(const f of r.fx)if(f.onid)addNote(f.onid);}
 for(const i of S.ifc)for(const t of to(i.id,'shows'))addNote(t)}
for(const id in N)if(N[id].kind==='goal')for(const a of to(id,'for'))addNote(a);
for(const w of WF)for(const ev of to(w.id,'event'))addNote(ev);
const blocks=Object.values(B);Object.values(B).forEach(b=>{b.title=title(b.n)});
// ---- relation bundles: one arrow per pair and field; label is the ontology's own word ----
const bundles=[];{const idx={};
 const put=(s,t,field,label,cls,item)=>{const a=blockOf(s),b=blockOf(t);if(!a||!b||a===b)return;const k=a+'|'+b+'|'+(cls==='effect'?'effect':field);let bu=idx[k];
  if(!bu){bu={id:'bd'+bundles.length,a,b,field,labels:[],cls,items:[]};idx[k]=bu;bundles.push(bu)}if(!bu.labels.includes(label))bu.labels.push(label);bu.items.push({s,t,...item})};
 for(const e of E){if(['realizes','for','actor','calls','covers_ends','event','shows'].includes(e.f)){const cls=e.f==='calls'?'call':e.f==='covers_ends'?'cover':'rel';put(e.s,e.t,e.f,fieldWord(e.f),cls,{f:e.f})}}
 for(const id in N){const n=N[id];for(const f of n.fx||[]){if(!f.onid)continue;const tb=blockOf(f.onid);put(id,f.onid,'effect',BADGE_WORD[f.do]||f.do,'effect',{f:f.do})}}
 for(const bu of bundles)bu.label=bu.labels.join(' · ')}
