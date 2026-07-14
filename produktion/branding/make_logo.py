#!/usr/bin/env python3
"""SIGNAL channel logo/avatar. Pure-Pillow vector-style mark: a tracked cyan signal source
(bright dot + broadcast arcs + reticle ticks) on a deep-space circular badge. Exports:
- avatar_full.png  800x800  circular badge + SIGNAL wordmark (channel avatar)
- mark_only.png    800x800  transparent, just the glyph (video watermark / overlays)
- avatar_512.png / _88.png / _48.png  downscales for QC at feed sizes."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad"
ANTON = os.path.join(SCRATCH, "fonts", "Anton-Regular.ttf")
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
CY = (46, 224, 232)
CYd = (46, 224, 232, 130)
INK = (233, 239, 247)
BG0 = (12, 20, 30)
BG1 = (5, 7, 11)
S = 800


def radial_bg(size, c0, c1):
    im = Image.new("RGB", (size, size), c1)
    px = im.load()
    cx = cy = size / 2
    R = size * 0.62
    for y in range(size):
        for x in range(0, size):
            d = ((x-cx)**2 + (y-cy)**2)**0.5 / R
            d = min(1, d)
            px[x, y] = (int(c0[0]+(c1[0]-c0[0])*d),
                        int(c0[1]+(c1[1]-c0[1])*d),
                        int(c0[2]+(c1[2]-c0[2])*d))
    return im


def draw_mark(d, cx, cy, scale, alpha=255, bold=1.0):
    """The signal glyph: broadcast arcs (upper-right) + reticle ring/ticks + bright core dot.
    bold multiplies stroke widths for legibility at tiny avatar sizes."""
    col = CY + (alpha,)
    colf = (46, 224, 232, int(alpha*0.55))
    lw = lambda base: max(3, int(base*scale*bold))
    # outer reticle ring
    r = int(150*scale)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=col, width=lw(8))
    # reticle ticks N/E/S/W crossing the ring
    tk = int(34*scale)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        x1 = cx+math.cos(a)*(r-tk); y1 = cy+math.sin(a)*(r-tk)
        x2 = cx+math.cos(a)*(r+tk); y2 = cy+math.sin(a)*(r+tk)
        d.line([(x1, y1), (x2, y2)], fill=col, width=lw(9))
    # broadcast arcs radiating upper-right (the "signal")
    for i, rr in enumerate((int(60*scale), int(98*scale), int(136*scale))):
        wdt = lw(15-i*3)
        d.arc([cx-rr, cy-rr, cx+rr, cy+rr], start=-72, end=12,
              fill=(colf if i == 2 else col), width=wdt)
    # bright core dot
    cr = int(30*scale)
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=col)
    cr2 = int(15*scale)
    d.ellipse([cx-cr2, cy-cr2, cx+cr2, cy+cr2], fill=(255, 255, 255, alpha))


def build_avatar(mode="avatar", transparent=False):
    """mode: 'avatar' = bold glyph filling the disc, NO text (reads at 48px);
             'wordmark' = glyph + SIGNAL text lockup (for larger uses)."""
    with_text = (mode == "wordmark")
    if transparent:
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    else:
        im = radial_bg(S, BG0, BG1).convert("RGBA")
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if with_text:
        cx, cy, sc, bold = S//2, S//2 - 56, 1.0, 1.0
    else:
        cx, cy, sc, bold = S//2, S//2, 1.55, 1.25   # big + bold, fills disc
    draw_mark(d, cx, cy, sc, bold=bold)
    glow = lay.filter(ImageFilter.GaussianBlur(18))
    im.alpha_composite(glow)
    im.alpha_composite(lay)
    if with_text:
        d2 = ImageDraw.Draw(im)
        fo = ImageFont.truetype(ANTON, 132)
        t = "SIGNAL"
        b = d2.textbbox((0, 0), t, font=fo); tw = b[2]-b[0]
        ty = cy + int(150*sc) + 30
        d2.text((S//2-tw//2, ty), t, font=fo, fill=INK+(255,),
                stroke_width=3, stroke_fill=(6, 8, 12, 255))
    if not transparent:
        mask = Image.new("L", (S, S), 0)
        ImageDraw.Draw(mask).ellipse([6, 6, S-6, S-6], fill=255)
        disc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        disc.paste(im, (0, 0), mask)
        ImageDraw.Draw(disc).ellipse([6, 6, S-6, S-6], outline=CY+(170,), width=6)
        im = disc
    return im


os.makedirs(HERE, exist_ok=True)
av = build_avatar(mode="avatar")
av.convert("RGBA").save(os.path.join(HERE, "avatar_full.png"))
wm = build_avatar(mode="wordmark")
wm.convert("RGBA").save(os.path.join(HERE, "avatar_wordmark.png"))
mark = build_avatar(mode="avatar", transparent=True)
mark.save(os.path.join(HERE, "mark_only.png"))
for sz in (512, 88, 48):
    av.resize((sz, sz), Image.LANCZOS).save(os.path.join(HERE, f"avatar_{sz}.png"))
print("logo built: avatar_full (bold, no text), avatar_wordmark, mark_only, QC 512/88/48")
