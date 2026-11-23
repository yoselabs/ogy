// ===== layout (deterministic columns, no overlap by construction) and orthogonal edge routing around blocks =====
const COLGAP=230,ROWGAP=110;
function layoutWorld(){
 const depth={};const callers=w=>E.filter(e=>e.f==='calls'&&e.t===w).map(e=>wfOf(N[e.s]).id);
 const dep=(w,seen=new Set())=>{if(depth[w]!==undefined)return depth[w];if(seen.has(w))return 0;seen.add(w);const c=callers(w);return depth[w]=c.length?1+Math.max(...c.map(x=>dep(x,seen))):0};
 for(const w of WF)dep(w.id);const maxWf=Math.max(...WF.map(w=>1+depth[w.id]));
 const goalFor=new Set(Object.values(B).filter(b=>b.n.kind==='goal').flatMap(b=>to(b.id,'for')));
 const colOf=b=>b.type==='frame'?1+depth[b.id]:(b.n.kind==='goal'||b.n.kind==='capability')?0:(b.n.kind==='actor'&&goalFor.has(b.id))?0:maxWf+1;
 const cols=[];for(const b of blocks)(cols[colOf(b)]??=[]).push(b);
 const rank={goal:0,capability:1,actor:2,workflow:0,entity:0};
 // order inside a column: kind order, then by the mean row of the blocks it links to in the column before
 for(let sweep=0;sweep<3;sweep++)for(let c=0;c<cols.length;c++){const L=cols[c];if(!L)continue;
  const bary=b=>{const ys=bundles.filter(u=>u.a===b.id||u.b===b.id).map(u=>B[u.a===b.id?u.b:u.a]).filter(o=>o&&colOf(o)<c).map(o=>o.y+o.h/2);return ys.length?ys.reduce((p,q)=>p+q)/ys.length:1e9};
  L.sort((p,q)=>sweep===0?(rank[p.n.kind]-rank[q.n.kind])||p.title.localeCompare(q.title):bary(p)-bary(q)||p.title.localeCompare(q.title));
  let y=0;for(const b of L){b.y=y;y+=b.h+ROWGAP}}
 let x=0;for(const L of cols){if(!L)continue;const w=Math.max(...L.map(b=>b.w));for(const b of L)b.x=x+(w-b.w)/2;x+=w+COLGAP}
 // centre each column on the tallest one
 const hs=cols.map(L=>L?L[L.length-1].y+L[L.length-1].h:0),H=Math.max(...hs);cols.forEach((L,i)=>{if(L)for(const b of L)b.y+=(H-hs[i])/2});
 for(const b of blocks){b.x=Math.round(b.x);b.y=Math.round(b.y)}}
// ---- grid router: Dijkstra over (cell, direction) with a bend cost and a reuse cost ----
class Router{
 constructor(bx,by,bw,bh,cell,rects,pad){this.c=cell;this.x0=bx;this.y0=by;this.nx=Math.ceil(bw/cell)+1;this.ny=Math.ceil(bh/cell)+1;this.pad=pad;this.blk=new Uint8Array(this.nx*this.ny);this.use=new Uint8Array(this.nx*this.ny);
  for(const r of rects){const i0=Math.floor((r.x-pad-bx)/cell),i1=Math.ceil((r.x+r.w+pad-bx)/cell),j0=Math.floor((r.y-pad-by)/cell),j1=Math.ceil((r.y+r.h+pad-by)/cell);
   for(let j=Math.max(0,j0);j<=Math.min(this.ny-1,j1);j++)for(let i=Math.max(0,i0);i<=Math.min(this.nx-1,i1);i++){const cx=bx+i*cell,cy=by+j*cell;if(cx>r.x-pad&&cx<r.x+r.w+pad&&cy>r.y-pad&&cy<r.y+r.h+pad)this.blk[j*this.nx+i]=1}}}
 cellAt(x,y){return{i:Math.round((x-this.x0)/this.c),j:Math.round((y-this.y0)/this.c)}}
 free(i,j){return i>=0&&j>=0&&i<this.nx&&j<this.ny&&!this.blk[j*this.nx+i]}
 // entry candidates around a rect: cells straight out of each side, with the border point they connect to
 ring(r,margin=10){const o=[],c=this.c,d=this.pad+c*0.5;
  const sides=[['R',r.x+r.w+d,null],['L',r.x-d,null],['B',null,r.y+r.h+d],['T',null,r.y-d]];
  for(const [s,fx,fy] of sides){if(s==='R'||s==='L'){for(let y=r.y+margin;y<=r.y+r.h-margin;y+=c){const k=this.cellAt(fx,y);if(this.free(k.i,k.j))o.push({i:k.i,j:k.j,bx:s==='R'?r.x+r.w:r.x,by:this.y0+k.j*c,d:s})}}
   else for(let x=r.x+margin;x<=r.x+r.w-margin;x+=c){const k=this.cellAt(x,fy);if(this.free(k.i,k.j))o.push({i:k.i,j:k.j,bx:this.x0+k.i*c,by:s==='B'?r.y+r.h:r.y,d:s})}}
  return o}
 at(p,dir,r){// one entry at a border point
  const d=this.pad+this.c*0.5,x=p.x+(dir==='R'?d:dir==='L'?-d:0),y=p.y+(dir==='B'?d:dir==='T'?-d:0);const k=this.cellAt(x,y);const side=dir==='R'||dir==='L';return free(this,k)?[{i:k.i,j:k.j,bx:side?p.x:this.x0+k.i*this.c,by:side?this.y0+k.j*this.c:p.y,d:dir}]:[]}
 path(starts,ends){const nx=this.nx,ny=this.ny,DX=[1,0,-1,0],DY=[0,1,0,-1];const N4=nx*ny*4,dist=new Float32Array(N4).fill(1e9),prev=new Int32Array(N4).fill(-1);
  const tgt=new Map();for(const e of ends)tgt.set(e.j*nx+e.i,e);
  const heap=[];const push=(k,v)=>{heap.push([v,k]);let i=heap.length-1;while(i>0){const p=(i-1)>>1;if(heap[p][0]<=heap[i][0])break;[heap[p],heap[i]]=[heap[i],heap[p]];i=p}};
  const pop=()=>{const t=heap[0],l=heap.pop();if(heap.length){heap[0]=l;let i=0;for(;;){let a=2*i+1,b=a+1,m=i;if(a<heap.length&&heap[a][0]<heap[m][0])m=a;if(b<heap.length&&heap[b][0]<heap[m][0])m=b;if(m===i)break;[heap[m],heap[i]]=[heap[i],heap[m]];i=m}}return t};
  for(const s of starts){const dirI={R:0,B:1,L:2,T:3}[s.d];const k=(s.j*nx+s.i)*4+dirI;dist[k]=0;prev[k]=-2;push(k,0)}
  let hit=-1;while(heap.length){const [v,k]=pop();if(v>dist[k])continue;const cell=k>>2,dir=k&3,i=cell%nx,j=(cell-i)/nx;
   if(tgt.has(cell)){hit=k;break}
   for(let nd=0;nd<4;nd++){if(((nd+2)&3)===dir)continue;const ni=i+DX[nd],nj=j+DY[nd];if(!this.free(ni,nj))continue;const nc=nj*nx+ni;const cost=1+(nd!==dir?5:0)+this.use[nc]*3;const nk=nc*4+nd;if(v+cost<dist[nk]){dist[nk]=v+cost;prev[nk]=k;push(nk,v+cost)}}}
  if(hit<0)return null;const cells=[];for(let k=hit;k>=0;k=prev[k]){cells.push(k>>2);if(prev[k]===-2)break}cells.reverse();
  const first=cells[0],last=cells[cells.length-1];const s=starts.find(s=>s.j*nx+s.i===first),e=tgt.get(last);
  for(const c of cells)this.use[c]=Math.min(250,this.use[c]+1);
  const P=cells.map(c=>{const i=c%nx,j=(c-i)/nx;return[this.x0+i*this.c,this.y0+j*this.c]});
  const pts=[[s.bx,s.by],...P,[e.bx,e.by]];
  // the first and last legs must be straight out of the border
  if(s.d==='R'||s.d==='L')pts[1]=[pts[1][0],s.by];else pts[1]=[s.bx,pts[1][1]];
  if(e.d==='R'||e.d==='L')pts[pts.length-2]=[pts[pts.length-2][0],e.by];else pts[pts.length-2]=[e.bx,pts[pts.length-2][1]];
  return simplify(pts)}}
function free(r,k){return r.free(k.i,k.j)}
function simplify(p){const o=[p[0]];for(let i=1;i<p.length-1;i++){const a=o[o.length-1],b=p[i],c=p[i+1];if((a[0]===b[0]&&b[0]===c[0])||(a[1]===b[1]&&b[1]===c[1]))continue;if(a[0]===b[0]&&a[1]===b[1])continue;o.push(b)}o.push(p[p.length-1]);return o}
// rounded orthogonal path
function pathD(p,r=9){let d=`M${p[0][0]},${p[0][1]}`;for(let i=1;i<p.length-1;i++){const a=p[i-1],b=p[i],c=p[i+1];const l1=Math.hypot(b[0]-a[0],b[1]-a[1]),l2=Math.hypot(c[0]-b[0],c[1]-b[1]);const k=Math.min(r,l1/2,l2/2);
  const ux=(b[0]-a[0])/l1,uy=(b[1]-a[1])/l1,vx=(c[0]-b[0])/l2,vy=(c[1]-b[1])/l2;d+=`L${b[0]-ux*k},${b[1]-uy*k}Q${b[0]},${b[1]} ${b[0]+vx*k},${b[1]+vy*k}`}
 const e=p[p.length-1];return d+`L${e[0]},${e[1]}`}
function routeAll(){// inter-block edges
 const rects=blocks.map(b=>({x:b.x,y:b.y,w:b.w,h:b.h}));const x0=Math.min(...blocks.map(b=>b.x))-120,y0=Math.min(...blocks.map(b=>b.y))-120,x1=Math.max(...blocks.map(b=>b.x+b.w))+120,y1=Math.max(...blocks.map(b=>b.y+b.h))+120;
 const R=new Router(x0,y0,x1-x0,y1-y0,16,rects,18);
 const order=[...bundles].sort((p,q)=>(B[p.a].x-B[p.b].x)**2+(B[p.a].y-B[p.b].y)**2-((B[q.a].x-B[q.b].x)**2+(B[q.a].y-B[q.b].y)**2));
 for(const u of order){const A=B[u.a],Bb=B[u.b];const s=R.ring(A),e=R.ring(Bb);u.pts=R.path(s,e)||[[A.x+A.w,A.y+A.h/2],[Bb.x,Bb.y+Bb.h/2]]}
 // inside each frame: from a row to the slot it leads to
 for(const w of WF){const f=B[w.id];const slots=f.steps.map(id=>({x:f.x+scr[id].lx,y:f.y+scr[id].ly,w:SW,h:scr[id].h}));
  const hdr={x:f.x,y:f.y,w:f.w,h:HEAD0};const IR=new Router(f.x,f.y,f.w,f.h,6,[...slots,hdr],7);f.iedges=[];
  const incoming={};for(const sid of f.steps){const S=scr[sid];S.bt?.forEach((bt,i)=>{for(const t of bt.r.then)if(scr[t])(incoming[t]??=[]).push({sid,i,y:S.ly+bt.y+bt.h/2})})}
  for(const t in incoming)incoming[t].sort((p,q)=>p.y-q.y);
  for(const t in incoming){const T=scr[t];const arr=incoming[t];arr.forEach((a,k)=>{const S=scr[a.sid],bt=S.bt[a.i];const ay=f.y+S.ly+bt.y+bt.h/2,ax=f.x+S.lx+SW;
    const ty=f.y+T.ly+Math.min(T.h-10,18+k*14);const start=IR.at({x:ax,y:Math.round(ay/6)*6},'R'),end=IR.at({x:f.x+T.lx,y:Math.round(ty/6)*6},'L');
    let pts=start.length&&end.length?IR.path(start,end):null;if(!pts)pts=[[ax,ay],[f.x+T.lx,ty]];
    const ok=T.end?(T.n.result==='failure'?'no':'ok'):'step';f.iedges.push({sid:a.sid,row:bt.r.id,to:t,pts,cls:ok})})}}
}
