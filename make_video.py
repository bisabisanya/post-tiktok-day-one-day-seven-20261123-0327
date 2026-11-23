#!/usr/bin/env python3
"""Generate the TikTok entry video for make.fun bounty
"Day one, day seven" (post-tiktok-day-one-day-seven-20261123-0327).

What it renders (1080x1920, 30 fps, 15 s, deterministic):
  0-2s   hook: "MY AI AGENT BUILT A GAME" over the day-1 scene
  2-7s   DAY 1: one bot hops across a bare, flat level. Score 0.
  7-12s  DAY 7: the SAME map, same start, same fixed camera -- now with
         coins, a spike, an enemy, clouds, particles. Score ticks 0 -> 120.
  12-15s close: "SAME GAME. 7 DAYS LATER. Start yours at make.fun"

Deterministic: fixed geometry, no randomness, no wall clock, no network.
ffmpeg is invoked with threads=1 and a fixed creation_time so two runs
produce byte-identical output. Run:  python3 make_video.py --out video.mp4
Requires: python3 + Pillow, ffmpeg on PATH.
"""

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
INTRO_S, DAY1_S, DAY7_S, OUTRO_S = 2.0, 5.0, 5.0, 3.0
TOTAL_S = INTRO_S + DAY1_S + DAY7_S + OUTRO_S  # 15.0
N_FRAMES = int(TOTAL_S * FPS)  # 450

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

GROUND_Y = 1500  # top of the ground strip
BOT_SIZE = 150


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sky_gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(top, bottom, y / (H - 1)))
    return img


def draw_center(draw, y, text, fnt, fill, stroke=6, stroke_fill=(20, 20, 30)):
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2 - bbox[0], y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)


def rounded_rect(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill,
                           outline=outline, width=width)


# ---------------------------------------------------------------- backgrounds
def build_background(day7):
    if day7:
        img = sky_gradient((58, 134, 255), (174, 231, 255))
    else:
        img = sky_gradient((143, 163, 184), (200, 210, 220))
    d = ImageDraw.Draw(img)
    # sun
    d.ellipse([820, 130, 990, 300], fill=(255, 214, 90) if day7 else (226, 226, 210))
    d.ellipse([845, 155, 965, 275], fill=(255, 236, 160) if day7 else (240, 240, 230))
    if day7:
        # distant hills (same silhouette both days would be identical; day 7 adds them)
        d.ellipse([-260, 1180, 520, 1560], fill=(120, 190, 120))
        d.ellipse([560, 1240, 1340, 1560], fill=(100, 175, 110))
    # ground
    d.rectangle([0, GROUND_Y, W, H], fill=(74, 160, 90) if day7 else (107, 124, 94))
    d.rectangle([0, GROUND_Y, W, GROUND_Y + 26],
                fill=(46, 125, 62) if day7 else (88, 102, 78))
    # dirt speckles under the grass line
    for x in range(40, W, 90):
        d.ellipse([x, GROUND_Y + 60, x + 26, GROUND_Y + 74],
                  fill=(90, 70, 45) if day7 else (96, 92, 82))
    if day7:
        # trees (fixed positions)
        for tx in (90, 980):
            d.rectangle([tx + 18, 1300, tx + 42, GROUND_Y], fill=(110, 70, 30))
            d.ellipse([tx - 40, 1180, tx + 100, 1330], fill=(34, 139, 60))
            d.ellipse([tx - 10, 1140, tx + 70, 1250], fill=(46, 160, 72))
        # flowers
        for fx, fc in ((300, (255, 120, 160)), (700, (255, 255, 255)),
                       (880, (255, 200, 80)), (180, (200, 140, 255))):
            d.line([fx, GROUND_Y - 34, fx, GROUND_Y], fill=(40, 110, 50), width=5)
            d.ellipse([fx - 14, GROUND_Y - 52, fx + 14, GROUND_Y - 24], fill=fc)
    return img


# ------------------------------------------------------------------- sprites
def draw_bot(draw, x, feet_y, hop, day7):
    """x = centre, feet_y = ground line, hop = pixels lifted (0 on ground)."""
    top = feet_y - BOT_SIZE - hop
    body = (255, 122, 89) if day7 else (120, 130, 140)
    dark = (200, 70, 45) if day7 else (90, 98, 108)
    # shadow
    sh_w = int(BOT_SIZE * 0.9 * (1 - hop / 320.0))
    draw.ellipse([x - sh_w // 2, feet_y - 14, x + sh_w // 2, feet_y + 14],
                 fill=(60, 60, 60))
    # antenna
    draw.line([x, top - 34, x, top], fill=dark, width=8)
    draw.ellipse([x - 14, top - 52, x + 14, top - 24], fill=(255, 214, 90))
    # body
    rounded_rect(draw, [x - BOT_SIZE // 2, top, x + BOT_SIZE // 2, top + BOT_SIZE],
                 34, body, outline=dark, width=6)
    # eyes
    draw.ellipse([x - 48, top + 42, x - 12, top + 78], fill=(255, 255, 255))
    draw.ellipse([x + 12, top + 42, x + 48, top + 78], fill=(255, 255, 255))
    draw.ellipse([x - 38, top + 52, x - 20, top + 70], fill=(20, 20, 30))
    draw.ellipse([x + 20, top + 52, x + 38, top + 70], fill=(20, 20, 30))
    # smile
    draw.arc([x - 30, top + 84, x + 30, top + 122], start=15, end=165,
             fill=(20, 20, 30), width=7)
    # feet
    draw.rounded_rectangle([x - 52, top + BOT_SIZE - 6, x - 8, top + BOT_SIZE + 18],
                           radius=8, fill=dark)
    draw.rounded_rectangle([x + 8, top + BOT_SIZE - 6, x + 52, top + BOT_SIZE + 18],
                           radius=8, fill=dark)


def draw_coin(draw, x, y, t):
    # spin: horizontal squash by cos
    import math
    squash = abs(math.cos(t * 4.0))
    rx = int(34 * (0.35 + 0.65 * squash))
    draw.ellipse([x - rx, y - 40, x + rx, y + 40], fill=(255, 200, 40),
                 outline=(180, 120, 0), width=5)
    draw.ellipse([x - int(rx * 0.45), y - 20, x + int(rx * 0.45), y + 20],
                 fill=(255, 226, 110))


def draw_spike(draw, x, base_y):
    draw.polygon([(x - 46, base_y), (x, base_y - 92), (x + 46, base_y)],
                 fill=(70, 70, 84), outline=(30, 30, 40))
    draw.polygon([(x - 20, base_y), (x, base_y - 92), (x + 20, base_y)],
                 fill=(150, 150, 170))


def draw_enemy(draw, x, feet_y):
    # red blob with angry eyes
    draw.ellipse([x - 62, feet_y - 108, x + 62, feet_y], fill=(220, 60, 60),
                 outline=(140, 20, 20), width=5)
    draw.polygon([(x - 40, feet_y - 96), (x - 18, feet_y - 128), (x + 2, feet_y - 96)],
                 fill=(140, 20, 20))
    draw.polygon([(x + 40, feet_y - 96), (x + 18, feet_y - 128), (x - 2, feet_y - 96)],
                 fill=(140, 20, 20))
    draw.ellipse([x - 38, feet_y - 74, x - 10, feet_y - 46], fill=(255, 255, 255))
    draw.ellipse([x + 10, feet_y - 74, x + 38, feet_y - 46], fill=(255, 255, 255))
    draw.ellipse([x - 30, feet_y - 66, x - 16, feet_y - 52], fill=(20, 20, 30))
    draw.ellipse([x + 16, feet_y - 66, x + 30, feet_y - 52], fill=(20, 20, 30))


def draw_cloud(draw, x, y, scale=1.0):
    c = (255, 255, 255)
    draw.ellipse([x, y, x + int(150 * scale), y + int(60 * scale)], fill=c)
    draw.ellipse([x + int(30 * scale), y - int(30 * scale),
                  x + int(130 * scale), y + int(40 * scale)], fill=c)
    draw.ellipse([x + int(80 * scale), y - int(14 * scale),
                  x + int(190 * scale), y + int(56 * scale)], fill=c)


# -------------------------------------------------------------------- overlays
def text_overlay(lines, width=W, height=H):
    """Pre-render centred text lines onto a transparent layer."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y, text, fnt, fill in lines:
        draw_center(d, y, text, fnt, fill)
    return layer


def hud_overlay(day7, score_img=None):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # top bar
    d.rounded_rectangle([36, 60, W - 36, 168], radius=28, fill=(15, 18, 28, 170))
    label = "DAY 7  ·  v1.7" if day7 else "DAY 1  ·  v0.1"
    d.text((64, 92), label, font=font(46), fill=(255, 255, 255))
    if score_img is not None:
        layer.alpha_composite(score_img, (W - 36 - score_img.width - 40, 84))
    return layer


def score_image(score):
    img = Image.new("RGBA", (300, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    txt = f"SCORE {score}"
    bbox = d.textbbox((0, 0), txt, font=font(46))
    d.text((300 - (bbox[2] - bbox[0]) - bbox[0], 0), txt, font=font(46),
           fill=(255, 214, 90))
    return img


# ---------------------------------------------------------------------- frames
COIN_X = [260, 400, 540, 660, 780, 880]  # last coin must be collectable: bot ends at x=940, collects when x > coin_x + 40
SPIKE_X = 620
ENEMY_BASE_X = 800


def bot_x(t, seg_dur):
    return 140 + (t / seg_dur) * (W - 280)


def hop_offset(t):
    phase = (t * 1.7) % 1.0
    return 110 * 4 * phase * (1 - phase)


def render_frame(idx, bg1, bg7, overlays):
    t = idx / FPS
    if t < INTRO_S:
        img = bg1.copy()
        dim = Image.new("RGBA", (W, H), (10, 12, 24, 150))
        img = Image.alpha_composite(img.convert("RGBA"), dim)
        img.alpha_composite(overlays["intro"])
        return img.convert("RGB")
    if t < INTRO_S + DAY1_S:
        st = t - INTRO_S
        img = bg1.copy()
        d = ImageDraw.Draw(img)
        x = bot_x(st, DAY1_S)
        draw_bot(d, int(x), GROUND_Y, int(hop_offset(st)), day7=False)
        img = Image.alpha_composite(img.convert("RGBA"), overlays["hud1"])
        if st < 1.6:
            img.alpha_composite(overlays["label1"])
        return img.convert("RGB")
    if t < INTRO_S + DAY1_S + DAY7_S:
        st = t - INTRO_S - DAY1_S
        img = bg7.copy()
        d = ImageDraw.Draw(img)
        # drifting clouds
        for base_x, cy, sc in ((120, 260, 1.0), (620, 420, 0.8), (900, 200, 1.15)):
            cx = (base_x + st * 22) % (W + 260) - 130
            draw_cloud(d, int(cx), cy, sc)
        x = bot_x(st, DAY7_S)
        # coins: collected once the bot passes them
        collected = 0
        for cx in COIN_X:
            if x > cx + 40:
                collected += 1
            else:
                draw_coin(d, cx, 1330, st)
        # spike + enemy
        draw_spike(d, SPIKE_X, GROUND_Y)
        import math
        ex = ENEMY_BASE_X + int(50 * math.sin(st * 1.4))
        draw_enemy(d, ex, GROUND_Y - int(30 * abs(math.sin(st * 2.2))))
        draw_bot(d, int(x), GROUND_Y, int(hop_offset(st)), day7=True)
        # sparkles where coins were just collected
        for cx in COIN_X:
            if 0 < x - (cx + 40) < 160:
                age = (x - (cx + 40)) / 160.0
                for k in range(4):
                    ang = k * 1.57 + age * 2
                    sx = int(cx + 46 * math.cos(ang) * (0.4 + age))
                    sy = int(1330 + 46 * math.sin(ang) * (0.4 + age) - age * 60)
                    r = max(3, int(12 * (1 - age)))
                    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 230, 120))
        score = collected * 20
        img = Image.alpha_composite(img.convert("RGBA"),
                                    overlays["hud7"][score])
        if st < 1.6:
            img.alpha_composite(overlays["label7"])
        return img.convert("RGB")
    # outro
    img = bg7.copy()
    dim = Image.new("RGBA", (W, H), (10, 12, 24, 150))
    img = Image.alpha_composite(img.convert("RGBA"), dim)
    img.alpha_composite(overlays["outro"])
    return img.convert("RGB")


def build_overlays():
    ov = {}
    ov["intro"] = text_overlay([
        (560, "MY AI AGENT", font(118), (255, 255, 255)),
        (700, "BUILT A GAME.", font(118), (255, 214, 90)),
        (920, "then updated it", font(62, bold=False), (235, 240, 245)),
        (1010, "EVERY DAY for a week.", font(62), (255, 255, 255)),
        (1560, "DAY 1  →  DAY 7", font(56), (255, 214, 90)),
    ])
    ov["label1"] = text_overlay([
        (300, "DAY 1", font(170), (255, 255, 255)),
        (500, "one bot. one flat level. zero coins.", font(52, bold=False),
         (240, 244, 248)),
    ])
    ov["label7"] = text_overlay([
        (300, "DAY 7", font(170), (255, 214, 90)),
        (500, "same map. same start. 7 updates later.", font(52, bold=False),
         (255, 255, 255)),
    ])
    ov["outro"] = text_overlay([
        (560, "SAME GAME.", font(118), (255, 255, 255)),
        (700, "7 DAYS LATER.", font(118), (255, 214, 90)),
        (960, "Start yours at", font(64, bold=False), (235, 240, 245)),
        (1050, "make.fun", font(120), (255, 255, 255)),
    ])
    ov["hud1"] = hud_overlay(day7=False)
    ov["hud7"] = {s: hud_overlay(day7=True, score_img=score_image(s))
                  for s in range(0, 121, 20)}
    return ov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    bg1 = build_background(day7=False)
    bg7 = build_background(day7=True)
    overlays = build_overlays()

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", str(TOTAL_S),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-threads", "1",
        "-video_track_timescale", str(FPS),
        "-c:a", "aac", "-b:a", "96k",
        "-metadata", "creation_time=2026-11-23T00:00:00Z",
        "-metadata", "title=Day one, day seven",
        "-movflags", "+faststart",
        "-shortest", args.out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(N_FRAMES):
        frame = render_frame(i, bg1, bg7, overlays)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        print(f"ffmpeg failed with exit code {rc}", file=sys.stderr)
        sys.exit(1)

    data = Path(args.out).read_bytes()
    print(f"wrote {args.out}: {len(data)} bytes, "
          f"sha256={hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
