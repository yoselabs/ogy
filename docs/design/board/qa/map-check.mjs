// Real-input checks of the Map: node docs/design/board/qa/map-check.mjs [tool|ogy|synthetic] [width]  (from the repository root)
// Reads only: the tool library runs on a temporary copy, the real KB is only read, the synthetic KB is built by synthetic.mjs.
// Every scene is a fresh page load (so "first render" is real); clicks are Input.dispatchMouseEvent. The bulk reachability walk
// sets location.hash (a navigation, not a click) because it visits every area; the click path is checked for one tile per run.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, run, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };

// Everything the page claims is compared with the inspection and standing documents read from the same server.
const PROBE = `(async () => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const doc = await (await fetch('/api/inspection', { credentials: 'same-origin' })).json();
  const st = await (await fetch('/api/standing', { credentials: 'same-origin' })).json();
  const layer = q('[data-part=map]').dataset.layer;
  const top = doc.entries.filter(e => e.layer === layer && typeof e.parent !== 'string');
  const areas = [...new Set(top.map(e => e.area))].sort();
  const tiles = all('[data-part=tile]');
  const shown = tiles.map(t => t.dataset.address.split('/')[1]).sort();
  const wrongCounts = [], wrongLinks = [], wrongMarks = [], wrongGoals = [];
  for (const t of tiles) {
    const [, area] = t.dataset.address.split('/');
    const mine = top.filter(e => e.area === area && e.kind !== 'area');
    const expected = {}; for (const e of mine) expected[e.kind] = (expected[e.kind] || 0) + 1;
    const got = {}; for (const c of t.querySelectorAll('.count')) got[c.dataset.kind] = Number(c.querySelector('[data-part=count]').textContent);
    if (JSON.stringify(Object.entries(expected).sort()) !== JSON.stringify(Object.entries(got).sort())) wrongCounts.push(area + ' ' + JSON.stringify(expected) + ' vs ' + JSON.stringify(got));
    for (const a of t.querySelectorAll('a.count, h2 a')) if (!a.getAttribute('href').startsWith('#/' + layer + '/' + area)) wrongLinks.push(a.getAttribute('href'));
    const row = st.areas[layer + '/' + area];
    const w = t.querySelector('[data-stat=waiting] b');
    if ((row?.questions || 0) !== (w ? Number(w.textContent) : 0)) wrongMarks.push(area + ' waiting ' + row?.questions + ' vs ' + w?.textContent);
    const owedExpected = st.work.filter(x => x.address === layer + '/' + area || x.address.startsWith(layer + '/' + area + '/')).length;
    const o = t.querySelector('[data-stat=owed] b');
    if (owedExpected !== (o ? Number(o.textContent) : 0)) wrongMarks.push(area + ' owed ' + owedExpected + ' vs ' + o?.textContent);
    const goalsHere = mine.filter(e => e.kind === 'goal').length;
    const lines = t.querySelectorAll('.goal-line').length, more = t.querySelector('.goal-lines .more');
    if (goalsHere && lines + (more ? Number(more.textContent.match(/\\d+/)[0]) : 0) < goalsHere) wrongGoals.push(area + ' goals ' + goalsHere + ' lines ' + lines);
  }
  const noGoal = tiles.filter(t => t.querySelector('.gap')).map(t => t.dataset.address.split('/')[1]);
  const goalLayer = !!doc.ontology.kinds.goal?.layers?.includes(layer);
  const items = all('.map [data-part], .map .card-header, .map .gap, .map .mention, .map .says, .map .count, .map .stat, .map h1, .map h2');
  const rects = items.filter(e => e.checkVisibility()).map(e => [e, e.getBoundingClientRect()]).filter(([, r]) => r.width > 1 && r.height > 1);
  let overlaps = 0; const where = [];
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const [a, ra] = rects[i], [b, rb] = rects[j];
    if (a.contains(b) || b.contains(a)) continue;
    if (Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left) > 2 && Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top) > 2) { overlaps++; where.push((a.dataset.part || a.className) + '|' + (b.dataset.part || b.className)); }
  }
  const measure = performance.getEntriesByName('map-render')[0];
  const small = all('.map a, .map button').filter(e => { const r = e.getBoundingClientRect(); return r.height < 28; }).length;
  return JSON.stringify({
    layer, areas, shown, wrongCounts, wrongLinks, wrongMarks, wrongGoals, noGoal, goalLayer, totals: st.totals, standingAreas: Object.keys(st.areas),
    marks: all('[data-part=marks]').length, goalLines: all('.goal-line').length, kindsPerTile: tiles.map(t => t.querySelectorAll('.count').length),
    bare: all('.map .mention:not([data-renderer])').length, renderMs: measure ? Math.round(measure.duration * 10) / 10 : null,
    overlaps, where: where.slice(0, 4), small,
    inner: all('.map *').filter(e => { const s = getComputedStyle(e); return /(auto|scroll)/.test(s.overflowY + s.overflowX) && (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1); }).map(e => e.className),
    wide: all('.map *').filter(e => e.getBoundingClientRect().right > innerWidth + 1).length, scrollW: [document.documentElement.scrollWidth, innerWidth],
    columns: new Set(tiles.map(t => Math.round(t.getBoundingClientRect().left))).size,
    tileRect: tiles[0] ? (r => [Math.round(r.width), Math.round(r.height)])(tiles[0].getBoundingClientRect()) : null,
    layerTab: q('#header [aria-current=page]')?.textContent ?? null, crumb: q('#crumb')?.innerText.replace(/\\s+/g, ' ').trim(),
    headerRects: JSON.stringify(all('#header .btn, #header .tab').map(e => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })),
    h1: q('.map h1')?.textContent,
  });
})()`;
const MEASURE = `(async () => { window.__scope = '.map'; const p = JSON.parse(await ${PROBE}); return JSON.stringify({ probe: p, text: ${TEXT}, contrast: ${CONTRAST}, words: ${VIEWER_WORDS} }); })()`;

// Every kind a tile lists is reachable on the area page its count links to: in the chain, the entities or a kind row.
const REACH = `(async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const tiles = [...document.querySelectorAll('[data-part=tile]')].map(t => [t.dataset.address, [...t.querySelectorAll('.count')].map(c => [c.dataset.kind, Number(c.querySelector('[data-part=count]').textContent), c.getAttribute('href')])]);
  const missing = [];
  for (const [scope, kinds] of tiles) for (const [kind, count, href] of kinds) {
    location.hash = href.replace(/^#/, ''); await wait(60);
    const page = document.querySelector('.area');
    const rows = page ? [...page.querySelectorAll('.kind-row[data-kind="' + kind + '"] [data-part=count]')] : [];
    const seen = rows.length ? Number(rows[0].textContent) : (page?.querySelector('.mention.kind-' + kind) ? count : null);
    if (seen !== count) missing.push(scope + ' ' + kind + ' ' + count + ' vs ' + seen);
  }
  return JSON.stringify({ visited: tiles.reduce((n, t) => n + t[1].length, 0), missing: missing.slice(0, 12), missingCount: missing.length });
})()`;
const parse = values => JSON.parse(values.find(value => value.startsWith('{')));
const exact = (a, b) => JSON.stringify(a) === JSON.stringify(b);

function judge(name, m, expect = {}) {
  const { probe, text, contrast, words } = m;
  if (!exact(probe.areas, probe.shown)) fail(name + ' tiles ' + probe.shown.length + ' vs areas ' + probe.areas.length + ' ' + probe.areas.filter(a => !probe.shown.includes(a)));
  for (const key of ['wrongCounts', 'wrongLinks', 'wrongMarks', 'wrongGoals']) if (probe[key].length) fail(name + ' ' + key + ' ' + probe[key].slice(0, 3).join('; '));
  const expectedGap = probe.goalLayer ? probe.noGoal.length : 0;
  if (!probe.goalLayer && probe.noGoal.length) fail(name + ' a layer without goals shows the no-goal gap');
  if (probe.overlaps) fail(name + ' overlaps ' + probe.overlaps + ' ' + probe.where.join(','));
  if (probe.inner.length) fail(name + ' scrolls inside ' + probe.inner.join(','));
  if (probe.bare) fail(name + ' ' + probe.bare + ' names not drawn by mention()');
  if (probe.wide) fail(name + ' ' + probe.wide + ' elements past the right edge');
  if (probe.scrollW[0] > probe.scrollW[1]) fail(name + ' horizontal scroll ' + probe.scrollW);
  if (probe.columns > 1 && probe.scrollW[1] <= 720) fail(name + ' phone is not one column ' + probe.columns);
  if (probe.small && probe.scrollW[1] <= 720) fail(name + ' ' + probe.small + ' touch targets under 28px');
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
  if (probe.renderMs == null || probe.renderMs > 300) fail(name + ' first render ' + probe.renderMs + ' ms');
  if (probe.layerTab !== (probe.layer === 'product' ? 'Product' : 'Software')) fail(name + ' layer tab ' + probe.layerTab);
  for (const [key, check] of Object.entries(expect)) if (!check(probe[key], probe)) fail(name + ' ' + key + ' = ' + JSON.stringify(probe[key]));
  console.log(name, JSON.stringify({ tiles: probe.shown.length, noGoal: expectedGap, marks: probe.marks, ms: probe.renderMs, tile: probe.tileRect, cols: probe.columns, type: text, contrast: contrast.min }));
}

const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });
const LAYERS = [['product', ''], ['software', 'software']];
const expectations = {
  tool: { product: { tiles: v => true }, software: {} },
  ogy: {},
  synthetic: {},
};

async function runs(label, repo, wait) {
  const started = await startServer(repo);
  try {
    const scenes = [];
    for (const width of widths) for (const theme of ['light', 'dark']) for (const [layer, route] of LAYERS)
      scenes.push({ name: `map-${label}-${width}-${theme}-${layer}`, route, fresh: true, ...sizeOf(width), wait, actions: [{ media: theme }, { eval: MEASURE }] });
    // The click path at a phone: a count on the home opens the area page, a second click on the header layer tab comes back.
    scenes.push({ name: `map-${label}-390-click`, route: '', fresh: true, ...sizeOf(390), wait,
      actions: [{ click: '[data-part=tile] .count' }, { wait: 600, eval: 'location.hash' }, { eval: 'document.querySelector(".area") ? "area-page" : "no-area-page"' }, { click: '#header .tab[data-layer=product]' }, { wait: 600, eval: 'location.hash + "|" + document.querySelectorAll("[data-part=tile]").length' },
        { click: '[data-part=tile] h2 a' }, { wait: 600, eval: 'location.hash + "|" + (document.querySelector(".area") ? "area-page" : "no-area-page")' }] });
    scenes.push({ name: `map-${label}-390-reach`, route: '', fresh: true, ...sizeOf(390), wait, actions: [{ wait: 300, eval: REACH }] });
    const results = await browse('map-' + label, scenes, started);
    const measured = results.filter(row => row.name.match(/-(light|dark)-/));
    measured.forEach(row => judge(row.name, parse(row.values), expectations[label]?.[row.name.split('-').at(-1)]));
    const click = results.find(row => row.name.endsWith('-click'));
    const [hash1, kind1, home, ...rest] = click.values;
    const [hash2, page2] = [rest[0], rest[1]];
    if (!/^#\/(product|software)\/[^/?]+\?kind=/.test(hash1) || kind1 !== 'area-page') fail(`${click.name} count click landed on ${hash1} ${kind1}`);
    if (!home.startsWith('#/|') || Number(home.split('|')[1]) < 1) fail(`${click.name} layer tab did not return to the Map: ${home}`);
    if (!/^#\/(product|software)\/[^/?]+\|area-page$/.test(rest[0] ?? '')) fail(`${click.name} tile name click landed on ${rest[0]}`);
    console.log(click.name, hash1, kind1, home, rest[0]);
    const reach = parse(results.find(row => row.name.endsWith('-reach')).values);
    if (reach.missingCount) fail(`${label} reach: ${reach.missingCount} of ${reach.visited} counts not visible on their area page: ${reach.missing.join('; ')}`);
    console.log(`map-${label}-reach`, JSON.stringify({ visited: reach.visited, missing: reach.missingCount }));
  } finally { await started.stop(); }
}

if (mode === 'tool') await runs('tool', await toolCopy('map-qa-tool'), 2500);
else if (mode === 'synthetic') {
  const made = await run('node', [join(here, 'synthetic.mjs')], { cwd: process.cwd() });
  if (made.code !== 0) throw Error('synthetic: ' + made.stderr);
  await runs('synthetic', JSON.parse(made.stdout).repo, 12000);
} else await runs('ogy', '.', 12000);
console.log(failures.length ? failures.length + ' failures' : 'all map checks passed');
process.exit(failures.length ? 1 : 0);
