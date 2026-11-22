// Real-input checks of the decision page: node docs/design/board/qa/decision-check.mjs [static|answer|ogy] [width]  (from the repository root)
// Never answers a decision of the real KB: answering runs on a temporary copy of the tool library; the real KB is only read.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, out, show, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'static';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };

const PROBE = `(() => {
  const q = s => document.querySelector(s), all = s => [...document.querySelectorAll(s)];
  const text = s => q(s)?.innerText.replace(/\\s+/g, ' ').trim() ?? null;
  const items = all('.decision [data-part], .decision .option, .decision .answer, .decision h1, .decision h2, .decision .pill, .decision .set-row, .decision .btn, .decision .field, .decision label, .decision input');
  const rects = items.map(e => [e, e.getBoundingClientRect()]).filter(([, r]) => r.width > 1 && r.height > 1);
  let overlaps = 0; const where = [];
  for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
    const [a, ra] = rects[i], [b, rb] = rects[j];
    if (a.contains(b) || b.contains(a)) continue;
    if (Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left) > 2 && Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top) > 2) { overlaps++; where.push(a.className + '|' + b.className); }
  }
  const wide = all('.decision *').filter(e => e.getBoundingClientRect().right > innerWidth + 1).length;
  return JSON.stringify({
    first: (q('.decision')?.innerText.split('\\n')[0] ?? '').trim(), target: all('.option.is-target').length,
    status: text('[data-part=status]'), question: text('[data-part=question]'), context: text('[data-part=context]'),
    options: all('[data-option]').length, radios: all('input[name=option]').length, checked: all('input[name=option]:checked').length,
    chosenMarks: all('[data-mark=chosen]').length, proposedMarks: all('[data-mark=proposed]').length,
    sets: all('[data-part=sets]').length, reach: all('[data-part=reach]').map(e => e.innerText.replace(/\\s+/g, ' ').trim()),
    reachOpen: all('details[data-part=reach]').map(e => e.open),
    proposal: text('[data-part=proposal]'), history: all('[data-part=history-entry]').map(e => e.innerText.replace(/\\s+/g, ' ').trim()),
    note: text('[data-part=note]'), delegated: text('[data-part=delegated]'),
    noteColour: q('[data-part=note]') ? getComputedStyle(q('[data-part=note]')).color : null,
    said: q('#said')?.value ?? null, noteValue: q('#note')?.value ?? null, preview: text('[data-part=preview]'), chosen: text('[data-part=chosen]'),
    recordDisabled: q('[data-action=record]')?.disabled ?? null, formHidden: q('[data-part=answer-section]')?.hidden ?? null,
    readback: q('[data-part=readback]')?.hidden ? null : text('[data-part=readback]'), next: q('[data-part=next]')?.innerText.trim() ?? null, nextHref: q('[data-part=next] a')?.getAttribute('href') ?? null,
    refusal: q('[data-part=refusal]')?.hidden === false ? text('[data-part=refusal]') : null,
    loading: text('[data-part=loading]'), waitingStat: q('#strip [data-stat=waiting] b')?.textContent ?? null,
    mentions: all('.decision a[data-renderer=mention]').length, hrefs: all('.decision a[data-renderer=mention]').map(a => a.getAttribute('href')).slice(0, 4),
    authoredOutside: all('.decision h1:not([data-authored])').length,
    overlaps, where: where.slice(0, 4), wide, scrollW: [document.documentElement.scrollWidth, innerWidth],
    focusRing: (() => { const e = document.activeElement; const s = getComputedStyle(e); return e.tagName.toLowerCase() + ' ' + s.outlineStyle + ' ' + s.outlineWidth; })(),
  });
})()`;
const MEASURE = `window.__scope='.decision';JSON.stringify({probe:JSON.parse(${PROBE}),text:${TEXT},contrast:${CONTRAST},words:${VIEWER_WORDS}})`;
const parse = values => JSON.parse(values.find(value => value.startsWith('{')));

function judge(name, measured, expect = {}) {
  const { probe, text, contrast, words } = measured;
  if (probe.overlaps) fail(name + ' overlaps ' + probe.overlaps + ' ' + probe.where.join(','));
  if (probe.wide) fail(name + ' ' + probe.wide + ' elements past the right edge');
  if (probe.scrollW[0] > probe.scrollW[1]) fail(name + ' horizontal scroll ' + probe.scrollW);
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
  for (const [key, check] of Object.entries(expect)) { const ok = check(probe[key], probe); if (!ok) fail(name + ' ' + key + ' = ' + JSON.stringify(probe[key])); }
  console.log(name, JSON.stringify({ status: probe.status, options: probe.options, chosen: probe.chosenMarks, checked: probe.checked, type: text, contrast: contrast.min }));
}

const has = (...parts) => value => parts.every(part => String(value).includes(part));
const decisions = {
  waiting: ['product/lending/decision/pickup-window', { status: has('Waiting for you'), first: has('Waiting for you'), chosenMarks: v => v === 0, options: v => v === 2, radios: v => v === 2, proposedMarks: v => v === 1, history: v => v.length === 0,
    reach: v => v.length === 1 && has('same for every option')(v[0]) && has('Weekdays') !== null, context: has('Why this is asked', 'evenings'), formHidden: v => v === false, recordDisabled: v => v === true }],
  hedged: ['product/lending/decision/late-fee', { first: has('Answered, 24 Nov 2026: 2 EUR per day, per tool'), status: has('Answered, 24 Nov 2026: ', '2 EUR per day, per tool', 'with a note'), chosenMarks: v => v === 1, history: v => v.length === 1 && has('for now', 'Two euros is fine for now')(v[0]),
    note: has('Note: for now'), proposal: has('Proposed:', 'because', 'You said (paraphrased): A small fee', 'Read as 2 EUR per day, per tool') }],
  delegated: ['product/lending/decision/fee-rounding', { first: has('Answered for you under delegation, 24 Nov 2026: Rounded up'), status: has('Answered for you under delegation, 24 Nov 2026: ', 'Rounded up'), chosenMarks: v => v === 1, delegated: has('Given for you under delegation'),
    history: v => v.length === 1 && has('Given for you under delegation')(v[0]) }],
  noOptions: ['product/lending/decision/reply-wait', { status: has('Waiting for you'), options: v => v === 0, formHidden: v => v === true, proposal: has('Proposed:', 'Reply wait', 'is: 2', 'Because Two days fit a weekend') }],
  missing: ['product/lending/decision/nope', {}],
};

const themes = ['light', 'dark'];
const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });

// One server, one browser: the exchange URL is good once, so every width and theme goes through the same session.
async function staticRuns() {
  const repo = await toolCopy();
  const started = await startServer(repo);
  try {
    const scenes = [];
    for (const width of widths) for (const theme of themes) for (const [key, [address]] of Object.entries(decisions))
      scenes.push({ name: `dec-tool-${width}-${theme}-${key}`, key, route: address, ...sizeOf(width), wait: 2500,
        actions: [{ media: theme }, { eval: key === 'missing' ? 'document.querySelector("#main").innerText.replace(/\\s+/g," ")' : MEASURE }] });
    const results = await browse('dec-tool', scenes, started);
    results.forEach((row, index) => {
      const { key } = scenes[index];
      if (key === 'missing') { if (!row.values.join('').includes('There is no decision')) fail(row.name + ' missing decision page: ' + row.values.join('|')); return; }
      judge(row.name, parse(row.values), decisions[key][1]);
    });
  } finally { await started.stop(); }
}

async function ogyRuns() {
  const started = await startServer('.');
  const pages = { hedgedReal: 'product/inspection/decision/map-layers', most: 'software/ontology/decision/rule-linked-by-follower', five: 'product/inspection/decision/product-map' };
  try {
    const scenes = [];
    for (const width of widths) for (const theme of themes) for (const [key, address] of Object.entries(pages))
      scenes.push({ name: `dec-ogy-${width}-${theme}-${key}`, key, route: address, ...sizeOf(width), wait: 24000, actions: [{ media: theme }, { eval: MEASURE }] });
    scenes[0].wait = 40000;
    const results = await browse('dec-ogy', scenes, started);
    results.forEach((row, index) => {
      const key = scenes[index].key;
      judge(row.name, parse(row.values), key === 'hedgedReal' ? { note: has('Yes, I guess'), status: has('Answered') } : { options: v => v >= 5, chosenMarks: v => v === 1 });
    });
  } finally { await started.stop(); }
}

const tab = { key: 'Tab', code: 'Tab', vk: 9 };
const ACTIVE = `document.activeElement.id + '|' + document.activeElement.tagName.toLowerCase()`;
const key = (name, vk, extra = {}) => ({ key: name, code: name, vk, ...extra });
const FOCUS_STATE = `JSON.stringify({ id: document.activeElement.id, said: document.querySelector('#said').value })`;

async function answerRuns() {
  for (const width of widths) {
    const repo = await toolCopy('dp-qa-answer-' + width);
    const started = await startServer(repo);
    const size = [width, width === 390 ? 844 : 1000], mobile = width === 390;
    const base = 'product/lending/decision/';
    const pickup = base + 'pickup-window', closing = base + 'closing-day';
    // Another writer answers pickup-window from inside the page's own session; a page that holds an older version is then stale.
    const OTHER = `fetch('/api/standing').then(r => r.json()).then(d => fetch('/api/answer', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ decision: '${pickup}', option: 'long', said: 'Every day', version: d.version }) }).then(r => r.status))`;
    const n = suffix => `dec-answer-${width}-${suffix}`;
    try {
      const scenes = [
        { name: n('pick'), route: pickup, size, mobile, wait: 2500, actions: [
          { eval: PROBE }, key('Tab', 9), { eval: PROBE },
          { click: '[data-option$="/option/short"] label' }, { eval: PROBE }, { shot: n('1-chosen') },
          { click: '#note' }, { type: 'only on weekdays' }, { click: '#said' }, key('End', 35), { type: ' (after work)' }, { eval: PROBE }, { shot: n('2-before-record') },
          { click: '[data-action=record]', wait: 3000 }, { eval: PROBE }, { shot: n('3-readback') },
          { click: '[data-part=next] a', wait: 1500 }, { eval: 'location.hash' }, { eval: PROBE }] },
        { name: n('optionlink'), route: base + 'late-fee', size, mobile, wait: 1500, actions: [
          { click: '[data-part=status] a', wait: 1500 }, { eval: 'location.hash' }, { eval: PROBE }, { shot: n('5-option-target') }] },
        { name: n('reach'), route: base + 'late-fee', size, mobile, wait: 1500, actions: [
          { eval: PROBE }, { click: 'details.reach summary', wait: 600 }, { eval: PROBE }, { shot: n('6-reach-open') }] },
        { name: n('keyboard'), route: base + 'visiting-hours', size, mobile, wait: 1500, actions: [
          { click: 'h1.question' }, key('Tab', 9), { eval: ACTIVE }, key('ArrowDown', 40), { eval: PROBE },
          key('Tab', 9), { eval: ACTIVE }, key('Tab', 9), { eval: ACTIVE }, { type: ' ok' }, key('Tab', 9), { eval: ACTIVE }, { type: 'by keyboard' }, key('Tab', 9), { eval: ACTIVE },
          key('Enter', 13, { text: '\r' }), { eval: 'new Promise(r => setTimeout(r, 2500))' }, { eval: PROBE }, { shot: n('7-keyboard-recorded') },
          { click: '[data-action=again]', wait: 600 }, { eval: PROBE }, { eval: ACTIVE }, { shot: n('8-again') }] },
        { name: n('focus'), route: base + 'late-fee', size, mobile, wait: 1500, actions: [
          { click: '[data-option$="/option/one"] label' }, { click: '#said' }, { type: ' X' }, { eval: OTHER, wait: 13000 }, { type: ' Y' }, { eval: FOCUS_STATE }] },
        { name: n('stale'), fresh: true, route: closing, size, mobile, wait: 2500, actions: [
          { eval: OTHER, wait: 1500 }, { click: '[data-option$="/option/yes"] label' }, { click: '[data-action=record]', wait: 2500 }, { eval: PROBE }, { shot: n('4-refused') }] },
      ];
      const results = await browse(`dec-answer-${width}`, scenes, started);
      const [pick, optionlink, reach, keyboard, focus, stale] = results;
      const p = values => JSON.parse(values);
      const v = pick.values;
      const probes = { before: p(v[0]), tab: p(v[1]), chosen: p(v[2]), typed: p(v[3]), recorded: p(v[4]), next: p(v[6]) };
      if (probes.before.waitingStat !== '4') fail(width + ' waiting count before = ' + probes.before.waitingStat);
      if (probes.before.recordDisabled !== true) fail(width + ' Record enabled before choosing');
      if (!probes.tab.focusRing.includes('solid 2px')) fail(width + ' focus ring after Tab ' + probes.tab.focusRing);
      if (probes.chosen.said !== 'Weekdays 17:00 to 19:00' || probes.chosen.checked !== 1) fail(width + ' click did not pre-fill the paraphrase: ' + probes.chosen.said);
      if (probes.chosen.recordDisabled !== false) fail(width + ' Record disabled after choosing');
      if (!probes.typed.preview?.includes('after work') || !probes.typed.preview.includes('only on weekdays')) fail(width + ' preview misses the typed words: ' + probes.typed.preview);
      const r = probes.recorded;
      if (!r.readback?.includes('Recorded: Weekdays 17:00 to 19:00') || !r.readback.includes('(after work)') || !r.readback.includes('only on weekdays')) fail(width + ' read-back: ' + r.readback);
      if (r.waitingStat !== '3') fail(width + ' waiting count after = ' + r.waitingStat);
      if (!r.status?.includes('Answered, ') || r.chosenMarks !== 1) fail(width + ' page did not turn answered: ' + r.status);
      if (!/decision\/(closing-day|reply-wait|visiting-hours)$/.test(r.nextHref || '')) fail(width + ' next link ' + r.nextHref);
      if (!probes.next.status) fail(width + ' next link led nowhere');
      for (const text of [probes.typed.preview, r.readback, probes.chosen.chosen]) for (const pattern of forbidden) if (new RegExp(pattern, 'i').test(text || '')) fail(width + ' forbidden word ' + pattern + ' in ' + text);
      const shown = await show(repo, pickup);
      if (!shown.includes('Weekdays 17:00 to 19:00 (after work)') || !shown.includes('only on weekdays')) fail(width + ' ogy show does not hold the answer: ' + shown.slice(0, 600));
      // An option mention leads to its decision's page with that option marked.
      if (!optionlink.values[0].endsWith('/late-fee/option/two') || p(optionlink.values[1]).target !== 1 || p(optionlink.values[1]).options !== 2) fail(width + ' option link: ' + optionlink.values[0] + ' ' + optionlink.values[1].slice(0, 120));
      // The collapsed reach list opens with a real click.
      const [shut, open] = [p(reach.values[0]), p(reach.values[1])];
      if (shut.reachOpen[0] !== false || open.reachOpen[0] !== true) fail(width + ' reach list did not open: ' + shut.reachOpen + ' ' + open.reachOpen);
      // Keyboard only: arrows choose, Tab walks to the fields, Enter records; "Not what I meant" clears the choice and returns to the options.
      const kv = keyboard.values;
      const [k1, k2, k3, k4, k5, k6, kRecorded, kAgain, kFocus] = [kv[0], p(kv[1]), kv[2], kv[3], kv[4], kv[5], p(kv[7]), p(kv[8]), kv[9]];
      if (!k1.startsWith('option-')) fail(width + ' Tab from the question did not reach an option: ' + k1);
      if (k2.checked !== 1 || k2.said !== 'Members and one guest') fail(width + ' ArrowDown did not choose the second option: ' + k2.said);
      if (![k3, k4, k5, k6].includes('said|input') || !k6.endsWith('|button')) fail(width + ' Tab order ' + [k3, k4, k5, k6].join(' > '));
      if (!kRecorded.readback?.includes('Recorded: Members and one guest') || !kRecorded.readback.includes('ok') || !kRecorded.readback.includes('by keyboard')) fail(width + ' keyboard read-back: ' + kRecorded.readback);
      if ((kAgain.readback !== null && kAgain.readback !== '') || kAgain.checked !== 0 || !kAgain.chosen?.includes('Choose an option above') || !kFocus.startsWith('option-')) fail(width + ' Not what I meant: ' + JSON.stringify([kAgain.readback, kAgain.checked, kAgain.chosen, kFocus]));
      // A refresh while typing keeps focus and the typed words.
      const f = JSON.parse(focus.values[0] === '200' ? focus.values[1] : focus.values[0]);
      if (f.id !== 'said' || !/ X.*Y$/.test(f.said)) fail(width + ' typing lost on refresh: ' + JSON.stringify(f));
      const s = JSON.parse(stale.values[1]);
      if (stale.values[0] !== '200') fail(width + ' the other writer was refused: ' + stale.values[0]);
      if (!s.refusal?.includes('changed since this page was read')) fail(width + ' stale refusal text: ' + s.refusal);
      const afterStale = await show(repo, closing);
      if (/answered/i.test(afterStale)) fail(width + ' stale write was recorded: ' + afterStale.slice(0, 300));
      console.log(width, 'answer flow', JSON.stringify({ before: probes.before.waitingStat, after: r.waitingStat, next: r.nextHref, refusal: s.refusal, keyboard: [k1, k3, k4, k5, k6], focus: f }));
    } finally { await started.stop(); }
  }
}

// Every decision of a KB, one after the other: no forbidden word, the chosen mark exactly when answered, the status first. (Navigation by hash, not by mouse.)
const SWEEP = `(async () => {
  const standing = await (await fetch('/api/standing')).json();
  const out = [];
  for (const [address, row] of Object.entries(standing.decisions)) {
    location.hash = '#/' + address;
    await new Promise(done => setTimeout(done, 300));
    const root = document.querySelector('.decision');
    const clone = root.cloneNode(true);
    clone.querySelectorAll('[data-authored]').forEach(e => e.remove());
    out.push({ address, status: row.status, first: (root.innerText.split('\\n')[0] || '').trim(), marks: root.querySelectorAll('[data-mark=chosen]').length, options: root.querySelectorAll('[data-option]').length, words: clone.innerText.replace(/\\s+/g, ' ') });
  }
  return JSON.stringify(out);
})()`;

async function sweepRuns() {
  const sets = [['tool', await toolCopy('dp-qa-sweep')], ['ogy', '.']];
  for (const [name, repo] of sets) {
    const started = await startServer(repo);
    try {
      const [row] = await browse('dec-sweep-' + name, [{ name: 'dec-sweep-' + name, route: 'waiting', size: [1440, 1000], wait: name === 'ogy' ? 40000 : 3000, actions: [{ eval: SWEEP }] }], started);
      const rows = JSON.parse(row.values[0]);
      let bad = 0;
      for (const d of rows) {
        const problems = [];
        if (d.status === 'answered' ? d.marks !== 1 : d.marks !== 0) problems.push('chosen marks ' + d.marks);
        if (!(d.first.includes(d.status === 'answered' ? 'Answered' : 'Waiting for you'))) problems.push('first line ' + d.first);
        for (const pattern of forbidden) if (new RegExp(pattern, 'i').test(d.words)) problems.push('forbidden ' + pattern);
        if (problems.length) { bad++; fail(name + ' ' + d.address + ': ' + problems.join('; ')); }
      }
      console.log('sweep', name, rows.length, 'decisions,', bad, 'broken');
    } finally { await started.stop(); }
  }
}

if (mode === 'static') await staticRuns();
else if (mode === 'ogy') await ogyRuns();
else if (mode === 'answer') await answerRuns();
else if (mode === 'sweep') await sweepRuns();
else { await staticRuns(); await answerRuns(); await sweepRuns(); await ogyRuns(); }
writeFileSync(join(out, 'decision-check-' + mode + '.txt'), failures.length ? failures.join('\n') : 'PASS');
console.log(failures.length ? 'FAIL ' + failures.length : 'PASS decision-check ' + mode);
process.exitCode = failures.length ? 1 : 0;
