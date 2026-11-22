// A synthetic knowledge base for the QA gate: the tool library copied into areas lending-02 ... lending-55.
// Prints {"repo": <folder>, "files": <count>} as JSON. Run from the repository root. Files are copied with their addresses
// rewritten (a test fixture only; nothing here writes into the repository's own knowledge base).
import { cpSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';

const target = mkdtempSync('/var/tmp/board-qa-synthetic-');
cpSync('tests/fixtures/tool-library', target, { recursive: true });
writeFileSync(join(target, 'ogy.yml'), 'land: main\n');
const kb = join(target, 'docs/kb');
const roots = ['product/lending', 'software/lending', 'built/product/lending', 'built/software/lending'];

function* files(folder) {
  for (const name of readdirSync(folder)) {
    const path = join(folder, name);
    if (statSync(path).isDirectory()) yield* files(path);
    else if (name.endsWith('.yml')) yield path;
  }
}

let count = 0;
for (let number = 2; number < 56; number++) {
  const name = 'lending-' + String(number).padStart(2, '0');
  for (const root of roots) {
    const base = join(kb, root);
    try { statSync(base); } catch { continue; }
    for (const file of files(base)) {
      const copy = file.replace('/lending/', '/' + name + '/');
      mkdirSync(dirname(copy), { recursive: true });
      writeFileSync(copy, readFileSync(file, 'utf8').replace(/\/lending(?=[/"' \n:])/g, '/' + name));
      count++;
    }
  }
}
console.log(JSON.stringify({ repo: target, files: count }));
