#!/usr/bin/env python3
"""SIGNAL canonical brand mark — RINGED PLANET (general cosmic, supersedes the reticle mark).
Polished Saturn: shaded sphere + rim-light crescent + 3D ring (back arc behind, front arc in
front) + glow + context stars. Same premium cyan/dark palette.
Outputs (canonical, overwrite): avatar_full.png (textless bold), avatar_wordmark.png,
mark_only.png (transparent watermark). + QC strip at 512/88/48."""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad"
ANTON = os.path.join(SCRATCH, "fonts", "Anton-Regular.ttf")
CY = (46, 224, 232)
CYb = (150, 244, 249)
INK = (233, 239, 247)
WHITE = (255, 255, 255)
BG0 = (13, 22, 32)
BG1 = (5, 7, 11)
S = 800
SS = 3
Z = S*SS
TILT = -24


def radial_bg(size, c0, c1):
    im = Image.new("RGB", (size, size), c1); px = im.load()
    cx = cy = size/2; R = size*0.62
    for y in range(size):
        for x in range(size):
            d = min(1, ((x-cx)**2+(y-cy)**2)**0.5/R)
            px[x, y] = (int(c0[0]+(c1[0]-c0[0])*d), int(c0[1]+(c1[1]-c0[1])*d), int(c0[2]+(c1[2]-c0[2])*d))
    return im


def sphere(cx, cy, R):
    """Shaded planet sphere: dark body, cyan rim-light crescent lower-right, terminator shading."""
    lay = Image.new("RGBA", (Z, Z), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # body radial: lighter toward light dir (lower-right), darker upper-left
    body = Image.new("RGBA", (Z, Z), (0, 0, 0, 0)); bpx = body.load()
    lx, ly = cx+R*0.5, cy+R*0.5
    for yy in range(cy-R, cy+R):
        for xx in range(cx-R, cx+R):
            if (xx-cx)**2+(yy-cy)**2 <= R*R:
                t = 1 - min(1, (((xx-lx)**2+(yy-ly)**2)**0.5)/(R*1.7))
                r = int(10+34*t); g = int(20+90*t); b = int(30+110*t)
                bpx[xx, yy] = (r, g, b, 255)
    lay.alpha_composite(body)
    # bright cyan rim-light crescent (lower-right limb)
    d.arc([cx-R, cy-R, cx+R, cy+R], start=-58, end=118, fill=CY+(255,), width=int(11*SS/1.0))
    d.arc([cx-R, cy-R, cx+R, cy+R], start=-40, end=95, fill=CYb+(255,), width=int(4*SS))
    return lay


def ring_layer(rw, rh, band, color, width):
    lay = Image.new("RGBA", (Z, Z), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx = cy = Z//2
    d.ellipse([cx-rw, cy-rh, cx+rw, cy+rh], outline=color, width=width)
    # thin inner structure line
    d.ellipse([cx-int(rw*0.82), cy-int(rh*0.82), cx+int(rw*0.82), cy+int(rh*0.82)],
              outline=(color[0], color[1], color[2], 150), width=max(2, width//3))
    return lay.rotate(TILT, resample=Image.BICUBIC, center=(cx, cy))


def mark_saturn():
    lay = Image.new("RGBA", (Z, Z), (0, 0, 0, 0))
    cx = cy = Z//2
    R = int(Z*0.185)
    rw, rh = int(Z*0.34), int(Z*0.115)
    ring = ring_layer(rw, rh, None, CY, int(10*SS))
    sph = sphere(cx, cy, R)
    # BACK half of ring (above sphere's tilted center): mask to upper region
    back_mask = Image.new("L", (Z, Z), 0)
    ImageDraw.Draw(back_mask).rectangle([0, 0, Z, cy], fill=255)
    back = Image.new("RGBA", (Z, Z), (0, 0, 0, 0))
    back.paste(ring, (0, 0), Image.composite(ring.split()[3], Image.new("L", (Z, Z), 0), back_mask))
    # FRONT half (below center)
    front_mask = Image.new("L", (Z, Z), 0)
    ImageDraw.Draw(front_mask).rectangle([0, cy, Z, Z], fill=255)
    front = Image.new("RGBA", (Z, Z), (0, 0, 0, 0))
    front.paste(ring, (0, 0), Image.composite(ring.split()[3], Image.new("L", (Z, Z), 0), front_mask))
    lay.alpha_composite(back)
    lay.alpha_composite(sph)
    lay.alpha_composite(front)
    return lay


def build(mode="avatar", transparent=False):
    with_text = (mode == "wordmark")
    if transparent:
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    else:
        im = radial_bg(S, BG0, BG1).convert("RGBA")
        # context stars in the disc
        d0 = ImageDraw.Draw(im)
        for (sx, sy, sr) in [(0.20, 0.24, 3), (0.80, 0.30, 4), (0.26, 0.76, 3), (0.78, 0.74, 3), (0.62, 0.18, 2)]:
            px, py = int(S*sx), int(S*sy)
            d0.ellipse([px-sr, py-sr, px+sr, py+sr], fill=(200, 225, 238, 220))
    markZ = mark_saturn()
    # scale/position: bigger for textless avatar, higher for wordmark
    if with_text:
        scale = 0.82; oy = -60
    else:
        scale = 1.14; oy = 0
    newsize = int(Z*scale)
    m = markZ.resize((newsize, newsize), Image.LANCZOS)
    # glow
    glow = m.filter(ImageFilter.GaussianBlur(int(9*SS*scale)))
    # downscale mark to badge space
    def to_badge(img):
        b = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        r = img.resize((int(img.width/SS), int(img.height/SS)), Image.LANCZOS)
        b.alpha_composite(r, ((S-r.width)//2, (S-r.height)//2 + oy))
        return b
    im.alpha_composite(to_badge(glow))
    im.alpha_composite(to_badge(m))
    if with_text:
        d2 = ImageDraw.Draw(im)
        fo = ImageFont.truetype(ANTON, 132)
        t = "SIGNAL"; b = d2.textbbox((0, 0), t, font=fo); tw = b[2]-b[0]
        d2.text((S//2-tw//2, S//2+118), t, font=fo, fill=INK+(255,), stroke_width=3, stroke_fill=(6, 8, 12, 255))
    if not transparent:
        mask = Image.new("L", (S, S), 0); ImageDraw.Draw(mask).ellipse([6, 6, S-6, S-6], fill=255)
        disc = Image.new("RGBA", (S, S), (0, 0, 0, 0)); disc.paste(im, (0, 0), mask)
        ImageDraw.Draw(disc).ellipse([6, 6, S-6, S-6], outline=CY+(170,), width=6)
        im = disc
    return im


av = build("avatar"); av.convert("RGBA").save(os.path.join(HERE, "avatar_full.png"))
wm = build("wordmark"); wm.convert("RGBA").save(os.path.join(HERE, "avatar_wordmark.png"))
mk = build("avatar", transparent=True); mk.save(os.path.join(HERE, "mark_only.png"))
# QC
strip = Image.new("RGB", (256+256+88+48+140, 300), (30, 32, 36)); sd = ImageDraw.Draw(strip)
fo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 20)
strip.paste(av.resize((256, 256), Image.LANCZOS).convert("RGB"), (20, 30), av.resize((256, 256), Image.LANCZOS))
sd.text((20, 8), "AVATAR", font=fo, fill=(220, 224, 228))
strip.paste(wm.resize((256, 256), Image.LANCZOS).convert("RGB"), (290, 30), wm.resize((256, 256), Image.LANCZOS))
sd.text((290, 8), "wordmark", font=fo, fill=(220, 224, 228))
strip.paste(av.resize((88, 88), Image.LANCZOS).convert("RGB"), (560, 60), av.resize((88, 88), Image.LANCZOS))
sd.text((560, 40), "88px", font=fo, fill=(220, 224, 228))
strip.paste(av.resize((48, 48), Image.LANCZOS).convert("RGB"), (668, 60), av.resize((48, 48), Image.LANCZOS))
sd.text((668, 40), "48px", font=fo, fill=(220, 224, 228))
strip.save(os.path.join(HERE, "_qc_avatar.png"))
print("brand mark (Saturn) built: avatar_full, avatar_wordmark, mark_only + _qc_avatar")
