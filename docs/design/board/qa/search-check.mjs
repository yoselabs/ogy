// Real-input checks of the search overlay: node docs/design/board/qa/search-check.mjs [tool|ogy] [width]  (from the repository root)
// Reads the real KB, answers nothing. Keys and clicks are real input events; the only eval that acts is selecting the box's text.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTRAST, TEXT, VIEWER_WORDS } from './measures.js';
import { browse, here, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };

const PROBE = `(() => {
  const d = document.querySelector('dialog.finder'), all = (s, r = d) => [...r.querySelectorAll(s)];
  const rows = all('.result'), more = all('.more');
  const rect = e => e.getBoundingClientRect();
  const parts = all('.result *, .group-head, .group-head *, .search-bar, .search-bar *, .more, .search-note').filter(e => rect(e).width > 1);
  let overlaps = 0; const where = [];
  for (let i = 0; i < parts.length; i++) for (let j = i + 1; j < parts.length; j++) {
    const a = parts[i], b = parts[j]; if (a.contains(b) || b.contains(a)) continue;
    const ra = rect(a), rb = rect(b);
    if (Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left) > 1 && Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top) > 1) { overlaps++; where.push(a.className + '|' + b.className); }
  }
  const dr = rect(d), cut = all('.result-name .mention').filter(e => e.scrollWidth > e.clientWidth + 1).length;
  const kindX = new Set(rows.map(r => Math.round(rect(r.querySelector('.kind-word')).right))).size;
  const act = document.activeElement;
  return JSON.stringify({
    open: d.open, rows: rows.length, more: more.map(m => m.textContent.trim()), groups: all('.group-head').map(g => g.textContent.trim()),
    first: rows[0] ? [rows[0].dataset.kind, rows[0].querySelector('.mention').textContent.trim(), rows[0].dataset.address, rows[0].querySelector('.result-context')?.textContent ?? ''] : null,
    addresses: rows.map(r => r.dataset.address), perGroup: all('.group').map(g => g.querySelectorAll('.result').length),
    selected: rows.map((r, i) => r.getAttribute('aria-selected') === 'true' ? i : -1).filter(i => i >= 0),
    note: d.querySelector('.search-note').textContent.trim(), value: d.querySelector('.search-input').value,
    kindWords: rows.slice(0, 5).map(r => r.querySelector('.kind-word').textContent), icons: rows.every(r => r.querySelector('svg.kind-icon')),
    hash: location.hash, overlaps, where: where.slice(0, 4), cut, dialog: [Math.round(dr.left), Math.round(dr.top), Math.round(dr.right), Math.round(dr.bottom)],
    viewport: [innerWidth, innerHeight], scrollW: [document.documentElement.scrollWidth, innerWidth], kindColumns: kindX,
    modal: d.matches(':modal'), focus: act === d.querySelector('.search-input') ? 'input' : String(act.className || act.tagName),
  });
})()`;
const MEASURE = `window.__scope='dialog.finder';JSON.stringify({probe:JSON.parse(${PROBE}),text:${TEXT},contrast:${CONTRAST},words:${VIEWER_WORDS}})`;
const key = (name, vk, extra = {}) => ({ key: name, code: name.length === 1 ? 'Key' + name.toUpperCase() : name, vk, ...extra });
const ctrlK = key('k', 75, { mod: 2 });
const SELECT = `document.querySelector('.search-input').select(); 'selected'`;
const type = text => ({ type: text, wait: 300 });

function judge(name, m, expect = {}) {
  const { probe, text, contrast, words } = m;
  if (probe.overlaps) fail(name + ' overlaps ' + probe.overlaps + ' ' + probe.where.join(','));
  if (probe.cut) fail(name + ' ' + probe.cut + ' titles cut off');
  if (probe.scrollW[0] > probe.scrollW[1]) fail(name + ' horizontal scroll ' + probe.scrollW);
  const [l, t, r, b] = probe.dialog;
  if (l < 0 || t < 0 || r > probe.viewport[0] || b > probe.viewport[1]) fail(name + ' dialog outside viewport ' + probe.dialog);
  if (text.min < 11 || text.max > 24 || text.distinct > 5) fail(name + ' type ' + JSON.stringify(text));
  if (contrast.min < 4.5) fail(name + ' contrast ' + contrast.min + ' ' + contrast.fails.join('; '));
  for (const pattern of forbidden) { const hit = words.match(new RegExp(pattern, 'i')); if (hit) fail(name + ' forbidden word ' + hit[0]); }
  if (probe.rows > 1 && probe.kindColumns !== 1) fail(name + ' kind column ragged ' + probe.kindColumns);
  if (probe.rows && !probe.icons) fail(name + ' a row has no kind icon');
  for (const [k, check] of Object.entries(expect)) if (!check(probe[k], probe)) fail(name + ' ' + k + ' = ' + JSON.stringify(probe[k]));
  console.log(name, JSON.stringify({ rows: probe.rows, first: probe.first, groups: probe.groups.slice(0, 4), perGroup: probe.perGroup.slice(0, 4), type: text, contrast: contrast.min }));
}

async function main() {
  const repo = mode === 'ogy' ? '.' : await toolCopy('dp-qa-search');
  const started = await startServer(repo);
  const wait = mode === 'ogy' ? 30000 : 2500;
  const queries = mode === 'ogy'
    ? [['topology', p => p.addresses.includes('software/cli/decision/view-topology')], ['decision mode', p => p.addresses.includes('product/inspection/decision/human-decision-mode')], ['decision', () => true]]
    : [['loan', p => p.addresses[0] === 'product/lending/entity/loan'], ['late fee', p => p.addresses[0] === 'product/lending/quantity/late-fee'], ['open', () => true]];
  try {
    const scenes = [];
    const runs = [];
    for (const width of widths) {
      const size = [width, width === 390 ? 844 : 1000], mobile = width === 390;
      for (const theme of ['light', 'dark']) {
        const n = s => `search-${mode}-${width}-${theme}-${s}`;
        const actions = [{ media: theme },
          { click: '#header .search', wait: 600 }, { eval: MEASURE }, { shot: n('1-open') },
          key('Escape', 27), { eval: PROBE }, { eval: 'document.activeElement.className' },
          ctrlK, { eval: PROBE }];
        for (const [q] of queries) actions.push({ eval: SELECT }, type(q), { eval: MEASURE }, { shot: n('2-' + q.replace(/ /g, '-')) });
        actions.push({ eval: SELECT }, type('zzzqq'), { eval: MEASURE }, { shot: n('3-nohit') });
        actions.push({ eval: SELECT }, type(queries[0][0]), key('ArrowDown', 40), key('ArrowDown', 40), { eval: PROBE }, key('ArrowUp', 38), { eval: PROBE }, key('Enter', 13, { text: '\r' }), { eval: PROBE });
        actions.push(ctrlK, { eval: PROBE }, { eval: SELECT }, type(queries[2][0]), { eval: PROBE });
        if (mode === 'ogy') actions.push({ click: '.more', wait: 500 }, { eval: PROBE });
        actions.push({ click: '.result', wait: 800 }, { eval: PROBE });
        scenes.push({ name: n('run'), fresh: true, route: '', size, mobile, wait, actions });
        runs.push(n);
      }
    }
    const results = await browse(`search-${mode}`, scenes, started);
    results.forEach((row, index) => {
        const n = runs[index];
        const v = row.values;
        let i = 0;
        const next = () => JSON.parse(v[i++]);
        const opened = next();
        judge(n('opened'), opened, { open: x => x === true, modal: x => x === true, focus: x => x === 'input', note: x => x.includes('Type a name') });
        if (next().open) fail(n('esc') + ' dialog still open after Esc');
        if (!/search/.test(v[i++])) fail(n('esc') + ' focus did not return to the header button: ' + v[i - 1]);
        const viaKey = next();
        if (!viaKey.open || viaKey.focus !== 'input') fail(n('ctrlk') + ' Ctrl K did not open with the box focused');
        for (const [q, check] of queries) {
          i++;
          judge(n(q), next(), { rows: x => x > 0, addresses: (_, p) => check(p) });
        }
        i++;
        judge(n('nohit'), next(), { rows: x => x === 0, note: x => x.startsWith('Nothing matches') && x.includes('zzzqq') });
        i++;
        const down2 = next(), up1 = next(), entered = next();
        if (down2.rows > 2 && down2.selected[0] !== 2) fail(n('keys') + ' two ArrowDown did not select row 2: ' + down2.selected);
        if (down2.rows > 1 && up1.selected[0] !== 1) fail(n('keys') + ' ArrowUp did not select row 1: ' + up1.selected);
        if (entered.open || !entered.hash.includes(up1.addresses[1] ?? up1.addresses[0])) fail(n('keys') + ' Enter did not go to the selected row: ' + entered.hash + ' open=' + entered.open);
        const again = next();
        if (!again.open) fail(n('reopen') + ' did not reopen');
        i++;
        const big = next();
        if (big.perGroup.some(x => x > 20)) fail(n('big') + ' a group shows more than 20 rows: ' + big.perGroup);
        if (mode === 'ogy') {
          if (!big.more.length) fail(n('big') + ' no "more" button on "decision"');
          const grown = next();
          if (!(grown.rows > big.rows)) fail(n('more') + ' "more" did not add rows');
        }
        const clicked = next();
        if (clicked.open || clicked.hash === entered.hash) fail(n('click') + ' real click on a row did not navigate: ' + clicked.hash);
        console.log(n('done'), 'enter->', entered.hash, 'click->', clicked.hash);
    });
  } finally { await started.stop(); }
  console.log(failures.length ? 'FAIL\n' + failures.join('\n') : 'PASS search-check ' + mode);
  process.exitCode = failures.length ? 1 : 0;
}
await main();
