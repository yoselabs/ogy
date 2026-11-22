// Real-input checks of the workflow page (stage 10): node docs/design/board/qa/flow-check.mjs [tool|ogy|synthetic] [width]  (from the repository root)
// Reads only: the tool library runs on a temporary copy, the real KB is only read; synthetic is a temporary copy of the tool library x55.
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, OVERLAP, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, run, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const level = Number(process.env.LEVEL || 1); // 1 is the default level; 2 and 3 run the same overlap rules over the fuller nodes
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };

// The shared overlap script, with the stage's two constants: nodes are `.flow-node`, edges are `.edge-layer path`.
const OVERLAP_VIEWPORT = OVERLAP.replace('"[data-local-id]"', '".flow-node"').replace('"#vp path, #vp polyline, #vp line"', '".edge-layer path"');

// The same four counts over the whole graph, not only the viewport (a phone shows a slice of a tall graph), plus the end-point rule.
const WHOLE = String.raw`(() => {
  const R = e => e.getBoundingClientRect();
  const hit = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2;
  const nodes = [...document.querySelectorAll('.flow-node')].map(e => [e, R(e)]);
  let blockOverlaps = 0;
  for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) if (hit(nodes[i][1], nodes[j][1])) blockOverlaps++;
  const texts = [];
  const walker = document.createTreeWalker(document.querySelector('.flow-canvas'), NodeFilter.SHOW_TEXT);
  for (let n; (n = walker.nextNode());) {
    if (!n.nodeValue.trim() || !n.parentElement.closest('.flow-node')) continue;
    const range = document.createRange(); range.selectNodeContents(n);
    for (const r of range.getClientRects()) if (r.width > 2) texts.push(r);
  }
  const paths = [...document.querySelectorAll('.edge-layer path.edge')];
  const sample = p => {
    const m = p.getScreenCTM(), L = p.getTotalLength(), out = [];
    for (let d = 0; d < L; d += 2) { const q = p.getPointAtLength(d); out.push([q.x * m.a + q.y * m.c + m.e, q.x * m.b + q.y * m.d + m.f]); }
    const q = p.getPointAtLength(L); out.push([q.x * m.a + q.y * m.c + m.e, q.x * m.b + q.y * m.d + m.f]);
    return out;
  };
  const all = paths.map(sample);
  const flat = all.flat();
  const textRunsCrossedByEdge = texts.filter(t => flat.some(s => s[0] > t.left && s[0] < t.right && s[1] > t.top + 1 && s[1] < t.bottom - 1)).length;
  const blocksEnteredByEdge = nodes.filter(([, r]) => flat.some(s => s[0] > r.left + 6 && s[0] < r.right - 6 && s[1] > r.top + 6 && s[1] < r.bottom - 6)).length;
  // Any edge point strictly inside any node's border box (a 2px skin is the border itself).
  const inside = nodes.filter(([, r]) => flat.some(s => s[0] > r.left + 2 && s[0] < r.right - 2 && s[1] > r.top + 2 && s[1] < r.bottom - 2)).length;
  const labels = [...document.querySelectorAll('.route-label')].map(R);
  const labelsOnBlocks = labels.filter(l => nodes.some(([, r]) => hit(l, r))).length;
  let labelsOverLabels = 0;
  for (let i = 0; i < labels.length; i++) for (let j = i + 1; j < labels.length; j++) if (hit(labels[i], labels[j])) labelsOverLabels++;
  // A label that an edge of another label's route runs through is also a fault: count text runs of labels crossed by any path.
  // A label sits on its own edge (it masks it); no other edge may run through it.
  const labelsCrossed = [...document.querySelectorAll('.route-label')].filter(e => {
    const l = R(e);
    return paths.some((p, i) => p.dataset.edge !== e.dataset.edgeLabel && all[i].some(s => s[0] > l.left + 1 && s[0] < l.right - 1 && s[1] > l.top + 1 && s[1] < l.bottom - 1));
  }).length;
  const border = (r, x, y) => {
    const inX = x >= r.left - 1.5 && x <= r.right + 1.5, inY = y >= r.top - 1.5 && y <= r.bottom + 1.5;
    return inX && inY && (Math.abs(x - r.left) <= 1.5 || Math.abs(x - r.right) <= 1.5 || Math.abs(y - r.top) <= 1.5 || Math.abs(y - r.bottom) <= 1.5);
  };
  const byNode = id => document.querySelector('.flow-node[data-node="' + CSS.escape(id) + '"]');
  const loose = [];
  paths.forEach((p, i) => {
    const a = all[i][0], b = all[i].at(-1), from = byNode(p.dataset.from), to = byNode(p.dataset.to);
    if (!from || !to) { loose.push(p.dataset.edge + ' no node'); return; }
    if (!border(R(from), a[0], a[1])) loose.push(p.dataset.edge + ' start off ' + p.dataset.from);
    if (!border(R(to), b[0], b[1])) loose.push(p.dataset.edge + ' end off ' + p.dataset.to);
  });
  // Edges that share a stretch (merged arrows): two paths with a point pair closer than 1px for more than 12px of length.
  let merged = 0;
  for (let i = 0; i < all.length; i++) for (let j = i + 1; j < all.length; j++) {
    let run = 0;
    for (const a of all[i]) { if (all[j].some(b => Math.abs(a[0] - b[0]) < 1 && Math.abs(a[1] - b[1]) < 1)) run += 2; }
    if (run > 12) merged++;
  }
  return { nodes: nodes.length, edges: paths.length, blockOverlaps, textRunsCrossedByEdge, blocksEnteredByEdge, inside, labels: labels.length, labelsOnBlocks, labelsOverLabels, labelsCrossed, loose, merged };
})()`;

const PROBE = String.raw`(async () => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const doc = await (await fetch('/api/inspection', { credentials: 'same-origin' })).json();
  const address = location.hash.replace(/^#\/?/, '').split('?')[0];
  const inWf = e => (e.parent || '') === address;
  const recs = [...doc.entries, ...doc.parts];
  const steps = recs.filter(p => inWf(p) && p.kind === 'step'), ends = recs.filter(p => inWf(p) && p.kind === 'end');
  const rows = recs.filter(p => ['case', 'choice', 'timeout'].includes(p.kind) && steps.some(s => s.address === p.parent));
  const rowIds = new Set(rows.map(r => r.address || (r.locator.owner + '#' + encodeURIComponent(r.locator.field) + '/' + r.locator.index)));
  const thens = doc.relations.filter(r => r.field === 'then' && r.target && (typeof r.source === 'string' ? rowIds.has(r.source) : rowIds.has(r.source.owner + '#' + encodeURIComponent(r.source.field) + '/' + r.source.index)));
  const wf = doc.entries.find(e => e.address === address);
  const scroll = q('.flow-scroll'), canvas = q('.flow-canvas');
  const whole = q('.flow-canvas .flow-node') ? ${WHOLE} : null;
  const external = new Set(thens.map(t => t.target).filter(t => !steps.some(s => s.address === t) && !ends.some(e => e.address === t)));
  return JSON.stringify({
    address, ready: q('.flow')?.dataset.state, direction: canvas?.dataset.direction ?? null,
    expectNodes: steps.length + ends.length + (wf?.fields?.start ? 1 : 0) + external.size,
    rolled: all('.route-more').reduce((sum, e) => sum + Number(e.dataset.count), 0),
    expectEdges: thens.length + (wf?.fields?.start ? 1 : 0) - all('.route-more').reduce((sum, e) => sum + Number(e.dataset.count), 0),
    steps: steps.length, ends: ends.length, whole,
    labelled: all('.route-label').length, expectLabels: thens.length - all('.route-more').reduce((sum, e) => sum + Number(e.dataset.count), 0),
    scroll: scroll ? [scroll.scrollWidth, scroll.clientWidth, scroll.scrollHeight, scroll.clientHeight] : null,
    docScroll: [document.documentElement.scrollWidth, innerWidth],
    canvasSize: canvas ? [parseFloat(canvas.style.width), parseFloat(canvas.style.height)] : null,
    mentions: all('.flow-node .mention').length, bare: all('.flow-node .mention:not([data-renderer])').length,
    nodeText: all('.flow-node').map(e => e.innerText.replace(/\s+/g, ' ').trim()),
    inlineText: all('.flow-node').filter(e => e.querySelector('p, .says')).length,
    endClasses: all('.flow-node.end-failure, .flow-node.end-success').map(e => e.className.match(/end-\w+/)[0] + ':' + getComputedStyle(e).borderTopColor),
    failureEndsGreen: all('.flow-node.end-failure').filter(e => /^rgb\(\s*(2[0-9]|[0-9]|1[0-9]?)\s*,\s*1[0-9]{2}/.test(getComputedStyle(e).borderTopColor)).length,
    head: q('.flow .page-head')?.innerText.replace(/\s+/g, ' ').trim().slice(0, 80) ?? null,
  });
})()`;
const MEASURE = `(async () => { window.__scope = '.flow'; const p = JSON.parse(await ${PROBE}); return JSON.stringify({ probe: p, overlap: ${OVERLAP_VIEWPORT}, text: ${TEXT}, contrast: ${CONTRAST}, words: ${VIEWER_WORDS} }); })()`;
const parse = values => JSON.parse(values.find(value => value.startsWith('{')));
const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });
const themes = ['light', 'dark'];

function judge(name, measured, wide) {
  const { probe, overlap, text, contrast, words } = measured;
  const w = probe.whole;
  if (probe.ready !== 'ready' || !w) return fail(name + ' not drawn: ' + probe.ready);
  if (w.nodes !== probe.expectNodes) fail(name + ' nodes ' + w.nodes + ' expected ' + probe.expectNodes);
  if (w.edges !== probe.expectEdges) fail(name + ' edges ' + w.edges + ' expected ' + probe.expectEdges);
  if (probe.labelled !== probe.expectLabels) fail(name + ' labels ' + probe.labelled + ' expected ' + probe.expectLabels);
  for (const key of ['blockOverlaps', 'textRunsCrossedByEdge', 'blocksEnteredByEdge', 'inside', 'labelsOnBlocks', 'labelsOverLabels', 'labelsCrossed', 'merged']) if (w[key]) fail(name + ' ' + key + '=' + w[key]);
  for (const key of ['blockOverlaps', 'textRunsCrossedByEdge', 'blocksEnteredByEdge', 'labelsOnBlocks']) {
    const found = overlap.match(new RegExp(key + '=(\\d+)'));
    if (!found) fail(name + ' overlap script missing ' + key); else if (+found[1]) fail(name + ' viewport ' + key + '=' + found[1]);
  }
  if (w.loose.length) fail(name + ' end points off a border: ' + w.loose.slice(0, 3).join('; '));
  if (probe.bare) fail(name + ' ' + probe.bare + ' names not drawn by mention()');
  if (level === 1 && probe.inlineText) fail(name + ' ' + probe.inlineText + ' nodes carry more than the header');
  if (probe.failureEndsGreen) fail(name + ' a failure end is drawn green');
  if (probe.docScroll[0] > probe.docScroll[1]) fail(name + ' horizontal document scroll ' + probe.docScroll);
  if (level === 1 && wide && probe.steps <= 3 && probe.scroll && probe.scroll[0] > probe.scroll[1]) fail(name + ' a ' + probe.steps + '-step workflow scrolls ' + probe.scroll);
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
  console.log(name, JSON.stringify({ steps: probe.steps, ends: probe.ends, nodes: w.nodes, edges: w.edges, labels: probe.labelled, canvas: probe.canvasSize, scroll: probe.scroll, dir: probe.direction }));
}

// Workflow addresses straight from the KB folder: <layer>/<area>/workflow/<id>.yml.
function workflowsOf(repo) {
  const found = [];
  for (const layer of ['product', 'software']) {
    const base = join(repo, 'docs/kb', layer);
    if (!existsSync(base)) continue;
    for (const area of readdirSync(base)) {
      const folder = join(base, area, 'workflow');
      if (existsSync(folder)) for (const file of readdirSync(folder)) if (file.endsWith('.yml')) found.push(`${layer}/${area}/workflow/${file.slice(0, -4)}`);
    }
  }
  return found.sort();
}

async function runs(label, repo, wait, pick = list => list) {
  const started = await startServer(repo);
  try {
    const workflows = pick(workflowsOf(repo));
    console.log(label, workflows.length, 'workflows');
    const scenes = [];
    for (const width of widths) for (const theme of themes) for (const route of workflows)
      scenes.push({ name: `flow-${label}-L${level}-${width}-${theme}-${route.replace(/\//g, '-')}`, route: `${route}?level=${level}`, ...sizeOf(width), wait, actions: [{ media: theme }, { eval: MEASURE }] });
    const results = await browse('flow-' + label, scenes, started);
    results.forEach((row, index) => {
      const values = row.values.find(value => value.startsWith('{'));
      if (!values) return fail(row.name + ' no measure: ' + row.values.join(' | '));
      judge(row.name, JSON.parse(values), scenes[index].size[0] > 700);
    });
  } finally { await started.stop(); }
}

// A real mouse click on a workflow of the area page opens its flow page.
async function clickThrough(repo) {
  const started = await startServer(repo);
  try {
    const scene = { name: 'flow-click', route: 'product/lending', size: [1440, 1000], wait: 3000,
      actions: [{ click: '[data-part=workflow] a.mention', wait: 2500 }, { eval: `JSON.stringify({ hash: location.hash, ready: document.querySelector('.flow')?.dataset.state, nodes: document.querySelectorAll('.flow-node').length })` }] };
    const [row] = await browse('flow-click', [scene], started);
    const got = JSON.parse(row.values.find(value => value.startsWith('{')));
    if (!/^#\/product\/lending\/workflow\//.test(got.hash) || got.ready !== 'ready' || !got.nodes) fail('click did not open a drawn flow page: ' + JSON.stringify(got));
    else console.log('click', JSON.stringify(got));
  } finally { await started.stop(); }
}

if (mode === 'tool') { const repo = await toolCopy('flow-qa-tool'); await runs('tool', repo, 2500); await clickThrough(repo); }
else if (mode === 'ogy') await runs('ogy', '.', 9000);
else {
  const made = JSON.parse((await run('node', [join(here, 'synthetic.mjs')])).stdout);
  await runs('synthetic', made.repo, 20000, list => list.filter((_, index) => index % 40 === 0));
}
console.log(failures.length ? failures.length + ' failures' : 'all flow checks passed');
process.exit(failures.length ? 1 : 0);
