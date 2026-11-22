// Real-input checks of the area page: node docs/design/board/qa/area-check.mjs [tool|ogy] [width]  (from the repository root)
// Reads only: the tool library runs on a temporary copy, the real KB is only read.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };

// Everything the page claims is compared with the inspection document read from the same server.
const PROBE = `(async () => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const doc = await (await fetch('/api/inspection', { credentials: 'same-origin' })).json();
  const scope = location.hash.replace(/^#\\/?/, '');
  const [layer, area] = scope.split('/');
  const entries = doc.entries.filter(e => e.layer === layer && e.area === area);
  const rel = (s, f) => doc.relations.filter(r => r.source === s && r.field === f).map(r => r.target);
  const workflows = entries.filter(e => e.kind === 'workflow').map(e => e.address).sort();
  const shown = all('[data-part=workflow]').map(e => e.dataset.address).sort();
  const hasGoals = doc.ontology.kinds.goal.layers.includes(layer);
  const wrong = [], loose = [];
  for (const wf of workflows) {
    const el = q('[data-part=workflow][data-address="' + wf + '"]');
    const cap = rel(wf, 'realizes')[0];
    if (!hasGoals || !el) continue;
    const group = el.closest('.chain-group');
    if (!cap) { if (group?.dataset.part !== 'no-goal') wrong.push(wf + ' loose but not under no-goal'); else loose.push(wf); continue; }
    const goals = rel(cap, 'realizes');
    if (!goals.length) { if (group?.dataset.part !== 'no-goal') wrong.push(wf + ' no goal but not under no-goal'); continue; }
    if (!goals.includes(group?.dataset.address)) wrong.push(wf + ' under ' + group?.dataset.address + ' not ' + goals);
  }
  const goals = entries.filter(e => e.kind === 'goal').map(e => e.address);
  const goalGroups = all('.chain-group[data-address]').map(e => e.dataset.address);
  const items = all('.area [data-part], .area .card-header, .area .gap, .area .pill, .area .mention, .area .says, .area h2');
  const rects = items.filter(e => e.checkVisibility()).map(e => [e, e.getBoundingClientRect()]).filter(([, r]) => r.width > 1 && r.height > 1);
  let overlaps = 0; const where = [];
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const [a, ra] = rects[i], [b, rb] = rects[j];
    if (a.contains(b) || b.contains(a)) continue;
    if (Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left) > 2 && Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top) > 2) { overlaps++; where.push((a.dataset.part || a.className) + '|' + (b.dataset.part || b.className)); }
  }
  const inner = all('.area *').filter(e => { const s = getComputedStyle(e); return /(auto|scroll)/.test(s.overflowY + s.overflowX) && (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1); }).map(e => e.className);
  const marks = all('.area .mention').filter(e => e.dataset.renderer === 'mention' || e.dataset.renderer === 'title-token').length;
  const bare = all('.area .mention:not([data-renderer])').length;
  return JSON.stringify({
    workflows, shown, wrong, loose, hasGoals, goals, goalGroups,
    noGoalLabel: q('[data-part=no-goal] .gap')?.innerText.trim() ?? null,
    gaps: all('.gap').map(e => e.innerText.replace(/\\s+/g, ' ').trim()),
    gapColour: q('.gap') ? getComputedStyle(q('.gap')).color : null,
    entities: all('[data-part=entity]').length, stateStrips: all('[data-part=states]').length,
    kindRows: all('[data-part=kind-row]').map(e => e.dataset.kind + ':' + e.querySelector('[data-part=count]').innerText), kindOpen: all('details[data-part=kind-row][open]').length,
    strips: all('[data-part=flow]').length, endMarks: all('[data-part=flow] .end-success, [data-part=flow] .end-failure').length,
    waitingStat: q('.area [data-stat=waiting] b')?.textContent ?? null, owedStat: q('.area [data-stat=owed] b')?.textContent ?? null,
    heading: q('.area .page-head')?.innerText.replace(/\\s+/g, ' ').trim().slice(0, 80) ?? null,
    mentions: marks, bare, inner, overlaps, where: where.slice(0, 4),
    wide: all('.area *').filter(e => e.getBoundingClientRect().right > innerWidth + 1).length, scrollW: [document.documentElement.scrollWidth, innerWidth],
    headerRects: JSON.stringify(all('#header .btn, #header .tab').map(e => { const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })),
    chainRect: q('.chain') ? Math.round(q('.chain').getBoundingClientRect().height) : null,
    capCols: (() => { const g = q('.chain-group'); const head = q('.chain-head'); if (!g || !head || head.offsetParent === null) return null; const c = g.querySelector('.cap-cell'), w = g.querySelector('.wf-cell'), k = [...head.children]; return [Math.round(c.getBoundingClientRect().left - k[1].getBoundingClientRect().left), Math.round(w.getBoundingClientRect().left - k[2].getBoundingClientRect().left)]; })(),
  });
})()`;
const MEASURE = `(async () => { window.__scope = '.area'; const p = JSON.parse(await ${PROBE}); return JSON.stringify({ probe: p, text: ${TEXT}, contrast: ${CONTRAST}, words: ${VIEWER_WORDS} }); })()`;
const parse = values => JSON.parse(values.find(value => value.startsWith('{')));

function judge(name, measured, expect = {}) {
  const { probe, text, contrast, words } = measured;
  if (JSON.stringify(probe.workflows) !== JSON.stringify([...new Set(probe.shown)].sort()) || probe.shown.length !== probe.workflows.length) fail(name + ' workflows ' + probe.workflows + ' shown ' + probe.shown);
  if (probe.wrong.length) fail(name + ' wrong row ' + probe.wrong.join('; '));
  if (probe.hasGoals && JSON.stringify([...probe.goals].sort()) !== JSON.stringify(probe.goalGroups.filter(g => probe.goals.includes(g)).sort())) fail(name + ' goal rows ' + probe.goalGroups + ' vs ' + probe.goals);
  if (probe.overlaps) fail(name + ' overlaps ' + probe.overlaps + ' ' + probe.where.join(','));
  if (probe.inner.length) fail(name + ' scrolls inside ' + probe.inner.join(','));
  if (probe.bare) fail(name + ' ' + probe.bare + ' names not drawn by mention()');
  if (probe.wide) fail(name + ' ' + probe.wide + ' elements past the right edge');
  if (probe.scrollW[0] > probe.scrollW[1]) fail(name + ' horizontal scroll ' + probe.scrollW);
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
  if (probe.capCols && probe.capCols.some(offset => Math.abs(offset) > 1)) fail(name + ' header columns misaligned ' + probe.capCols);
  for (const [key, check] of Object.entries(expect)) { if (!check(probe[key], probe)) fail(name + ' ' + key + ' = ' + JSON.stringify(probe[key])); }
  console.log(name, JSON.stringify({ wf: probe.workflows.length, goals: probe.goals.length, gaps: probe.gaps, entities: probe.entities, kinds: probe.kindRows.length, type: text, contrast: contrast.min }));
}

const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });
const themes = ['light', 'dark'];
const tool = { 'product/lending': { gaps: v => Array.isArray(v), entities: v => v >= 1 } };
const ogy = { 'product/review': {}, 'product/inspection': {}, 'product/removal': {}, 'product/capture': {}, 'software/viewing': { hasGoals: v => v === false }, 'software/cli': {}, 'software/ontology': { kindRows: v => v.length >= 3 } };

async function runs(label, repo, pages, wait) {
  const started = await startServer(repo);
  try {
    const scenes = [];
    for (const width of widths) for (const theme of themes) for (const route of Object.keys(pages))
      scenes.push({ name: `area-${label}-${width}-${theme}-${route.replace('/', '-')}`, route, ...sizeOf(width), wait, actions: [{ media: theme }, { eval: MEASURE }] });
    scenes[0].wait = wait * 1.5;
    const results = await browse('area-' + label, scenes, started);
    results.forEach((row, index) => judge(row.name, parse(row.values), pages[scenes[index].route]));
  } finally { await started.stop(); }
}

if (mode === 'tool') await runs('tool', await toolCopy('area-qa-tool'), tool, 2500);
else await runs('ogy', '.', ogy, 12000);
console.log(failures.length ? failures.length + ' failures' : 'all area checks passed');
process.exit(failures.length ? 1 : 0);
