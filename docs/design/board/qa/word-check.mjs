// Language pass check: node docs/design/board/qa/word-check.mjs [tool|ogy] [width]  (from the repository root)
// Visits every route, takes the viewer's own text (authored KB text removed by its data-authored mark) and fails on any word that is
// not a glossary term, an ontology word (kind and field names) or in a words.js file; on a glossary "avoid" word, on a forbidden
// pattern, on jargon that no glossary line explains, and on a plural such as "1 steps". Reads only; no answer is recorded.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { browse, here, run, startServer, toolCopy } from './decision-lib.mjs';

const mode = process.argv[2] || 'tool';
const widths = process.argv[3] ? [Number(process.argv[3])] : [1440, 390];
const lines = name => readFileSync(join(here, name), 'utf8').trim().split('\n').filter(Boolean);
const forbidden = lines('forbidden.txt');
const jargon = lines('jargon.txt');
const failures = [];
const fail = text => { failures.push(text); console.log('FAIL', text); };
const jsRoot = 'src/ogy/web/static/js';

const wordsOf = text => (text.toLowerCase().match(/[a-z][a-z']*/g) || []);
const stems = word => [word, word.replace(/'s$/, ''), word.replace(/ies$/, 'y'), word.replace(/es$/, ''), word.replace(/s$/, ''), word.replace(/ed$/, ''), word.replace(/ed$/, 'e'), word.replace(/ing$/, ''), word.replace(/ing$/, 'e'), word.replace(/ly$/, '')];

// Fixed words: every string (and the output of every function) in ui/words.js and each views/*/words.js, shell and spotlight words.
function wordFiles(dir) {
  return readdirSync(dir).flatMap(name => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? wordFiles(path) : name === 'words.js' ? [path] : [];
  });
}
async function fixedVocabulary() {
  const vocab = new Set(); const counts = {};
  const take = value => {
    if (typeof value === 'string') wordsOf(value).forEach(word => vocab.add(word));
    else if (typeof value === 'function') take(value(3, 5));
    else if (Array.isArray(value)) value.forEach(take);
    else if (value && typeof value === 'object') Object.values(value).forEach(take);
  };
  for (const path of wordFiles(jsRoot)) { const { words } = await import(pathToFileURL(join(process.cwd(), path))); counts[path] = Object.keys(words).length; take(words); }
  return { vocab, counts };
}

// Glossary words and the words it says to avoid, read from `ogy glossary` of the repository under test.
async function glossary(repo) {
  const done = await run('uv', ['run', '--frozen', '--no-sync', 'ogy', '--repo', repo, 'glossary']);
  const terms = new Set(); const avoid = new Set();
  for (const line of done.stdout.split('\n')) {
    const term = line.match(/^ {2}([a-z][a-z -]*): /); if (term) wordsOf(term[1]).forEach(word => terms.add(word));
    const bad = line.match(/^ {4}avoid: (.*)$/); if (bad) bad[1].split(';').map(part => part.trim()).filter(part => part && !part.startsWith('?')).forEach(part => avoid.add(part));
  }
  return { terms, avoid };
}

// The viewer's own text of the live page: every text node outside an element marked data-authored, joined by spaces.
const COLLECT = `(() => { const parts = [];
  const walk = node => { for (const child of node.childNodes) {
    if (child.nodeType === 3) parts.push(child.textContent);
    else if (child.nodeType === 1 && !child.hasAttribute('data-authored') && !/^(SCRIPT|STYLE|TEMPLATE)$/.test(child.tagName)) { parts.push(' '); walk(child); parts.push(' '); }
    if (child.nodeType === 1 && child.hasAttribute('data-authored')) parts.push(' '); } };
  walk(document.body); return parts.join('').replace(/\\s+/g, ' '); })()`;

// In the page: visit every route, wait for it to settle, return the viewer's text per route and the ontology's own words.
const SWEEP = routes => `(async () => {
  const sleep = ms => new Promise(done => setTimeout(done, ms));
  const doc = await (await fetch('/api/inspection', { credentials: 'same-origin' })).json();
  const onto = new Set(); const walk = (value, depth) => { if (!value || typeof value !== 'object' || depth > 8) return;
    for (const [key, inner] of Object.entries(value)) { key.split(/[_\\-. ]/).forEach(w => onto.add(w.toLowerCase())); if (typeof inner === 'string' && /^[a-z][a-z_-]{1,20}$/.test(inner)) onto.add(inner); walk(inner, depth + 1); } };
  walk(doc.ontology, 0);
  const list = ${JSON.stringify(routes)}.flatMap(r => r === '@sample' ? ['workflow', 'decision', 'entity', 'actor', 'goal', 'capability'].flatMap(k => doc.entries.filter(e => e.kind === k && e.address.split('/').length === 4).slice(0, 3).map(e => e.address)) : r === '@entries' ? doc.entries.filter(e => e.address.split('/').length === 4).map(e => e.address) : [r]);
  const out = {};
  for (const route of list) {
    location.hash = '#/' + route; await sleep(250);
    for (let i = 0; i < 40 && /Loading|Reading|Laying/.test(document.getElementById('main').innerText); i++) await sleep(100);
    await sleep(150);
    const entry = doc.entries.find(e => e.address === route);
    const crumb = document.querySelector('#crumb li:last-child')?.textContent.trim() ?? '';
    const plural = [...document.querySelectorAll('body *')].filter(e => e.children.length === 0 && /^\\+?1 [a-z]+s$/i.test(e.textContent.trim()) && !/status$/i.test(e.textContent.trim())).map(e => e.textContent.trim());
    out[route] = { text: (${COLLECT}), plural, crumb, titled: Boolean(entry && (entry.title || entry.sentence)), key: route.split('/')[3] ?? null };
  }
  return JSON.stringify({ routes: out, onto: [...onto] });
})()`;
const parse = values => JSON.parse(values.find(value => value.startsWith('{')));
const escape = text => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

function judge(name, { routes, onto }, vocab, gloss) {
  const known = new Set([...vocab, ...gloss.terms, ...onto]);
  const ok = word => word.length < 2 || stems(word).some(form => known.has(form));
  const unknown = new Map();
  if (process.env.DUMP) for (const [route, one] of Object.entries(routes)) if (route.includes(process.env.DUMP)) console.log('TEXT', route, '|', one.text);
  for (const [route, one] of Object.entries(routes)) {
    const text = one.text.replace(/\b\d{1,2}:\d{2}\s?[AP]M\b/gi, ' ').replace(/\b\d{0,2} ?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,4}\b/gi, ' ');
    for (const word of new Set(wordsOf(text))) if (!ok(word)) unknown.set(word, (unknown.get(word) || []).concat(route));
    for (const pattern of forbidden) { const hit = text.match(new RegExp(pattern, 'i')); if (hit) fail(`${name} ${route}: forbidden "${hit[0]}"`); }
    for (const pattern of jargon) { const hit = text.match(new RegExp(pattern, 'i')); if (hit) fail(`${name} ${route}: unexplained jargon "${hit[0]}"`); }
    for (const term of gloss.avoid) if (new RegExp(`\\b${escape(term)}\\b`, 'i').test(text)) fail(`${name} ${route}: glossary says to avoid "${term}"`);
    for (const one1 of one.plural) fail(`${name} ${route}: "${one1}"`);
    if (one.titled && one.key && one.crumb.toLowerCase().replace(/[ _]/g, "-") === one.key) fail(`${name} ${route}: the breadcrumb shows the key "${one.key}", not the entry's title`);
  }
  for (const [word, where] of unknown) fail(`${name}: "${word}" is no glossary, ontology or words.js word (${where.length} routes, e.g. ${where[0]})`);
  console.log(name, JSON.stringify({ routes: Object.keys(routes).length, vocabulary: known.size, unknown: unknown.size }));
}

const sizeOf = width => ({ size: [width, width === 390 ? 844 : 1000], mobile: width === 390 });
const fixedRoutes = ['', 'software', 'waiting', 'owed', 'nowhere'];

async function runs(label, repo, wait, sampleRoutes) {
  const { vocab, counts } = await fixedVocabulary();
  for (const [path, n] of Object.entries(counts)) if (path.endsWith('ui/words.js') && n >= 60) fail(`${path} has ${n} entries; the viewer's fixed list stays under 60`);
  const gloss = await glossary(repo);
  const started = await startServer(repo);
  try {
    const scenes = [];
    for (const width of widths) for (const theme of ['light', 'dark'])
      scenes.push({ name: `words-${label}-${width}-${theme}`, route: '', ...sizeOf(width), wait, actions: [{ media: theme }, { eval: SWEEP([...fixedRoutes, ...sampleRoutes]) }] });
    scenes[0].wait = wait * 1.5;
    const results = await browse('words-' + label, scenes, started);
    results.forEach(row => judge(row.name, parse(row.values), vocab, gloss));
  } finally { await started.stop(); }
}

if (mode === 'tool') await runs('tool', await toolCopy('words-qa-tool'), 2500, ['@entries']);
else await runs('ogy', '.', 12000, ['product/review', 'product/capture', 'software/viewing', 'software/cli', '@sample']);
console.log(failures.length ? failures.length + ' failures' : 'all word checks passed');
process.exit(failures.length ? 1 : 0);
