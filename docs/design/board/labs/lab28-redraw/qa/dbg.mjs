// usage: CHROME=... node dbg.mjs "<js expression>"  prints the value in the loaded page
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const port = 9300 + Math.floor(Math.random() * 100);
const proc = spawn(process.env.CHROME, ["--headless=new", "--no-sandbox", "--disable-gpu", `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/claude-501/dbg${port}`, "file://" + path.resolve(here, "../index.html")], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let tabs; for (let i = 0; i < 50; i++) { try { tabs = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); if (tabs.length) break; } catch {} await sleep(200); }
const ws = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
await sleep(1500);
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id === 1) { console.log(d.result.result?.value ?? JSON.stringify(d.result)); proc.kill(); process.exit(0); } };
ws.send(JSON.stringify({ id: 1, method: "Runtime.evaluate", params: { expression: process.argv[2], returnByValue: true } }));
