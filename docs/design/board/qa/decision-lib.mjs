// Shared helpers of the decision page checks: a temporary KB copy, a server for it, one browser run per scene list.
import { spawn } from 'node:child_process';
import { cpSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const here = dirname(fileURLToPath(import.meta.url));
export const out = process.env.OUT || join(here, 'out');
mkdirSync(out, { recursive: true });

export function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { env: { ...process.env, TMPDIR: '/var/tmp' }, ...options });
    let stdout = '', stderr = '';
    child.stdout.on('data', chunk => { stdout += chunk; });
    child.stderr.on('data', chunk => { stderr += chunk; });
    child.on('error', reject);
    child.on('exit', code => resolve({ code, stdout, stderr }));
  });
}

const ogy = (repo, ...args) => run('uv', ['run', '--frozen', '--no-sync', 'ogy', '--repo', repo, ...args]);

// Two waiting decisions with options and one waiting decision without, on top of the tool library fixture. Written through ogy put.
const SEED = [
  { address: 'product/lending/quantity/pickup-hours', says: 'Hours a member may collect per day.', is: 2, unit: 'hours' },
  { address: 'product/lending/decision/pickup-window', question: 'When can a member collect a reserved tool?',
    context: 'Members asked for evenings; the workshop closes early on Fridays, so a window has to be named before reminders can mention it.',
    options: { short: { label: 'Weekdays 17:00 to 19:00', sets: { 'product/lending/quantity/pickup-hours': { says: 'Hours a member may collect per day.', is: 2, unit: 'hours' } } },
      long: { label: 'Every day 10:00 to 20:00', sets: { 'product/lending/quantity/pickup-hours': { says: 'Hours a member may collect per day.', is: 10, unit: 'hours' } } } },
    proposal: { chose: 'short', why: 'Fewer volunteers needed.' } },
  { address: 'product/lending/decision/closing-day', question: 'Is the workshop closed on public holidays?',
    options: { yes: { label: 'Closed on public holidays' }, no: { label: 'Open on public holidays' } },
    proposal: { chose: 'yes', why: 'Volunteers are off then.' } },
  { address: 'product/lending/decision/visiting-hours', question: 'May members bring a guest to the workshop?',
    options: { alone: { label: 'Members only' }, guest: { label: 'Members and one guest' } },
    proposal: { chose: 'guest', why: 'Guests become members.' } },
];

export async function toolCopy(name = 'dp-qa-tool') {
  const repo = join('/var/tmp', name);
  rmSync(repo, { recursive: true, force: true });
  cpSync('tests/fixtures/tool-library', repo, { recursive: true });
  writeFileSync(join(repo, 'ogy.yml'), 'land: main\n');
  for (const args of [['init', '-q', '-b', 'main'], ['config', 'user.email', 'qa@example.invalid'], ['config', 'user.name', 'qa'], ['add', '-A'], ['commit', '-q', '-m', 'fixture']]) {
    const done = await run('git', ['-C', repo, ...args]);
    if (done.code !== 0) throw Error('git ' + args.join(' ') + ': ' + done.stderr);
  }
  const put = await ogy(repo, 'put', JSON.stringify(SEED));
  if (put.code !== 0) throw Error('put refused: ' + put.stdout + put.stderr);
  return repo;
}

export const show = async (repo, address) => (await ogy(repo, 'show', address)).stdout;

export async function startServer(repo) {
  const server = spawn('uv', ['run', '--frozen', '--no-sync', 'ogy', 'serve', '--repo', repo, '--port', '0'], { env: { ...process.env, TMPDIR: '/var/tmp' } });
  const url = await new Promise((resolve, reject) => {
    for (const stream of [server.stdout, server.stderr]) stream.on('data', chunk => { const match = String(chunk).match(/http:\/\/\S+/); if (match) resolve(match[0]); });
    server.on('exit', code => reject(Error('server exited ' + code)));
  });
  return { server, url, origin: new URL(url).origin, stop: () => new Promise(done => { server.once('exit', done); server.kill(); }) };
}

// One browser, many scenes; the first scene carries the one-use exchange URL, the others reuse its cookie.
export async function browse(name, scenes, started) {
  const spec = scenes.map((scene, index) => ({ ...scene, url: (index === 0 ? started.url : started.origin + '/' + (scene.fresh ? '?fresh=' + index : '')) + '#/' + scene.route }));
  const file = join(out, name + '.json');
  writeFileSync(file, JSON.stringify(spec));
  const result = await run('node', [join(here, 'cdp.mjs'), file], { env: { ...process.env, OUT: out, TMPDIR: '/var/tmp' } });
  if (result.code !== 0) throw Error('cdp ' + name + ': ' + result.stderr);
  return result.stdout.trim().split('\n').map(line => { const parts = line.split(' | '); return { name: parts[0], values: parts.slice(1) }; });
}
