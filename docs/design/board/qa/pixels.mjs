// Screenshots of every page the board has, on the tool library, to compare two builds of the stylesheet byte for byte:
//   OUT=/var/tmp/before node docs/design/board/qa/pixels.mjs ; (change the CSS) ; OUT=/var/tmp/after node ... ; cmp the *.png pairs.
// Run from the repository root. A pruned stylesheet must leave every file identical (or the difference must be looked at).
import { browse, startServer, toolCopy } from './decision-lib.mjs';

// The header's load time changes every minute; everything else is deterministic.
const HIDE = `document.querySelectorAll('.hdr-meta').forEach(e => { e.style.visibility = 'hidden'; }); 'hidden'`;
const routes = ['', 'software', 'product/lending', 'software/lending', 'waiting', 'product/lending/decision/fee-rounding', 'nowhere'];
const started = await startServer(await toolCopy('pixels-qa-tool'));
try {
  const scenes = [];
  for (const [width, mobile] of [[1440, false], [390, true]]) for (const theme of ['light', 'dark']) for (const route of routes)
    scenes.push({ name: `px-${width}-${theme}-${route.replaceAll('/', '_') || 'map'}`, route, fresh: true, size: [width, width === 390 ? 844 : 1000], mobile, wait: 1800, actions: [{ media: theme }, { eval: HIDE }] });
  for (const theme of ['light', 'dark'])
    scenes.push({ name: `px-search-${theme}`, route: '', fresh: true, size: [1440, 1000], wait: 1800, actions: [{ media: theme }, { eval: HIDE }, { key: 'k', code: 'KeyK', vk: 75, mod: 2 }, { type: 'loan', wait: 600 }] });
  await browse('pixels', scenes, started);
} finally { await started.stop(); }
