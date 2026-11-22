// Real-input checks of the shell: node shell-check.mjs <repo> [width]  (run from the repository root)
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const scratch = dirname(here);
const out = process.env.OUT || here;
const repo = process.argv[2];
const width = Number(process.argv[3] || 1440);
const height = width === 390 ? 844 : 1000;
mkdirSync(out, { recursive: true });

function run(command, args, env) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { env: { ...process.env, TMPDIR: '/var/tmp', ...env } });
    let stdout = '', stderr = '';
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    child.on('error', reject);
    child.on('exit', code => resolve({ code, stdout, stderr }));
  });
}

const server = spawn('uv', ['run', '--frozen', '--no-sync', 'python', scratch + '/s3-data-serve.py', repo], { env: { ...process.env, TMPDIR: '/var/tmp' } });
const first = await new Promise((resolve, reject) => {
  server.stdout.on('data', chunk => { const m = String(chunk).match(/http:\/\/\S+/); if (m) resolve(m[0]); });
  server.on('exit', code => reject(Error('server exited ' + code)));
});
const base = new URL(first).origin;

const HEADER_RECTS = `JSON.stringify([...document.querySelectorAll('#header button, #header a, #header span.tab, #header .hdr-id, #header kbd')].map(e => { const r = e.getBoundingClientRect(); return [e.className || e.tagName, Math.round(r.left * 10) / 10, Math.round(r.top * 10) / 10, Math.round(r.width * 10) / 10, Math.round(r.height * 10) / 10]; }))`;
const COUNTS = `fetch('/api/standing').then(r => r.json()).then(d => JSON.stringify({ shown: [...document.querySelectorAll('#strip [data-stat]')].map(e => [e.dataset.stat, Number(e.querySelector('b').textContent)]),
  totals: d.totals, waitingDecisions: Object.values(d.decisions).filter(x => x.status === 'waiting').length,
  tab: document.querySelector('#tab-waiting .tab-count')?.textContent.trim(), repository: d.repository, headerName: document.querySelector('.hdr-name')?.textContent }))`;
const FOCUS = `JSON.stringify((() => { const e = document.activeElement; const s = getComputedStyle(e);
  return [e.closest('#header,#strip,#crumb,#main,#rail')?.id || 'none', e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + ' ' + (e.textContent || '').trim().slice(0, 14), s.outlineStyle, s.outlineWidth]; })())`;
const SCROLL = `JSON.stringify([document.documentElement.scrollWidth, innerWidth, document.body.scrollWidth])`;
const RESET = `(() => { document.body.setAttribute('tabindex', '-1'); document.body.focus(); document.body.removeAttribute('tabindex'); return 'reset'; })()`;
const tab = { key: 'Tab', code: 'Tab', vk: 9 };
const routes = ['#/board', '#/nowhere', '#/board?rail=waiting', '#/board?sel=product/lending/workflow/borrow'];
const scenes = routes.map((hash, index) => ({
  name: 'shell-' + width + '-' + index, size: [width, height], mobile: width === 390, wait: index === 0 ? Number(process.env.WAIT || 3000) : 3000,
  url: (index === 0 ? first.replace(/\/\?/, '/?') + hash : base + '/' + hash),
  actions: [{ eval: HEADER_RECTS }, ...(index === 0 ? [{ eval: COUNTS }, { eval: `document.querySelector('#header button').disabled` }] : []), { eval: SCROLL },
    { eval: RESET, wait: 100 }, ...Array.from({ length: 16 }, () => [tab, { eval: FOCUS }]).flat()],
}));
// Real clicks: a rail tab must not move anything, and Back must return to the previous route.
scenes.push({ name: 'shell-' + width + '-click', size: [width, height], mobile: width === 390, wait: 2500, url: base + '/#/nowhere',
  actions: [{ eval: HEADER_RECTS }, { click: '#tab-waiting' }, { eval: 'location.hash' }, { eval: HEADER_RECTS },
    { eval: `document.querySelector('#tab-waiting').getAttribute('aria-selected')` },
    { click: '#crumb a' }, { eval: 'location.hash' }, { eval: `document.querySelector('#header button').disabled` },
    { click: '#header button' }, { eval: 'location.hash' }] });
const spec = join(out, 'shell-' + width + '.json');
writeFileSync(spec, JSON.stringify(scenes));
const result = await run('node', [join(here, 'cdp.mjs'), spec], { OUT: out });
server.kill();
const lines = result.stdout.trim().split('\n').map(line => line.split(' | '));
const failures = [];
const rects = [];
lines.forEach(parts => {
  const name = parts[0];
  const evals = parts.slice(1).filter(value => !/^vp=\d+x\d+/.test(value.trim()));
  if (name.endsWith('-click')) {
    const [before, hashAfterTab, after, selected, hashCrumb, backDisabled, hashBack] = evals;
    if (before !== after) failures.push('rail tab click moved a header control');
    if (!hashAfterTab.includes('rail=waiting')) failures.push('rail tab did not set rail=waiting: ' + hashAfterTab);
    if (selected !== 'true') failures.push('rail tab not selected');
    if (!/^#\/($|board|\?)/.test(hashCrumb) && hashCrumb !== '') failures.push('breadcrumb link did not go to the board: ' + hashCrumb);
    if (backDisabled !== 'false') failures.push('Back is disabled after one navigation');
    if (hashBack !== '#/nowhere?rail=waiting' && hashBack !== '#/nowhere') failures.push('Back did not return: ' + hashBack);
    console.log(name, 'click:', evals.join(' | '));
    return;
  }
  let at = 0;
  rects.push(JSON.parse(evals[at++]));
  if (name.endsWith('-0')) {
    const counts = JSON.parse(evals[at++]);
    const shown = Object.fromEntries(counts.shown);
    for (const key of Object.keys(counts.totals)) if (shown[key] !== counts.totals[key]) failures.push('count ' + key + ' shows ' + shown[key] + ' but standing says ' + counts.totals[key]);
    if (counts.totals.waiting !== counts.waitingDecisions) failures.push('waiting ' + counts.totals.waiting + ' != waiting decisions ' + counts.waitingDecisions);
    if (Number(counts.tab) !== counts.totals.waiting) failures.push('rail Waiting count ' + counts.tab);
    if (counts.repository !== counts.headerName) failures.push('header name ' + counts.headerName);
    console.log(name, 'counts:', JSON.stringify(shown), 'waiting decisions', counts.waitingDecisions);
    if (evals[at++] !== 'true') failures.push('Back is enabled on the first page of history');
  }
  const scroll = JSON.parse(evals[at++]);
  if (scroll[0] > scroll[1] || scroll[2] > scroll[1]) failures.push(name + ' horizontal scroll ' + scroll);
  let focus = evals.slice(at + 1).map(value => JSON.parse(value));
  // One pass of Tab: stop when focus comes back to the first stop. The canvas is out of scope, so board routes check six stops.
  const wrap = name.endsWith('-1') ? focus.findIndex((f, i) => i > 0 && f[1] === focus[0][1] && f[0] === focus[0][0]) : -1;
  focus = focus.slice(0, wrap > 0 ? wrap : name.endsWith('-1') ? focus.length : 6);
  const leave = focus.findIndex(f => f[0] === 'none');
  if (leave >= 0) focus = focus.slice(0, leave);
  const order = ['header', 'strip', 'crumb', 'main', 'rail'];
  let last = -1;
  focus.forEach(([region, label, style, widthPx]) => {
    const rank = order.indexOf(region);
    if (rank < last) failures.push(name + ' tab order went back to ' + region + ' at ' + label);
    last = Math.max(last, rank);
    if (!(style === 'solid' && widthPx === '2px')) failures.push(name + ' no 2px ring on ' + label + ' (' + style + ' ' + widthPx + ')');
  });
  if (name.endsWith('-1')) for (const region of ['header', 'main', 'rail']) if (!focus.some(f => f[0] === region)) failures.push(name + ' Tab never reached ' + region);
  console.log(name, 'tab:', focus.map(f => f[0] + ':' + f[1].trim()).join(' > '));
});
for (let i = 1; i < rects.length; i++) if (JSON.stringify(rects[i]) !== JSON.stringify(rects[0])) failures.push('header rects differ on route ' + i + ': ' + JSON.stringify(rects[i]) + ' vs ' + JSON.stringify(rects[0]));
if (result.stdout.includes('ERRORS:')) failures.push('page errors: ' + result.stdout.split('ERRORS:')[1]);
console.log(failures.length ? 'FAIL\n' + failures.join('\n') : 'PASS shell-check ' + width);
process.exitCode = failures.length ? 1 : 0;
