// usage: CHROME=<chrome binary> [OUT=<folder>] node qa/check.mjs
// Real mouse and wheel events over CDP at 1440x1000, tool-library data, at the default zoom and at the zoom of each level.
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.OUT || path.join(here, "../shots");
fs.mkdirSync(OUT, { recursive: true });
const CHROME = process.env.CHROME || "/nix/store/hm4rnivlsid3bqi1zdzlvfbkdvgv9v13-chromium-unwrapped-156.0.8078.47/libexec/chromium/chromium";
const port = 9500 + Math.floor(Math.random() * 400);
const prof = fs.mkdtempSync("/tmp/lab29b-prof-");
const proc = spawn(CHROME, ["--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let tabs;
for (let i = 0; i < 50; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); if (tabs.length) break; } catch {} await sleep(200); }
const ws = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map(); const errs = [];
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d.result || d); pend.delete(d.id); }
  else if (d.method === "Runtime.exceptionThrown") errs.push(d.params.exceptionDetails.exception?.description?.split("\n")[0] || d.params.exceptionDetails.text);
  else if (d.method === "Runtime.consoleAPICalled" && d.params.type === "error") errs.push("console: " + d.params.args.map((a) => a.value ?? a.description).join(" "));
  else if (d.method === "Log.entryAdded" && d.params.entry.level === "error") errs.push("log: " + d.params.entry.text); };
const send = (method, params = {}) => new Promise((r) => { pend.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const ev = async (e) => { const r = await send("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true }); return r.result?.value ?? r.exceptionDetails?.exception?.description; };
const mouse = (type, x, y, o = {}) => send("Input.dispatchMouseEvent", { type, x, y, button: "left", clickCount: 1, ...o });
const shot = async (name) => { const r = await send("Page.captureScreenshot", { format: "png" }); fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.data, "base64")); };
const wheel = async (x, y, dy, mods = 0) => { await send("Input.dispatchMouseEvent", { type: "mouseWheel", x, y, deltaX: 0, deltaY: dy, modifiers: mods }); await sleep(120); };
await send("Page.enable"); await send("Runtime.enable"); await send("Log.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: "file://" + path.resolve(here, "../lab29b-standalone.html") }); await sleep(1500);
const fails = []; const log = (...a) => console.log(...a); const fail = (m) => { fails.push(m); log("  FAIL", m); };

// ---- the page-side audit: returns violations for the current view ----
const AUDIT = `(()=>{
const out={overlap:[],crossed:[],entering:[],small:[],raw:[],consistency:[],badges:[],counts:{}};
const svg=document.getElementById('svg');
const R=e=>e.getBoundingClientRect();
const inter=(a,b,m=0)=>a.left+m<b.right-m&&a.right-m>b.left+m&&a.top+m<b.bottom-m&&a.bottom-m>b.top+m;
// 1. blocks: outline rects of every .blk, and inside a frame the slot rects
const bl=[...document.querySelectorAll('.blk')].map(g=>({id:g.dataset.id,r:R(g.querySelector('rect.nb,rect.f'))}));
for(let i=0;i<bl.length;i++)for(let j=i+1;j<bl.length;j++)if(inter(bl[i].r,bl[j].r,1))out.overlap.push('block '+bl[i].id.split('/').slice(-2).join('/')+' x '+bl[j].id.split('/').slice(-2).join('/'));
for(const g of document.querySelectorAll('.blk.frame')){const slots=[...g.querySelectorAll('.slot')].map(s=>({id:s.dataset.sid||s.querySelector('[data-sid]')?.dataset.sid,r:R(s.querySelector('rect'))}));
 for(let i=0;i<slots.length;i++)for(let j=i+1;j<slots.length;j++)if(inter(slots[i].r,slots[j].r,1))out.overlap.push('slot '+slots[i].id+' x '+slots[j].id)}
// text boxes
const texts=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()&&R(t).width>0).map(t=>{const r=R(t);const cs=getComputedStyle(t);const m=t.getScreenCTM();const px=parseFloat(cs.fontSize)*Math.hypot(m.a,m.b);return{t,txt:t.textContent.trim(),r:{left:r.left,right:r.right,top:r.top+r.height*.18,bottom:r.bottom-r.height*.18},px}});
out.counts.texts=texts.length;
// text over text inside one block
for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){const a=texts[i],b=texts[j];if(inter(a.r,b.r,1.5)&&a.t.closest('.blk')&&a.t.closest('.blk')===b.t.closest('.blk')&&!a.t.closest('[data-entry]')==!b.t.closest('[data-entry]')||inter(a.r,b.r,1.5)&&a.t.closest('[data-entry]')!==b.t.closest('[data-entry]'))out.overlap.push('text "'+a.txt.slice(0,24)+'" x "'+b.txt.slice(0,24)+'"')}
// 4. size
for(const t of texts)if(t.px<10.95)out.small.push(t.txt.slice(0,30)+' '+t.px.toFixed(1)+'px');
for(const e of document.querySelectorAll('#card *,#tip *,#rel *,#top *')){if(e.children.length===0&&e.textContent.trim()&&e.offsetParent){const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<10.95)out.small.push('html '+e.textContent.trim().slice(0,24)+' '+fs+'px')}}
// 2/3. edges
const blockRects=bl.map(b=>({id:b.id,r:b.r}));
function samples(p){const L=p.getTotalLength(),m=p.getScreenCTM(),o=[];for(let d=0;d<=L;d+=2){const q=p.getPointAtLength(d);o.push({x:m.a*q.x+m.c*q.y+m.e,y:m.b*q.x+m.d*q.y+m.f})}return o}
for(const p of svg.querySelectorAll('path.edge,path.iedge')){const pts=samples(p);const name=(p.closest('.edgeg')?.dataset.bd)||'in-frame';
 const own=p.closest('.edgeg')?bundles.find(b=>b.id===name):null;
 for(const t of texts){if(pts.some(q=>q.x>t.r.left&&q.x<t.r.right&&q.y>t.r.top&&q.y<t.r.bottom)){out.crossed.push(name+' crosses "'+t.txt.slice(0,30)+'"')}}
 if(p.classList.contains('edge'))for(const b of blockRects){const r=b.r;if(pts.some(q=>q.x>r.left+2&&q.x<r.right-2&&q.y>r.top+2&&q.y<r.bottom-2))out.entering.push(name+' enters '+b.id.split('/').slice(-2).join('/'))}
 else for(const s of document.querySelectorAll('.slot rect:first-child,.scr>rect.w')){const r=R(s);if(r.width&&pts.some(q=>q.x>r.left+2&&q.x<r.right-2&&q.y>r.top+2&&q.y<r.bottom-2))out.entering.push('in-frame edge enters a slot')}}
// 5. consistency of identities
const byId={};for(const e of document.querySelectorAll('[data-entry]')){const t=e.querySelector('.mt');if(!t)continue;const cs=getComputedStyle(t);const col=e.tagName==='g'?cs.fill:cs.color;(byId[e.dataset.entry]??=new Set()).add(JSON.stringify([t.textContent,[...e.classList].join(' '),col,cs.fontWeight]))}
for(const k in byId)if(byId[k].size>1)out.consistency.push(k.split('/').slice(-2).join('/')+' -> '+[...byId[k]].join(' | '));
out.counts.entries=Object.keys(byId).length;
// 6. raw keys with dashes where a title exists
const keys=Object.values(N).filter(n=>/-/.test(n.key)).map(n=>n.key);
const code=new Set(Object.values(N).filter(n=>n.invoked).map(n=>n.invoked));
const all=[...texts.map(t=>t.txt),...[...document.querySelectorAll('#card *,#tip *,#rel *')].filter(e=>!e.children.length).map(e=>e.textContent.trim())];
for(const s of all){if(code.has(s)||/^library borrow/.test(s))continue;for(const k of keys)if(new RegExp('(^|[^a-z-])'+k+'($|[^a-z-])').test(s))out.raw.push(k+' in "'+s.slice(0,40)+'"')}
// 7. effect badges
for(const b of document.querySelectorAll('.badge')){const ys=[...b.querySelectorAll('.mn,text')].map(t=>R(t).top).filter((v,i,a)=>true);const rows=[...b.querySelectorAll('text.mt')].map(t=>Math.round(R(t).top));out.badges.push({op:b.dataset.op,target:b.dataset.target.split('/').pop(),names:[...b.querySelectorAll('text.mt')].map(t=>t.textContent),values:[...b.querySelectorAll('text.val')].map(t=>t.textContent),tops:rows,sorted:rows.every((v,i)=>i===0||v>=rows[i-1]-1)})}
out.counts.level=LAB.level;out.counts.scale=+LAB.scale.toFixed(3);return out})()`;
async function audit(label) {
  const o = await ev(AUDIT); const c = o.counts;
  log(`[${label}] scale ${c.scale} level ${c.level}: texts ${c.texts}, entries ${c.entries}; overlap ${o.overlap.length}, crossed ${o.crossed.length}, entering ${o.entering.length}, small ${o.small.length}, raw ${o.raw.length}, consistency ${o.consistency.length}, badges ${o.badges.length}`);
  for (const k of ["overlap", "crossed", "entering", "small", "raw", "consistency"]) for (const m of [...new Set(o[k])].slice(0, 6)) fail(`${label}: ${k}: ${m}`);
  for (const b of o.badges) if (!b.sorted) fail(`${label}: badge ${b.target} lists fields out of top-to-bottom order`);
  return o;
}
const wheelTo = async (target, x = 720, y = 500) => { const s = await ev("LAB.scale"); await wheel(x, y, Math.log(target / s) / -0.0016); };
const blockPos = (sub) => ev(`(()=>{const b=LAB.blocks.find(b=>b.id.includes(${JSON.stringify(sub)}));const w=document.getElementById('stage').getBoundingClientRect();return [LAB.tx+(b.x+b.w/2)*LAB.scale,LAB.ty+(b.y+b.h/2)*LAB.scale]})()`);
const centreOn = async (sub, scale, dx = 0, dy = 0) => ev(`(()=>{const b=LAB.blocks.find(b=>b.id.includes(${JSON.stringify(sub)}));LAB.setScale(${scale},b.x+b.w/2+${dx},b.y+b.h/2+${dy});return LAB.level})()`);

// ===== self-test: the audit must see what it is built to see =====
async function selfTest() {
  await ev(`(()=>{const svg=document.getElementById('svg');const t=[...svg.querySelectorAll('text')].find(t=>t.closest('.blk')&&t.textContent.trim().length>4);const c=t.cloneNode(true);c.setAttribute('class','selftest');c.setAttribute('dy','2');t.parentNode.appendChild(c);
    const b=t.closest('.blk');const rb=b.querySelector('rect.nb,rect.f').getBoundingClientRect(),rt=t.getBoundingClientRect();const X=v=>(v-LAB.tx)/LAB.scale,Y=v=>(v-LAB.ty)/LAB.scale;const m=document.createElementNS('http://www.w3.org/2000/svg','path');m.setAttribute('class','edge selftest');m.setAttribute('d','M'+X(rb.left-30)+','+Y(rt.top+rt.height/2)+'L'+X(rb.right+30)+','+Y(rt.top+rt.height/2));document.getElementById('vp').appendChild(m)})()`);
  const o = await ev(AUDIT); await ev("document.querySelectorAll('.selftest').forEach(e=>e.remove())");
  log("auditor self-test (a doubled text, an edge straight through a block): overlap", o.overlap.length, "entering", o.entering.length, "crossed", o.crossed.length);
  if (!(o.overlap.length > 0 && o.entering.length > 0 && o.crossed.length > 0)) fail("the audit missed an injected defect");
}
// ===== run =====
await shot("1-default-fit"); const base = await audit("default fit"); await selfTest();
log("blocks", await ev("LAB.blocks.length"), "bundles", await ev("LAB.bundles.length"));
// real drag pans
const tx0 = await ev("LAB.tx"); await mouse("mouseMoved", 700, 880, { button: "none" }); await mouse("mousePressed", 700, 880);
for (let i = 1; i <= 6; i++) await mouse("mouseMoved", 700 + 20 * i, 880 - 10 * i, { buttons: 1 }); await mouse("mouseReleased", 820, 820); await sleep(200);
const dx = (await ev("LAB.tx")) - tx0; log("pan dx", dx); if (Math.abs(dx - 120) > 6) fail("drag did not pan by the drag distance: " + dx);
await ev("document.getElementById('fit').click()"); await sleep(300);
// real wheel zoom: out to the map level, then each level
await wheelTo(0.25); await audit("zoomed out 25%"); await shot("2-zoomed-out");
await ev("LAB.fit()"); await wheelTo(0.5); await audit("map 50%"); await shot("3-map");
await centreOn("workflow/borrow", 0.5); await wheelTo(1.0); await audit("flow 100% (wheel)"); await shot("4-flow");
await centreOn("workflow/borrow", 1.0, 0, 0); await shot("4b-flow-borrow");
await centreOn("workflow/borrow", 1.7); await wheelTo(1.7); await audit("detail 170% (wheel)"); await shot("5-detail-borrow");
for (const [sub, s, name, dx2, dy2] of [["workflow/remind", 1.6, "6-detail-remind", 0, 0], ["workflow/notify", 1.6, "6b-detail-notify", 0, 0], ["entity/loan", 1.5, "7-entity-loan-detail", 0, 0], ["actor/member", 1.2, "8-actor-card", 0, 0], ["goal/tools", 1.2, "9-goal-card", 0, 150], ["capability/lend", 1.2, "10-capability-card", 0, 0], ["workflow/notify", 1.0, "11-flow-notify", 0, 0]]) {
  await centreOn(sub, s, dx2, dy2); await sleep(200); await audit(name); await shot(name); }
// hover and click with the real mouse: a mention (one tooltip), a block (selection card), an edge, the relations panel
await ev("LAB.fit()"); await sleep(200);
let p = await blockPos("goal/tools");
const mp = await ev("(()=>{const r=document.querySelector('.blk .mn text.mt').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()");
await mouse("mouseMoved", mp[0], mp[1], { button: "none" }); await sleep(250);
const tipInfo = await ev("[document.querySelectorAll('#tip').length,getComputedStyle(document.getElementById('tip')).display,document.querySelectorAll('svg title').length].join()");
log("tooltip on a mention (count,display,svg titles):", tipInfo); if (tipInfo !== "1,block,0") fail("hover tooltip: expected one custom tooltip and no native titles in the svg: " + tipInfo);
await shot("11b-hover-mention");
await mouse("mousePressed", p[0], p[1]); await mouse("mouseReleased", p[0], p[1]); await sleep(300); await shot("12-selected-goal");
await audit("selected goal card open");
p = await blockPos("workflow/remind"); await mouse("mouseMoved", p[0], p[1], { button: "none" }); await mouse("mousePressed", p[0], p[1]); await mouse("mouseReleased", p[0], p[1]); await sleep(300);
const sel = await ev("LAB.sel"); log("selected after click", sel); if (!/remind/.test(sel || "")) fail("click did not select the Remind workflow");
await shot("13-selected-remind"); await audit("selected remind");
const sm = await ev("(()=>{const r=document.querySelector('#rel summary').getBoundingClientRect();return [r.left+40,r.top+10]})()"); await mouse("mouseMoved", sm[0], sm[1], { button: "none" }); await mouse("mousePressed", sm[0], sm[1]); await mouse("mouseReleased", sm[0], sm[1]); await sleep(300);
await shot("14-relations-panel"); await audit("relations panel open");
await mouse("mouseMoved", 5, 600, { button: "none" }); await send("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape" }); await sleep(200);
await ev("LAB.fit()"); await sleep(200); await audit("default fit again");
// Loan badge: fields top to bottom with values
await centreOn("workflow/borrow", 1.7); const bo = await audit("detail (badge check)");
const loan = bo.badges.find((b) => b.target === "loan");
log("loan badge", JSON.stringify(loan));
if (!loan || loan.names.length < 3) fail("Loan badge does not list its fields"); else if (!loan.values.length) fail("Loan badge shows no values");
if (errs.length) for (const e of [...new Set(errs)]) fail("console: " + e);
log(fails.length ? `\n${fails.length} FAILURES` : "\nALL CHECKS PASSED");
proc.kill(); fs.rmSync(prof, { recursive: true, force: true });
process.exit(fails.length ? 1 : 0);
