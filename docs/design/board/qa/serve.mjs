// Starts `ogy serve` for one knowledge base and resolves with the one-use exchange URL it prints. Run from the repository root.
import { spawn } from 'node:child_process';

export async function startBoard(repo) {
  const server = spawn('uv', ['run', '--frozen', '--no-sync', 'ogy', '--repo', repo, 'serve', '--port', '0'],
    { env: { ...process.env, TMPDIR: '/var/tmp' } });
  const url = await new Promise((resolve, reject) => {
    const seen = chunk => { const match = String(chunk).match(/http:\/\/\S+/); if (match) resolve(match[0]); };
    server.stdout.on('data', seen);
    server.stderr.on('data', seen);
    server.on('exit', code => reject(Error('server exited ' + code)));
    server.on('error', reject);
  }).catch(error => { server.kill(); throw error; });
  return { server, url };
}

export function stopBoard(server) {
  return new Promise(resolve => { server.once('exit', resolve); server.kill(); });
}
