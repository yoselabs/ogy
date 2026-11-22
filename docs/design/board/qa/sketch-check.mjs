// Real-input checks of the sketch (stage 15): node docs/design/board/qa/sketch-check.mjs [tool|ogy] [width]  (from the repository root)
// An MCP call (HTTP, the server's own `sketch` tool) shows a sketch; the page is driven with real mouse and key input. The tool library
// copy is the only KB that is written to (Keep, then Record, is typed and clicked there); this repository's KB is read only.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { readdirSync } from 'node:fs';
import { CONTRAST, OVERLAP, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, run, show as showEntry, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };
const themes = ['light', 'dark'];
const OVERLAP_FLOW = OVERLAP.replace('"[data-local-id]"', '".flow-node"').replace('"#vp path, #vp polyline, #vp line"', '".edge-layer path"');

// What the page shows of a sketch: its nodes and edges with their treatment, the colours of every sketched element against the status
// colours, the rows of what it would touch, the Agent tab's block and where the page is.
const PROBE = String.raw`(() => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const token = name => { const probe = document.createElement('span'); probe.style.color = 'var(' + name + ')'; document.body.append(probe); const c = getComputedStyle(probe).color; probe.remove(); return c; };
  const status = new Set(['--ok', '--ok-bg', '--ok-line', '--fail', '--fail-bg', '--fail-line', '--warn', '--warn-bg', '--warn-line'].map(token));
  const sketched = all('#main .is-sketch');
  const coloured = [];
  for (const root of sketched) for (const e of [root, ...root.querySelectorAll('*')]) {
    const c = getComputedStyle(e);
    for (const prop of ['borderTopColor', 'borderLeftColor', 'borderBottomColor', 'borderRightColor', 'backgroundColor', 'color', 'stroke', 'fill'])
      if (status.has(c[prop])) coloured.push((e.className.baseVal ?? e.className) + ' ' + prop + ' ' + c[prop]);
  }
  const nodes = all('#main .flow-node'), real = n => n.classList.contains('is-external');
  const edges = all('#main .edge');
  const first = q('#main .flow-node.is-sketch:not(.flow-start)');
  const style = first ? getComputedStyle(first) : null;
  const text = e => e?.innerText.replace(/\s+/g, ' ').trim() ?? null;
  return JSON.stringify({
    hash: location.hash, state: q('#main .sketch')?.dataset.state ?? null, tag: q('[data-part=sketch-tag]')?.textContent ?? null, title: text(q('[data-part=sketch-title]')),
    notKept: text(q('[data-part=not-kept]')), empty: text(q('[data-part=no-sketch]')),
    nodes: nodes.length, sketchNodes: nodes.filter(n => n.classList.contains('is-sketch')).length, realNodes: nodes.filter(real).length,
    plain: nodes.filter(n => !real(n) && !n.classList.contains('is-sketch')).length,
    wordMarks: all('#main .is-sketch .sketch-word').length, wordable: all('#main .is-sketch[data-address]').length,
    realDashed: nodes.filter(real).filter(n => getComputedStyle(n).borderStyle.startsWith('dashed')).length,
    sketchClassOnReal: nodes.filter(n => real(n) && n.classList.contains('is-sketch')).length,
    treatment: style ? { border: style.borderTopStyle + ' ' + style.borderTopWidth, hatch: style.backgroundImage.includes('repeating-linear-gradient') } : null,
    edges: edges.length, sketchEdges: edges.filter(e => e.classList.contains('is-sketch')).length, afterFailure: all('#main .edge.after-failure').length,
    dashedEdges: edges.filter(e => getComputedStyle(e).strokeDasharray !== 'none').length,
    endClasses: all('#main .flow-node.kind-end').map(n => [...n.classList].filter(c => /^end-/.test(c)).join()).filter(Boolean),
    coloured, cards: all('#main .sketch-card').length, cardsPlain: all('#main .sketch-card:not(.is-sketch)').length,
    touch: all('[data-touch]').map(e => [e.dataset.touch, e.dataset.how, text(e.querySelector('.touch-how'))]),
    keep: Boolean(q('[data-action=keep]')), dismiss: Boolean(q('[data-action=dismiss-sketch]')),
    agent: text(q('[data-part=agent-sketch]')), agentRequest: text(q('.agent-sketch-request')), tab: q('[role=tab][aria-selected=true]')?.dataset.tab ?? null,
    log: all('.agent-call').map(e => e.textContent.replace(/\s+/g, ' ').trim()), note: q('#note')?.value ?? null,
    levels: all('[data-part=levels] [aria-pressed=true]').map(e => e.dataset.level),
    steps: all('#main .flow-node.kind-step').map(e => e.dataset.address), wide: all('#main *').filter(e => e.getBoundingClientRect().right > innerWidth + 1 && !e.closest('.flow-scroll')).length,
    doc: [document.documentElement.scrollWidth, innerWidth],
  });
})()`;
const KEPT = String.raw`(() => {
  const q = s => document.querySelector(s), text = e => e?.innerText.replace(/\s+/g, ' ').trim() ?? null;
  return JSON.stringify({ hash: location.hash, chosen: text(q('[data-part=chosen]')), said: q('#said')?.value ?? null, active: document.activeElement?.id ?? null,
    radio: q('input[name=option]:checked')?.value ?? null, readback: text(q('[data-part=readback]')), refusal: text(q('[data-part=refusal]')), target: q('.is-target')?.dataset.option ?? null });
})()`;
const MEASURE = `window.__scope='#main';JSON.stringify({text:${TEXT},contrast:${CONTRAST},words:${VIEWER_WORDS},overlap:${OVERLAP_FLOW}})`;
const VERSION = `fetch('/api/version', { credentials: 'same-origin' }).then(r => r.json()).then(j => 'VERSION ' + j.version)`;
const parse = values => values.filter(value => value.startsWith('{')).map(value => JSON.parse(value));
const versions = values => values.filter(value => value.startsWith('VERSION ')).map(value => value.slice(8));
const has = (...parts) => value => parts.every(part => String(value).includes(part));

// Every file of the repository's knowledge base with its text, to say afterwards exactly which files moved.
const tree = repo => new Map(readdirSync(join(repo, 'docs/kb'), { recursive: true, withFileTypes: true }).filter(e => e.isFile()).map(e => { const file = join(e.parentPath, e.name); return [file, readFileSync(file, 'utf8')]; }));

async function tokenOf(repo) {
  const dir = (await run('git', ['-C', repo, 'rev-parse', '--absolute-git-dir'])).stdout.trim();
  return readFileSync(join(dir, 'ogy/server.token'), 'utf8').trim();
}

const call = (started, token, name, args) => ({ call: {
  url: started.origin + '/mcp/', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream', 'X-Ogy-Token': token },
  body: { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } } }, wait: 1500 });
const draw = (started, token, args) => call(started, token, 'sketch', { action: 'show', session: 'qa agent', ...args });
const clear = (started, token) => call(started, token, 'sketch', { action: 'dismiss', session: 'qa agent' });

// A three-step workflow with what it touches, in the put format. Steps: ask (actor), hold (a failure way), confirm (creates something).
const reserve = (home, actor, thing, entity, attribute, capability) => [{
  address: `${home}/workflow/reserve-a-tool`, says: 'A member reserves a tool for a day.', start: 'ask', realizes: capability,
  steps: {
    ask: { says: 'The member asks to reserve a tool.', actor, choices: { reserve: { label: 'Reserve', then: 'hold' }, leave: { label: 'Leave', then: 'left' } } },
    hold: { says: 'The library holds the tool for the member.', cases: {
      taken: { order: 1, when: { text: 'the tool is out', reads: [thing] }, then: 'full', effects: [{ do: 'change', on: attribute }] },
      otherwise: { then: 'confirm' } } },
    confirm: { says: 'The library confirms the hold.', cases: { otherwise: { then: 'held', effects: [{ do: 'create', on: entity }, { do: 'delete', on: entity }] } } } },
  ends: { held: { says: 'The tool is held.', result: 'success' }, full: { says: 'The tool is out.', result: 'failure' }, left: { says: 'The member left.', result: 'failure' } } },
  { address: `${home}/entity/reservation`, says: 'One reservation of one tool by one member.' }];
const TOOL = {
  records: reserve('product/lending', 'product/lending/actor/member', 'product/lending/entity/tool', 'product/lending/entity/loan', 'product/lending/entity/tool/attribute/out', 'product/lending/capability/lend-tools'),
  decision: 'product/lending/decision/reserve-how', option: 'reserve',
};
// A question the sketch stands for: its option `reserve` sets nothing (an option's `sets` cannot carry a workflow's steps), its
// proposal is shown before and after.
const seedDecision = async repo => {
  const record = { address: TOOL.decision, question: 'Should members be able to reserve a tool for a day?', context: 'The sketch shows how a reservation would run.',
    options: { reserve: { label: 'Members reserve a tool' }, skip: { label: 'No reservations' } }, proposal: { chose: 'reserve', why: 'The library is empty on busy days.' } };
  const put = await run('uv', ['run', '--frozen', '--no-sync', 'ogy', '--repo', repo, 'put', JSON.stringify([record])]);
  if (put.code !== 0) throw Error('decision refused: ' + put.stdout + put.stderr);
};
const OGY = {
  records: reserve('product/inspection', 'product/shared/actor/owner', 'product/review/entity/review-round', 'product/review/entity/review-round', 'product/review/entity/review-round', 'product/inspection/capability/preview-a-new-requirement'),
  decision: null, option: null, // no decision of this KB sets the sketch as drawn, and this KB is not written: no Keep here
};

function judgeShown(name, probe, keep = true) {
  const checks = {
    hash: has('#/sketch'), state: v => v === 'ready', tag: v => v === 'sketch', notKept: has('Not in the knowledge base'),
    sketchNodes: v => v >= 7, plain: v => v === 0, sketchClassOnReal: v => v === 0, realDashed: v => v === 0,
    wordMarks: v => v === probe.wordable && v >= 7, sketchEdges: v => v > 0 && v === probe.edges, afterFailure: v => v === 0,
    dashedEdges: v => v === probe.edges, endClasses: v => v.length === 0, treatment: v => v && /^dashed 1(\.5)?px$/.test(v.border) && v.hatch,
    coloured: v => v.length === 0, keep: v => v === keep, dismiss: v => v === true, cardsPlain: v => v === 0 && probe.cards > 0,
    agent: has('sketch'), levels: v => v.join() === '2', doc: v => v[0] <= v[1],
  };
  for (const [key, check] of Object.entries(checks)) if (!check(probe[key])) fail(name + ' ' + key + ' = ' + JSON.stringify(probe[key]));
  const touch = new Map(probe.touch.map(([address, how]) => [address, how]));
  if (probe.touch.length < 3) fail(name + ' only ' + probe.touch.length + ' would-touch rows');
  if ([...touch.values()].some(how => !['change', 'link', 'linked-from', 'reaches', 'reached-by'].includes(how))) fail(name + ' unknown touch ' + [...touch.values()]);
  if (probe.touch.some(([address]) => probe.steps.includes(address))) fail(name + ' a sketched step is listed as touched');
}
const measured = (name, values) => {
  const m = JSON.parse(values.find(value => value.startsWith('{') && JSON.parse(value).words));
  const counts = ['blockOverlaps', 'textRunsCrossedByEdge', 'blocksEnteredByEdge', 'labelsOnBlocks'].map(key => [key, Number(m.overlap.match(new RegExp(key + '=(\\d+)'))?.[1] ?? NaN)]);
  for (const [key, count] of counts) if (count !== 0) fail(name + ' overlap ' + key + '=' + count);
  if (m.text.min < 11 || m.text.max > 24 || m.text.distinct > 5) fail(name + ' type ' + JSON.stringify(m.text));
  if (m.contrast.min < 4.5) fail(name + ' contrast ' + m.contrast.min + ' ' + m.contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = m.words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
};
const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });

function scenesFor(started, token, kit, wait, options = {}) {
  const base = 'product/lending/decision/';
  const scenes = [];
  for (const width of widths) for (const theme of themes) {
    const t = `${width}-${theme}`, size = sizeOf(width), desk = width !== 390;
    const args = { title: 'Reserve a tool', records: kit.records, ...(kit.decision ? { decision: kit.decision, option: kit.option } : {}) };
    scenes.push({ name: `sketch-show-${t}`, route: '', fresh: true, ...size, wait, actions: [
      { media: theme }, clear(started, token), { eval: VERSION }, { eval: PROBE },
      draw(started, token, args), { eval: PROBE }, { shot: `sketch-${t}-1-shown` }, { eval: MEASURE },
      { click: '[data-level="3"]' }, { eval: PROBE }, { shot: `sketch-${t}-2-level3` }, { click: '[data-level="2"]' },
      { click: '[data-action=dismiss-sketch]', wait: 900 }, { click: '#tab-agent' }, { eval: PROBE }, { shot: `sketch-${t}-3-dismissed` }, { eval: VERSION }] });
    scenes.push({ name: `sketch-agent-${t}`, route: '', fresh: true, ...size, wait, actions: [
      { media: theme }, clear(started, token), { eval: VERSION }, draw(started, token, args), { eval: PROBE },
      clear(started, token), { eval: PROBE }, { eval: VERSION }] });
    scenes.push({ name: `sketch-busy-${t}`, route: base + 'closing-day', fresh: true, ...size, wait, actions: [
      { media: theme }, clear(started, token), { click: '#note' }, { type: 'only weekdays' },
      draw(started, token, args), { eval: PROBE }, { shot: `sketch-${t}-4-busy` },
      ...(desk ? [] : [{ click: '#tab-agent' }]), { click: '[data-action=open-sketch]', wait: 1500 }, { eval: PROBE }] });
    scenes.push({ name: `sketch-refuse-${t}`, route: '', fresh: true, ...size, wait, actions: [
      { media: theme }, clear(started, token),
      draw(started, token, { title: 'Nothing', records: [{ address: 'product/lending/nokind/x', says: 'No such kind.' }] }),
      draw(started, token, { title: 'Half', records: kit.records, decision: 'product/lending/decision/reserve-how' }),
      { click: '#tab-agent' }, { eval: PROBE }] });
    if (options.keep) scenes.push({ name: `sketch-keep-${t}`, route: '', fresh: true, ...size, wait, actions: [
      { media: theme }, clear(started, token), draw(started, token, args), { eval: VERSION },
      { click: '[data-action=keep]', wait: 1200 }, { eval: KEPT }, { shot: `sketch-${t}-5-keep` }, { eval: VERSION },
      { click: '[data-action=record]', wait: 1800 }, { eval: KEPT }, { shot: `sketch-${t}-6-recorded` }, { eval: VERSION }] });
  }
  return scenes;
}

let scenesKit = TOOL;
function judge(row, scene, values) {
  const list = parse(values.filter(value => !value.startsWith('VERSION ')));
  const [v0, v1] = versions(values);
  if (scene.startsWith('sketch-show')) {
    const probes = list.filter(item => 'hash' in item);
    const [before, shown, level3, gone] = probes;
    judgeShown(row.name + ' shown', shown, Boolean(scenesKit.decision));
    measured(row.name, values);
    if (before.hash !== '#/') fail(row.name + ' started at ' + before.hash);
    if (level3.levels.join() !== '3' || level3.sketchNodes < shown.sketchNodes) fail(row.name + ' level 3 ' + level3.levels + ' ' + level3.sketchNodes);
    judgeShown(row.name + ' level 3', { ...level3, levels: ['2'] }, Boolean(scenesKit.decision));
    if (gone.hash.split('?')[0] !== '#/' || gone.sketchNodes !== 0 || gone.agent !== null) fail(row.name + ' dismiss left ' + gone.hash + ' ' + gone.agent);
    if (!gone.log.some(has('Sketch dismissed'))) fail(row.name + ' the log does not say it was dismissed: ' + gone.log);
    if (v0 !== v1) fail(row.name + ' inspection version moved ' + v0 + ' -> ' + v1);
    console.log(row.name, JSON.stringify({ nodes: shown.sketchNodes, edges: shown.sketchEdges, touch: shown.touch.length, treatment: shown.treatment }));
  } else if (scene.startsWith('sketch-agent')) {
    const [shown, gone] = list.filter(item => 'hash' in item);
    if (shown.sketchNodes < 7 || !has('#/sketch')(shown.hash)) fail(row.name + ' not shown: ' + shown.hash);
    if (gone.sketchNodes !== 0 || gone.hash.split('?')[0] !== '#/' || !has('There is no sketch')(gone.empty ?? 'There is no sketch') ) fail(row.name + ' agent dismiss left ' + gone.hash);
    if (v0 !== v1) fail(row.name + ' inspection version moved');
    console.log(row.name, JSON.stringify({ shown: shown.hash, gone: gone.hash }));
  } else if (scene.startsWith('sketch-busy')) {
    const [page, opened] = list.filter(item => 'hash' in item);
    if (!has('closing-day')(page.hash) || page.sketchNodes !== 0 || !has('only weekdays')(page.note)) fail(row.name + ' the typing page was moved: ' + page.hash + ' ' + page.note);
    if (!has('asks you to look', 'shows a sketch')(page.agentRequest ?? 'asks you to look shows a sketch') && !has('shows a sketch')(page.agentRequest)) fail(row.name + ' no request: ' + page.agentRequest);
    judgeShown(row.name + ' opened', opened, true);
    console.log(row.name, JSON.stringify({ stayed: page.hash, request: page.agentRequest, opened: opened.hash }));
  } else if (scene.startsWith('sketch-refuse')) {
    const [refused] = list.filter(item => 'hash' in item);
    if (refused.agent !== null || refused.hash.split('?')[0] !== '#/') fail(row.name + ' a refused sketch changed the page: ' + refused.hash + ' ' + refused.agent);
    if (refused.log.length < 2 || !refused.log.slice(0, 2).every(has('Refused'))) fail(row.name + ' the log does not show both refusals: ' + refused.log);
    console.log(row.name, JSON.stringify(refused.log.slice(0, 2)));
  }
}

function judgeKeep(row, values) {
  const [opened, recorded] = parse(values.filter(value => !value.startsWith('VERSION '))).filter(item => 'chosen' in item);
  const [v0, v1, v2] = versions(values);
  if (!has('reserve-how/option/reserve', 'keep=1')(opened.hash)) fail(row.name + ' Keep went to ' + opened.hash);
  if (!has('Members reserve a tool')(opened.chosen) || opened.active !== 'said' || !has('reserve')(opened.radio)) fail(row.name + ' the answer form is not ready: ' + JSON.stringify(opened));
  if (!has('Members reserve a tool')(opened.said)) fail(row.name + ' the paraphrase is not the option label: ' + opened.said);
  if (v0 !== v1) fail(row.name + ' Keep alone changed the knowledge base ' + v0 + ' -> ' + v1);
  if (v2 === v1) fail(row.name + ' Record changed nothing');
  if (!has('Recorded')(recorded.readback) || recorded.refusal) fail(row.name + ' no read-back: ' + recorded.readback + ' ' + recorded.refusal);
}

// Three states of the knowledge base around a sketch that stands for an option: the proposal before, nothing moved by showing,
// dismissing or Keep, and after Record the answer in the decision's file and nothing else (the sketch itself is never written).
const WROTE = [/decision\/reserve-how\.yml$/];

async function toolRuns() {
  const repo = await toolCopy('dp-qa-sketch');
  await seedDecision(repo);
  const started = await startServer(repo);
  const token = await tokenOf(repo);
  try {
    const keepOf = scene => scene.name.startsWith('sketch-keep');
    const others = scenesFor(started, token, TOOL, 2500).filter(scene => !keepOf(scene));
    const [files0, shown0] = [tree(repo), await showEntry(repo, TOOL.decision)];
    if (!shown0.includes('reserve-how/proposal')) fail('the seeded decision has no proposal: ' + shown0.slice(0, 200));
    const results = await browse('sketch-tool', others, started);
    results.forEach((row, index) => judge(row, others[index].name, row.values));
    const files1 = tree(repo);
    const moved = [...new Set([...files0.keys(), ...files1.keys()])].filter(file => files0.get(file) !== files1.get(file));
    if (moved.length) fail('showing, dismissing, refusing and the busy page wrote into the repository: ' + moved);
    // Keep, then Record, writes once: each scene gets its own copy of the repository, checked by file and by ogy show.
    const count = scenesFor(started, token, TOOL, 2500, { keep: true }).filter(keepOf).length;
    for (let index = 0; index < count; index++) {
      const fresh = await toolCopy('dp-qa-sketch-keep');
      await seedDecision(fresh);
      const server = await startServer(fresh);
      try {
        const scene = scenesFor(server, await tokenOf(fresh), TOOL, 2500, { keep: true }).filter(keepOf)[index];
        const [before, shownBefore] = [tree(fresh), await showEntry(fresh, TOOL.decision)];
        const [row] = await browse('sketch-keep', [scene], server);
        judgeKeep(row, row.values);
        const after = tree(fresh);
        const changed = [...new Set([...before.keys(), ...after.keys()])].filter(file => before.get(file) !== after.get(file));
        const shown = await showEntry(fresh, TOOL.decision);
        if (shownBefore.includes('answers') || !shownBefore.includes('reserve-how/proposal')) fail(row.name + ' before: not a proposal alone: ' + shownBefore.slice(0, 200));
        if (changed.length !== WROTE.length || !WROTE.every(pattern => changed.some(file => pattern.test(file)))) fail(row.name + ' Record moved ' + changed);
        if (!shown.includes('answers') || !shown.includes('"chose": "reserve"') || !shown.includes('reserve-how/proposal')) fail(row.name + ' ogy show: answer or proposal missing: ' + shown.slice(0, 300));
        if ((await showEntry(fresh, TOOL.records[0].address)).includes('step/hold')) fail(row.name + ' the sketched workflow was written');
        console.log(row.name, JSON.stringify({ changed: changed.map(file => file.split('docs/kb/')[1]), answer: shown.split('\n').find(line => /answers/.test(line))?.slice(0, 90) }));
      } finally { await server.stop(); }
    }
  } finally { await started.stop(); }
}

async function ogyRuns() {
  scenesKit = OGY;
  const started = await startServer('.');
  const token = await tokenOf('.');
  try {
    const scenes = scenesFor(started, token, OGY, 30000).filter(scene => !scene.name.startsWith('sketch-busy') && (!process.env.ONLY || scene.name.includes(process.env.ONLY)));
    scenes[0].wait = 45000;
    const results = await browse('sketch-ogy', scenes, started);
    results.forEach((row, index) => judge(row, scenes[index].name, row.values));
  } finally { await started.stop(); }
}

await (mode === 'ogy' ? ogyRuns() : toolRuns());
console.log(failures.length ? failures.length + ' failures' : 'sketch checks passed');
process.exit(failures.length ? 1 : 0);
