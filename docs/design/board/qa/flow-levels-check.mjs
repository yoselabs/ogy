// Real-input checks of the workflow page's levels, effects, calls and failure path (stage 11):
//   node docs/design/board/qa/flow-levels-check.mjs [tool|ogy]  (from the repository root)
// The overlap and end-point rules over every level are flow-check.mjs run with LEVEL=1, 2 and 3; this script is what is new.
// Reads only: the tool library runs on a temporary copy; the real KB is only read.
import { browse, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };
const parse = row => { const value = row.values.find(item => item.startsWith('{')); if (!value) { fail(row.name + ' no measure: ' + row.values.join(' | ')); return null; } return JSON.parse(value); };
const WF = 'product/lending/workflow/';

// One pass over a drawn page: sizes, header-only text at level 1, wrapped kind words, step links, edges, badges, counts.
const MEASURE = String.raw`(() => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const token = name => { const probe = document.createElement('span'); probe.style.color = 'var(' + name + ')'; document.body.append(probe); const c = getComputedStyle(probe).color; probe.remove(); return c; };
  const size = s => { const e = q(s); return e ? getComputedStyle(e).fontSize : null; };
  const bodies = all('.flow-node:not(.flow-start)');
  const edge = key => { const e = q('.edge[data-edge*="' + key + '"]'); return e ? { cls: e.getAttribute('class'), stroke: getComputedStyle(e).stroke, marker: e.getAttribute('marker-end') } : null; };
  return JSON.stringify({
    ready: q('.flow')?.dataset.state, level: q('.flow')?.dataset.level, hash: location.hash,
    sizes: { header: size('.flow-node .card-header .mention'), kind: size('.flow-node .kind-word'), label: size('.route-label') },
    extra: bodies.filter(e => e.innerText.replace(/\s+/g, ' ').trim() !== e.querySelector('.card-header').innerText.replace(/\s+/g, ' ').trim()).length,
    wrapped: all('.flow-node .kind-word').filter(e => e.getClientRects().length > 1 || e.getBoundingClientRect().height > 20).length,
    stepLinks: all('.flow-node.kind-step .card-header a.mention[data-select]').filter(a => /sel=/.test(a.getAttribute('href'))).length,
    steps: all('.flow-node.kind-step').length,
    deadHrefs: all('.flow-node .card-header a.mention').filter(a => /\/(step|end)\/[^/]+$/.test(a.getAttribute('href') || '') && !/sel=/.test(a.getAttribute('href'))).length,
    fail: token('--fail'), okLine: token('--ok-line'), failLine: token('--fail-line'),
    otherwise: edge('/case/otherwise'), sent: edge('/case/sent'),
    failEdges: all('.edge.after-failure').length,
    endText: all('.flow-node.kind-end').map(e => e.innerText.replace(/\s+/g, ' ').trim()),
    fx: all('.flow-node .fx').map(e => ({ op: e.dataset.effect, border: getComputedStyle(e).borderLeftColor, text: e.innerText.replace(/\s+/g, ' ').trim(), mentions: e.querySelectorAll('.mention[data-renderer]').length })),
    tags: all('.flow-node .fx-tag').map(e => e.innerText.replace(/\s+/g, ' ').trim()),
    call: all('.flow-node [data-part=call]').map(e => e.innerText.replace(/\s+/g, ' ').trim()),
    ways: all('.flow-node .flow-way').length,
    thenBy: all('.flow-node .flow-label').filter(e => /THEN, BY HOW IT ENDED/.test(e.innerText)).length,
    more: all('.route-more').map(e => Number(e.dataset.count)),
    touched: all('[data-part=touched] .touched').map(e => e.innerText.replace(/\s+/g, ' ').trim()),
    doc: [document.documentElement.scrollWidth, innerWidth],
  });
})()`;

const sized = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });

// Levels 1 to 3 of every workflow: the font sizes do not change, level 1 carries only headers, no kind word wraps.
async function levels(label, started, workflows, widths) {
  const scenes = [];
  for (const width of widths) for (const theme of ['light', 'dark']) for (const wf of workflows) for (const level of [1, 2, 3])
    scenes.push({ name: `lv-${label}-${width}-${theme}-L${level}-${wf.replace(/\//g, '-')}`, route: `${wf}?level=${level}`, ...sized(width), wait: 2500, actions: [{ media: theme }, { eval: MEASURE }] });
  const rows = await browse('flow-levels-' + label, scenes, started);
  const sizes = new Map();
  rows.forEach((row, index) => {
    const m = parse(row); if (!m) return;
    const scene = scenes[index], level = Number(/-L(\d)-/.exec(row.name)[1]);
    const name = row.name;
    if (m.ready !== 'ready' || m.level !== String(level)) return fail(name + ' not drawn at its level: ' + m.ready + ' ' + m.level);
    if (m.wrapped) fail(name + ' ' + m.wrapped + ' kind words wrap');
    if (m.stepLinks !== m.steps) fail(name + ' ' + m.steps + ' steps, ' + m.stepLinks + ' with a select link');
    if (m.deadHrefs) fail(name + ' ' + m.deadHrefs + ' headers link to a route that does not exist');
    if (level === 1 && m.extra) fail(name + ' level 1 has text beyond the header in ' + m.extra + ' nodes');
    if (level === 1 && m.fx.length) fail(name + ' level 1 draws effect badges');
    if (level >= 2 && !m.fx.length && /borrow|notify/.test(name)) fail(name + ' no effect badges');
    if (level === 3 && /remind/.test(name) && (!m.thenBy || !m.ways)) fail(name + ' no THEN, BY HOW IT ENDED list');
    if (level === 2 && /remind/.test(name) && !/^RUNS/.test(m.call[0] || '')) fail(name + ' call step shows no RUNS: ' + m.call);
    if (m.doc[0] > m.doc[1]) fail(name + ' horizontal document scroll ' + m.doc);
    const key = name.replace(/-L\d-/, '-');
    if (!sizes.has(key)) sizes.set(key, JSON.stringify(m.sizes));
    else if (sizes.get(key) !== JSON.stringify(m.sizes)) fail(name + ' font sizes changed with the level: ' + sizes.get(key) + ' then ' + JSON.stringify(m.sizes));
    if (/remind/.test(name)) remind(name, level, m);
    if (/borrow/.test(name) && level >= 2) borrow(name, m);
    if (/notify/.test(name) && level >= 2 && m.fx.filter(f => f.op === 'tell').length !== 2) fail(name + ' expected two tell badges');
    console.log(name, JSON.stringify({ sizes: m.sizes, fx: m.fx.length, more: m.more, tags: m.tags, touched: m.touched.length }));
  });
}

// The failure path: the edge from the case that covers notify's failed end.
function remind(name, level, m) {
  if (!m.otherwise?.cls.includes('after-failure')) fail(name + ' otherwise edge is not after-failure: ' + JSON.stringify(m.otherwise));
  else if (m.otherwise.stroke !== m.fail) fail(name + ' after-failure stroke ' + m.otherwise.stroke + ' is not the failure token ' + m.fail);
  if (m.otherwise && !/edge-cross/.test(m.otherwise.marker)) fail(name + ' after-failure head has no cross mark');
  if (m.sent?.cls.includes('after-failure')) fail(name + ' the sent edge is drawn as a failure');
  if (m.failEdges !== 1) fail(name + ' ' + m.failEdges + ' failure edges, expected 1');
  const done = m.endText.find(text => /^Done/.test(text)) || '';
  if (level >= 2 && !/also reached after Notify failed/.test(done)) fail(name + ' the end it reaches does not say it: ' + done);
  if (level === 1 && /also reached/.test(done)) fail(name + ' level 1 end carries text beyond its header');
}

// Borrow's Record step: create has the green edge, delete the red one, a transition names from and to.
function borrow(name, m) {
  const create = m.fx.find(f => f.op === 'create');
  if (!create) fail(name + ' no create badge');
  else if (create.border !== m.okLine) fail(name + ' create badge edge ' + create.border + ' is not ' + m.okLine);
  for (const f of m.fx.filter(f => f.op === 'delete')) if (f.border !== m.failLine) fail(name + ' delete badge edge ' + f.border);
  if (!m.tags.some(tag => /→ \S+/.test(tag))) fail(name + ' no transition tag: ' + m.tags);
  for (const f of m.fx) if (!f.mentions) fail(name + ' badge names nothing: ' + f.text);
  if (!m.touched.length) fail(name + ' the strip of touched entities is empty');
}

// Real mouse: a step title selects it, a choice in the side panel walks, a count opens its rows, a level button changes the level.
async function clicks(label, started) {
  const flow = `${WF}borrow`;
  const SELECTED = `JSON.stringify({ hash: location.hash, selected: [...document.querySelectorAll('.flow-node.is-selected')].map(e => e.dataset.node.split('/').slice(-2).join('/')), walk: !!document.querySelector('.rail-panel .walk'), choices: document.querySelectorAll('.rail-panel .walk-choice').length, rows: document.querySelectorAll('.rail-panel .walk-row').length, level: document.querySelector('.flow').dataset.level, ways: document.querySelectorAll('.flow-way').length, state: document.querySelector('.flow').dataset.state })`;
  const scenes = [
    { name: 'click-step', route: flow, ...sized(1440), wait: 2500, actions: [{ click: '.flow-node.kind-step a.mention[data-select]', wait: 600 }, { eval: SELECTED }, { shot: 'click-step-selected' }, { click: '.walk-choice', wait: 600 }, { eval: SELECTED }] },
    { name: 'click-count', route: flow, ...sized(1440), wait: 2500, actions: [{ click: '.route-more', wait: 600 }, { eval: SELECTED + ' + ""' }, { eval: `JSON.stringify({ count: Number(document.querySelector('.route-more').dataset.count), rows: document.querySelectorAll('.rail-panel .walk-row').length })` }] },
    { name: 'click-level', route: flow, ...sized(1440), wait: 2500, actions: [{ click: '.level-button[data-level="3"]', wait: 2000 }, { eval: SELECTED }, { click: '.level-button[data-level="1"]', wait: 2000 }, { eval: SELECTED }] },
    { name: 'click-step-phone', route: flow, ...sized(390), wait: 2500, actions: [{ click: '.flow-node.kind-step a.mention[data-select]', wait: 600 }, { eval: SELECTED }] },
  ];
  const rows = await browse('flow-levels-click-' + label, scenes, started);
  if (process.env.RAW) console.log(JSON.stringify(rows));
  const [step, count, level, phone] = rows.map(row => row.values.filter(item => item.startsWith('{')).map(item => JSON.parse(item)));
  if (!/sel=/.test(step[0].hash) || step[0].selected.length !== 1 || !step[0].walk || !step[0].choices) fail('click-step: ' + JSON.stringify(step[0]));
  if (step[1].selected[0] === step[0].selected[0] || step[1].selected.length !== 1) fail('click-step: a choice did not walk to another node: ' + JSON.stringify(step[1]));
  if (!count[1] || count[1].rows < count[1].count + 1 || count[0].rows !== count[1].rows) fail('click-count: a count of ' + count[1]?.count + ' opened ' + count[1]?.rows + ' rows');
  if (level[0].level !== '3' || !level[0].ways && level[0].level !== '3') fail('click-level 3: ' + JSON.stringify(level[0]));
  if (level[1].level !== '1' || level[1].ways) fail('click-level 1: ' + JSON.stringify(level[1]));
  if (!phone[0].walk) fail('click-step-phone: nothing in the side panel: ' + JSON.stringify(phone[0]));
  console.log('clicks', JSON.stringify({ step, count, level: level.map(l => l.level), phone: phone[0].walk }));
}

let stopped = false;
async function main() {
  const repo = mode !== 'ogy' ? await toolCopy('flow-levels-tool') : '.';
  const started = await startServer(repo);
  try {
    if (mode === 'clicks') await clicks('tool', started);
    else if (mode === 'tool') {
      await levels('tool', started, ['borrow', 'close-loan', 'notify', 'remind'].map(id => WF + id), [1440, 390]);
      stopped = true; await started.stop(); // the exchange URL works once: the clicks get their own server
      const second = await startServer(repo);
      try { await clicks('tool', second); } finally { await second.stop(); }
      return done();
    } else {
      const ids = ['product/review/workflow/review-and-reply', 'product/removal/workflow/remove-entry', 'product/capture/workflow/capture-entries', 'product/checks/workflow/check-and-land'];
      await levels('ogy', started, ids, [1440]);
    }
  } finally { if (!stopped) await started.stop(); }
  done();
}
function done() {
  console.log(failures.length ? failures.length + ' failures' : 'all level checks passed');
  process.exit(failures.length ? 1 : 0);
}
await main();
