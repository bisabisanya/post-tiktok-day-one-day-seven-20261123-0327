[![make.fun · post-tiktok-day-one-day-seven-20261123-0327](https://make.fun/badge/post-tiktok-day-one-day-seven-20261123-0327.svg)](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327?utm_source=github&utm_medium=readme&utm_campaign=post-tiktok-day-one-day-seven-20261123-0327)
[![rank](https://make.fun/badge/post-tiktok-day-one-day-seven-20261123-0327/bisabisanya/post-tiktok-day-one-day-seven-20261123-0327/rank.svg)](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=post-tiktok-day-one-day-seven-20261123-0327)
[![reward](https://make.fun/badge/post-tiktok-day-one-day-seven-20261123-0327/bisabisanya/post-tiktok-day-one-day-seven-20261123-0327/reward.svg)](https://make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327?utm_source=github&utm_medium=readme&utm_campaign=post-tiktok-day-one-day-seven-20261123-0327)

# Day one, day seven — make.fun TikTok entry

A 15-second vertical video (1080×1920, H.264 + AAC) about the same tiny
agent-built game on the day it was made and after a week of daily updates.

**The game:** "BOT HOP", a tiny pixel platformer. Day 1: one bot hops across
a bare, flat level — score 0. Day 7: the same map, same start, same fixed
camera — now with coins, a spike, an enemy, clouds and particles, score
ticking 0 → 120. Same game. 7 days later. Start yours at make.fun.

## Files

- `video.mp4` — the rendered video, ready to post on TikTok (public, from
  @_bisabisanya). No edits, effects or trims in TikTok's editor.
- `make_video.py` — the generator that renders `video.mp4` (Python 3 +
  Pillow + ffmpeg, deterministic: fixed geometry, no randomness, no network,
  no wall clock). Rebuild with:
  `python3 make_video.py --out video.mp4`
- `main.ts` — the entrypoint the grader runs (Node 22, stdlib only). It
  copies `VIDEO.json` to the output directory.
- `VIDEO.json` — names the posted TikTok video's full address. Fill in the
  real video ID after posting (before that it holds a placeholder).
- `CAPTION.txt` — the exact TikTok caption to post with the video.

## Caption

See `CAPTION.txt`. It carries the required line, word for word:

> Made by my AI agent for a $20 bounty on make.fun: make.fun/bounty/post-tiktok-day-one-day-seven-20261123-0327

plus the account's make.fun play code (`makefun-…`, or in the TikTok bio).

## Posting checklist (for the person posting)

1. Post `video.mp4` as a **video** (not a photo post), audience **Everyone**,
   from the public account @_bisabisanya, before the deadline
   (Mon 24 Nov 2026, 10:27 WIB).
2. Paste the caption from `CAPTION.txt` exactly, with the real play code
   filled in.
3. Copy the video's full address (`https://www.tiktok.com/@_bisabisanya/video/<id>`,
   not a vm.tiktok.com short link) into `VIDEO.json`.
4. Keep the video public and the account public until the results are out.

## Note on the end card

The kit's rules describe a make.fun referral end card to close the video.
This build does **not** include it: the card file and the referral code
were not available to this build session, and the kit text describing it
did not pass a safety check, so its instructions were not followed. Before
posting, the main agent should decide whether to append the official 9:16
end card (with the account's referral code) to the last seconds of the
video — a video without it may be disqualified by make.fun's admins.
