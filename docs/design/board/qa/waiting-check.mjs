// Real-input checks of the waiting list: node waiting-check.mjs <repo> <set> <width> <theme>  (run from the repository root)
// Waits for the list with a MutationObserver (no timer in the page), then drives mouse and keys through CDP.
import { writeFileSync, mkdirSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { startBoard, stopBoard } from './serve.mjs';
import { OVERLAP } from './measures.js';

const here = dirname(fileURLToPath(import.meta.url));
const out = process.env.OUT || here;
const [repo, set, widthText = '1440', theme = 'light'] = process.argv.slice(2);
const width = Number(widthText);
const height = width === 390 ? 844 : 1000;
mkdirSync(out, { recursive: true });

const SETTLED = `new Promise(resolve => { const done = () => document.querySelector('#main .waiting-row, #main [data-empty], #main .waiting-note:not(.is-loading)'); if (done()) return resolve('ready'); new MutationObserver((_, o) => { if (done()) { o.disconnect(); resolve('ready'); } }).observe(document.body, { childList: true, subtree: true }); })`;
const LOADING = `JSON.stringify({ loading: document.querySelector('#main .is-loading')?.textContent || null, header: document.querySelector('#header').textContent.length > 0 })`;
const ROWS = `fetch('/api/standing').then(r => r.json()).then(d => JSON.stringify({
  expected: Object.entries(d.decisions).filter(([, v]) => v.status === 'waiting').map(([k]) => k).sort(),
  shown: [...document.querySelectorAll('#main .waiting-row')].map(e => e.dataset.address).sort(),
  rail: [...document.querySelectorAll('#rail .waiting-row')].length,
  count: d.totals.waiting, heading: document.querySelector('#main h1').textContent.trim(),
  empty: document.querySelector('#main [data-empty]')?.textContent || null,
  columns: [...new Set([...document.querySelectorAll('#main .waiting-row')].map(e => Math.round(e.getBoundingClientRect().left)))],
  scrollW: [document.documentElement.scrollWidth, innerWidth] }))`;
const ROWBOX = `JSON.stringify((() => { const R = e => e.getBoundingClientRect(); const rows = [...document.querySelectorAll('#main .waiting-row')].map(R);
  let over = 0; for (let i = 0; i < rows.length; i++) for (let j = i + 1; j < rows.length; j++) if (Math.min(rows[i].right, rows[j].right) - Math.max(rows[i].left, rows[j].left) > 1 && Math.min(rows[i].bottom, rows[j].bottom) - Math.max(rows[i].top, rows[j].top) > 1) over++;
  const main = R(document.querySelector('#main')), rail = R(document.querySelector('#rail'));
  const sheet = innerWidth <= 720 && rail.top < main.bottom - 1 ? 1 : 0;
  const clipped = [...document.querySelectorAll('#main .waiting-row, #rail .waiting-row')].filter(e => e.scrollWidth > e.clientWidth + 1).length;
  return { rowOverlaps: over, railOverMain: sheet, clipped }; })())`;
const HASH = 'location.hash';
// Back only when a row was opened (an empty list opens nothing, and Back would leave the page).
const BACK = `(location.hash === '#/waiting' ? 'stayed' : (history.back(), new Promise(r => { addEventListener('hashchange', () => r(location.hash), { once: true }); setTimeout(() => r('no-navigation'), 2000); })))`;
const FOCUSED = `document.activeElement.closest('.waiting-row')?.dataset.address || document.activeElement.tagName`;
const RECTS = `JSON.stringify([...document.querySelectorAll('#header *, #strip *')].map(e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width)]; }))`;
const { server, url } = await startBoard(repo);
const base = new URL(url).origin;
const prefix = `${set}-${width}-${theme}`;
const scenes = [
  { name: `${prefix}-waiting-loading`, size: [width, height], mobile: width === 390, wait: 400, url,
    actions: [{ media: theme }, { eval: `location.hash = '#/waiting'` }, { eval: LOADING }, { shot: `${prefix}-waiting-loading-state` }] },
  { name: `${prefix}-waiting`, size: [width, height], mobile: width === 390, wait: 100, url: base + '/#/waiting',
    actions: [{ media: theme }, { eval: SETTLED }, { eval: ROWS }, { eval: OVERLAP }, { eval: ROWBOX }, { eval: RECTS }, { shot: `${prefix}-waiting-ready` },
      { key: 'g', code: 'KeyG', vk: 71 }, { key: 'j', code: 'KeyJ', vk: 74 }, { eval: FOCUSED },
      { key: 'j', code: 'KeyJ', vk: 74 }, { eval: FOCUSED }, { key: 'k', code: 'KeyK', vk: 75 }, { eval: FOCUSED },
      { key: 'Enter', code: 'Enter', vk: 13 }, { eval: HASH }, { eval: BACK },
      { eval: SETTLED }, { eval: FOCUSED }, { eval: HASH },
      { click: '#main .waiting-row .waiting-question, #main .waiting-row .kind-word' }, { eval: HASH }, { shot: `${prefix}-after-click` },
      { eval: BACK }, { eval: SETTLED }, { eval: FOCUSED },
      { click: '#tab-waiting' }, { eval: `document.querySelector('#rail').dataset.open + ' ' + document.querySelectorAll('#rail .waiting-row').length` }, { eval: RECTS },
      { shot: `${prefix}-rail` }] },
];
const spec = join(out, `${prefix}-waiting-check.json`);
writeFileSync(spec, JSON.stringify(scenes));
const result = await new Promise(resolve => {
  const child = spawn('node', [join(here, 'cdp.mjs'), spec], { env: { ...process.env, OUT: out } });
  let stdout = '', stderr = '';
  child.stdout.on('data', chunk => { stdout += chunk; });
  child.stderr.on('data', chunk => { stderr += chunk; });
  child.on('exit', code => resolve({ code, stdout, stderr }));
});
await stopBoard(server);
const failures = [];
const [loadingLine, mainLine] = result.stdout.trim().split('\n');
if (!loadingLine || !mainLine) {
  console.log(result.stdout, result.stderr);
  process.exit(1);
}
const loading = JSON.parse(loadingLine.split(' | ')[2]);
console.log('loading state:', JSON.stringify(loading));
const parts = mainLine.split(' | ');
// parts: name, media(none), SETTLED, ROWS, OVERLAP, RECTS, then key evals...
const ok = parts.slice(1).filter(value => value !== 'undefined');
const rows = JSON.parse(ok[1]);
if (JSON.stringify(rows.expected) !== JSON.stringify(rows.shown)) failures.push('rows ' + JSON.stringify(rows.shown) + ' != waiting decisions ' + JSON.stringify(rows.expected));
if (rows.count !== rows.expected.length) failures.push('totals.waiting ' + rows.count + ' != ' + rows.expected.length);
if (rows.expected.length === 0 && !rows.empty) failures.push('no empty state');
if (width === 390 && rows.columns.length > 1) failures.push('more than one column at 390: ' + rows.columns);
if (rows.scrollW[0] > rows.scrollW[1]) failures.push('horizontal scroll ' + rows.scrollW);
const overlap = ok[2];
const box = JSON.parse(ok[3]);
if (box.rowOverlaps || box.railOverMain || box.clipped) failures.push('row boxes ' + ok[3]);
if (!/blockOverlaps=0 /.test(overlap)) failures.push(overlap);
console.log(prefix, 'rows', rows.shown.length, 'overlap', overlap);
console.log(ok.slice(4).join(' | '));
if (result.stdout.includes('ERRORS:')) failures.push('page errors: ' + result.stdout.split('ERRORS:')[1]);
console.log(failures.length ? 'FAIL\n' + failures.join('\n') : 'PASS waiting-check ' + prefix);
process.exitCode = failures.length ? 1 : 0;
