#!/usr/bin/env python3
"""SIGNAL YouTube channel banner. 2560x1440 with all key content inside the
1546x423 always-visible safe area. Backdrop from Higgsfield (letterbox cropped),
center scrim for legibility, ping-glyph + SIGNAL wordmark + tagline + kicker.
Exports banner.png + banner.jpg (<6MB) + _qc_banner_safe.png (safe-area guide)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad"
ANTON = os.path.join(SCRATCH, "fonts", "Anton-Regular.ttf")
ARCHIVO = os.path.join(SCRATCH, "fonts", "ArchivoBlack-Regular.ttf")
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
CY = (46, 224, 232)
INK = (233, 239, 247)
MUT = (150, 175, 195)
NOISE = (242, 178, 76)
W, H = 2560, 1440
SAFE_W, SAFE_H = 1546, 423
BG = os.path.join(HERE, "plates", "banner_bg_B.png")


def f(p, s): return ImageFont.truetype(p, s)


def line_w(d, t, fo, tr=0):
    b = d.textbbox((0, 0), t, font=fo); return (b[2]-b[0]) + tr*max(0, len(t)-1)


def track(d, xy, t, fo, fill, tr):
    x, y = xy
    for ch in t:
        d.text((x, y), ch, font=fo, fill=fill)
        b = d.textbbox((0, 0), ch, font=fo); x += (b[2]-b[0]) + tr


def prep_backdrop():
    im = Image.open(BG).convert("RGB")
    # crop baked letterbox: trim ~12% top and bottom, keep full width
    w, h = im.size
    cut = int(h*0.12)
    im = im.crop((0, cut, w, h-cut))
    im = ImageOps.fit(im, (W, H), method=Image.LANCZOS, centering=(0.5, 0.5))
    return im


def center_scrim(im, cx, cy, rw, rh, power=150):
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], fill=power)
    m = m.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGB", (W, H), (3, 6, 10))
    return Image.composite(dark, im, m)


def build():
    im = prep_backdrop()
    cx, cy = W//2, H//2
    im = center_scrim(im, cx, cy-10, 760, 300, power=165)
    base = im.convert("RGBA")

    # --- lockup: ping glyph + SIGNAL, centered ---
    glyph = Image.open(os.path.join(HERE, "mark_only.png")).convert("RGBA")
    g = 190
    glyph = glyph.resize((g, g), Image.LANCZOS)
    fo = f(ANTON, 176)
    d = ImageDraw.Draw(base)
    word = "SIGNAL"
    ww = line_w(d, word, fo)
    gap = 40
    wy = cy - 150
    # center the WORDMARK optically; hang glyph to its left
    tx = cx - ww//2 + 20
    x0 = tx - gap - g
    # glyph vertically centered to the wordmark cap height
    gy = wy - 6
    # glow for glyph
    gl = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gl.alpha_composite(glyph, (x0, gy))
    gl = gl.filter(ImageFilter.GaussianBlur(16))
    base.alpha_composite(gl)
    base.alpha_composite(glyph, (x0, gy))
    # wordmark with glow + stroke
    tgl = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(tgl).text((tx, wy), word, font=fo, fill=CY+(255,))
    tgl = tgl.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(tgl)
    d.text((tx, wy), word, font=fo, fill=INK+(255,), stroke_width=4, stroke_fill=(6, 8, 12, 255))

    # --- tagline ---
    tag = "THE EVIDENCE BEHIND SPACE'S BIGGEST CLAIMS"
    tfo = f(FMB, 40)
    tr = 4
    tw = line_w(d, tag, tfo, tr)
    ty = wy + 200
    # divider rule
    d.line([(cx-tw//2-40, ty-26), (cx-tw//2-18, ty-26)], fill=CY+(255,), width=4)
    d.line([(cx+tw//2+18, ty-26), (cx+tw//2+40, ty-26)], fill=CY+(255,), width=4)
    track(d, (cx-tw//2, ty), tag, tfo, INK+(255,), tr)

    # --- kicker: format + cadence, with signal/noise cue ---
    kick = "CLAIM   ·   EVIDENCE   ·   VERDICT"
    kfo = f(FM, 34); ktr = 6
    kw = line_w(d, kick, kfo, ktr)
    ky = ty + 70
    track(d, (cx-kw//2, ky), kick, kfo, MUT+(255,), ktr)
    # tiny SIGNAL(cyan)->NOISE(amber) bar under kicker
    bw, bh = 360, 8
    bx = cx-bw//2; by = ky+62
    for i in range(bw):
        t = i/bw
        r = int(46+(242-46)*t); gg = int(224+(178-224)*t); b = int(232+(76-232)*t)
        d.line([(bx+i, by), (bx+i, by+bh)], fill=(r, gg, b, 255))
    d.text((bx-96, by-8), "SIGNAL", font=f(FM, 22), fill=CY+(230,))
    d.text((bx+bw+18, by-8), "NOISE", font=f(FM, 22), fill=NOISE+(230,))

    out = base.convert("RGB")
    out.save(os.path.join(HERE, "banner.png"))
    q = 92
    jp = os.path.join(HERE, "banner.jpg")
    out.save(jp, "JPEG", quality=q, optimize=True)
    while os.path.getsize(jp) > 6_000_000 and q > 70:
        q -= 4; out.save(jp, "JPEG", quality=q, optimize=True)
    # QC with safe-area guides
    qc = out.copy(); qd = ImageDraw.Draw(qc)
    sx, sy = (W-SAFE_W)//2, (H-SAFE_H)//2
    qd.rectangle([sx, sy, sx+SAFE_W, sy+SAFE_H], outline=(255, 80, 80), width=3)
    qd.text((sx+8, sy+8), "SAFE AREA 1546x423 (always visible)", font=f(FMB, 26), fill=(255, 120, 120))
    # tv/desktop visible ~2560x423 center band
    qc.resize((1280, 720), Image.LANCZOS).save(os.path.join(HERE, "_qc_banner_safe.png"))
    print(f"banner.png {out.size}  jpg {os.path.getsize(jp)//1024}KB q{q}")


build()
