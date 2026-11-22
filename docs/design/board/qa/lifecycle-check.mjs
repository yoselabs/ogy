// Real-input checks of the lifecycle page and the owed list: node docs/design/board/qa/lifecycle-check.mjs [tool|ogy] [width]
// (from the repository root). Reads only: the tool library runs on a temporary copy, the real KB is only read.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, OVERLAP, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };

// The overlap script of the standing protocol with this page's two constants: its blocks (states and edge labels) and its edge layer.
const OVERLAP_HERE = OVERLAP.replace('"#vp path, #vp polyline, #vp line"', '".lc-svg path"');

// Everything the page claims is compared with the inspection document and the standing read from the same server.
const LIFECYCLE = `(async () => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const doc = await (await fetch('/api/inspection', { credentials: 'same-origin' })).json();
  let standing = null;
  for (let i = 0; i < 90 && !standing?.totals; i++) { standing = await (await fetch('/api/standing', { credentials: 'same-origin' })).json(); if (!standing.totals) await new Promise(r => setTimeout(r, 1000)); }
  const address = location.hash.replace(/^#\\/?/, '').split('?')[0];
  const everything = [...doc.entries, ...doc.parts];
  const under = prefix => everything.filter(e => typeof e.address === 'string' && e.address.startsWith(prefix + '/'));
  const states = under(address).filter(e => e.kind === 'state').map(e => e.address).sort();
  const transitions = under(address).filter(e => e.kind === 'transition');
  const effectAt = l => doc.parts.find(p => p.kind === 'effect' && p.locator.owner === l.owner && p.locator.field === l.field && p.locator.index === l.index);
  const firers = t => doc.relations.filter(r => r.field === 'on' && r.target === t.address && typeof r.source === 'object' && effectAt(r.source)?.fields.do === 'transition').map(r => r.source.owner);
  const rel = (s, f) => doc.relations.filter(r => r.source === s && r.field === f).map(r => r.target);
  const expectOwed = transitions.filter(t => !firers(t).length).map(t => t.address).sort();
  const expectEdges = transitions.reduce((n, t) => n + Math.max(1, rel(t.address, 'from').length), 0);
  const unusedInStanding = standing.work.filter(w => w.cause === 'unused' && w.address.startsWith(address + '/')).map(w => w.address).sort();
  const rows = all('[data-part=transition]');
  const paths = all('[data-part=transitions] [data-part=fired-by]');
  const blocks = all('.lc-node, .lc-label');
  const rects = blocks.filter(e => e.checkVisibility()).map(e => [e, e.getBoundingClientRect()]);
  const inner = all('.lifecycle *').filter(e => { const s = getComputedStyle(e); return /(auto|scroll)/.test(s.overflowY + s.overflowX) && (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1); }).map(e => e.className);
  const arrows = all('.lc-edge').map(e => e.getAttribute('d'));
  const stage = q('.lc-stage');
  return JSON.stringify({
    address, states, shownStates: all('.lc-node[data-part=state]').map(e => e.dataset.address).sort(),
    expectOwed, owedRows: rows.filter(r => r.dataset.owed === 'true').map(r => r.dataset.address).sort(), unusedInStanding,
    owedEdges: all('.lc-edge.is-owed').length, owedEdgeAddresses: [...new Set(all('.lc-edge.is-owed').map(e => e.dataset.transition))].sort(),
    owedLabels: all('.lc-label.is-owed').length, expectEdges, edges: arrows.length, labels: all('.lc-label').length,
    rowCount: rows.length, transitions: transitions.length,
    firedBy: paths.map(p => p.querySelectorAll('.mention').length), pathLinks: paths.flatMap(p => [...p.querySelectorAll('a.mention')].map(a => a.getAttribute('href'))).slice(0, 6),
    firedByExpected: transitions.reduce((n, t) => n + firers(t).length, 0),
    tagged: all('[data-part=transitions] .lc-owed').length, gapText: q('[data-part=transitions] .gap')?.innerText.trim() ?? null,
    owedStat: q('.lifecycle [data-stat=owed] b')?.textContent ?? null,
    marks: all('.lifecycle .mark-unagreed, .lifecycle .mark-changed').length,
    noStates: Boolean(q('[data-part=no-states]')),
    fallback: all('[data-part=diagram-fallback] .mention').length, direction: stage?.dataset.direction ?? 'list',
    stage: stage ? { w: stage.offsetWidth, h: stage.offsetHeight, laid: stage.classList.contains('is-laid'), scale: stage.style.transform || 'none', host: q('.lc-host').clientWidth } : null,
    arrowHeads: all('.lc-edge').every(e => e.getAttribute('marker-end')),
    blockRects: rects.length, inner, bare: all('.lifecycle .mention:not([data-renderer])').length,
    scrollW: [document.documentElement.scrollWidth, innerWidth],
    overlap: ${OVERLAP_HERE},
    heading: q('.lifecycle h1, .lifecycle .page-head')?.innerText.replace(/\\s+/g, ' ').trim().slice(0, 40) ?? null,
  });
})()`;

const OWED = `(async () => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  let standing = null;
  for (let i = 0; i < 90 && !standing?.totals; i++) { standing = await (await fetch('/api/standing', { credentials: 'same-origin' })).json(); if (!standing.totals) await new Promise(r => setTimeout(r, 1000)); }
  const rows = all('[data-part=owed-row]');
  const key = w => w.address + ' ' + w.cause;
  const shown = rows.map(r => r.dataset.address + ' ' + r.dataset.cause).sort();
  const expected = standing.work.map(key).sort();
  const wrongGroup = rows.filter(r => r.closest('.owed-cause')?.dataset.cause !== r.dataset.cause || r.closest('.owed-layer')?.dataset.layer !== r.dataset.address.split('/')[0]).length;
  const inner = all('.owed-page *').filter(e => { const s = getComputedStyle(e); return /(auto|scroll)/.test(s.overflowY + s.overflowX) && (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1); }).map(e => e.className);
  const stat = q('#strip [data-stat=owed]');
  return JSON.stringify({
    rows: rows.length, owedTotal: standing.totals.owed, work: standing.work.length, count: q('[data-part=count]')?.textContent.trim() ?? null,
    same: JSON.stringify(shown) === JSON.stringify(expected), wrongGroup,
    layers: all('.owed-layer').map(e => e.dataset.layer), causes: all('.owed-cause').map(e => e.dataset.cause),
    unusedLoan: rows.some(r => r.dataset.address.endsWith('/entity/loan/transition/return') && r.dataset.cause === 'unused'),
    stripLink: stat?.getAttribute('href') ?? null, stripCount: stat?.querySelector('b')?.textContent ?? null,
    bare: all('.owed-page .mention:not([data-renderer])').length, inner, scrollW: [document.documentElement.scrollWidth, innerWidth],
    marks: all('.owed-page .mark-unagreed, .owed-page .mark-changed').length,
    leaks: rows.filter(r => !r.querySelector('a.mention')).length,
  });
})()`;

const wrap = (scope, probe) => `(async () => { window.__scope = '${scope}'; const p = JSON.parse(await ${probe}); return JSON.stringify({ probe: p, text: ${TEXT}, contrast: ${CONTRAST}, words: ${VIEWER_WORDS} }); })()`;
const parse = values => { const found = values.find(value => value.startsWith('{')); if (!found) throw Error('no measurement: ' + values.join(' | ')); return JSON.parse(found); };
const noise = c => /blockOverlaps=0 textRunsCrossedByEdge=0\/\d+ blocksEnteredByEdge=0\/\d+ labelsOnBlocks=0\/0$/.test(c);

function common(name, { probe, text, contrast, words }) {
  if (probe.inner.length) fail(name + ' scrolls inside ' + probe.inner.join(','));
  if (probe.bare) fail(name + ' ' + probe.bare + ' names not drawn by mention()');
  if (probe.scrollW[0] > probe.scrollW[1]) fail(name + ' horizontal scroll ' + probe.scrollW);
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
}

function judgeLifecycle(name, measured) {
  const { probe } = measured;
  common(name, measured);
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  if (!probe.states.length) {
    if (!probe.noStates) fail(name + ' an entity without states says nothing');
    return console.log(name, JSON.stringify({ direction: 'none', states: 0, transitions: probe.transitions, type: measured.text, contrast: measured.contrast.min }));
  }
  // What the list under the graph says holds whether or not the graph could be drawn at this width.
  if (!same(probe.expectOwed, probe.owedRows)) fail(name + ' owed rows ' + probe.owedRows + ' expected ' + probe.expectOwed);
  if (!same(probe.expectOwed.filter(a => probe.unusedInStanding.includes(a)), probe.expectOwed)) fail(name + ' standing says unused ' + probe.unusedInStanding + ' not ' + probe.expectOwed);
  if (probe.tagged !== probe.expectOwed.length) fail(name + ' owed tags in the list ' + probe.tagged + ' of ' + probe.expectOwed.length);
  if (probe.expectOwed.length && probe.gapText === null) fail(name + ' owed row without its sentence');
  if (probe.rowCount !== probe.transitions) fail(name + ' transition rows ' + probe.rowCount + ' of ' + probe.transitions);
  if (probe.firedBy.length !== probe.firedByExpected || probe.firedBy.some(n => n < 2)) fail(name + ' fired-by paths ' + probe.firedBy + ' expected ' + probe.firedByExpected);
  if (probe.fallback) {
    if (probe.fallback !== probe.states.length) fail(name + ' fallback names ' + probe.fallback + ' of ' + probe.states.length + ' states');
    return console.log(name, JSON.stringify({ direction: 'list', states: probe.states.length, transitions: probe.transitions, type: measured.text, contrast: measured.contrast.min }));
  }
  if (!same(probe.states, probe.shownStates)) fail(name + ' states ' + probe.states + ' shown ' + probe.shownStates);
  if (!same(probe.expectOwed, probe.owedEdgeAddresses)) fail(name + ' owed edges ' + probe.owedEdgeAddresses + ' expected ' + probe.expectOwed);
  if (probe.owedLabels < probe.expectOwed.length) fail(name + ' owed labels ' + probe.owedLabels);
  if (probe.edges !== probe.expectEdges || probe.labels !== probe.expectEdges) fail(name + ' edges ' + probe.edges + ' labels ' + probe.labels + ' expected ' + probe.expectEdges);
  if (!probe.arrowHeads) fail(name + ' an edge without an arrowhead');
  if (!probe.stage?.laid) fail(name + ' diagram not laid out');
  if (probe.stage?.scale !== 'none' && measuredScale(probe.stage) < 0.8) fail(name + ' diagram scaled below 80% ' + probe.stage.scale);
  if (!noise(probe.overlap)) fail(name + ' overlap ' + probe.overlap);
  console.log(name, JSON.stringify({ direction: probe.direction, states: probe.states.length, transitions: probe.transitions, owed: probe.expectOwed.length, firedBy: probe.firedBy, stage: probe.stage, marks: probe.marks, overlap: probe.overlap, type: measured.text, contrast: measured.contrast.min }));
}
const measuredScale = stage => stage.host / stage.w;

function judgeOwed(name, measured) {
  const { probe } = measured;
  common(name, measured);
  if (probe.rows !== probe.owedTotal || probe.rows !== probe.work) fail(name + ' rows ' + probe.rows + ' totals.owed ' + probe.owedTotal + ' work ' + probe.work);
  if (!probe.same) fail(name + ' rows differ from standing.work');
  if (probe.wrongGroup) fail(name + ' ' + probe.wrongGroup + ' rows in the wrong layer or cause group');
  if (probe.count !== String(probe.owedTotal)) fail(name + ' count ' + probe.count);
  if (probe.stripLink !== '#/owed' || probe.stripCount !== String(probe.owedTotal)) fail(name + ' strip ' + probe.stripLink + ' ' + probe.stripCount);
  if (probe.leaks) fail(name + ' rows without a link ' + probe.leaks);
  if (mode === 'tool' && !probe.unusedLoan) fail(name + ' Loan return not listed as unused');
  console.log(name, JSON.stringify({ rows: probe.rows, layers: probe.layers, causes: probe.causes, marks: probe.marks, type: measured.text, contrast: measured.contrast.min }));
}

const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });
const themes = ['light', 'dark'];
const pages = mode === 'tool'
  ? ['product/lending/entity/loan']
  : ['product/capture/entity/entry', 'product/review/entity/decision', 'product/review/entity/review-round'];

async function runs(label, repo, wait) {
  const started = await startServer(repo);
  try {
    const scenes = [];
    for (const width of widths) for (const theme of themes) {
      for (const route of pages) scenes.push({ kind: 'lifecycle', name: `lc-${label}-${width}-${theme}-${route.split('/').slice(1).join('-')}`, route, ...sizeOf(width), wait, actions: [{ media: theme }, { eval: wrap('.lifecycle', LIFECYCLE) }] });
      scenes.push({ kind: 'owed', name: `owed-${label}-${width}-${theme}`, route: 'owed', ...sizeOf(width), wait, actions: [{ media: theme }, { eval: wrap('.owed-page', OWED) }] });
    }
    // Real clicks: a path's workflow name opens the workflow, the strip's owed count opens the list, a row opens its entity.
    const clicks = [
      { name: `lc-${label}-click-path`, route: pages[0], ...sizeOf(1440), wait, actions: [{ click: '[data-part=transitions] [data-part=fired-by] a.mention' }, { eval: 'location.hash' }] },
      { name: `lc-${label}-click-strip`, route: pages[0], ...sizeOf(1440), wait, actions: [{ click: '#strip [data-stat=owed]' }, { eval: 'location.hash' }] },
      { name: `lc-${label}-click-row`, route: 'owed', ...sizeOf(1440), wait, actions: [{ click: '.owed-row[data-cause=unused] a.mention', wait: 800 }, { eval: 'location.hash' }] },
    ];
    scenes[0].wait = wait * 1.5;
    // One browser run: the exchange URL works once, so the click scenes ride the same cookie.
    const results = await browse('lifecycle-' + label, [...scenes, ...clicks], started);
    results.slice(0, scenes.length).forEach((row, index) => (scenes[index].kind === 'owed' ? judgeOwed : judgeLifecycle)(row.name, parse(row.values)));
    const done = results.slice(scenes.length);
    const hash = row => row.values.find(value => value.startsWith('#/'));
    if (!/^#\/[^/]+\/[^/]+\/workflow\/[^/]+$/.test(hash(done[0]) || '')) fail(label + ' path click went to ' + hash(done[0]));
    if (hash(done[1]) !== '#/owed') fail(label + ' strip click went to ' + hash(done[1]));
    if (!/^#\/[^/]+\/[^/]+\/(entity|workflow)\/[^/]+$/.test(hash(done[2]) || '')) fail(label + ' row click went to ' + hash(done[2]));
    console.log(label, 'clicks', hash(done[0]), hash(done[1]), hash(done[2]));
  } finally { await started.stop(); }
}

if (mode === 'tool') await runs('tool', await toolCopy('lifecycle-qa-tool'), 3500);
else await runs('ogy', '.', 14000);
console.log(failures.length ? failures.length + ' failures' : 'all lifecycle checks passed');
process.exit(failures.length ? 1 : 0);
