// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry is the X post itself: the house reads POST.json from this
// repository, fetches the post from X, and builds the dossier the judge
// reads (first picture + post text). Nothing this program writes is judged.
//
// So all this program does is carry POST.json from the repository into the
// grader's output directory, byte for byte. It takes no network, no wall
// clock, and no files outside the repository, so its two runs write the
// same bytes.
//
// Local run (mirrors the grader's paths):
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const source = join(BOT_DIR, 'POST.json');
const target = join(OUTPUT_DIR, 'POST.json');

mkdirSync(OUTPUT_DIR, { recursive: true });

let post;
try {
  post = readFileSync(source);
} catch (err) {
  console.error(`cannot read ${source}: ${(err as Error).message}`);
  process.exit(1);
}

// The post file must be a JSON object naming an X post address; fail loudly
// on anything else instead of copying garbage into /output.
let parsed: unknown;
try {
  parsed = JSON.parse(post.toString('utf8'));
} catch (err) {
  console.error(`POST.json is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}
if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
  console.error('POST.json must be a JSON object like {"url": "https://x.com/<handle>/status/<id>"}');
  process.exit(1);
}
if (typeof (parsed as { url?: unknown }).url !== 'string') {
  console.error('POST.json must carry a string "url" field');
  process.exit(1);
}
const url = (parsed as { url: string }).url;
// Light shape check: an X post address, id digits only (the house refuses
// anything else, so fail here with a clear message instead of shipping it).
if (!/^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/[^/]+\/status\/\d+$/.test(url)
    && !/^https:\/\/(www\.|mobile\.)?(x\.com|twitter\.com)\/i\/web\/status\/\d+$/.test(url)) {
  console.error(`POST.json url does not look like an X post address: ${url}`);
  process.exit(1);
}

writeFileSync(target, post);
