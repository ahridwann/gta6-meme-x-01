#!/usr/bin/env python3
"""Draw the gta6-meme-x-01 meme (1024x1024 PNG).

Concept: a GTA 6 loading screen parody. Sunset over Leonida / Vice City,
palm silhouettes, a loading bar stuck at 99% after a 13-year wait, and
make.fun's ghost (the official press-kit mark) standing in the scene as the
one who's been waiting with you. All art drawn here with PIL; the ghost is
the official mark from https://make.fun/press/ (mark-1024.png), composited
in, never redrawn or altered beyond scaling.

Joke, in one line: waited 13 years for GTA 6, and the download is STILL
at 99%.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size):
    return ImageFont.truetype(FONT_BOLD, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, stops):
    """stops: list of (position 0..1, (r,g,b))."""
    img = Image.new("RGB", size)
    px = img.load()
    h = size[1]
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = lerp(c0, c1, f)
                break
        else:
            col = stops[-1][1]
        for x in range(size[0]):
            px[x, y] = col
    return img


def draw_palm(draw, base_x, base_y, height, lean, color):
    """A simple palm silhouette: curved trunk + smooth tapered frond blades."""
    top_x = base_x + lean
    top_y = base_y - height
    # trunk: thick segmented curve
    steps = 24
    prev = (base_x, base_y)
    for i in range(1, steps + 1):
        f = i / steps
        x = base_x + lean * f * f + math.sin(f * 2.2) * 6 * (1 - f)
        y = base_y - height * f
        draw.line([prev, (x, y)], fill=color, width=max(10, int(16 * (1 - f * 0.55))))
        prev = (x, y)
    # fronds: smooth tapered blades fanning out of the crown, drooping down
    for k in range(7):
        ang = math.radians(-168 + 156 * k / 6)  # fan across the top
        length = height * (0.40 + 0.08 * math.sin(k * 2.4))
        droop = length * 0.38
        center = []
        for j in range(13):
            t = j / 12
            x = top_x + math.cos(ang) * length * t
            y = top_y + math.sin(ang) * length * t + droop * t * t
            center.append((x, y))
        # build a tapered blade polygon from the centerline
        left, right = [], []
        for j, (x, y) in enumerate(center):
            t = j / (len(center) - 1)
            # perpendicular direction (approx from segment direction)
            j2 = min(j + 1, len(center) - 1)
            dx = center[j2][0] - center[max(j - 1, 0)][0]
            dy = center[j2][1] - center[max(j - 1, 0)][1]
            n = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / n, dx / n
            w = 13 * (1 - t) + 1.5
            left.append((x + nx * w, y + ny * w))
            right.append((x - nx * w, y - ny * w))
        draw.polygon(left + right[::-1], fill=color)


def main():
    random.seed(6)

    # --- sky: dusk gradient, purple -> magenta -> orange -------------------
    sky = vertical_gradient(
        (W, 700),
        [
            (0.00, (38, 12, 74)),
            (0.38, (122, 22, 110)),
            (0.68, (214, 48, 120)),
            (1.00, (255, 126, 61)),
        ],
    )
    img = Image.new("RGB", (W, H))
    img.paste(sky, (0, 0))

    # stars in the upper sky
    d = ImageDraw.Draw(img)
    for _ in range(70):
        x = random.randint(0, W - 1)
        y = random.randint(0, 260)
        r = random.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 220))

    # sun with glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy, sr = 512, 470, 120
    for rad, alpha in [(300, 28), (230, 45), (175, 70)]:
        gd.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(255, 170, 80, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - sr, cy - sr, cx + sr, cy + sr], fill=(255, 209, 102, 255))

    # distant skyline along the horizon
    horizon = 700
    skyline = (26, 8, 46)
    x = -20
    while x < W + 20:
        bw = random.randint(46, 110)
        bh = random.randint(50, 170)
        d.rectangle([x, horizon - bh, x + bw, horizon], fill=skyline)
        # a few lit windows
        for _ in range(random.randint(2, 7)):
            wx = random.randint(x + 6, x + bw - 10)
            wy = random.randint(horizon - bh + 8, horizon - 12)
            d.rectangle([wx, wy, wx + 5, wy + 7], fill=(255, 214, 130))
        x += bw + random.randint(4, 26)

    # sea: dark teal gradient + sunset reflection streak
    sea = vertical_gradient((W, H - horizon), [(0.0, (14, 74, 96)), (1.0, (7, 38, 58))])
    img.paste(sea, (0, horizon))
    d = ImageDraw.Draw(img)
    for i in range(26):
        y = horizon + 14 + i * 12
        wdt = random.randint(60, 200)
        xx = cx - wdt // 2 + random.randint(-40, 40)
        # keep the streaks out of the center column where the ghost stands
        if xx + wdt > 360 and xx < 664:
            continue
        d.line([(xx, y), (xx + wdt, y)], fill=(255, 150, 90), width=3)

    # palm silhouettes framing the scene
    palm = (24, 7, 40)
    draw_palm(d, 60, H - 8, 430, 130, palm)
    draw_palm(d, 985, H - 8, 390, -120, palm)
    draw_palm(d, 150, H - 8, 300, 90, palm)

    # --- headline ----------------------------------------------------------
    def text_center(y, s, fnt, fill, stroke=0, stroke_fill=(0, 0, 0)):
        tw = d.textlength(s, font=fnt)
        d.text(((W - tw) / 2, y), s, font=fnt, fill=fill,
               stroke_width=stroke, stroke_fill=stroke_fill)

    text_center(58, "GTA 6", font(168), (255, 255, 255), stroke=7, stroke_fill=(12, 4, 24))
    # letterspaced subtitle
    sub = "W E L C O M E   T O   L E O N I D A"
    text_center(252, sub, font(46), (255, 233, 168), stroke=3, stroke_fill=(12, 4, 24))

    # --- loading bar, stuck at 99% ----------------------------------------
    bx0, bx1, by0, by1 = 150, 874, 372, 436
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=32,
                        outline=(255, 255, 255), width=6)
    fill_to = bx0 + int((bx1 - bx0 - 12) * 0.99)
    d.rounded_rectangle([bx0 + 6, by0 + 6, fill_to, by1 - 6], radius=26,
                        fill=(230, 0, 126))
    text_center(by0 + 8, "99%", font(40), (255, 255, 255), stroke=2, stroke_fill=(12, 4, 24))

    # --- punchline ---------------------------------------------------------
    text_center(468, "13 YEARS LATER\u2026 STILL 99%.", font(50),
                (255, 255, 255), stroke=4, stroke_fill=(12, 4, 24))

    # --- make.fun ghost, standing in the scene -----------------------------
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([392, 900, 632, 938], fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, shadow)

    ghost = Image.open(os.path.join(HERE, "assets", "mark-1024.png")).convert("RGBA")
    ghost = ghost.resize((252, 252), Image.LANCZOS)
    img.alpha_composite(ghost, (386, 648))

    d = ImageDraw.Draw(img)
    text_center(928, "make.fun", font(46), (255, 255, 255), stroke=3, stroke_fill=(12, 4, 24))

    out = os.path.join(HERE, "meme.png")
    img.convert("RGB").save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
