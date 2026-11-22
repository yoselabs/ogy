// Real-input checks of the spotlight: node docs/design/board/qa/spotlight-check.mjs [tool|ogy] [width]  (from the repository root)
// An MCP call (HTTP, the server's own tool) points at entries; the page is driven with real mouse and key input. The tool library copy
// is the only KB that is written to (an answer is typed, never recorded); this repository's KB is read only.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, run, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };
const themes = ['light', 'dark'];

const PROBE = `(() => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const spots = all('[data-spot]');
  const rects = spots.map(e => e.getBoundingClientRect());
  let overlaps = 0;
  for (let i = 0; i < spots.length; i++) for (let j = i + 1; j < spots.length; j++) {
    if (spots[i].contains(spots[j]) || spots[j].contains(spots[i])) continue;
    const a = rects[i], b = rects[j];
    if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 2 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 2) overlaps++;
  }
  const dimmed = all('[data-dim]');
  const badge = spots[0] ? getComputedStyle(spots[0], '::before') : null;
  const railText = s => q(s)?.innerText.replace(/\\s+/g, ' ').trim() ?? null;
  return JSON.stringify({
    hash: location.hash, seq: document.body.dataset.spotlightSequence ?? null, at: Number(document.body.dataset.spotlightAt ?? 0), painted: Number(document.body.dataset.spotlightPaintedAt ?? 0),
    requestMark: q('#tab-agent')?.hasAttribute('data-request') ?? false, away: all('.agent-away').length, awayCurrent: Boolean(q('.agent-target[aria-current] .agent-away')), note: q('#note')?.value ?? null,
    spots: spots.map(e => e.dataset.spot).sort(), current: all('[data-spot-current]').map(e => e.dataset.spot), main: q('#main')?.dataset.spotlight ?? null,
    spotsDimmed: spots.filter(e => e.closest('[data-dim]')).length, targetChildrenDimmed: spots.reduce((n, e) => n + e.querySelectorAll('[data-dim]').length, 0),
    dimmed: dimmed.length, dimOpacity: dimmed[0] ? getComputedStyle(dimmed[0]).opacity : null,
    spotClasses: all('*').filter(e => [...e.classList].some(c => /spot/i.test(c))).length,
    outline: spots[0] ? getComputedStyle(spots[0]).outlineStyle + ' ' + getComputedStyle(spots[0]).outlineWidth : null, badge: badge ? badge.content : null,
    tab: q('[role=tab][aria-selected=true]')?.dataset.tab ?? null, agentCount: q('#tab-agent .tab-count')?.textContent.trim() ?? null,
    title: railText('[data-part=agent-title]'), connection: railText('[data-part=agent-connection]'), connState: q('[data-part=agent-connection]')?.dataset.state ?? null,
    rows: all('.agent-target').map(e => e.innerText.replace(/\\s+/g, ' ').trim()), step: railText('.agent-step'), stepNow: q('.agent-target[aria-current]')?.dataset.n ?? null,
    request: railText('.agent-request'), empty: railText('[data-part=agent-empty]'), log: all('.agent-call').map(e => e.textContent.replace(/\\s+/g, ' ').trim()),
    disabled: all('[data-part=agent-nav] .btn').map(e => e.dataset.action + ':' + e.disabled),
    scrollTop: Math.round(q('#main')?.scrollTop ?? -1), scrollable: q('#main') ? q('#main').scrollHeight > q('#main').clientHeight + 2 : null,
    wide: all('#main *, #rail *').filter(e => e.getBoundingClientRect().right > innerWidth + 1).length, scrollW: [document.documentElement.scrollWidth, innerWidth],
    overlaps, badgeBox: rects.map(r => [Math.round(r.left), Math.round(r.top)]).slice(0, 4),
  });
})()`;
const MEASURE = `window.__scope='#rail';JSON.stringify({probe:JSON.parse(${PROBE}),text:${TEXT},contrast:${CONTRAST},words:${VIEWER_WORDS}})`;
const VERSION = `fetch('/api/version', { credentials: 'same-origin' }).then(r => r.json()).then(j => 'VERSION ' + j.version)`;
const parse = values => JSON.parse(values.find(value => value.startsWith('{')));
const calls = values => values.filter(value => value.startsWith('CALL ')).map(value => JSON.parse(value.slice(5)));
const versions = values => values.filter(value => value.startsWith('VERSION ')).map(value => value.slice(8));
const probes = values => values.filter(value => value.startsWith('{')).map(value => JSON.parse(value).probe ?? JSON.parse(value));

async function tokenOf(repo) {
  const dir = (await run('git', ['-C', repo, 'rev-parse', '--absolute-git-dir'])).stdout.trim();
  return readFileSync(join(dir, 'ogy/server.token'), 'utf8').trim();
}

const show = (started, token, title, targets, session = 'qa agent') => ({ call: {
  url: started.origin + '/mcp/', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream', 'X-Ogy-Token': token },
  body: { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'spotlight', arguments: { action: 'show', title, targets, session } } } }, wait: 700 });

// The server keeps one spotlight for every page and scene: each scene starts by clearing it, like an agent that dismisses.
const clear = (started, token) => ({ call: { url: started.origin + '/mcp/', headers: { 'Content-Type': 'application/json', Accept: 'application/json, text/event-stream', 'X-Ogy-Token': token },
  body: { jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name: 'spotlight', arguments: { action: 'dismiss', session: 'qa agent' } } } }, wait: 400 });
const base = 'product/lending/decision/';
const TOOL = {
  pickup: [
    { address: base + 'pickup-window', says: 'The question waiting for you.' },
    { address: base + 'pickup-window/option/short', says: 'Short days: fewer volunteers.' },
    { address: base + 'pickup-window/option/long', says: 'Long days: more hours for members.' },
    { address: 'product/lending/quantity/pickup-hours', says: 'The number both options set.' }],
  closing: [{ address: base + 'closing-day', says: 'A different question.' }, { address: base + 'closing-day/option/yes', says: 'Closed on holidays.' }],
};
const OGY = [
  { address: 'product/inspection/decision/show-what-does-not-exist-yet', says: 'Decide how to show an invented flow.' },
  { address: 'product/inspection/decision/show-what-does-not-exist-yet/option/both', says: 'The proposed option.' },
  { address: 'product/inspection/decision/show-what-does-not-exist-yet/option/illustration-only', says: 'Sketches stay in the server.' },
  { address: 'product/inspection/decision/show-what-does-not-exist-yet/option/unagreed-entries', says: 'Real entries are the preview.' }];

function judge(name, probe, expect = {}) {
  if (probe.overlaps) fail(name + ' numbered targets overlap ' + probe.overlaps);
  if (probe.wide) fail(name + ' ' + probe.wide + ' elements past the right edge');
  if (probe.scrollW[0] > probe.scrollW[1]) fail(name + ' horizontal scroll ' + probe.scrollW);
  if (probe.spotClasses) fail(name + ' ' + probe.spotClasses + ' elements carry a spotlight-only class');
  if (probe.spotsDimmed || probe.targetChildrenDimmed) fail(name + ' a target is dimmed');
  for (const [key, check] of Object.entries(expect)) if (!check(probe[key], probe)) fail(name + ' ' + key + ' = ' + JSON.stringify(probe[key]));
}
const has = (...parts) => value => parts.every(part => String(value).includes(part));
const measure = (name, measured) => {
  const { text, contrast, words } = measured;
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' rail contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
};
const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });

async function toolRuns() {
  const repo = await toolCopy('dp-qa-spot');
  const started = await startServer(repo);
  const token = await tokenOf(repo);
  try {
    const scenes = [];
    for (const width of widths) for (const theme of themes) {
      const t = `${width}-${theme}`, size = sizeOf(width), desk = width !== 390;
      scenes.push({ name: `spot-follow-${t}`, route: '', fresh: true, ...size, wait: 2500, actions: [
        { media: theme }, clear(started, token), { eval: VERSION }, { eval: PROBE },
        show(started, token, 'Pickup window', TOOL.pickup), { eval: PROBE }, { shot: `spot-${t}-1-shown` }, { eval: MEASURE },
        { click: '[data-action=next]' }, { eval: PROBE }, { shot: `spot-${t}-2-next` },
        { click: '[data-action=next]' }, { click: '[data-action=next]' }, { eval: PROBE },
        { click: '[data-action=back]' }, { eval: PROBE },
        { click: '[data-action=dismiss]', wait: 900 }, { click: '#tab-agent' }, { eval: PROBE }, { shot: `spot-${t}-3-dismissed` }, { eval: VERSION }] });
      scenes.push({ name: `spot-scroll-${t}`, route: base + 'late-fee', fresh: true, size: desk ? [1440, 420] : size.size, mobile: size.mobile, wait: 2500, actions: [
        { media: theme }, clear(started, token), { wheel: 220, at: [desk ? 500 : 200, 250] }, { eval: PROBE },
        show(started, token, 'Another question', TOOL.closing), { eval: PROBE }, { click: '[data-action=dismiss]', wait: 1200 }, { eval: PROBE }] });
      scenes.push({ name: `spot-busy-${t}`, route: base + 'pickup-window', fresh: true, ...size, wait: 2500, actions: [
        { media: theme }, clear(started, token), { click: '[data-option$="/option/short"] label' }, { click: '#note' }, { type: 'only weekdays' },
        show(started, token, 'Closing days', TOOL.closing), { eval: PROBE }, { shot: `spot-${t}-4-busy-page` },
        ...(desk ? [] : [{ click: '#tab-agent' }]), { click: '[data-action=show]', wait: 900 }, { eval: PROBE }, { shot: `spot-${t}-6-after-show-me` }] });
      scenes.push({ name: `spot-typing-${t}`, route: base + 'closing-day', fresh: true, ...size, wait: 2500, actions: [
        { media: theme }, clear(started, token), show(started, token, 'Pickup window', TOOL.pickup),
        { click: '[data-option$="/option/short"] label' }, { click: '#note' }, { type: 'typed while the agent pointed' },
        { call: { ...clear(started, token).call }, wait: 700 }, { eval: PROBE }, { shot: `spot-${t}-7-dismissed-while-typing` }] });
      scenes.push({ name: `spot-refuse-${t}`, route: base + 'closing-day', fresh: true, ...size, wait: 2500, actions: [
        { media: theme }, clear(started, token), show(started, token, 'Nothing', [{ address: 'product/lending/actor/nobody', says: 'No such entry.' }]),
        { click: '#tab-agent' }, { eval: PROBE }] });
    }
    const results = await browse('spot-tool', scenes, started);
    results.forEach((row, index) => {
      const scene = scenes[index].name;
      const list = probes(row.values), [, call] = calls(row.values), [v0, v1] = versions(row.values);
      if (scene.startsWith('spot-follow')) {
        const [before, shown, , next, forward, back, gone] = list;
        const measured = parse(row.values.filter(value => value.startsWith('{') && JSON.parse(value).words)); measure(row.name, measured);
        if (call.status !== 200) fail(row.name + ' call status ' + call.status);
        const latency = shown.painted - call.t0;
        if (!(latency < 250)) fail(row.name + ' targets painted ' + latency + ' ms after the call began');
        judge(row.name + ' shown', shown, { hash: has('pickup-window', 'rail=agent'), spots: v => v.join() === '1,2,3,4', current: v => v.join() === '1', main: v => v === 'on', dimmed: v => v > 0, dimOpacity: v => v === '0.45',
          tab: v => v === 'agent', agentCount: has('4'), title: has('Pickup window'), rows: v => v.length === 4 && has('The question waiting')(v[0]), step: has('1 of 4'), connState: v => v === 'live', outline: has('solid', '2px') });
        judge(row.name + ' next', next, { current: v => v.join() === '2', stepNow: v => v === '2', step: has('2 of 4') });
        judge(row.name + ' end', forward, { current: v => v.join() === '4', disabled: v => v.includes('next:true') });
        judge(row.name + ' back', back, { current: v => v.join() === '3' });
        judge(row.name + ' dismissed', gone, { hash: v => v.split('?')[0] === '#/', spots: v => v.length === 0, dimmed: v => v === 0, main: v => v === null, empty: has('pointed at nothing'), log: v => v.length >= 2 && has('Dismissed')(v[0]) });
        if (before.hash !== '#/') fail(row.name + ' started at ' + before.hash);
        if (v0 !== v1) fail(row.name + ' inspection version moved ' + v0 + ' -> ' + v1);
        console.log(row.name, JSON.stringify({ latency, callMs: call.t1 - call.t0, shown: shown.spots, rows: shown.rows.length, log: gone.log }));
      } else if (scene.startsWith('spot-scroll')) {
        const [start, shown, back] = list;
        judge(row.name + ' shown', shown, { hash: has('closing-day'), spots: v => v.join() === '1,2' });
        if (start.scrollable && start.scrollTop < 20) fail(row.name + ' the page did not scroll first: ' + start.scrollTop);
        if (back.hash !== start.hash) fail(row.name + ' dismiss returned to ' + back.hash + ', was ' + start.hash);
        if (Math.abs(back.scrollTop - start.scrollTop) > 1) fail(row.name + ' dismiss scroll ' + back.scrollTop + ', was ' + start.scrollTop);
        console.log(row.name, JSON.stringify({ hash: [start.hash, back.hash], scrolled: [start.scrollTop, back.scrollTop], scrollable: start.scrollable }));
      } else if (scene.startsWith('spot-busy')) {
        const [page, followed] = list;
        judge(row.name + ' busy', page, { hash: has('pickup-window'), spots: v => v.length === 0, agentCount: has('2'), tab: v => v === 'agent', request: has('asks you to look'), requestMark: v => v === true, note: has('only weekdays'),
          disabled: v => v.includes('next:true') && v.includes('back:true') });
        judge(row.name + ' followed', followed, { hash: has('closing-day', 'rail=agent'), spots: v => v.join() === '1,2', request: v => v === null });
        console.log(row.name, JSON.stringify({ stayed: page.hash, request: page.request, followed: followed.hash }));
      } else if (scene.startsWith('spot-typing')) {
        const [stayed] = list;
        judge(row.name, stayed, { hash: has('pickup-window'), spots: v => v.length === 0, note: has('typed while the agent pointed') });
        console.log(row.name, JSON.stringify({ hash: stayed.hash, note: stayed.note }));
      } else {
        const [refused] = list;
        judge(row.name, refused, { hash: has('closing-day'), spots: v => v.length === 0, log: v => has('Refused', 'no such entry')(v[0]) });
        console.log(row.name, JSON.stringify(refused.log));
      }
    });
  } finally { await started.stop(); }
}

const GROUP3 = [
  { address: 'product/inspection/decision/preview-a-new-requirement', says: 'Review the agreed preview direction.' },
  { address: 'product/inspection/capability/preview-a-new-requirement', says: 'Every option sets this entry.' },
  { address: 'product/inspection/workflow/preview-requirement', says: 'It realizes the capability.' },
  { address: 'software/viewing/interface/inspection-data', says: 'Serves the preview step; unbuilt.' },
  { address: 'software/viewing/rule/agent-inspection-parity', says: 'Both interfaces satisfy it.' },
  { address: 'product/inspection/decision/inspection-outcome', says: 'The answered decision behind the goal.' }];
const hop = [{ click: '[data-action=next]' }, { eval: PROBE }];

async function ogyRuns() {
  const started = await startServer('.');
  const token = await tokenOf('.');
  try {
    const scenes = [];
    for (const width of widths) for (const theme of themes) {
      const t = `${width}-${theme}`;
      scenes.push({ name: `spot-ogy-${t}`, route: '', fresh: true, ...sizeOf(width), wait: 30000, actions: [
        { media: theme }, clear(started, token), { eval: VERSION }, show(started, token, 'How to show what does not exist yet', OGY), { eval: PROBE }, { shot: `spot-ogy-${t}-1-shown` },
        { click: '[data-action=next]' }, { eval: PROBE }, { click: '[data-action=dismiss]', wait: 1200 }, { eval: PROBE }, { eval: VERSION }] });
    }
    for (const width of widths) for (const theme of themes) {
      const t = `${width}-${theme}`;
      scenes.push({ name: `spot-hops-${t}`, route: '', fresh: true, ...sizeOf(width), wait: 30000, actions: [
        { media: theme }, clear(started, token), show(started, token, 'What the preview decision touches', GROUP3), { eval: PROBE }, { shot: `spot-hops-${t}-1` },
        ...Array(5).fill(hop).flat(), { shot: `spot-hops-${t}-6` }, { click: '[data-action=dismiss]', wait: 1500 }, { eval: PROBE }] });
    }
    scenes[0].wait = 45000;
    const results = await browse('spot-ogy', scenes, started);
    results.forEach((row, index) => {
      if (scenes[index].name.startsWith('spot-hops')) {
        const list = probes(row.values), start = list[0], gone = list.at(-1);
        // Each hop either numbers an element the owner can see or the Agent tab says that the target is not on this page.
        list.slice(0, 6).forEach((probe, hopIndex) => {
          const named = probe.current.length === 1 || probe.awayCurrent;
          if (!named) fail(row.name + ' hop ' + (hopIndex + 1) + ' shows nothing and says nothing: ' + probe.hash);
          judge(row.name + ' hop ' + (hopIndex + 1), probe, {});
        });
        if (gone.hash.split('?')[0] !== '#/' || gone.spots.length) fail(row.name + ' dismiss after hops returned to ' + gone.hash);
        console.log(row.name, JSON.stringify({ hops: list.slice(0, 6).map(p => [p.hash.split('?')[0].split('/').slice(-2).join('/'), p.current.join(), p.awayCurrent]), back: gone.hash }));
        return;
      }
      const [shown, next, gone] = probes(row.values), [, call] = calls(row.values), [v0, v1] = versions(row.values);
      const latency = shown.painted - call.t0;
      if (!(latency < 250)) fail(row.name + ' targets painted ' + latency + ' ms after the call began');
      judge(row.name + ' shown', shown, { spots: v => v.join() === '1,2,3,4', hash: has('show-what-does-not-exist-yet'), dimmed: v => v > 0 });
      judge(row.name + ' next', next, { current: v => v.join() === '2' });
      judge(row.name + ' dismissed', gone, { hash: v => v.split('?')[0] === '#/', spots: v => v.length === 0 });
      if (v0 !== v1) fail(row.name + ' inspection version moved');
      console.log(row.name, JSON.stringify({ latency, spots: shown.spots, hash: shown.hash }));
    });
  } finally { await started.stop(); }
}

await (mode === 'ogy' ? ogyRuns() : toolRuns());
console.log(failures.length ? failures.length + ' failures' : 'spotlight checks passed');
process.exit(failures.length ? 1 : 0);
