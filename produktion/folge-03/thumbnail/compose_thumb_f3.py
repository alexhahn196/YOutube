#!/usr/bin/env python3
"""SIGNAL F3 Thumbnail — §13-System (wie F2-Master):
- 1 Fokusobjekt (Voyager, Plate), 1 Textblock 2-4 Woerter, Cap-Height >=25% (>=180px/720)
- Weiss+Amber, 6-10px Stroke, KEIN Verdict/Verneinung (Schaufenster-Regel)
- Ziel: mittlere Luminanz >=85/255, <=35-40% near-black; Anton + Cyan-Brand-Chip
- Outputs: 3 Kandidaten + Feed-Mocks (168x94) + Graustufen-Squint + Master
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
HERE = os.path.dirname(os.path.abspath(__file__))
PLATE = os.path.join(HERE, "..", "thumbnail_plate.png")
FONTS = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad/fonts"
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
MONO  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
W, H = 1280, 720
INK = (245, 243, 232)
AMBER = (255, 179, 71)
CY = (46, 224, 232)

def load_plate(brighten=1.0, sat=1.0, gamma=0.80):
    im = Image.open(PLATE).convert("RGB")
    im = im.resize((W, H), Image.LANCZOS)
    lut = [min(255, int(255 * (i/255) ** gamma)) for i in range(256)] * 3
    im = im.point(lut)
    if brighten != 1.0: im = ImageEnhance.Brightness(im).enhance(brighten)
    if sat != 1.0: im = ImageEnhance.Color(im).enhance(sat)
    return im

def stroke_text(d, xy, txt, font, fill, stroke=6):
    d.text(xy, txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=(5,8,12))

def brand_chip(d):
    f = ImageFont.truetype(MONO, 26)
    d.ellipse([28, 30, 42, 44], fill=CY)
    d.text((52, 26), "SIGNAL", font=f, fill=INK, stroke_width=3, stroke_fill=(5,8,12))

def scrim(im, width=560):
    """Links-Scrim hinter Textzone fuer Lesbarkeit (sanfter Verlauf)."""
    ov = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(ov)
    for x in range(0, width):
        a = int(52 * (1 - x/width))
        ds.line([(x, 120), (x, 660)], fill=a)
    return Image.composite(Image.new("RGB", (W, H), (3, 5, 9)), im, ov)

def metrics(im):
    g = im.convert("L"); hist = g.histogram()
    total = sum(hist); mean = sum(i*c for i,c in enumerate(hist))/total
    near_black = sum(hist[:26])/total
    return mean, near_black

# ---- V1: "TURNED AROUND?" (Claim-Ride zum Titel) ----
def v1():
    im = scrim(load_plate(brighten=1.10, sat=1.10))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(ANTON, 168)
    f2 = ImageFont.truetype(ANTON, 196)
    stroke_text(d, (46, 180), "TURNED", f1, INK, 7)
    stroke_text(d, (42, 360), "AROUND?", f2, AMBER, 9)
    brand_chip(d)
    return im

# ---- V2: "ONE RISKY FIX LEFT" ----
def v2():
    im = scrim(load_plate(brighten=1.08, sat=1.08))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(ANTON, 150)
    f2 = ImageFont.truetype(ANTON, 176)
    stroke_text(d, (46, 150), "ONE RISKY", f1, INK, 7)
    stroke_text(d, (42, 320), "FIX LEFT", f2, AMBER, 9)
    f_sub = ImageFont.truetype(ANTON, 58)
    stroke_text(d, (50, 560), "25,000,000,000 KM AWAY", f_sub, INK, 4)
    brand_chip(d)
    return im

# ---- V3: "2 INSTRUMENTS LEFT" (Zahlen-Punch) ----
def v3():
    im = scrim(load_plate(brighten=1.10, sat=1.10))
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(ANTON, 240)
    f2 = ImageFont.truetype(ANTON, 120)
    stroke_text(d, (46, 150), "2", f1, AMBER, 10)
    stroke_text(d, (170, 240), "INSTRUMENTS", f2, INK, 6)
    stroke_text(d, (46, 420), "LEFT", ImageFont.truetype(ANTON, 190), AMBER, 9)
    brand_chip(d)
    return im

outs = {"v1_TURNEDAROUND": v1(), "v2_RISKYFIX": v2(), "v3_2INSTRUMENTS": v3()}
feed = Image.new("RGB", (3*168+40, 94+20), (15,15,15))
for i,(name,im) in enumerate(outs.items()):
    p = os.path.join(HERE, f"cand_{name}.jpg")
    im.save(p, quality=92)
    mean, nb = metrics(im)
    print(f"{name}: mean_lum={mean:.0f}/255  near_black={nb*100:.0f}%  {'OK' if mean>=85 and nb<=0.40 else 'CHECK'}")
    small = im.resize((168, 94), Image.LANCZOS)
    small.save(os.path.join(HERE, f"feed_{name}.jpg"), quality=90)
    feed.paste(small, (10+i*(168+10), 10))
    im.convert("L").resize((168,94)).save(os.path.join(HERE, f"gray_{name}.jpg"), quality=90)
feed.save(os.path.join(HERE, "feedmock_all.jpg"), quality=92)
print("3 Kandidaten + Feed-Mocks + Graustufen gebaut")
