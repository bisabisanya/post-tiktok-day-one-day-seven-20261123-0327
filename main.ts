// Entry for the make.fun TikTok bounty "Day one, day seven"
// (post-tiktok-day-one-day-seven-20261123-0327, program/v1).
//
// The entry is the video itself: it is posted publicly on TikTok and
// VIDEO.json at this repository's root names its full address. Until the
// video is posted, VIDEO.json holds a placeholder address; the person
// posting replaces it with the video's real TikTok URL before submitting.
// This program only copies VIDEO.json to the grader's output directory,
// where the gate reads it. Nothing this program writes about the video is
// scored.
//
// The video (video.mp4, next to this file) is generated deterministically
// by make_video.py (python3 + Pillow + ffmpeg, no network, no wall clock).
// It shows the same tiny agent-built game, "BOT HOP", on day one and on
// day seven: same map, same start, same fixed camera, visibly more going
// on the second time.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'VIDEO.json'), join(OUTPUT_DIR, 'VIDEO.json'));
} catch (err) {
  // A missing or unreadable VIDEO.json is fatal: without it the gate has
  // no video to read, so fail loudly instead of writing an empty output.
  console.error(`VIDEO.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
// Success prints nothing: the gate reads VIDEO.json from the output dir.
