#!/usr/bin/env python3
"""Render the 17 November 2026 front page (entry.png), 1024x1024.

Pillow renderer, build time only. Every fact comes from NEWS_FACTS.md
in the work dir (reporting dated Tuesday 17 November 2026).
Deterministic: no randomness, no timestamps, fixed fonts.
"""
import hashlib
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (20, 20, 20)
GOLD = (216, 201, 138)
FONT_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def centre(draw, x, y, w, text, fnt, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text((x + (w - tw) / 2, y), text, font=fnt, fill=fill)


def draw_bridge(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(220, 233, 242))
    d.ellipse([x1 - 52, y0 + 8, x1 - 22, y0 + 38], fill=(240, 200, 90))
    # water
    d.rectangle([x0, y1 - 28, x1, y1], fill=(127, 168, 201))
    for wy in (y1 - 20, y1 - 12, y1 - 5):
        for wx in range(x0 + 8, x1 - 20, 34):
            d.arc([wx, wy, wx + 26, wy + 10], 0, 180, fill=(255, 255, 255), width=2)
    # towers
    mid = (y0 + y1) // 2 - 6
    for tx in (x0 + 62, x1 - 78):
        d.rectangle([tx, mid - 52, tx + 14, mid + 4], fill=(60, 60, 60))
    # deck: left span intact, right span collapsed into the water
    d.rectangle([x0 + 8, mid, x0 + 168, mid + 7], fill=(40, 40, 40))
    d.polygon([(x0 + 168, mid), (x0 + 168, mid + 7), (x1 - 30, y1 - 26),
               (x1 - 38, y1 - 30)], fill=(40, 40, 40))
    # suspension cables on the intact span
    d.line([(x0 + 69, mid - 52), (x0 + 120, mid)], fill=(90, 90, 90), width=2)
    d.line([(x0 + 69, mid - 52), (x0 + 168, mid)], fill=(90, 90, 90), width=2)


def draw_jet(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(220, 233, 242))
    # rising-sun disc
    d.ellipse([x0 + 26, y0 + 18, x0 + 86, y0 + 78], fill=(176, 58, 46))
    # contrails
    cy0 = (y0 + y1) // 2 - 6
    for cy in (cy0 + 4, cy0 + 16):
        d.line([(x0 + 10, cy), (x0 + 190, cy - 8)], fill=(255, 255, 255), width=3)
    # jet silhouette (delta shape, flying right)
    cx, cy = x0 + 205, cy0
    d.polygon([(cx - 70, cy + 6), (cx + 55, cy - 8), (cx + 78, cy),
               (cx + 55, cy + 8), (cx - 70, cy + 14)], fill=(30, 30, 30))
    d.polygon([(cx - 30, cy - 2), (cx - 8, cy - 30), (cx + 6, cy - 2)],
              fill=(30, 30, 30))
    d.polygon([(cx - 30, cy + 8), (cx - 12, cy + 28), (cx + 2, cy + 8)],
              fill=(30, 30, 30))
    d.polygon([(cx - 70, cy - 2), (cx - 52, cy - 16), (cx - 44, cy - 2)],
              fill=(30, 30, 30))


def draw_drone(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(232, 224, 200))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(180, 164, 120))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 8
    # arms and rotors
    for dx, dy in ((-52, -26), (52, -26), (-52, 26), (52, 26)):
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=(60, 60, 60), width=4)
        d.ellipse([cx + dx - 22, cy + dy - 6, cx + dx + 22, cy + dy + 6],
                  outline=(60, 60, 60), width=3)
    # body + camera
    d.rounded_rectangle([cx - 34, cy - 16, cx + 34, cy + 16], radius=8,
                        fill=(40, 40, 40))
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(220, 60, 50))
    # ground marker cross
    gx, gy = cx, y1 - 34
    d.line([(gx - 10, gy), (gx + 10, gy)], fill=(176, 58, 46), width=3)
    d.line([(gx, gy - 10), (gx, gy + 10)], fill=(176, 58, 46), width=3)


def draw_tanker(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(242, 227, 213))
    d.ellipse([x1 - 56, y0 + 10, x1 - 26, y0 + 40], fill=(240, 200, 90))
    d.rectangle([x0, y1 - 34, x1, y1], fill=(127, 168, 201))
    for wy in (y1 - 24, y1 - 12):
        for wx in range(x0 + 8, x1 - 20, 34):
            d.arc([wx, wy, wx + 26, wy + 10], 0, 180, fill=(255, 255, 255), width=2)
    # hull and deck cargo
    d.polygon([(x0 + 24, y1 - 62), (x0 + 298, y1 - 62), (x0 + 282, y1 - 34),
               (x0 + 40, y1 - 34)], fill=(30, 30, 30))
    for bx in (x0 + 44, x0 + 96, x0 + 148):
        d.rectangle([bx, y1 - 92, bx + 44, y1 - 62], fill=(176, 58, 46))
    d.rectangle([x0 + 236, y1 - 96, x0 + 262, y1 - 62], fill=(90, 90, 90))
    # funnel smoke
    for i, r in enumerate((9, 7, 5)):
        d.ellipse([x0 + 246 + i * 8, y1 - 118 - i * 10,
                   x0 + 246 + i * 8 + 2 * r, y1 - 118 - i * 10 + 2 * r],
                  fill=(150, 150, 150))


def draw_chip(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(237, 231, 216))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # pins
    for i in range(5):
        px = x0 + 96 + i * 22
        d.rectangle([px, cy - 52, px + 8, cy - 38], fill=(120, 120, 120))
        d.rectangle([px, cy + 38, px + 8, cy + 52], fill=(120, 120, 120))
        py = y0 + 22 + i * 16
        d.rectangle([cx - 62, py, cx - 48, py + 7], fill=(120, 120, 120))
        d.rectangle([cx + 48, py, cx + 62, py + 7], fill=(120, 120, 120))
    # chip body
    d.rectangle([cx - 48, cy - 38, cx + 48, cy + 38], fill=(46, 64, 83))
    d.rectangle([cx - 28, cy - 20, cx + 28, cy + 20], outline=GOLD, width=2)
    f = SANS_B(26)
    t = "AI"
    tw = d.textlength(t, font=f)
    d.text((cx - tw / 2, cy - 16), t, font=f, fill=(255, 255, 255))


def draw_virus(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=(247, 232, 232))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # spikes
    import math
    for k in range(12):
        a = k * math.pi / 6
        x2 = cx + int(52 * math.cos(a))
        y2 = cy + int(52 * math.sin(a))
        d.line([(cx + int(30 * math.cos(a)), cy + int(30 * math.sin(a))),
                (x2, y2)], fill=(176, 58, 46), width=4)
        d.ellipse([x2 - 5, y2 - 5, x2 + 5, y2 + 5], fill=(176, 58, 46))
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(150, 40, 40))
    for dx, dy in ((-12, -8), (10, -12), (-4, 10), (14, 8)):
        d.ellipse([cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4],
                  fill=(220, 120, 110))


PANELS = [
    dict(kicker="UKRAINE", color=(31, 78, 121), art=draw_bridge,
         head="Crimea bridge falls",
         deck="Ukraine hits the Kerch bridge; its road arch collapses. Russia strikes Kyiv's bridges overnight.",
         fact="2 KILLED, TRAFFIC HALTED"),
    dict(kicker="ASIA", color=(176, 58, 46), art=draw_jet,
         head="Jets scramble over Japan",
         deck="Two suspected Russian planes enter Japanese airspace; Tokyo protests to Moscow.",
         fact="FIRST BREACH SINCE SEPT 2024"),
    dict(kicker="SUDAN", color=(125, 102, 8), art=draw_drone,
         head="Sudan's drone dead",
         deck="UN: 2,230 civilians verified killed this year; over 1,630 died in drone strikes.",
         fact="KORDOFAN WORST HIT"),
    dict(kicker="YEMEN", color=(17, 122, 101), art=draw_tanker,
         head="Houthis close in on Aden",
         deck="Fighters advance to about 60 km of the port city; government troops dig in to defend it.",
         fact="SAUDI REPLACES COALITION CHIEF"),
    dict(kicker="TECHNOLOGY", color=(108, 52, 131), art=draw_chip,
         head="Nvidia beats, Wall St falls",
         deck="Chipmaker tops forecasts and guides to $130bn; S&P 500 hits its lowest close since July.",
         fact="REVENUE $115.8BN, UP 103%"),
    dict(kicker="AMERICA", color=(26, 82, 118), art=draw_virus,
         head="Measles-free no more",
         deck="PAHO rules the US has lost its measles elimination status; 5,412 cases in 2026, most since 1991.",
         fact="96% OF CASES UNVACCINATED"),
]

STRIP = [
    "Pentagon fails its ninth audit in a row",
    "White House: agencies need its OK before staff testify",
    "US tightens AI-chip licences for five countries",
    "Depardieu drops appeal; assault conviction now final",
]


def render(path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top band ---
    d.rectangle([0, 0, W, 108], fill=(0, 0, 0))
    centre(d, 0, 8, W, "THE WORLD", SERIF_B(38), (255, 255, 255))
    centre(d, 0, 50, W, "ONE DAY, ONE PAGE", SANS_B(17), GOLD)
    centre(d, 0, 72, W, "TUESDAY 17 NOVEMBER 2026", SERIF_B(26),
           (255, 255, 255))
    d.rectangle([0, 108, W, 111], fill=GOLD)

    # --- six-panel grid ---
    mx, gap = 16, 12
    pw = (W - 2 * mx - 2 * gap) // 3          # 322
    ph = 395
    gy0 = 120
    for i, p in enumerate(PANELS):
        col, row = i % 3, i // 3
        x = mx + col * (pw + gap)
        y = gy0 + row * (ph + gap)
        d.rectangle([x, y, x + pw, y + ph], fill=(255, 255, 255),
                    outline=(180, 175, 160), width=1)
        # kicker strip
        d.rectangle([x, y, x + pw, y + 34], fill=p["color"])
        centre(d, x, y + 6, pw, p["kicker"], SANS_B(19), (255, 255, 255))
        # picture
        p["art"](d, x + 8, y + 42, x + pw - 8, y + 182)
        d.line([(x + 8, y + 182), (x + pw - 8, y + 182)],
               fill=(180, 175, 160), width=1)
        # headline, max 2 lines
        hf = SERIF_B(29)
        lines = wrap(d, p["head"], hf, pw - 24)
        assert len(lines) <= 2, p["head"]
        hy = y + 192
        for ln in lines:
            centre(d, x, hy, pw, ln, hf, INK)
            hy += 34
        # deck, max 3 lines
        df = SANS(18)
        dlines = wrap(d, p["deck"], df, pw - 24)
        assert len(dlines) <= 3, p["deck"]
        dy = hy + 6
        for ln in dlines:
            centre(d, x, dy, pw, ln, df, (50, 50, 50))
            dy += 22
        # key-fact line
        centre(d, x, dy + 8, pw, p["fact"], SANS_B(15), p["color"])

    # --- bottom band ---
    by = 922
    d.rectangle([0, by, W, by + 3], fill=(0, 0, 0))
    sf = SANS(16)
    line1 = "ALSO TODAY:  " + STRIP[0] + "  \u2022  " + STRIP[1]
    line2 = STRIP[2] + "  \u2022  " + STRIP[3]
    centre(d, 0, by + 10, W, line1, SANS_B(16), INK)
    centre(d, 0, by + 32, W, line2, SANS(16), (50, 50, 50))
    centre(d, 0, by + 56, W,
           "Every story above was reported on Tuesday 17 November 2026.",
           SERIF_I(15), INK)
    centre(d, 0, by + 78, W,
           "Sources: Reuters \u00b7 AP \u00b7 BBC News \u00b7 OHCHR \u00b7 The Guardian",
           SANS(13), (100, 100, 100))

    img.save(path, "PNG")
    return img


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    render(out)
    data = open(out, "rb").read()
    print("entry.png", len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())
