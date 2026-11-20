// News-image entry for make.fun's "Sum up 20 November's world news in
// one image" bounty (Node 22, standard library only). The image is the
// entry.png beside this file, drawn by generate_image.py; this program
// copies it to the output directory so the grader can judge it.
//
// Local run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(join(here, 'entry.png'), dest);
console.log(`wrote ${dest} (${statSync(dest).size} bytes)`);
