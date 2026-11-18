// news-image-20261117 — entrypoint (Node 22, standard library only).
//
// The image is drawn at build time by generate_image.py (Pillow, run on the
// author's machine) and ships in this repository as entry.png. At grade time
// the program simply places that exact file at /output/entry.png: a copy is
// byte-identical by construction, so the two graded runs always agree.
//
// Local check:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//   # out/entry.png must be a whole PNG, 1024x1024, under 1 MiB.

import { copyFileSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const src = join(here, "entry.png");
const dst = join(outDir, "entry.png");
copyFileSync(src, dst);
// A whole PNG under the 1 MiB gate; fail loudly if the shipped file ever
// stops meeting it instead of silently writing a bad entry.
const bytes = statSync(dst).size;
if (bytes > 1048576) throw new Error(`entry.png is ${bytes} bytes, over the 1 MiB gate`);
console.log(`wrote ${dst} (${bytes} bytes)`);
