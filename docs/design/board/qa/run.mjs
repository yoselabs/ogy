// Run from the repository: node /path/to/board-qa/run.mjs [--blank]
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { OVERLAP, TEXT, VIEWER_WORDS } from './measures.js';

const here = dirname(fileURLToPath(import.meta.url));
const scratch = dirname(here);
const out = process.env.OUT || here;
const blank = process.argv.includes('--blank');
const scenes = JSON.parse(readFileSync(join(here, 'scenes.json'), 'utf8'));
const forbidden = readFileSync(join(here, 'forbidden.txt'), 'utf8').trim().split('\n');
const results = [];
const lines = [];
mkdirSync(out, { recursive: true });

function line(text) {
  lines.push(text);
  console.log(text);
}

function execute(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { env: { ...process.env, TMPDIR: '/var/tmp' }, ...options });
    let stdout = '', stderr = '';
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    child.on('error', reject);
    child.on('exit', code => resolve({ code, stdout, stderr }));
  });
}

async function startServer(source) {
  // Identical launch and URL extraction to s3-data-check.mjs; its helper is unchanged.
  const server = spawn('uv', ['run', '--frozen', '--no-sync', 'python', scratch + '/s3-data-serve.py', source], { env: { ...process.env, TMPDIR: '/var/tmp' } });
  const url = await new Promise((resolve, reject) => {
    server.stdout.on('data', chunk => { const match = String(chunk).match(/http:\/\/\S+/); if (match) resolve(match[0]); });
    server.on('exit', code => reject(Error('server exited ' + code)));
    server.stderr.on('data', chunk => process.stderr.write(chunk));
    server.on('error', reject);
  }).catch(error => { server.kill(); throw error; });
  return { server, url };
}

function failures(measures) {
  const failed = [];
  for (const name of ['blockOverlaps', 'textRunsCrossedByEdge', 'blocksEnteredByEdge', 'labelsOnBlocks']) {
    const value = measures.overlap.match(new RegExp(name + '=(\\d+)'));
    if (!value) throw Error('Missing overlap count: ' + name);
    if (+value[1] > 0) failed.push(name + '=' + value[1]);
  }
  if (measures.text.min === null || measures.text.min < 11) failed.push('font min=' + measures.text.min);
  if (measures.text.max > 24) failed.push('font max=' + measures.text.max);
  if (measures.text.distinct > 5) failed.push('font sizes=' + measures.text.distinct);
  for (const pattern of forbidden) {
    const match = measures.viewerWords.match(new RegExp(pattern, 'i'));
    if (match) failed.push('forbidden ' + JSON.stringify(match[0]) + ' (' + pattern + ')');
  }
  return failed;
}

async function capture(scene, repo, width, height, theme) {
  let server;
  const name = scene.set + '-' + width + '-' + theme + '-' + scene.name;
  try {
    let url = 'data:text/html,<h1 style="font-size:16px">Heading</h1>';
    if (!blank) {
      const started = await startServer(repo);
      server = started.server;
      // Preserve the one-use exchange query when adding the scene's home hash.
      const home = new URL(scene.url, started.url);
      if (!home.search) home.search = new URL(started.url).search;
      url = home.href;
    }
    const expression = 'JSON.stringify({overlap:(' + OVERLAP + '),text:(' + TEXT
      + '),viewerWords:(' + VIEWER_WORDS + ')})';
    const spec = [{ ...scene, name, url, size: [width, height], mobile: width === 390,
      actions: [{ media: theme }, { key: 'Tab', code: 'Tab', vk: 9 },
        { eval: expression }] }];
    const input = join(out, name + '.json');
    writeFileSync(input, JSON.stringify(spec, null, 2));
    const run = await execute('node', [join(here, 'cdp.mjs'), input],
      { env: { ...process.env, OUT: out, TMPDIR: '/var/tmp' } });
    if (run.code !== 0) throw Error('CDP exit ' + run.code + ': ' + run.stderr);
    const payload = run.stdout.split(' | ').find(part => part.startsWith('{"overlap":'));
    if (!payload) throw Error('No measures: ' + run.stdout + run.stderr);
    const measured = JSON.parse(payload);
    const failed = failures(measured);
    if (run.stdout.includes('ERRORS:')) failed.push(run.stdout.split('ERRORS:')[1].trim());
    results.push({ set: scene.set, width, height, theme, scene: scene.name,
      screenshot: join(out, name + '.png'), ...measured, failures: failed });
    line(name + ': ' + (failed.length ? 'FAIL ' + failed.join('; ') : 'PASS')
      + ' | ' + measured.overlap + ' | type=' + JSON.stringify(measured.text));
  } finally {
    if (server) await new Promise(resolve => { server.once('exit', resolve); server.kill(); });
  }
}

async function main() {
  for (const scene of scenes) {
    let repo = scene.set === 'tool' ? 'tests/fixtures/tool-library' : '.';
    if (scene.set === 'synthetic' && !blank && process.env.SYNTHETIC_REPO) {
      repo = process.env.SYNTHETIC_REPO; // a copy made by synthetic.py earlier; skips minutes of generation
    } else if (scene.set === 'synthetic' && !blank) {
      const made = await execute('uv', ['run', '--frozen', '--no-sync', 'python', join(here, 'synthetic.py')]);
      writeFileSync(join(out, 'synthetic.txt'), made.stdout + made.stderr);
      if (made.code !== 0) throw Error('Synthetic generation refused (exit ' + made.code + '):\n' + made.stderr);
      const generated = JSON.parse(made.stdout.trim());
      repo = generated.repo;
      line('synthetic: ' + generated.entries + ' entries');
    }
    for (const [width, height] of [[1440, 1000], [390, 844]]) {
      for (const theme of ['light', 'dark']) await capture(scene, repo, width, height, theme);
    }
  }
}

let error;
try { await main(); } catch (caught) { error = String(caught); line('STOP ' + error); }
writeFileSync(join(out, 'results.json'), JSON.stringify({ blank, results, error }, null, 2));
writeFileSync(join(out, blank ? 'blank.txt' : 'baseline.txt'), lines.join('\n') + '\n');
process.exitCode = error || results.some(result => result.failures.length) ? 1 : 0;
