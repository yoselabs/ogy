// usage: CHROME=<chrome binary> OUT=<folder> node check.mjs   (real mouse and wheel events over CDP, same pattern as ../../../qa/cdp.mjs)
import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = process.env.OUT || path.join(here, "shots");
fs.mkdirSync(OUT, { recursive: true });
const port = 9500 + Math.floor(Math.random() * 400);
const proc = spawn(process.env.CHROME, ["--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${port}`, `--user-data-dir=${OUT}/prof${port}`, "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let tabs;
for (let i = 0; i < 50; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); if (tabs.length) break; } catch {} await sleep(200); }
const ws = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const pend = new Map(), errs = [];
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d.result || d); pend.delete(d.id); }
  else if (d.method === "Runtime.exceptionThrown") errs.push(d.params.exceptionDetails.exception?.description?.split("\n").slice(0, 3).join(" | ") || d.params.exceptionDetails.text);
  else if (d.method === "Runtime.consoleAPICalled" && d.params.type === "error") errs.push("console: " + d.params.args.map((a) => a.value ?? a.description).join(" ")); };
const send = (method, params = {}) => new Promise((r) => { pend.set(++id, r); ws.send(JSON.stringify({ id, method, params })); });
const ev = async (e) => { const r = await send("Runtime.evaluate", { expression: e, returnByValue: true, awaitPromise: true }); return r.result?.value ?? r.exceptionDetails?.exception?.description; };
const mouse = (type, x, y, o = {}) => send("Input.dispatchMouseEvent", { type, x, y, button: "left", clickCount: 1, ...o });
const shot = async (name) => { const r = await send("Page.captureScreenshot", { format: "png" }); fs.writeFileSync(`${OUT}/${name}.png`, Buffer.from(r.data, "base64")); };
const centre = (sel) => ev(`(()=>{const e=document.querySelector(${JSON.stringify(sel)});if(!e)return null;const r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()`);
const click = async (x, y) => { await mouse("mouseMoved", x, y, { button: "none" }); await mouse("mousePressed", x, y); await mouse("mouseReleased", x, y); await sleep(700); };
const state = () => ev(`B.cam.s.toFixed(2)+" "+document.getElementById("world").dataset.lod`);
const log = (...a) => console.log(...a);

await send("Page.enable"); await send("Runtime.enable");
const theme = process.env.THEME || "light";
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: theme }] });
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: "file://" + path.resolve(here, "../index.html") }); await sleep(1500);
log("start", await state(), await ev("JSON.stringify(B.rects)")); await shot("1-zoomed-out-areas");
// real drag pans
const before = await ev("B.cam.x"); await mouse("mouseMoved", 700, 500, { button: "none" }); await mouse("mousePressed", 700, 500);
for (let i = 1; i <= 6; i++) await mouse("mouseMoved", 700 + 20 * i, 500 + 10 * i, { buttons: 1 }); await mouse("mouseReleased", 820, 560); await sleep(300);
log("pan dx", (await ev("B.cam.x")) - before);
// real wheel zooms at the cursor
await send("Input.dispatchMouseEvent", { type: "mouseWheel", x: 900, y: 400, deltaX: 0, deltaY: -300 }); await sleep(300);
log("after wheel", await state()); await shot("2-after-wheel");
await send("Input.dispatchMouseEvent", { type: "mouseWheel", x: 900, y: 400, deltaX: 0, deltaY: 40, modifiers: 2 }); await sleep(200); // trackpad pinch arrives as ctrl+wheel
log("after pinch-out", await state());
// click the borrow workflow header at areas level, flies in
await ev("document.getElementById('fit').click()"); await sleep(700);
let p = await centre('.frame[data-a$="workflow/borrow"] .frame-hd'); await click(p[0], p[1]); await sleep(500);
log("borrow", await state()); await shot("3-borrow-detail");
await ev("document.getElementById('fit').click()"); await sleep(700);
// decision: late fee (answered, ogy impact data) and reply wait (waiting, derived)
await ev(`B.fitRect(B.worldRect(document.querySelector('[data-a$="decision/late-fee"]')),200,1)`); await sleep(600);
p = await centre('.dec[data-a$="decision/late-fee"]'); await click(p[0], p[1]); await sleep(700);
log("late-fee", await state(), await ev("document.querySelectorAll('.impact').length+' impacted, panel '+document.getElementById('panel').classList.contains('open')")); await shot("4-decision-late-fee");
await ev("B.select(null)"); await ev(`B.fitRect(B.worldRect(document.querySelector('[data-a$="decision/reply-wait"]')),200,1)`); await sleep(600);
p = await centre('.dec[data-a$="decision/reply-wait"]'); await click(p[0], p[1]); await sleep(700);
log("reply-wait", await ev("document.querySelectorAll('.impact').length+' impacted'")); await shot("5-decision-reply-wait");
// interface
await ev("B.select(null)"); await ev(`B.fitRect(B.worldRect(document.querySelector('[data-a$="interface/borrow-page"]')),300,1)`); await sleep(600);
p = await centre('.screen[data-a$="interface/borrow-page"] .bar'); await click(p[0], p[1]); await shot("6-interface");
// overlap check: text boxes of different leaf elements must not intersect at detail zoom
await ev("B.select(null)"); await ev(`B.fitRect(B.worldRect(document.querySelector('.frame[data-a$="workflow/borrow"]')),40,1.2)`); await sleep(600);
log("overlaps", await ev(`(()=>{const els=[...document.querySelectorAll('.step .hd b,.step .says,.row .rl,.row .to,.fx,.end b,.chip,.btn,.cli')].filter(e=>e.offsetParent&&getComputedStyle(e).visibility!=='hidden');
 const rs=els.map(e=>[e,e.getBoundingClientRect()]);let n=[];for(let i=0;i<rs.length;i++)for(let j=i+1;j<rs.length;j++){const a=rs[i][1],b=rs[j][1];if(rs[i][0].contains(rs[j][0])||rs[j][0].contains(rs[i][0]))continue;
 const w=Math.min(a.right,b.right)-Math.max(a.left,b.left),h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);if(w>2&&h>2)n.push(rs[i][0].textContent.slice(0,20)+' x '+rs[j][0].textContent.slice(0,20));}return n.length+' '+n.slice(0,6).join(' ; ')})()`));
log("min font px", await ev(`Math.min(...[...document.querySelectorAll('#world *')].filter(e=>e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&getComputedStyle(e).visibility!=='hidden'&&e.offsetParent).map(e=>parseFloat(getComputedStyle(e).fontSize)*B.cam.s)).toFixed(1)`));
await shot("7-workflow-fit");
log(errs.length ? "ERRORS: " + [...new Set(errs)].join(" ;; ") : "no page errors");
ws.close(); proc.kill(); await new Promise((r) => proc.once("exit", r)); fs.rmSync(`${OUT}/prof${port}`, { recursive: true, force: true, maxRetries: 5 }); process.exit(0);
