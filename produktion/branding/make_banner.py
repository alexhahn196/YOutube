#!/usr/bin/env python3
"""SIGNAL YouTube banner — professional layout, measured vertical rhythm (no overlap).
2560x1440; all content inside the 1546x423 safe area. Backdrop from Higgsfield (letterbox
cropped) + center scrim. Stack: [Saturn glyph + SIGNAL] · cyan divider · tagline · format line,
each row measured via textbbox and spaced with real gaps, block vertically centered."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad"
ANTON = os.path.join(SCRATCH, "fonts", "Anton-Regular.ttf")
FM = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
CY = (46, 224, 232)
INK = (233, 239, 247)
MUT = (156, 182, 200)
W, H = 2560, 1440
SAFE_W, SAFE_H = 1546, 423
CX, CY_ = W // 2, H // 2
BG = os.path.join(HERE, "plates", "banner_bg_B.png")

_d = ImageDraw.Draw(Image.new("RGB", (4, 4)))


def font(p, s): return ImageFont.truetype(p, s)


def measure(t, fo, tr=0):
    """returns (width, top, bottom) — top/bottom are y-extent relative to draw origin."""
    b = _d.textbbox((0, 0), t, font=fo)
    w = (b[2] - b[0]) + tr * max(0, len(t) - 1)
    return w, b[1], b[3]


def track_draw(d, x, y, t, fo, fill, tr):
    for ch in t:
        d.text((x, y), ch, font=fo, fill=fill)
        bb = d.textbbox((0, 0), ch, font=fo)
        x += (bb[2] - bb[0]) + tr


def prep_backdrop():
    im = Image.open(BG).convert("RGB")
    w, h = im.size
    cut = int(h * 0.12)                 # trim baked letterbox
    im = im.crop((0, cut, w, h - cut))
    return ImageOps.fit(im, (W, H), method=Image.LANCZOS, centering=(0.5, 0.5))


def center_scrim(im, rw, rh, power=175):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([CX - rw, CY_ - rh, CX + rw, CY_ + rh], fill=power)
    m = m.filter(ImageFilter.GaussianBlur(230))
    return Image.composite(Image.new("RGB", (W, H), (3, 6, 10)), im, m)


def build():
    im = center_scrim(prep_backdrop(), 820, 320).convert("RGBA")
    d = ImageDraw.Draw(im)

    # ---- type specs ----
    word_fo = font(ANTON, 150)
    tag_fo = font(FMB, 31); tag_tr = 7
    fmt_fo = font(FM, 27); fmt_tr = 12
    tagline = "THE EVIDENCE BEHIND SPACE'S BIGGEST CLAIMS"
    fmt = "CLAIM     ·     EVIDENCE     ·     VERDICT"

    # ---- glyph ----
    glyph = Image.open(os.path.join(HERE, "mark_only.png")).convert("RGBA")
    G = 168
    glyph = glyph.resize((G, G), Image.LANCZOS)

    # ---- measure rows ----
    word = "SIGNAL"
    ww, wtop, wbot = measure(word, word_fo)
    wh = wbot - wtop                       # visual cap height
    lockup_h = max(G, wh)
    tw, ttop, tbot = measure(tagline, tag_fo, tag_tr); th = tbot - ttop
    fw, ftop, fbot = measure(fmt, fmt_fo, fmt_tr); fh = fbot - ftop

    GAP1 = 60      # lockup -> divider/tagline (generous, kills the old overlap)
    GAP2 = 30      # tagline -> format
    total = lockup_h + GAP1 + th + GAP2 + fh
    top = CY_ - total // 2                  # vertically center the whole block

    # ---- row 1: lockup (glyph + wordmark), horizontally centered ----
    gap_gw = 34
    lock_w = G + gap_gw + ww
    lx = CX - lock_w // 2
    row1_mid = top + lockup_h // 2
    # glyph centered on the row
    gy = int(row1_mid - G / 2)
    gl = Image.new("RGBA", im.size, (0, 0, 0, 0)); gl.alpha_composite(glyph, (lx, gy))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))
    im.alpha_composite(glyph, (lx, gy))
    # wordmark: draw so its visual top sits at row top; align vertical center to row_mid
    tx = lx + G + gap_gw
    wy = int(row1_mid - wh / 2 - wtop)
    tgl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(tgl).text((tx, wy), word, font=word_fo, fill=CY + (255,))
    im.alpha_composite(tgl.filter(ImageFilter.GaussianBlur(20)))
    d.text((tx, wy), word, font=word_fo, fill=INK + (255,), stroke_width=4, stroke_fill=(6, 8, 12, 255))

    # ---- divider rule (in the gap, centered) ----
    div_y = top + lockup_h + GAP1 // 2
    d.line([(CX - 90, div_y), (CX - 26, div_y)], fill=CY + (230,), width=3)
    d.line([(CX + 26, div_y), (CX + 90, div_y)], fill=CY + (230,), width=3)
    d.ellipse([CX - 4, div_y - 4, CX + 4, div_y + 4], fill=CY + (255,))

    # ---- row 2: tagline ----
    ty = top + lockup_h + GAP1 - ttop
    track_draw(d, CX - tw // 2, ty, tagline, tag_fo, INK + (255,), tag_tr)

    # ---- row 3: format line ----
    fy = top + lockup_h + GAP1 + th + GAP2 - ftop
    track_draw(d, CX - fw // 2, fy, fmt, fmt_fo, MUT + (255,), fmt_tr)

    out = im.convert("RGB")
    out.save(os.path.join(HERE, "banner.png"))
    q = 92; jp = os.path.join(HERE, "banner.jpg")
    out.save(jp, "JPEG", quality=q, optimize=True)
    while os.path.getsize(jp) > 6_000_000 and q > 70:
        q -= 4; out.save(jp, "JPEG", quality=q, optimize=True)

    # QC: safe-area guide + a tight center crop to verify no overlap
    qc = out.copy(); qd = ImageDraw.Draw(qc)
    sx, sy = (W - SAFE_W) // 2, (H - SAFE_H) // 2
    qd.rectangle([sx, sy, sx + SAFE_W, sy + SAFE_H], outline=(255, 90, 90), width=3)
    qd.text((sx + 8, sy + 8), "SAFE AREA 1546x423", font=font(FMB, 24), fill=(255, 120, 120))
    qc.resize((1280, 720), Image.LANCZOS).save(os.path.join(HERE, "_qc_banner_safe.png"))
    out.crop((CX - 660, CY_ - 210, CX + 660, CY_ + 210)).save(os.path.join(HERE, "_qc_center.png"))
    print(f"banner rebuilt {out.size}  jpg {os.path.getsize(jp)//1024}KB  block_h={total} in safe {SAFE_H}")


build()
