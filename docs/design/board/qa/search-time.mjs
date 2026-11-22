// Time of the search index on 5,000 synthetic entries: node docs/design/board/qa/search-time.mjs
import { buildIndex, search } from '../../../../src/ogy/web/static/js/views/search/index.js';
const kinds = ['workflow', 'entity', 'decision', 'rule', 'quantity', 'step', 'state', 'option'];
const nodes = [];
for (let i = 0; i < 5000; i++) {
  const kind = kinds[i % kinds.length];
  const area = 'product/area-' + (i % 30);
  const key = `thing-${i}-${['borrow', 'return', 'late', 'fee', 'loan', 'member'][i % 6]}`;
  nodes.push({ id: `${area}/${kind}/${key}`, address: `${area}/${kind}/${key}`, key, kind, area, parent: null, top: true, title: '', says: `A sentence about ${key} and the workshop number ${i}.` });
}
const byId = new Map(nodes.map(n => [n.id, n]));
let t = performance.now();
const index = buildIndex({ nodes, byId });
console.log('build ms', (performance.now() - t).toFixed(1), index.length);
for (const q of ['t', 'th', 'loan', 'late fee', 'workshop number', 'zzzz', 'decision thing']) {
  t = performance.now();
  for (let i = 0; i < 20; i++) search(index, q);
  console.log(JSON.stringify(q), ((performance.now() - t) / 20).toFixed(2), 'ms per keystroke');
}
