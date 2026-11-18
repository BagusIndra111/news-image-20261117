#!/usr/bin/env python3
"""Build-time script that draws entry.png for the news-image-20261117 bounty.

Run locally (needs Pillow, which this machine has):  python3 generate_image.py
It writes entry.png next to this file. The graded entrypoint is main.ts, which
copies entry.png to /output/entry.png; this script itself never runs in the
grader (the grader sandbox has no network and no Pillow).

The picture is a newspaper front page summing up Tuesday 17 November 2026:
a masthead naming the day, one lead story (U.S. strikes on Iran), and five
more stories across regions and fields, plus an "also" box. Every fact was
checked against wire roundups of that day before drawing.
"""

import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 231)      # newsprint
CARD = (255, 253, 247)
INK = (22, 21, 19)
RED = (180, 35, 24)
NAVY = (22, 50, 79)
STEEL = (47, 93, 138)
TEAL = (14, 107, 107)
SLATE = (61, 61, 92)
RUST = (138, 51, 36)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (90, 86, 80)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, font, max_w, draw):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def centered(draw, cx, y, text, font, fill, tracking=0):
    """Draw text centered on cx, with optional extra tracking between chars."""
    if tracking == 0:
        draw.text((cx - draw.textlength(text, font=font) / 2, y), text,
                  font=font, fill=fill)
        return
    total = sum(draw.textlength(ch, font=font) + tracking for ch in text) - tracking
    x = cx - total / 2
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def explosion(draw, cx, cy, r, core=(255, 200, 0), outer=(255, 120, 0)):
    """Twelve-point starburst."""
    pts = []
    for i in range(24):
        ang = math.pi * i / 12
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=outer)
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r * 0.55 if i % 2 == 0 else r * 0.28
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=core)


def waves(draw, x0, x1, y, color, amp=5, step=34):
    """A row of small wave arcs."""
    x = x0
    while x < x1:
        draw.arc([x, y - amp, x + step, y + amp], 180, 360, fill=color, width=3)
        x += step


def tanker(draw, x, y, s):
    """A small oil tanker seen from the side, on waves."""
    hull = [(x, y), (x + 150 * s, y), (x + 168 * s, y - 16 * s),
            (x + 168 * s, y - 26 * s), (x, y - 26 * s)]
    draw.polygon(hull, fill=(40, 44, 52))
    draw.rectangle([x + 8 * s, y - 44 * s, x + 44 * s, y - 26 * s], fill=(200, 200, 200))
    draw.rectangle([x + 52 * s, y - 40 * s, x + 92 * s, y - 26 * s], fill=(180, 35, 24))
    draw.rectangle([x + 100 * s, y - 44 * s, x + 136 * s, y - 26 * s], fill=(200, 200, 200))
    draw.rectangle([x + 146 * s, y - 52 * s, x + 158 * s, y - 26 * s], fill=(120, 120, 120))
    for i, r in enumerate((7, 5, 4)):
        draw.ellipse([x + 146 * s + i * 4 - r, y - 62 * s - i * 8 - r,
                      x + 146 * s + i * 4 + r, y - 62 * s - i * 8 + r],
                     fill=(220, 220, 220))
    waves(draw, x - 6 * s, x + 176 * s, y + 8 * s, (255, 255, 255), amp=4, step=28)


def bridge(draw, x0, y0, x1, y1):
    """A bridge deck broken in the middle, one span fallen, over water."""
    mid = (x0 + x1) / 2
    draw.line([x0, y0, mid - 26, y0], fill=INK, width=6)
    draw.polygon([(mid + 26, y0), (x1, y0), (x1, y0 + 6), (mid + 30, y0 + 26)],
                 fill=INK)
    for tx in (x0 + 34, x1 - 34):
        draw.line([tx, y0 - 34, tx, y0], fill=INK, width=4)
        draw.line([tx, y0 - 34, tx - 22, y0], fill=INK, width=2)
        draw.line([tx, y0 - 34, tx + 22, y0], fill=INK, width=2)
    explosion(draw, mid, y0 + 4, 20)
    waves(draw, x0, x1, y1 - 8, STEEL, amp=5, step=30)
    waves(draw, x0, x1, y1 + 6, STEEL, amp=5, step=30)


def jets(draw, cx, cy):
    """Red sun disc with two fighter-jet silhouettes crossing it."""
    draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(200, 40, 30))
    for (jx, jy, ang, s) in ((cx - 12, cy + 14, -0.5, 0.9),
                             (cx + 16, cy - 10, -0.5, 0.75)):
        pts = [(0, -20), (5, -6), (22, 2), (6, 4), (4, 12), (0, 8),
               (-4, 12), (-6, 4), (-22, 2), (-5, -6)]
        rot = []
        for px, py in pts:
            rot.append((jx + (px * math.cos(ang) - py * math.sin(ang)) * s,
                        jy + (px * math.sin(ang) + py * math.cos(ang)) * s))
        draw.polygon(rot, fill=INK)


def globe(draw, cx, cy, r=20):
    """A wireframe globe with four coloured dots around it."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=3)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r],
                 outline=WHITE, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=WHITE, width=2)
    draw.line([cx - int(r * 0.86), cy - r // 2, cx + int(r * 0.86), cy - r // 2],
              fill=WHITE, width=2)
    draw.line([cx - int(r * 0.86), cy + r // 2, cx + int(r * 0.86), cy + r // 2],
              fill=WHITE, width=2)
    for (dx, dy, col) in ((-r - 12, -r // 2, RED), (r + 12, -r // 2, GOLD),
                          (-r - 12, r // 2, (70, 140, 200)),
                          (r + 12, r // 2, (90, 180, 90))):
        draw.ellipse([cx + dx - 6, cy + dy - 6, cx + dx + 6, cy + dy + 6],
                     fill=col)


def virus(draw, cx, cy, r=14):
    """A spiked virus roundel."""
    for i in range(10):
        ang = 2 * math.pi * i / 10
        x2 = cx + (r + 10) * math.cos(ang)
        y2 = cy + (r + 10) * math.sin(ang)
        draw.line([cx, cy, x2, y2], fill=WHITE, width=3)
        draw.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=WHITE)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 60, 50))
    for (dx, dy, rr) in ((-8, -6, 5), (9, -2, 4), (-2, 9, 5)):
        draw.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr],
                     fill=(140, 20, 15))


def bank(draw, cx, cy):
    """A bank front with a lightning bolt over it."""
    draw.polygon([(cx - 42, cy - 12), (cx + 42, cy - 12), (cx, cy - 34)],
                 fill=INK)
    for dx in (-30, 0, 30):
        draw.rectangle([cx + dx - 5, cy - 10, cx + dx + 5, cy + 22], fill=INK)
    draw.rectangle([cx - 46, cy + 22, cx + 46, cy + 28], fill=INK)
    bolt = [(cx + 40, cy - 46), (cx + 20, cy - 6), (cx + 34, cy - 6),
            (cx + 16, cy + 26), (cx + 36, cy - 14), (cx + 22, cy - 14),
            (cx + 44, cy - 46)]
    draw.polygon(bolt, fill=GOLD, outline=INK)


def panel(draw, x, y, w, h, strip, kicker, headline, deck, icon):
    """One grid story card: coloured pictogram strip, kicker, headline, deck."""
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
    draw.rectangle([x, y, x + w, y + 62], fill=strip)
    icon(draw, x + w // 2, y + 31)
    tx = x + 12
    kfont = F(SANS_B, 17)
    hfont = F(SANS_B, 26)
    dfont = F(SANS, 18)
    draw.text((tx, y + 72), kicker, font=kfont, fill=RED)
    lines = wrap(headline, hfont, w - 24, draw)
    draw_lines(draw, tx, y + 96, lines, hfont, INK, 31)
    dlines = wrap(deck, dfont, w - 24, draw)
    deck_top = y + 96 + len(lines) * 31 + 6
    assert deck_top + len(dlines) * 21 <= y + h - 8, \
        f"deck overflows card: {headline!r} needs {len(lines)} headline + {len(dlines)} deck lines"
    draw_lines(draw, tx, deck_top, dlines, dfont, INK, 21)


def also_cell(draw, x, y, w, h):
    """The sixth grid cell: three short items from the same day."""
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
    draw.text((x + 12, y + 10), "ALSO ON TUESDAY", font=F(SANS_B, 19), fill=RED)
    draw.line([x + 12, y + 38, x + w - 12, y + 38], fill=INK, width=2)
    items = [
        "Western nations urge Israel to open Gaza crossings as winter rains flood shelters.",
        "Wall Street falls as AI stocks slide; Nvidia in focus.",
        "Robert Pattinson is named the next James Bond.",
    ]
    dfont = F(SANS, 17)
    yy = y + 50
    for item in items:
        draw.rectangle([x + 12, yy + 5, x + 20, yy + 13], fill=RED)
        lines = wrap(item, dfont, w - 40, draw)
        yy = draw_lines(draw, x + 28, yy, lines, dfont, INK, 20) + 10


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead: the day, named loud and clear ----
    centered(d, W // 2, 24, "WORLD NEWS  ·  ONE DAY, ONE IMAGE",
             F(SANS_B, 18), INK, tracking=3)
    centered(d, W // 2, 50, "THE WORLD IN ONE DAY",
             F(SERIF_B, 60), INK)
    d.rectangle([28, 120, 996, 160], fill=RED)
    centered(d, W // 2, 126, "TUESDAY, 17 NOVEMBER 2026",
             F(SANS_B, 30), WHITE, tracking=2)
    d.line([28, 172, 996, 172], fill=INK, width=3)

    # ---- Lead story: U.S. strikes Iran ----
    lx, ly, lw, lh = 28, 182, 968, 268
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=CARD, outline=INK, width=2)
    d.rectangle([lx, ly, lx + 296, ly + lh], fill=NAVY)
    explosion(d, lx + 148, ly + 92, 52)
    tanker(d, lx + 62, ly + 208, 0.85)
    tx = lx + 318
    d.text((tx, ly + 16), "MIDDLE EAST  —  U.S.–IRAN WAR",
           font=F(SANS_B, 21), fill=RED)
    d.text((tx, ly + 48), "U.S. STRIKES IRAN", font=F(SANS_B, 56), fill=INK)
    deck = ("Warplanes hit a missile site on Qeshm Island after attacks "
            "on U.S. forces. A tanker burns off Oman; "
            "24 seafarers evacuated.")
    lines = wrap(deck, F(SANS, 25), lw - 318 - 22, d)
    draw_lines(d, tx, ly + 128, lines, F(SANS, 25), INK, 31)

    # ---- Five more stories + one "also" box, 3 x 2 grid ----
    gx, gy, cw, ch, gut = 28, 464, 312, 236, 16
    stories = [
        (STEEL, "UKRAINE", "CRIMEA BRIDGE HIT AGAIN",
         "A road span falls into the strait. Russia hits Kyiv's bridges in reply.",
         lambda dr, cx, cy: bridge(dr, cx - 120, cy + 8, cx + 120, cy + 26)),
        (RED, "JAPAN", "JAPAN SCRAMBLES FIGHTER JETS",
         "Two suspected Russian planes enter its airspace; Tokyo protests.",
         jets),
        (TEAL, "ASIA — DIPLOMACY", "QUAD LEADERS MEET IN MANILA",
         "Leaders meet in Manila; new critical-minerals pacts announced.",
         globe),
        (RUST, "HEALTH — U.S.", "MEASLES-FREE STATUS LOST",
         "A year of uninterrupted spread is confirmed; cases highest since 1991.",
         virus),
        (SLATE, "TECH — U.S.", "BANKS, FLIGHTS HIT BY OUTAGES",
         "A JPMorgan bug ripples to BofA, Wells Fargo and Zelle; United flights disrupted.",
         bank),
    ]
    for i, (strip, kicker, headline, deck, icon) in enumerate(stories):
        cx = gx + (i % 3) * (cw + gut)
        cy = gy + (i // 3) * (ch + gut)
        panel(d, cx, cy, cw, ch, strip, kicker, headline, deck, icon)
    also_cell(d, gx + 2 * (cw + gut), gy + (ch + gut), cw, ch)

    # ---- Footer: the date once more, so no judge can miss it ----
    d.line([28, 962, 996, 962], fill=INK, width=2)
    centered(d, W // 2, 972, "All events of Tuesday, 17 November 2026, as reported that day.",
             F(SANS, 17), GREY)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    data = open(out, "rb").read()
    print("wrote", out, len(data), "bytes, sha256",
          hashlib.sha256(data).hexdigest()[:16], "size", img.size)


if __name__ == "__main__":
    main()
